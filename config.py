# This is the Google Calendar link that you want to point to to sync your tasks. 
THINGS_CALENDAR_ID: str = "d80beafee68bdb1b2b26937ac30ba3a4322cf06d07d4767922e114e19ba0edcb@group.calendar.google.com"

# Completed scope sets how far back you want this application to look for completed tasks. 
COMPLETED_SCOPE: str = '90d'

# The default duration is in minutes. Duration tags can be toggled on and off. 
DEFAULT_DURATION: int = 60
DURATION_TAGS = True

# Zen Mode removes completed tasks from the calendar. 
ZEN_MODE: bool = True 

# Deadlines calendar settings 
DEADLINES_CALENDAR: bool = True
DEADLINES_CALENDAR_ID: str = "8a7f62c5d445063fc29b0441c3c3c39b033c792d195444ad5ce10c4ea68d9472@group.calendar.google.com"

# This is used when making any changes to tasks in Things using the applications URL scheme. 
THINGS_AUTH_TOKEN: str = "z7yzZqL1S1qtCNrCiDsXtA"

# This is for setting up your logging
EXTERNAL_LOGGING: bool = True
LOGGING_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FMT: str = "%Y-%m-%d %H:%M:%S"

# GCAL_API_KEY = "AIzaSyAtwljhzc28kvNjygpqqpiiiSvHqlogx4Y"
# GCAL_CLIENT_ID = "1000153549621-m5k09jr9maiaj87v5ob442b92u0cc3vq.apps.googleusercontent.com"
# GCAL_CLIENT_SECRET = "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"