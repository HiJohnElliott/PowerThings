# This is the Google Calendar link that you want to point to to sync your tasks. 
THINGS_CALENDAR_ID: str = ""

# Completed scope sets how far back you want this application to look for completed tasks. 
COMPLETED_SCOPE: str = '90d'

# The default duration is in minutes. Duration tags can be toggled on and off. 
DEFAULT_DURATION: int = 60
DURATION_TAGS = True

# Zen Mode removes completed tasks from the calendar. 
ZEN_MODE: bool = True 

# Deadlines calendar settings 
DEADLINES_CALENDAR: bool = True
DEADLINES_CALENDAR_ID: str = ""

# This is used when making any changes to tasks in Things using the applications URL scheme. 
THINGS_AUTH_TOKEN: str = ""

# This is for setting up your logging
EXTERNAL_LOGGING: bool = True
LOGGING_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FMT: str = "%Y-%m-%d %H:%M:%S"

