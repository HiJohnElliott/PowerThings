"""Sync Service for Things and Calendar

This program will routinely check your tasks in Things and if they are not synced to your calendar, a new event is created so that your scheduled tasks appear. 

This program will also check on the times of existing task-events in Calendar and if the time of the event differs from the task, the task will be updated. 
"""
import task_controller

def main():
    task_controller.add_new_tasks_to_calendar()
    # check for changes in things tasks
    # if change detected: 
        # Add new tasks to cal 
        # update tasks on cal 


if __name__ == "__main__":
    main()