import logging

class State:
	def __init__(self):
		self.current_tasks: list[dict] = []
		self.current_events: list[dict] = []
		self.current_deadlines: list[dict] = []


	def detect_task_updates(self, updated_tasks: list[dict]) -> bool:
		if updated_tasks == self.current_tasks:
			return False 
		else:
			logging.debug("TASK UPDATE FOUND")
			return True
		
	
	def detect_event_updates(self, updated_events: list[dict]) -> bool:
		if updated_events == self.current_deadlines:
			return False
		else:
			return True


	def detect_deadline_updates(self, updated_deadlines: list[dict]) -> bool:
		if updated_deadlines == self.current_deadlines:
			return False
		else:
			logging.debug("DEADLINE UPDATE FOUND")
			return True
		

	def list_altered_events(self, updated_events: list[dict]) -> list[str]:
		return [e.get('description') for e in updated_events if e not in self.current_events]

		