"""Sync Service for Things and Calendar

This program will routinely check your tasks in Things and if they are not synced to your calendar, a new event is created so that your scheduled tasks appear. 

This program will also check on the times of existing task-events in Calendar and if the time of the event differs from the task, the task will be updated. 
"""
from task_controller import CurrentTasks
import Things.api as things
import google_calendar as gCal
import sync_controller as sync
import threading
import time
import gc
from pprint import pprint


def main(state, service):
    if state.detect_state_updates():
        updated_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        
        if updates := state.list_updated_tasks(updated_tasks):
            sync.update_tasks_on_calendar(service, updates)
        
        if state.detect_new_reminder_times():
            sync.add_new_tasks_to_calendar(service)
        
        # TODO: add function to update tasks on cal for any tasks that are changed  
        
        state.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')


if __name__ == "__main__":
    # Set the state and initiate the Google Calendar service/auth flow
    state = CurrentTasks()
    state.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')
    service = gCal.authenticate_google_calendar()

    # Thread 1: Listen for change notifications from gCal 


    # Thead 2: Monitor Things db for changes to tasks
    while True:
        main(state, service)
        # gc.collect()
        time.sleep(1)