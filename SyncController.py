from SyncTypes import TaskEvent, TaskChange, EventChange, DeadlineEvent, DeadlineChange
from Google import GoogleCalendar as GCal
import Things.makeThings as makeThings
import logging
import config



def _make_duration_tag(duration: int) -> str:
		if duration % 60 != 0:
			return f"{duration}m"
		else:
			return f"{int(duration / 60)}h"


def _replace_duration_tag(tags: list[str], duration_tag: str) -> list[str]:
	if isinstance(duration_tag, int):
		duration_tag = str(duration_tag)
	if not tags:
		tags.append(duration_tag)
		return tags
	else:
		for tag in tags:
			if tag[-1] in 'hm' and tag[:-1].isdigit():
				tags.remove(tag)
		tags.append(duration_tag)
		return tags   



def sync_task_changes(list_of_changes: list[TaskEvent]):

	def _push_task_change(te: TaskEvent) -> None:
		if te.has_event:
			duration = te.event.duration
		match te.task_change_type:
			case TaskChange.NONE:
				pass
			
			case TaskChange.NEW:
				makeThings.make_new_task(title=te.event.title,
										 when=f"{te.event.start_date} {te.event.start_time}",
										 tags=[duration])
			
			case TaskChange.UPDATE:
				logging.debug(F":::CHANGING TASK:::\n{te.event.title}")
				task_id: str = te.event.uuid
				
				current_task_tags: list[str] | None = te.task.tags
				if not current_task_tags:
					updated_tags: list[str] = [_make_duration_tag(te.event.duration)]
				else:
					updated_tags: list[str] = _replace_duration_tag(current_task_tags, duration)
				
				makeThings.update_task(auth_token=config.THINGS_AUTH_TOKEN,
									   task_id=task_id,
									   title=te.event.title,
									   when=f"{te.event.start_date} {te.event.start_time}",
									   tags=updated_tags)

			case TaskChange.TIME:
				logging.debug("::CHANGING TASK TIME::")
				task_id: str = te.event.uuid

				current_task_tags: list[str] | None = te.task.tags
				if not current_task_tags:
					updated_tags: list[str] = [_make_duration_tag(te.event.duration)]
				else:
					updated_tags: list[str] = _replace_duration_tag(current_task_tags, duration)

				makeThings.update_task(auth_token=config.THINGS_AUTH_TOKEN,
									   task_id=task_id,
									   title=te.event.title,
									   when=f"{te.task.start_date} {te.event.start_time}",
									   tags=updated_tags)

	for task_change in list_of_changes:
		_push_task_change(task_change)

		 


def sync_event_changes(service: object, list_of_changes: list[TaskEvent]) -> None:
	
	def _push_change(te: TaskEvent) -> None:

		match te.event_change_type:
			case EventChange.NONE:
				pass
	
			case EventChange.NEW:
				GCal.create_event(service = service,
								  calendar_id = config.THINGS_CALENDAR_ID,
								  event_name = te.task.title,
								  task_uuid = te.task.uuid,
								  event_date = te.task.start_date,
								  event_start_time = te.task.reminder_time,
								  duration=te.task.duration)
		
			case EventChange.UPDATE:
				GCal.update_event(service = service, 
								  calendar_id = config.THINGS_CALENDAR_ID,
								  event_id = te.event.id,
								  event_name = te.task.title,
								  task_uuid = te.task.uuid,
								  event_date = te.task.start_date,
								  event_start_time = te.task.reminder_time,
								  duration = te.task.duration)
		
			case EventChange.DELETE:
				GCal.delete_event(service = service,
								  calendar_id = config.THINGS_CALENDAR_ID,
								  event_id = te.event.id)
				
	for task in list_of_changes: 
		_push_change(task)
	


def sync_deadline_changes(service: object, list_of_changes: list[DeadlineEvent]) -> None:

	def _push_change(de: DeadlineEvent) -> None:

		match de.event_change_type:
			case DeadlineChange.NONE:
				pass
				
			case DeadlineChange.NEW: 
				GCal.create_event(service = service,
								  calendar_id = config.DEADLINES_CALENDAR_ID,
								  event_name = de.deadline.title,
								  task_uuid = de.deadline.uuid,
								  event_date = de.deadline.deadline,
								  all_day=True)
				
			case DeadlineChange.UPDATE: 
				GCal.update_event(service = service,
								  calendar_id = config.DEADLINES_CALENDAR_ID,
								  event_id = de.event.id,
								  event_name = de.deadline.title,
								  task_uuid = de.deadline.uuid,
								  event_date = de.deadline.deadline,
								  all_day=True)
				
			case DeadlineChange.DELETE:
				GCal.delete_event(service = service,
								  calendar_id = config.DEADLINES_CALENDAR_ID,
								  event_id = de.event.id,
								  all_day=True)
				
	for task in list_of_changes: 
		_push_change(task)
	