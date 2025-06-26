# from datetime import datetime
import Things.api as things
import logging
import config


class State:
    def __init__(self):
        self.current_tasks = list()


    def list_tasks_in_scope() -> list[int]:
        return list(things.today()
                    + things.upcoming()
                    + things.completed(last=config.COMPLETED_SCOPE))


    def detect_state_updates(self) -> bool:
        """Returns True if changes are found in Things app"""
            
        updated_tasks = things.today() + things.upcoming() + things.completed(last=config.COMPLETED_SCOPE)
        if updated_tasks == self.current_tasks:
            return False 
        else:
            logging.debug("State Update Found")
            return True
        


    def list_new_tasks(self, updated_tasks: list[dict]) -> bool:
        new_tasks = [task for task in updated_tasks if task not in self.current_tasks and task.get('status') != 'completed']
        valid_reminder_times = [task for task in new_tasks if task.get('reminder_time')]
        
        if valid_reminder_times:
            logging.debug(f"New Task Found: {valid_reminder_times}\n")
            return valid_reminder_times
        else:
            return False
        


    def list_updated_tasks(self, updated_tasks: list[dict]) -> list[str]:
        updated_tasks_list = []

        for task in updated_tasks:
            state_task = [i for i in self.current_tasks if i['uuid'] == task['uuid']]
            if not state_task:
                # If a task is totally new, then it's ID won't be in state_task yet
                pass 
            elif task == state_task[0]:
                # If the state_task and updated task are the same then we don't need to update anything
                pass
            elif not state_task[0].get('reminder_time'):
                # No need to update the calendar if there is no reminder time. 
                pass
            elif not task.get('reminder_time'):
                # If the reminder_time has been deleted from the task then skip it here. 
                pass
            elif task.get('status') == 'completed':
                # If the task is already completed we can pass on updating it. 
                pass

            else:
                # Only update this event if one of these fields specifically has changed 
                state_task = state_task[0]
                state_task_values = {'title': state_task.get('title'),
                                     'uuid': state_task.get('uuid'),
                                     'start_date': state_task.get('start_date'),
                                     'reminder_time': state_task.get('reminder_time'),
                                     'tags': state_task.get('tags')}
                
                updated_task_values = {'title': task.get('title'),
                                       'uuid': task.get('uuid'),
                                       'start_date': task.get('start_date'),
                                       'reminder_time': task.get('reminder_time'),
                                       'tags': task.get('tags')}
                
                if state_task_values != updated_task_values:
                    logging.debug(f"Updated Task Found: {task.get('uuid')} | {task.get('title')}")
                    task.update({'change_type': 'update'})
                    updated_tasks_list.append(task)
                else:
                    logging.debug(f"No updated tasks found")

        return updated_tasks_list
