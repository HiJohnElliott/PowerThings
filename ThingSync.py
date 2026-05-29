# Built In modules
from typing import Generator
import logging

# Local Modules
from SyncTypes import Task, Event, TaskEvent, DLTask, DLEvent, DeadlineEvent, DeadlineChange, TaskChange, EventChange
from SyncController import sync_event_changes, sync_task_changes, sync_deadline_changes
from Google import Calendar as GCal
from StateController import State
import config
import things

# Third party modules



def sync(state: State, service, first_run: bool = False):
	try:
		current_tasks: list[dict] = things.upcoming() + things.today() + things.completed(last=config.COMPLETED_SCOPE)	
		current_events = GCal.get_upcoming_events(
			service=service, 
			state=state,
			calendar_id=config.THINGS_CALENDAR_ID
		)
	except Exception as e:
		logging.error(f"Main() function cannot run due to error gathering tasks or calendar events\n{e}")
		return
	
	if first_run or state.detect_task_updates(current_tasks) or state.list_altered_events(current_events):
		all_events: list[Event] = [Event(event) for event in current_events]
		events_dict: dict[str: Event] = {event.uuid: event for event in all_events if event.uuid}
		tasks: list[Task] = [Task(task) for task in current_tasks]
	
		taskEvents: list[TaskEvent] = []
		for t in tasks:
			matching_event = events_dict.get(t.uuid)
			if matching_event:
				taskEvents.append(TaskEvent(t, matching_event))
			else:
				taskEvents.append(TaskEvent(t, None))

		if config.TWO_WAY_SYNC:
			altered_events: list[str] = state.list_altered_events(current_events)
			for te in taskEvents:
				if te.task.uuid in altered_events and not te.cores_match:
					te.task_change_type = TaskChange.UPDATE
					te.event_change_type = EventChange.NONE
		
		task_changes: Generator = (task for task in taskEvents if task.task_change_type != TaskChange.NONE)
		event_changes: Generator = (task for task in taskEvents if task.task_change_type != EventChange.NONE)

		sync_task_changes(task_changes)
		sync_event_changes(service, event_changes)

		state.current_tasks = current_tasks
		state.current_events = current_events


		# Detect and make changes to the Deadlines calendar. 
		if config.DEADLINES_CALENDAR:
			updated_deadlines: list[dict] = things.deadlines()
			if state.detect_deadline_updates(updated_deadlines):
				try:
					updated_deadline_events: list[dict] = GCal.get_upcoming_events(
						service, state=state,
						calendar_id=config.DEADLINES_CALENDAR_ID
					)
				except Exception as e:
					logging.error(f"main() cannot update deadlines due to an error: \n{e}")
			
				dl_tasks: list[DLTask] = [DLTask(task) for task in updated_deadlines]
		
				dl_events: list[DLEvent] = [DLEvent(event) for event in updated_deadline_events]
				dl_events_dict: dict[str: DLEvent] = {event.uuid: event for event in dl_events if event.uuid}

				deadline_events: list[DeadlineEvent] = []
				for task in dl_tasks:
					if task.uuid in dl_events_dict:
						deadline_events.append(DeadlineEvent(task, dl_events_dict.pop(task.uuid)))
					else:
						deadline_events.append(DeadlineEvent(task, None))
				
				if dl_events_dict:
					for _, event in dl_events_dict.items():
						deadline_events.append(DeadlineEvent(None, event))

				deadline_changes: Generator = (dl for dl in deadline_events if dl.event_change_type != DeadlineChange.NONE)
				sync_deadline_changes(service, deadline_changes)

				state.current_deadlines = updated_deadlines