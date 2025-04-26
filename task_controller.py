import google_calendar as gCal
from datetime import datetime
import Things.api as things
from pprint import pprint
import keys


# This class holds the state of extant tasks. 
# It can be used to compare the state of tasks in the Things app versus the state
# of sync between the app and the calendar. It can also be used to detect changes
# in the Things app versus the sync state of tasks. 
class CurrentTasks:
    def __init__(self):
        self.current_tasks = list()


    # Returns True if changes are found in Things app 
    def detect_task_updates(current_state) -> bool:
        updated_tasks = things.today() + things.upcoming()
        if updated_tasks == current_state:
            return False 
        else:
            new_tasks = [task for task in updated_tasks if task not in current_state]
            valid_reminder_times = [task for task in new_tasks if task.get('reminder_time')]
            if valid_reminder_times:
                return True
            else:
                return False