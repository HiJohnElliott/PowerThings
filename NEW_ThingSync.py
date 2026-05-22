# Built In modules
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Generator
import logging
import time

# Local Modules
from NEW_SyncController import sync_event_changes, sync_task_changes
from SyncTypes import Task, Event, TaskEvent, TaskChange, EventChange
from StateController import State
import GoogleCalendar as GCal
import config
import system # import FileChangeHandler, caffeinate, things_database_file_path
import things

# Third party modules
from watchdog.observers import Observer




def main(state: State, service, first_run: bool = False):
	try:
		current_tasks: list[dict] = things.upcoming() + things.today() + things.completed(last=config.COMPLETED_SCOPE)	
		current_events = GCal.get_upcoming_events(
			service=service, 
			state=state,
			calendar_id=config.THINGS_CALENDAR_ID
		).get("items")	
	except Exception as e:
		logging.error(f"Main() function cannot run due to error gathering tasks or calendar events\n{e}")
		return
	
	# state.current_tasks = current_tasks
	# state.current_events = current_events
		
	if state.detect_task_updates(current_tasks) or first_run:
		all_events: list[Event] = [Event(event) for event in current_events]
		events: dict[str: Event] = {event.uuid: event for event in all_events if event.uuid}
		tasks: list[Task] = [Task(task) for task in current_tasks]
	
		taskEvents: list[TaskEvent] = []
		for t in tasks:
			matching_event = events.get(t.uuid)
			if matching_event:
				taskEvents.append(TaskEvent(t, matching_event))
			else:
				taskEvents.append(TaskEvent(t, None))
		
		task_changes: Generator = (task for task in taskEvents if task.task_change_type != TaskChange.NONE)
		event_changes: Generator = (task for task in taskEvents if task.task_change_type != EventChange.NONE)

		sync_task_changes(task_changes)
		sync_event_changes(service, event_changes)

		state.current_tasks = current_tasks
		state.current_events = current_events

		# Detect and make changes to the Deadlines calendar. 
		# if config.DEADLINES_CALENDAR and state.detect_deadline_updates():
		# 	try:
		# 		updated_deadlines: list[dict] = things.deadlines()
		# 		updated_deadline_events: list[dict] = GCal.get_upcoming_events(service, state=state, calendar_id=config.DEADLINES_CALENDAR_ID).get('items')
		# 	except Exception as e:
		# 		logging.error(f"main() cannot update deadlines due to an error: \n{e}")
		




if __name__ == "__main__":
	# Set the start time 
	start: time = datetime.now()
	
	
	# Set the logging level and format
	logging_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
	date_fmt: str = "%Y-%m-%d %H:%M:%S"
	
	logs = logging.basicConfig(
		level=config.LOGGING_LEVEL,
		format=config.LOGGING_FORMAT,
		datefmt=config.DATE_FMT
	)
	
	if config.EXTERNAL_LOGGING:
		file_handler = RotatingFileHandler(
			filename="logs/PowerThings.log",
			maxBytes=255*1024*1024,
			backupCount=5
		)
		formatter = logging.Formatter(fmt=config.LOGGING_FORMAT, datefmt=config.DATE_FMT)
		file_handler.setFormatter(formatter)
		logging.getLogger().addHandler(file_handler)


	# Initiate the Google Calendar service/auth flow
	service = GCal.authenticate_google_calendar()

	
	#Set the initial task state
	state = State()
	state.current_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)
	state.current_events = GCal.get_upcoming_events(service, state=state, calendar_id=config.THINGS_CALENDAR_ID).get('items')
	state.current_deadlines = things.deadlines()

	# Subprocess to caffeinate the Mac while application is running to prevent sleep
	system.caffeinate()
	
	# The main application. {}
	try:
		# Start by running the main update loop first to update calendars on start up.  
		main(state=state, service=service, first_run=True)
		
		# The main Loop when TWO_WAY_SYNC is activated
		if config.TWO_WAY_SYNC:
			while True: 
				main(state, service)
				time.sleep(config.SYNC_INTERVAL)

		else:
			# When NOT TWO_WAY_SYNC, monitoring the Things DB and run main() when changes are detected
			path = system.things_database_file_path()
			filename = 'Things Database.thingsdatabase/main.sqlite'   
			event_handler = system.FileChangeHandler(filename, state, service)
			observer = Observer()
			observer.schedule(event_handler, path=path, recursive=True)
			observer.start()
			observer.join()

	except KeyboardInterrupt:
		if not config.TWO_WAY_SYNC:
			observer.stop()
		end: time = datetime.now()
		logging.info(f"""\n\n\tThingSync stopped by KeyBoard Interupt\n\tRun time duration | {end - start}\n""")
	except Exception as e:
		if not config.TWO_WAY_SYNC:
			observer.stop()
		end: time = datetime.now()
		logging.info(f"\n\n\tThingSync encountered a fatal error. \n\tRun time duration | {end - start}\n----------ERROR BODY----------")
		logging.info(f"{e}")
		logging.info(f"{e.with_traceback()}")

	
