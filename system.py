from watchdog.events import FileSystemEventHandler
from ThingSync import main
import subprocess
import logging
import glob
import os



class FileChangeHandler(FileSystemEventHandler):
	def __init__(self, target_file, state, service):
		self.target_file = os.path.abspath(target_file)
		self.state = state
		self.service = service
		
	def on_modified(self, event):
		main(self.state, self.service)		



def caffeinate() -> None:
    PID = os.getpid()
    logging.debug(f"Caffeinating process number {PID}...")
    subprocess.Popen(['caffeinate', '-s', '-w', str(PID)])
    logging.debug(f"Caffeination successfull for process {PID}")



def things_database_file_path() -> str:			
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