import logging

class State:
	def __init__(self):
		self.current_tasks: list[dict] = list()
		self.current_events: list[dict] = list()
		self.current_deadlines: list[dict] = list()


	def detect_task_updates(self, updated_tasks: list[dict]) -> bool:
		if updated_tasks == self.current_tasks:
			return False 
		else:
			logging.debug("TASK UPDATE FOUND")
			return True
		

	def detect_deadline_updates(self, updated_deadlines: list[dict]) -> bool:
		if updated_deadlines == self.current_deadlines:
			return False
		else:
			logging.debug("DEADLINE UPDATE FOUND")
			return True