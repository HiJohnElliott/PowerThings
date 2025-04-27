"""Sync Service for Things and Calendar

This program will routinely check your tasks in Things and if they are not synced to your calendar, a new event is created so that your scheduled tasks appear. 

This program will also check on the times of existing task-events in Calendar and if the time of the event differs from the task, the task will be updated. 
"""
from task_controller import CurrentTasks
import Things.api as things
import sync_controller
import threading
import time


def main(state):
    if CurrentTasks.detect_task_updates(state, current_state=state.current_tasks):
        sync_controller.add_new_tasks_to_calendar()
        # update tasks on cal 
        state.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')


if __name__ == "__main__":
    # Set the state
    state = CurrentTasks()
    state.current_tasks = things.today() + things.upcoming() + things.completed(last='1d')

    # Thread 1: Listen for change notifications from gCal 


    # Thead 2: Monitor Things db for changes to tasks
    while True:
        main(state)
        time.sleep(1)