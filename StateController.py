# from datetime import datetime
import Things.api as things
import logging
import keys


# This class holds the state of extant tasks. 
# It can be used to compare the state of tasks in the Things app versus the state
# of sync between the app and the calendar. It can also be used to detect changes
# in the Things app versus the sync state of tasks. 
class State:
    def __init__(self):
        self.current_tasks = list()


    def detect_state_updates(self) -> bool:
        """Returns True if changes are found in Things app"""
            
        updated_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        if updated_tasks == self.current_tasks:
            return False 
        else:
            logging.debug("State Update Found")
            return True


    def detect_new_reminder_times(self) -> bool:
        """Returns True if new reminder timse are found on any new tasks"""
        
        #TODO: Remove updated_tasks function calls from this function and make a param that gets passed instead     
        updated_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        new_tasks = [task for task in updated_tasks if task not in self.current_tasks]
        valid_reminder_times = [task for task in new_tasks if task.get('reminder_time')]
        
        if valid_reminder_times:
            logging.info("Updated Reminder Time Found")
            return True
        else:
            return False
        

    def list_updated_tasks(self, updated_tasks: list[dict]) -> list[str]:
        updated_task_ids = []

        for task in updated_tasks:
            state_task = [i for i in self.current_tasks if i['uuid'] == task['uuid']]
            if not state_task:
                # If a task is totally new, then it's ID won't be in state_task yet
                pass 
            elif task == state_task[0]:
                # If the state_task and updated task are the same then we don't need to update anything
                pass
            elif not state_task[0].get('reminder_time'):
                pass
                # No need to update the calendar if there is no reminder time. 
                
                # TODO: There is a case here where a task can have a reminder_time that is later taken away. 
                # When this is the case, the state_task will have reminder_time and the task in this loop won't. 
                # This would ideally mean that the task should be deleted from the calendar since it no longer has a reminder time. 

                # The other case that should be handled here is that a task no longer has a start_date. 
                # If no start_date or reminder_time, then the task should be deleted from the calendar. 

                # The solution here could be to have this function return a list[dict] with each uuid having a having an instruction. For example: 
                # [{123456789: update}, {987654321: update}, {6789012345: delete}]
                # This way, each uuid has an instruction that can be passed to the sync_controller. 
            else:
                # Only update this event if one of these fields specifically has changed 
                state_task = state_task[0]
                state_task_values = {'title': state_task['title'],
                                     'uuid': state_task['uuid'],
                                     'reminder_time': state_task['reminder_time']}
                
                updated_task_values = {'title': task['title'],
                                       'uuid': task['uuid'],
                                       'reminder_time': task['reminder_time']}
                
                if state_task_values != updated_task_values:
                    logging.debug(f"{task['uuid']} | {task['title']}")
                    updated_task_ids.append(task['uuid'])

        return updated_task_ids

