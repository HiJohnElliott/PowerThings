import GoogleCalendar as GCal
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



def add_new_tasks_to_calendar(new_tasks: list[dict], calendar_events: list[dict]) -> list[dict]:
    confirmed_tasks: list[dict] = []
    
    calendar_task_uuids: list[str] = [event.get('description') for event in calendar_events]
    
    # Compare current tasks and calendar events to find only those tasks that are not yet on the calendar
    new_tasks = [task for task in new_tasks if task['uuid'] not in calendar_task_uuids] 

    if new_tasks:
        for new_task in new_tasks:
            new_task['change_type'] = 'new'
            confirmed_tasks.append(new_task)
    
    return confirmed_tasks



def update_tasks_on_calendar(updates: list[dict], updated_events: list[dict]) -> None:
    task_updates: list[dict] = []

    if not updated_events:
        logging.warning("No upcoming task events returned by Google Calendar. Adding updated tasks to calendar as NEW")
        for e in updates:
            e['change_type'] = 'new'
        return task_updates

    update_ids: list[str] = [task['uuid'] for task in updates]

    task_uuid_event_id_pairs: dict = {event['description']: event['id'] for event in updated_events if event.get('description') in update_ids}

    for task in updates:
        if not task_uuid_event_id_pairs.get(task['uuid']):
            # This passes on attempting to update the calendar event if it has been deleted manually by user or is otherwise not on the calendar.
            pass
        else:
            task.update({'calendar_event_id': task_uuid_event_id_pairs.get(task['uuid'])})
            task_updates.append(task)
            
    return task_updates



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
                    


def add_new_deadline_to_calendar(new_deadlines: list[dict], calendar_events: list[dict]) -> list[dict]:
    confirmed_deadlines: list[dict] = []

    calendar_deadline_uuids: list[str] = [event.get('description') for event in calendar_events]

    # Compare current deadlines and calendar events to find only those tasks that are not yet on the calendar
    new_deadlines: list = [dl for dl in new_deadlines if dl['uuid'] not in calendar_deadline_uuids]

    if new_deadlines:
        for deadline in new_deadlines:
            deadline['change_type'] = 'new_deadline'
            confirmed_deadlines.append(deadline)
    
    return confirmed_deadlines



def update_deadlines_on_calendar(updated_deadlines: list[dict], updated_deadline_events: list[dict]) -> list[dict]:
    deadline_updates: list[dict] = []

    if not updated_deadline_events:
        logging.warning("No upcoming deadlines returned by Google Calendar. Adding updated deadlines as NEW")
        for dl in updated_deadlines:
            dl['change_type'] = 'new_deadline'
        return deadline_updates
    
    update_ids: list[str] = [dl['uuid'] for dl in updated_deadlines]

    deadline_uuid_event_id_pairs: dict = {event['description']: event['id'] for event in updated_deadline_events if event.get('description') in update_ids}

    for deadline in updated_deadlines:
        if not deadline_uuid_event_id_pairs.get(deadline['uuid']):
            # This passes on attempting to update the calendar event if it has been deleted manually by user or is otherwise not on the calendar.
            pass
        else:
            deadline.update({'calendar_event_id': deadline_uuid_event_id_pairs.get(deadline['uuid'])})
            deadline_updates.append(deadline)

        return deadline_updates



def remove_completed_deadlines(updated_deadlines: list[dict], updated_deadline_events: list) -> list[dict]:
        removed_deadlines = []
        
        completed_deadline_ids: list[str] = [dl.get('uuid') for dl in updated_deadlines]

        removed_calendar_event_ids: list[str] = [event.get('id') for event in updated_deadline_events if event.get('description') not in completed_deadline_ids]

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
                                  event_id = task.get('calendar_event_id'))
                
    for task in list_of_changes: 
        push_change(task)
    