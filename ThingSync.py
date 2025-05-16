"""Sync Service for Things and Calendar

This program will routinely check your tasks in Things and if they are not synced to your calendar, a new event is created so that your scheduled tasks appear. 

This program will also check on the times of existing task-events in Calendar and if the time of the event differs from the task, the task will be updated. 
"""
import tracemalloc
import threading
import logging
import time
import gc

from task_controller import CurrentTasks
import Things.api as things
import google_calendar as gCal
import sync_controller as sync

from pprint import pprint



def main(state, service):
    if state.detect_state_updates():
        updated_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        
        if updates := state.list_updated_tasks(updated_tasks):
            sync.update_tasks_on_calendar(service, updates)
        
        if state.detect_new_reminder_times():
            sync.add_new_tasks_to_calendar(service)
    
        
        state.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')
        print(f"{gc.collect()} items garbage collected")


if __name__ == "__main__":
    # Set the state and initiate the Google Calendar service/auth flow
    logs = logging.basicConfig(level=logging.INFO)
    state = CurrentTasks()
    state.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')
    service = gCal.authenticate_google_calendar()

    # Thread 1: Listen for change notifications from gCal 


    # Thead 2: Monitor Things db for changes to tasks
    while True:
        # tracemalloc.start()
        main(state, service)
        # snapshot = tracemalloc.take_snapshot()
        # stats = snapshot.statistics('lineno')
        # print('\n')
        # for stat in stats:
        #     print(stat)
        # print('\n')
        # gc.collect()
        time.sleep(1)