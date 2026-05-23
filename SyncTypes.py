# Built-in modules
from datetime import date, time, datetime
from enum import Enum, auto

# Local modules
import config

class EventChange(Enum):
	NONE = auto()
	NEW = auto()
	UPDATE = auto()
	DELETE = auto()


class TaskChange(Enum): 
	NONE = auto()
	NEW = auto()
	UPDATE = auto()
	TIME = auto()



class Task:
	def __init__(self, task: dict):
		self._start_date: date | None = None
		self._reminder_time: time | None = None
		self._updated: datetime = None
		self._eligable: bool = False
		self._core: tuple = tuple()

		self.task_body: dict = task
		self.uuid: str = task.get('uuid')
		self.title: str = task.get('title')
		self.status: str = task.get('status')
		self.start_date: date = task.get('start_date')
		self.reminder_time: time = task.get('reminder_time')
		self.duration: int = self._parse_duration_tag(task.get('tags'))
		self.tags: list[str] = task.get('tags')
		self.updated: datetime = task.get('modified')
		self.eligable: bool = False
		self.core: tuple = tuple()

	def _parse_duration_tag(self, tags: list[str]) -> int:
		"""Take in a task object and return the number of minutes for the duaration
		
		- Duration tags are in the form an integer that is suffixed with an 'm' or an 'h'.
		- For example, '30m', '1h', '5h', or '15m' are all valid tags. 
		- This function takes in a Things task object and returns the duration in minutes if there is a valid duration tag. 
		- If there are multple valid duration tags on the task it only returns the value in minutes of the first one. 
		"""
		if not config.DURATION_TAGS:
			return config.DEFAULT_DURATION
		elif not tags:
			return config.DEFAULT_DURATION
		
		valid_duration_tags = [tag for tag in tags if tag[-1] in 'hm' and tag[:-1].isdigit()]
		
		if not valid_duration_tags:
			return config.DEFAULT_DURATION
		elif valid_duration_tags[0][-1] == 'h':
			return int(valid_duration_tags[0][:-1]) * 60
		else:
			return int(valid_duration_tags[0][:-1])


	@property
	def start_date(self) -> date:
		return self._start_date
	
	@start_date.setter
	def start_date(self, start_date: str):
		if start_date:
			try:
				self._start_date = date.fromisoformat(start_date)
			except ValueError:
				self._start_date = None            
		else:
			self._start_date = None


	@property
	def reminder_time(self) -> time:
		return self._reminder_time

	@reminder_time.setter
	def reminder_time(self, reminder_time: str | datetime) -> None:
		if isinstance(reminder_time, str):
			self._reminder_time = time.fromisoformat(reminder_time)
		elif isinstance(reminder_time, time):
			self._reminder_time = reminder_time
		elif isinstance(reminder_time, datetime):
			self._reminder_time = reminder_time
		else:
			self._reminder_time = None


	@property
	def updated(self) -> datetime:
		return self._updated
	
	@updated.setter
	def updated(self, update: datetime) -> None:
		if isinstance(update, str):
			self._updated = datetime.fromisoformat(update)
		else:
			self._updated = None


	@property
	def eligable(self) -> bool: 
		return self._eligable
	
	@eligable.setter
	def eligable(self, _: bool) -> None:
		if self.status == "incomplete":
			if self.start_date and self.reminder_time:
				self._eligable = True
			else:
				self._eligable = False

	@property
	def core(self) -> tuple:
		return self._core

	@core.setter
	def core(self, _: tuple) -> None:
		self._core = (
			self.title,
			self.start_date,
			self.reminder_time,
			self.duration
		)



