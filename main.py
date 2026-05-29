# Built In modules
from logging.handlers import RotatingFileHandler
from datetime import datetime
import subprocess
import logging
import time
import glob
import os

# Local Modules
from Google import Calendar as GCal
from StateController import State
import ThingSync
import config

# Third party modules
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import things



class FileChangeHandler(FileSystemEventHandler):
	def __init__(self, target_file, state, service):
		self.target_file = os.path.abspath(target_file)
		self.state = state
		self.service = service
		
	def on_modified(self, event):
		ThingSync.sync(self.state, self.service)		



def _caffeinate() -> None:
    PID = os.getpid()
    logging.debug(f"Caffeinating process number {PID}...")
    subprocess.Popen(['caffeinate', '-s', '-w', str(PID)])
    logging.debug(f"Caffeination successfull for process {PID}")



def _things_database_file_path() -> str:			
		DEFAULT_FILEPATH_31616502 = (
		"~/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac"
		"/ThingsData-*/Things Database.thingsdatabase/main.sqlite"
		)
		DEFAULT_FILEPATH_31516502 = (
			"~/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac"
			"/Things Database.thingsdatabase/main.sqlite"
		)

		try:
			DEFAULT_FILEPATH = next(glob.iglob(os.path.expanduser(DEFAULT_FILEPATH_31616502)))
		except StopIteration:
			DEFAULT_FILEPATH = os.path.expanduser(DEFAULT_FILEPATH_31516502)

		return DEFAULT_FILEPATH




def main():
		# Set the start time 
	start: time = datetime.now()
	
	
	# Set the logging level and format
	logging.basicConfig(
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
	state.current_events = GCal.get_upcoming_events(service, state=state, calendar_id=config.THINGS_CALENDAR_ID)
	state.current_deadlines = things.deadlines()

	# Subprocess to caffeinate the Mac while application is running to prevent sleep
	_caffeinate()
	
	# The main application.
	try:
		# Start by running the main update loop first to update calendars on start up.  
		ThingSync.sync(state=state, service=service, first_run=True)
		
		# The main Loop when TWO_WAY_SYNC is activated
		if config.TWO_WAY_SYNC:
			while True: 
				ThingSync.sync(state, service)
				time.sleep(config.SYNC_INTERVAL)

		else:
			# When NOT TWO_WAY_SYNC, monitoring the Things DB and run main() when changes are detected
			path = _things_database_file_path()
			filename = 'Things Database.thingsdatabase/main.sqlite'   
			event_handler = FileChangeHandler(filename, state, service)
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



	
if __name__ == "__main__":
	main()