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
def detect_task_updates(current_tasks) -> bool:
    updated_tasks = things.today() #+ things.upcoming()
    if updated_tasks == current_tasks:
        return False 
    else:
        return True



def add_new_tasks_to_calendar():
    """Add New Tasks to Calendar
    
    This function compares the current state of tasks in Things and the tasks on the calendar
    to determine which new tasks need to be added to calendar. """
    
    # Make list of tasks and a list of their Things uuids
    current_tasks = things.today() + things.upcoming()
    task_uuids = [task['uuid'] for task in current_tasks if task.get('reminder_time')]

    # Set up the calendar Service
    service = gCal.authenticate_google_calendar()
    calendar_id = keys.THINGS_CALENDAR_ID

    # Get events from GCal and create a list of events that have Things uuids
    events = gCal.get_upcoming_events(service=service, calendar_id=calendar_id, max_results=100)
    calendar_task_uuids = [event['description'] for event in events['items']]
    
    # Compare current tasks and calendar events to find only those tasks that are not yet on the calendar
    new_tasks = [task for task in task_uuids if task not in calendar_task_uuids] 

    if new_tasks:
        for new_task in new_tasks:
            task = things.get(new_task)
            gCal.create_event(service = service,
                              calendar_id = calendar_id,
                              event_name = task['title'],
                              task_uuid = task['uuid'],
                              event_date = task['start_date'],
                              event_start_time = task['reminder_time'],
                              )
    else:
        print('No New Tasks to add')



if __name__ == "__main__":
    add_new_tasks_to_calendar()
    
    # pprint(Things.get('6zrcNmzxfuNyvUFw9KwpxB'))
    
    
