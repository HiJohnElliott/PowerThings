# ThingSync
#### A simple Python sync service for the Things task manager. 

## Description
The [award-winning Things app made by Cultured Code](https://culturedcode.com/things/) is a masterclass in UI design on Apple's various devices and is one of the best ways to manage tasks on any platform. While it does a great job of balancing simplicity and capability, there has always been one feature that I've felt was missing: calendar syncing. While seeing a list of all the tasks you need to do is very helpful in organizing your work, it doesn't help you get a very good sense for how those tasks will fit in to your day. A calendar is much better suited to this task and is also better at allowing you to see how your tasks will fit in to the context of all of your other appointments. 

ThingSync works as a sync service between your Things application and a calendar of your choosing. It is designed to be modular, configurable, and unobtrusive so that it can be custom tailored to meet a wide variety of needs and preferences and to run in the background on a Mac while using a minimum of system resources. 


## What ThingSync Does
Once ThingSync is running, a Things task will be synced to your calendar if it meets the following criteria: 

1. It has a due date set in the future or in the last 90 days
2. It has a reminder time set
3. The task's status is "incomplete"

Naturally, to appear on a calendar, a task needs to be incomplete, have a start date, and also have a reminder time set. In the Things app, if the task has a start date and reminder time and is showing on your Today or Upcoming views, then it should also appear on your calendar. 

ThingSync will also update your calendar events based on changes you make to your tasks in Things. For example, if you change the title, date, or time of a task, it will be changed on the calendar event as well.

At this time, ThingSync is only a one-way sync. In other words, your tasks in the Things app are treated as the source of truth and any changes made on the calendar itself will not be synced back to your tasks in Things. 


## Zen Mode
There are two different ways to conceptually handle completed tasks on your calendar. One way, is to have a persistent record for all of your tasks so that you can go back in time and see what tasks you completed in the context of your other calendar appointments. In this mode, once a task is scheduled, it stays on your calendar forever whether it is completed or not. This mental model matches well with way all over calendar events work since they don't disappear once they are in the past. 

The other way to handle completed tasks is by removing them from the calendar once they are completed since they no longer need to get done and no longer require your focus. This mental model more closely aligns with the experience you get in a task manager where tasks *do* disappear from view once they are completed. 

With Zen Mode activated, once a task is completed, it is removed from your calendar so that you are only presented with tasks that still need to be done and you aren't burdened by the clutter of already completed tasks. This will also better match with the state of your tasks in Things. 

By default, Zen Mode is turned on. However, this can be changed by opening the `config.py` file and setting ZEN_MODE to `False`. 


## Default Duration and Duration Tags 
The `config.py` contains a setting for default duration. By default this duration is set to 60 minutes for all calendar events. To change the default duration of all calendar events, simply set `DEFAULT_DURATION` to the number of minutes you would like. 

If you would like to have more control over the duration of your calendar events, you can use duration tags on your task in Things, and the calendar event will instead use the duration specified in the tag instead of the default. For example, adding a tag like "45m" or "1h" will set the duration of that task's calendar event to 45 minutes and 1 hour respectively. You can even change the duration tag after the event has been added to your calendar to update the duration of the calendar event. 

Duration tags need to be formatted as an integer followed by an "h" for number of hours or an "m" for the number of minutes. Adding other tags to the task is totally safe as only tags that contain an integer and end in an "h" or an "m" will be treated like a duration tag. If you have more than one duration tag added to a task, only the first tag will be used to set the duration. 


## The Deadlines Calendar
Tasks and projects that have deadlines can be added to a deadlines calender. The deadlines calendar can be turned on and off in the config.py file. If you turn this feature on, you will need to supply a calendar URL for `DEADLINES_CALENDAR_ID` in the .env file. 

When deadlines are included on a task or project, the deadline will appear on your deadline calendar as an all day event. Personally, I would recommend creating a sepereate calendar called Deadlines in Google Calendar and setting it to red to match Things color pattern. This also makes it easy to see your upcoming deadlines at a glance in the month view of your calenadering app of choice. 

# Setup 
## Setting Up Google Calendar
- Directions for setting up the Google API
- Grabbing the Google Calendar ID 
- Getting the Things Auth token 


## UV and Managing Dependencies 
This project makes use of [UV](https://github.com/astral-sh/uv) to manage dependencies. If you have UV installed on your machine, you can simply use `uv run ThingSync.py` to get up and running quickly without the need for complicated package management. If you would like to install UV, [you can learn how to do so here](https://docs.astral.sh/uv/guides/install-python/). You can of course manage the dependencies using the `pyprojet.toml` file as well or however you choose. 


## What ThingSync is *Not*
ThingSync does not directly use [Things Cloud](https://culturedcode.com/things/support/articles/2803586/) to gather your task data. Instead, ThingSync checks the actual data used by the Things application on your Mac to check for changes directly on device. This is made possible by the excellent [Things.py](https://pypi.org/project/things.py/) library which is maintained at this [GitHub link](https://github.com/thingsapi/things.py). This also means that the Things application is exclusively responsible for handling the syncing of data with Things Cloud and thus, must be running to get changes made on other devices. 


## Known Issues 
- Tasks with reoccuring events are not supported yet. For example, if a task is on your Today or Upcoming views and repeats every week, only the nearest upcoming event will show on the calendar and not any subsequent reocurring events. 
- When converting a task that is on your calendar to a project, an error occurs when crashes ThingSync due to the uuid of the task no longer appearing where it should. 


## Features in Consideration for Future Development 
- Support for reoccuring events 
- Auto-Scheudling of events. This would take a look at any event on your Today view without a reminder time, evaluting the tasks on your calendar and what kind of task it is, and add a reminder time to the task 
- Two-way Sync. This would ideally allow for you to manually move calendar events around on your calendar app of choice and it would change the information on the task in things. 
- A morning summary email gets sent at a specified time that lists all of your tasks for the day. Maybe even an AI-generated bit artwork in the email about your tasks for the day.  