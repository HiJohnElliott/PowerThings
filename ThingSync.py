"""Sync Service for Things and Calendar

This program will routinely check your tasks in Things and if they are not synced to your calendar, a new event is created so that your scheduled tasks appear. 

This program will also check on the times of existing task-events in Calendar and if the time of the event differs from the task, the task will be updated. 
"""
import logging
import time

from StateController import State
import SyncController as Sync
import GoogleCalendar as GCal
import Things.api as things
import system
import config


def main(state: State, service):
    if state.detect_state_updates():
        updated_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)
        updated_events = GCal.get_upcoming_events(service, calendar_id=config.THINGS_CALENDAR_ID).get('items')

        changes = []
        
        if new := state.list_new_tasks(updated_tasks):
            changes.extend(Sync.add_new_tasks_to_calendar(new, updated_events))
        
        if updates := state.list_updated_tasks(updated_tasks):
            changes.extend(Sync.update_tasks_on_calendar(updates, updated_events))
        
        if config.ZEN_MODE == True:
            completed = Sync.remove_completed_tasks(updated_tasks, updated_events)
            changes.extend(completed)
                
        if changes:
            Sync.sync_calendar_changes(service, changes)

        state.current_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)






if __name__ == "__main__":
    # Set the logging level
    logs = logging.basicConfig(level=logging.DEBUG,
                               format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                               datefmt="%Y-%m-%d %H:%M:%S")
    
    #Set the task state, and initiate the Google Calendar service/auth flow
    state = State()
    state.current_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)
    service = GCal.authenticate_google_calendar()

    # Subprocess to caffeinate the Mac while application is running to prevent sleep
    system.caffeinate()

    # Thead 1: Monitor Things db for changes to tasks
    while True:
        main(state, service)
        time.sleep(1)
   
    # Thread 2: Listen for change notifications from GCal 

    
