import google_calendar as gCal
import Things.api as things
import keys




def add_new_tasks_to_calendar(service) -> None:
    """# Add New Tasks to Calendar
    
    This function compares the current state of tasks in Things and the tasks on the calendar
    to determine which new tasks need to be added to calendar.

    ## Paramaters
    service: The google calendar service that handles the authenticaion flow. 
    
    """
    
    # Make list of tasks and a list of their Things uuids
    current_tasks = things.today() + things.upcoming()
    task_uuids = [task['uuid'] for task in current_tasks if task.get('reminder_time')]

    # Get events from GCal and create a list of events that have Things uuids
    events = gCal.get_upcoming_events(service=service, 
                                      calendar_id=keys.THINGS_CALENDAR_ID, 
                                      max_results=1000)
    calendar_task_uuids = [event['description'] for event in events['items']]
    
    # Compare current tasks and calendar events to find only those tasks that are not yet on the calendar
    new_tasks = [task for task in task_uuids if task not in calendar_task_uuids] 

    if new_tasks:
        for new_task in new_tasks:
            task = things.get(new_task)
            gCal.create_event(service = service,
                              calendar_id = keys.THINGS_CALENDAR_ID,
                              event_name = task['title'],
                              task_uuid = task['uuid'],
                              event_date = task['start_date'],
                              event_start_time = task['reminder_time'],
                              )
    else:
        print('No new tasks to add')



