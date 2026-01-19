from watchdog.observers import Observer

from StateController import State
import SyncController as Sync
import GoogleCalendar as GCal
import Things.api as things
import system # import FileChangeHandler, caffeinate, things_database_file_path
import config

from datetime import datetime
from logging.handlers import RotatingFileHandler
import logging
import time


def main(state: State, service):
    if state.detect_task_updates():
        updated_tasks: list[dict] = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)
        updated_events: list[dict] = GCal.get_upcoming_events(service, calendar_id=config.THINGS_CALENDAR_ID).get('items')

        changes = []
        
        if new := Sync.add_new_tasks_to_calendar(updated_tasks, updated_events):
            changes.extend(new)

        if updates := Sync.update_tasks_on_calendar(updated_events):
            changes.extend(updates)
        
        if config.ZEN_MODE == True:
            completed = Sync.remove_completed_tasks(updated_tasks, updated_events)
            changes.extend(completed)
                
        if changes:
            Sync.sync_calendar_changes(service, changes)

        state.current_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)


        if config.DEADLINES_CALENDAR == True and state.detect_deadline_updates():
            updated_deadlines: list[dict] = things.deadlines()
            updated_deadline_events: list[dict] = GCal.get_upcoming_events(service, calendar_id=config.DEADLINES_CALENDAR_ID).get('items')
            
            deadline_changes: list[dict] = []

            deadline_changes.extend(Sync.add_new_deadline_to_calendar(updated_deadlines, updated_deadline_events))
            
            if detected_updates := state.list_updated_deadlines(updated_deadlines):
                deadline_changes.extend(Sync.update_deadlines_on_calendar(detected_updates, updated_deadline_events))

            if config.ZEN_MODE == True:
                completed_deadlines = Sync.remove_completed_deadlines(updated_deadlines, updated_deadline_events)
                deadline_changes.extend(completed_deadlines)

            if deadline_changes:
                Sync.sync_calendar_changes(service, deadline_changes)

            state.current_deadlines = things.deadlines()





if __name__ == "__main__":
    # Set the start time 
    start: time = datetime.now()
    
    # Set the logging level and format
    logging_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    date_fmt: str = "%Y-%m-%d %H:%M:%S"
    
    logs = logging.basicConfig(level=config.LOGGING_LEVEL,
                               format=config.LOGGING_FORMAT,
                               datefmt=config.DATE_FMT)
    
    if config.EXTERNAL_LOGGING == True:
        file_handler = RotatingFileHandler(
            filename="logs/PowerThings.log",
            maxBytes=255*1024*1024,
            backupCount=5
        )
        
        formatter = logging.Formatter(fmt=config.LOGGING_FORMAT, datefmt=config.DATE_FMT)
        file_handler.setFormatter(formatter)

        logging.getLogger().addHandler(file_handler)



    
    #Set the initial task state
    state = State()
    state.current_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)
    state.current_deadlines = things.deadlines()

    # Initiate the Google Calendar service/auth flow
    service = GCal.authenticate_google_calendar()

    # Subprocess to caffeinate the Mac while application is running to prevent sleep
    system.caffeinate()

    # Thead 1: Monitor Things db for changes to tasks
    try:
        # Point to the Things DB for monitoring and run main() when changes are detected to the Things DB
        path = system.things_database_file_path()
        filename = 'Things Database.thingsdatabase/main.sqlite'   
        event_handler = system.FileChangeHandler(filename, state, service)
        observer = Observer()
        observer.schedule(event_handler, path=path, recursive=True)
        observer.start()
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        end: time = datetime.now()
        logging.info(f"""\n\n\tThingSync stopped by KeyBoard Interupt\n\tRun time duration | {end - start}\n""")
    except Exception as e:
        observer.stop()
        end: time = datetime.now()
        logging.info(f"""\n\n\tThingSync encountered a fatal error. \n\tRun time duration | {end - start}\n-----ERROR BODY-----\n\n{e}""")

    
