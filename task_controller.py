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


    def detect_state_updates(self) -> bool:
        """Returns True if changes are found in Things app"""
        
        updated_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        if updated_tasks == self.current_tasks:
            return False 
        else:
            print("State Update Found")
            return True


    def detect_new_reminder_times(self) -> bool:
        """Returns True if new reminder timse are found on any new tasks"""
            
        updated_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        new_tasks = [task for task in updated_tasks if task not in self.current_tasks]
        valid_reminder_times = [task for task in new_tasks if task.get('reminder_time')]
        
        if valid_reminder_times:
            print("New Reminder Time Found")
            return True
        else:
            # Set the state of current_tasks so that this function doesn't run again on the next main() loop
            self.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')
            return False