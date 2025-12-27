from dotenv import load_dotenv
import os

load_dotenv()

# This is the Google Calendar link that you want to point to to sync your tasks. 
THINGS_CALENDAR_ID: str = os.getenv('THINGS_CALENDAR_ID')

# Completed scope sets how far back you want this application to look for completed tasks. 
# If you have tasks that get moved from day to day 
COMPLETED_SCOPE: str = '90d'

# The default duration is in minutes. Duration tags can be toggled on and off. 
DEFAULT_DURATION: int = 60
DURATION_TAGS = True

# Zen Mode removes tasks from the calendar once they have been completed. 
# Leaving this as False means that once a task has been added, it stays on the calendar even after it has been completed.
ZEN_MODE: bool = True 

# Deadlines calendar settings 
DEADLINES_CALENDAR: bool = True
DEADLINES_CALENDAR_ID: str = os.getenv("DEADLINES_CALENDAR_ID")

# This is used when making any changes to tasks in Things using the applications URL scheme. 
THINGS_AUTH_TOKEN: str = os.getenv('THINGS_AUTH_TOKEN')

# This is for setting up your logging
EXTERNAL_LOGGING: bool = True
LOGGING_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FMT: str = "%Y-%m-%d %H:%M:%S"

# These are for turning 2-way sync on and off and setting the sync interval
TWO_WAY_SYNC: bool = True
SYNC_INTERVAL: int = 600