class Event:
	def __init__(self, event: dict):
		self._start_date: date = date
		self._start_time: time = time
		self._event_uuid: str | None = str
		self._duration: int = int
		self._updated: datetime = None
		self._event_core: tuple = tuple()
		
		self.event_body = event
		self.title = event.get('summary')
		self.start_date = event.get("start")["dateTime"]
		self.start_time = event.get("start")["dateTime"]
		self.id = event.get("id")
		self.uuid = event.get("description")
		self.duration = self._get_duration()
		self.updated = event.get('updated')
		self.core: tuple = tuple()

	def _is_valid_things_uuid(self, uuid: str) -> bool:
		if not isinstance(uuid, str):
			return False 
		id_len: int = len(uuid)
		if id_len == 21 or id_len == 22:
			return True
		else:
			return False


	def _get_duration(self) -> int:
		start_datetime: datetime = datetime.fromisoformat(self.event_body.get('start')['dateTime'])
		end_datetime: datetime = datetime.fromisoformat(self.event_body.get('end')['dateTime'])
		delta: int = int((end_datetime - start_datetime).seconds / 60)
		return delta

	@property
	def start_date(self) -> date:
		return self._start_date
	
	@start_date.setter
	def start_date(self, start_date: str) -> None:
		if start_date:
			try:
				self._start_date: date = datetime.fromisoformat(start_date).date()
			except ValueError:
				self._start_date: date = None


	@property
	def start_time(self) -> time:
		return self._start_time

	@start_time.setter
	def start_time(self, start: str) -> None:
		if isinstance(start, str):
			self._start_time = datetime.fromisoformat(start).time()
		else:
			self._start_time = None
	

	@property
	def uuid(self) -> str | None:
		return self._event_uuid

	@uuid.setter
	def uuid(self, description: str) -> None:
		if self._is_valid_things_uuid(description):
			self._event_uuid = description
		else:
			self._event_uuid = False


	@property
	def updated(self) -> datetime:
		return self._updated
	
	@updated.setter
	def updated(self, update: str) -> None:
		if isinstance(update, str):
			self._updated = datetime.fromisoformat(update)
		else:
			self._updated = None
	
	@property
	def core(self) -> tuple:
		return self._event_core
	
	@core.setter
	def core(self, _: tuple) -> None:
		self._event_core = (
			self.title,
			self.start_date,
			self.start_time,
			self.duration
		)




class TaskEvent:
	def __init__(self, task: Task, event: dict):
		self._has_event: bool = False
		self._has_task: bool = False
		self._event_change_type: EventChange = EventChange.NONE
		self._task_change_type: TaskChange = TaskChange.NONE

		self.task: Task = task
		self.event: Event = event
		self.has_event: bool = False
		self.has_task: bool = False	
		self.event_change_type: EventChange = EventChange.NONE
		self.task_change_type: TaskChange = TaskChange.NONE


	@property
	def has_event(self) -> bool:
		return self._has_event
	
	@has_event.setter
	def has_event(self, _: Event) -> None:
		if isinstance(self.event, Event):
			self._has_event = True
		else:
			self._has_event = False


	@property
	def has_task(self) -> bool:
		return self._has_task
	
	@has_task.setter
	def has_task(self, _: Task) -> None:
		if isinstance(self.task, Task):
			self._has_task = True
		else:
			self._has_task = False


	@property
	def event_change_type(self) -> EventChange:
		return self._event_change_type

	@event_change_type.setter
	def event_change_type(self, _: EventChange):
		if not self.task.eligable and not self.has_event:
			self._event_change_type = EventChange.NONE
		
		elif self.task.eligable and not self.has_event:
			self._event_change_type = EventChange.NEW
		
		elif self.has_task and self.has_event:
			if self.task.core != self.event.core:
				self._event_change_type = EventChange.UPDATE
		
			if not self.task.reminder_time and self.task.start_date != datetime.now().date():
				self.task.reminder_time = self.event.start_time
				self._event_change_type = EventChange.UPDATE
				self._task_change_type = TaskChange.TIME

		delete_statuses: tuple = ('completed', 'cancelled')
		if self.task.status in delete_statuses and self.has_event:
			self._event_change_type = EventChange.DELETE
		

	@property
	def task_change_type(self) -> TaskChange:
		return self._task_change_type

	@task_change_type.setter
	def task_change_type(self, _: TaskChange) -> None:
		if not self.has_task and self.has_event:
			self._task_change_type = TaskChange.NEW


	