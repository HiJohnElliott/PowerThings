import GoogleCalendar as GCal
import Things.api as things
import logging
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
    events = GCal.get_upcoming_events(service=service, 
                                      calendar_id=keys.THINGS_CALENDAR_ID, 
                                      max_results=1000)
    
    if not events:
        logging.warning("No upcoming events returned by Google Calendar")
        return
    
    calendar_task_uuids = [event.get('description') for event in events.get('items')]
    
    # Compare current tasks and calendar events to find only those tasks that are not yet on the calendar
    new_tasks = [task for task in task_uuids if task not in calendar_task_uuids] 

    if new_tasks:
        for new_task in new_tasks:
            task = things.get(new_task)
            GCal.create_event(service = service,
                              calendar_id = keys.THINGS_CALENDAR_ID,
                              event_name = task['title'],
                              task_uuid = task['uuid'],
                              event_date = task['start_date'],
                              event_start_time = task['reminder_time'],
                              )
    else:
        logging.debug('No new tasks to add')


def update_tasks_on_calendar(service, task_updates: list[str]) -> None:
    events = GCal.get_upcoming_events(service=service, 
                                      calendar_id=keys.THINGS_CALENDAR_ID, 
                                      max_results=1000)
    
    if not events:
        logging.warning("No upcoming events returned by Google Calendar")
        return

    task_uuid_event_id_pairs = {event['description']: event['id'] for event in events['items'] if event.get('description') in task_updates}

    for task in task_updates:
        if not task_uuid_event_id_pairs.get(task):
            # This passes on attempting to update the calendar event if it has been deleted manually by user or is otherwise not on the calendar.
            pass
        else:
            things_task = things.get(task)
            GCal.update_event(service=service, 
                            calendar_id=keys.THINGS_CALENDAR_ID,
                            event_id=task_uuid_event_id_pairs.get(task),
                            event_name=things_task.get('title'),
                            task_uuid=things_task.get('uuid'),
                            event_date=things_task.get('start_date'),
                            event_start_time=things_task.get('reminder_time')
                            )


