"""Sync Service for Things and Calendar

This program will routinely check your tasks in Things and if they are not synced to your calendar, a new event is created so that your scheduled tasks appear. 

This program will also check on the times of existing task-events in Calendar and if the time of the event differs from the task, the task will be updated. 
"""

# import statements 
from datetime import datetime, time
from pprint import pprint
import time
import api as things

def get_upcoming_tasks():
    return things.upcoming()


def get_upcoming_calendar_events():
    ...

def add_calendar_event(event_name: str, event_date: str, event_time: str, details: str, task_url: str):
    ...


def update_things_task(task_id: str):
    # This will inherit functions from makeThings.py
    ...




if __name__ == "__main__":

    pprint(get_upcoming_tasks())
    # for task in get_upcoming_tasks():
        # if task.get('reminder_time'):
        # print(f"{task['uuid']:<22} | {task['title']} | {task['start_date']}")
        
        
        
        # if 'reminder_time' in task:
        #     print(f"{task['uuid']:<22} | {task['title']} | {task['start_date']}")
        # if task['area'] == 'Home':
        #     print(task)
    # pprint(things.get('7SfVtqmdqSgMzmDS3bTnJR'))