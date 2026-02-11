# from datetime import datetime
import things
import logging
import config


class State:
    def __init__(self):
        self.current_tasks: list[dict] = list()
        self.current_deadlines: list[dict] = list()


    def detect_task_updates(self) -> bool:
        """Returns True if changes are found in Things app"""
        updated_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)

        if updated_tasks == self.current_tasks:
            return False 
        else:
            logging.debug("TASK UPDATE FOUND")
            return True
        

    def detect_deadline_updates(self) -> bool:
        updated_deadlines = things.deadlines()
        
        if updated_deadlines == self.current_deadlines:
            return False
        else:
            logging.debug("DEADLINE UPDATE FOUND")
            return True


    def list_updated_deadlines(self, updated_deadlines: list[dict]) -> list[dict]:
        updated_deadlines_list: list[dict] = []

        for deadline in updated_deadlines:
            # First check to see if the task is in current_tasks already. 
            state_deadline = [i for i in self.current_deadlines if i['uuid'] == deadline['uuid']]
            if not state_deadline:
                # If a task is totally new, then it's ID won't be in self.current_tasks yet and we can skip it.
                pass 
            elif deadline == state_deadline[0]:
                # If the state_task and updated task are the same then we don't need to update anything
                pass
            elif not state_deadline[0].get('deadline'):
                # No need to update the calendar if there is no deadline. 
                pass
            elif not deadline.get('deadline'):
                # If the deadline has been deleted from the task then we skip it here. 
                pass
            elif deadline.get('status') == 'completed':
                # If the task is already completed we can pass on updating it. 
                pass

            else:
                # Only update this event if one of these fields specifically has changed 
                state_deadline = state_deadline[0]
                state_task_values = {'title': state_deadline.get('title'),
                                     'uuid': state_deadline.get('uuid'),
                                     'deadline': state_deadline.get('deadline')}
                
                updated_task_values = {'title': deadline.get('title'),
                                       'uuid': deadline.get('uuid'),
                                       'deadline': deadline.get('deadline')}
                
                if state_task_values != updated_task_values:
                    logging.debug(f"UPDATED DEADLINE FOUND: {deadline.get('uuid')} | {deadline.get('title')}")
                    deadline.update({'change_type': 'update_deadline'})
                    updated_deadlines_list.append(deadline)
                else:
                    logging.debug(f"No updated deadlines found")

        return updated_deadlines_list