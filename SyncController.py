from datetime import datetime
import GoogleCalendar as GCal
import Things.api as things
import makeThings
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
    
    valid_duration_tags = [tag for tag in task_object.get('tags') 
                          if tag[-1] in 'hm' 
                          and tag[:-1].isdigit()]
    
    if not valid_duration_tags:
        return config.DEFAULT_DURATION
    
    if valid_duration_tags[0][-1] == 'h':
        return int(valid_duration_tags[0][:-1]) * 60
    else:
        return int(valid_duration_tags[0][:-1])



def add_new_tasks_to_calendar(updated_tasks: list[dict], calendar_events: list[dict]) -> list[dict]:
    confirmed_tasks: list[dict] = []
    
    calendar_task_uuids: list[str] = [event.get('description') for event in calendar_events]
    
    # Compare current tasks and calendar events to find only those tasks that are not yet on the calendar
    new_tasks = [task for task in updated_tasks if task['uuid'] not in calendar_task_uuids 
                 and task.get('reminder_time')
                 and task.get('status') == 'incomplete'] 

    if new_tasks:
        for new_task in new_tasks:
            new_task['change_type'] = 'new'
            confirmed_tasks.append(new_task)
    
    return confirmed_tasks



def update_tasks_on_calendar(updated_events: list[dict]) -> list[dict]:
    if not updated_events:
        logging.debug(f"No events on calendar to update")
    else:
        updates: list[dict] = []
        
        for event in updated_events:
                things_task: dict = things.get(event.get('description'))
                task_duration: int = parse_duration_tag(things_task)

                event_start_datetime: datetime = datetime.fromisoformat(event.get('start').get('dateTime'))
                event_end_datetime: datetime = datetime.fromisoformat(event.get('end').get('dateTime'))
                event_duration: int = int((event_end_datetime - event_start_datetime).total_seconds() / 60) 

                task_obj: dict = {'uuid': things_task.get('uuid'), 
                                    'title': things_task.get('title'),
                                    'start_date': things_task.get('start_date'),
                                    'reminder_time': things_task.get('reminder_time'),
                                    'duration': task_duration}
                
                event_obj: dict = {'uuid': event.get('description'),
                                    'title': event.get('summary'),
                                    'start_date': event_start_datetime.date().isoformat(),
                                    'reminder_time': event_start_datetime.time().strftime("%H:%M"),
                                    'duration': event_duration}
                
                if task_obj != event_obj:
                    things_task['calendar_event_id'] = event.get('id')
                    things_task['change_type'] = 'update'
                    # This if statement is responsible for handling the Things application deleting reminder_times once they have passed. 
                    # If the reminder_time passes, and then the user moves the reminder to a later date, the task itself is updated in the app here with
                    # the existing start time of the calendar event such that the reminder_time of the task is now the start time of the calendar event.
                    if not things_task.get('reminder_time') and things_task.get('start_date') != datetime.now().date():
                        things_task['reminder_time'] = event_start_datetime.time().strftime("%H:%M")
                        when_datetime = f"{things_task.get('start_date')} {things_task.get('reminder_time')}"
                        makeThings.update_task(auth_token=config.THINGS_AUTH_TOKEN, 
                                               task_id=things_task.get('uuid'), 
                                               when=when_datetime)

                    updates.append(things_task)
                
            
        return updates



def remove_completed_tasks(updated_tasks: list[dict], updated_events: list) -> list[dict]:
        completed_tasks: list[dict] = []
        
        completed_task_ids: list[str] = [task.get('uuid') for task in updated_tasks if task.get('status') == 'completed']
        
        completed_calendar_event_ids: dict = {event.get('description'): event.get('id') for event in updated_events if event.get('description') in completed_task_ids}

        if completed_calendar_event_ids:
            for task in updated_tasks:
                if completed_calendar_event_ids.get(task['uuid']): 
                    task.update({'change_type': 'delete',
                                    'calendar_event_id': completed_calendar_event_ids.get(task['uuid'])})
                    
                    completed_tasks.append(task)

        return completed_tasks
                    


def add_new_deadline_to_calendar(current_deadlines: list[dict], calendar_events: list[dict]) -> list[dict]:
    confirmed_deadlines: list[dict] = []

    calendar_deadline_uuids: list[str] = [event.get('description') for event in calendar_events]

    # Compare current deadlines and calendar events to find only those deadlines that are not yet on the calendar
    new_deadlines: list = [dl for dl in current_deadlines if dl['uuid'] not in calendar_deadline_uuids]

    if new_deadlines:
        for deadline in new_deadlines:
            deadline['change_type'] = 'new_deadline'
            confirmed_deadlines.append(deadline)
    
    return confirmed_deadlines



def update_deadlines_on_calendar(updated_deadlines: list[dict], updated_deadline_events: list[dict]) -> list[dict]:
    deadline_updates: list[dict] = []

    if not updated_deadline_events:
        logging.warning("No upcoming deadlines returned by Google Calendar")
        return deadline_updates
    
    deadline_ids: list[str] = [dl['uuid'] for dl in updated_deadlines]

    deadline_uuid_event_id_pairs: dict = {event['description']: event['id'] for event in updated_deadline_events if event.get('description') in deadline_ids}

    for deadline in updated_deadlines:
        if not deadline_uuid_event_id_pairs.get(deadline['uuid']):
            # This passes on attempting to update the calendar event if it has been deleted manually by user or is otherwise not on the calendar.
            pass
        else:
            deadline.update({'calendar_event_id': deadline_uuid_event_id_pairs.get(deadline['uuid'])})
            deadline_updates.append(deadline)

        return deadline_updates



def remove_completed_deadlines(updated_deadlines: list[dict], updated_deadline_events: list) -> list[dict]:
        removed_deadlines: list[dict] = []
        
        deadline_ids: list[str] = [dl.get('uuid') for dl in updated_deadlines]

        removed_calendar_event_ids: list[str] = [event.get('id') for event in updated_deadline_events if event.get('description') not in deadline_ids]

        for dl in removed_calendar_event_ids:
            removed_deadlines.append({'change_type': 'delete_deadline', 
                                      'calendar_event_id': dl
                                      })

        return removed_deadlines





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
                
            case 'new_deadline': 
                GCal.create_event(service = service,
                                  calendar_id = config.DEADLINES_CALENDAR_ID,
                                  event_name = task.get('title'),
                                  task_uuid = task.get('uuid'),
                                  event_date = task.get('deadline'),
                                  all_day=True)
                
            case 'update_deadline': 
                GCal.update_event(service = service,
                                  calendar_id = config.DEADLINES_CALENDAR_ID,
                                  event_id = task.get('calendar_event_id'),
                                  event_name = task.get('title'),
                                  task_uuid = task.get('uuid'),
                                  event_date = task.get('deadline'),
                                  all_day=True)
                
            case 'delete_deadline':
                GCal.delete_event(service = service,
                                  calendar_id = config.DEADLINES_CALENDAR_ID,
                                  event_id = task.get('calendar_event_id'),
                                  all_day=True)
                
    for task in list_of_changes: 
        push_change(task)
    