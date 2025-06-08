from concurrent.futures import ThreadPoolExecutor
import GoogleCalendar as GCal
import Things.api as things
import logging
import config


def parse_duration_tag(task_object: str) -> int:
    """Take in a task object and return the number of minutes for the duaration
    
    - Duration tags are in the form an integer that is suffixed with an 'm' or an 'h'.
    - For example, '30m', '1h', '5h', or '15m' are all valid tags. 
    - This function takes in a Things task object and returns the duration in minutes if there is a valid duration tag. 
    - If there are multple valid duration tags on the task it only returns the value in minutes of the first one. 
    """
    if config.DURATION_TAGS == False:
         return config.DEFAULT_DURATION
    
    if not task_object.get('tags'):
         return config.DEFAULT_DURATION
    
    valid_duation_tags = [tag for tag in task_object.get('tags') 
                          if tag[-1] in 'hm' 
                          and tag[:-1].isdigit()]
    
    if not valid_duation_tags:
        return config.DEFAULT_DURATION
    
    if valid_duation_tags[0][-1] == 'h':
        return int(valid_duation_tags[0][:-1]) * 60
    else:
        return int(valid_duation_tags[0][:-1])



def add_new_tasks_to_calendar(service, updated_tasks: list[dict], calendar_events: list[dict]) -> None:
    """# Add New Tasks to Calendar
    
    This function compares the current state of tasks in Things and the tasks on the calendar
    to determine which new tasks need to be added to calendar.

    ## Paramaters
    service: The google calendar service that handles the authenticaion flow. 
    
    """
    
    # Make list of tasks and a list of their Things uuids
    task_uuids = [task['uuid'] for task in updated_tasks if task.get('reminder_time') and task.get('status') != 'completed']
    
    calendar_task_uuids = [event.get('description') for event in calendar_events]
    
    # Compare current tasks and calendar events to find only those tasks that are not yet on the calendar
    new_tasks = [task for task in task_uuids if task not in calendar_task_uuids] 

    if new_tasks:
        for new_task in new_tasks:
            task = things.get(new_task)
            duration = parse_duration_tag(task)
            GCal.create_event(service = service,
                              calendar_id = config.THINGS_CALENDAR_ID,
                              event_name = task['title'],
                              task_uuid = task['uuid'],
                              event_date = task['start_date'],
                              event_start_time = task['reminder_time'],
                              duration=duration
                              )
    else:
        logging.debug('No new tasks to add')



def update_tasks_on_calendar(service, task_updates: list[str], updated_events: list[dict]) -> None:
    
    if not updated_events:
        logging.warning("No upcoming events returned by Google Calendar")
        return

    task_uuid_event_id_pairs = {event['description']: event['id'] for event in updated_events if event.get('description') in task_updates}

    for task in task_updates:
        if not task_uuid_event_id_pairs.get(task):
            # This passes on attempting to update the calendar event if it has been deleted manually by user or is otherwise not on the calendar.
            pass
        else:
            things_task = things.get(task)
            duration = parse_duration_tag(things_task)
            GCal.update_event(service=service, 
                            calendar_id=config.THINGS_CALENDAR_ID,
                            event_id=task_uuid_event_id_pairs.get(task),
                            event_name=things_task.get('title'),
                            task_uuid=things_task.get('uuid'),
                            event_date=things_task.get('start_date'),
                            event_start_time=things_task.get('reminder_time'),
                            duration=duration
                            )



def remove_completed_tasks_on_calendar(service, updated_tasks: list[dict], calendar_events: list) -> list[dict]:
        completed_task_list = [] # This is here for later when we change the whole main loop over to make changes in one go. 
        
        todays_completed_task_ids = [task.get('uuid') for task in updated_tasks if task.get('status') == 'completed']
        
        completed_calendar_events = [event for event in calendar_events if event.get('description') in todays_completed_task_ids]

        if completed_calendar_events:
            for event in completed_calendar_events:
                    GCal.delete_event(service=service,
                                    calendar_id=config.THINGS_CALENDAR_ID,
                                    event_id=event.get('id'))
                    


def sync_calendar_changes(service: object, list_of_changes: list[dict]) -> None:
    
    def push_change(task: dict) -> None:
        duration = parse_duration_tag(task)

        match task.get('change_type'):
            case 'new':
                GCal.create_event(service = service,
                                  calendar_id = config.THINGS_CALENDAR_ID,
                                  event_name = task.get('title'),
                                  task_uuid = task.get('uuid'),
                                  event_date = task.get('start_date'),
                                  event_start_time = task.get('reminder_time'),
                                  duration=duration)
        
            case 'update':
                GCal.update_event(service = service, 
                                  calendar_id = config.THINGS_CALENDAR_ID,
                                  event_id = task.get('calendar_event_id'),
                                  event_name = task.get('title'),
                                  task_uuid = task.get('uuid'),
                                  event_date = task.get('start_date'),
                                  event_start_time = task.get('reminder_time'),
                                  duration = duration)
        
            case 'delete':
                GCal.delete_event(service = service,
                                  calendar_id = config.THINGS_CALENDAR_ID,
                                  event_id = task.get('calendar_event_id'))

    with ThreadPoolExecutor(max_workers=64) as executor:
        executor.map(push_change, list_of_changes)
    