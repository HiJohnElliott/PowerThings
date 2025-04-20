from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
from pprint import pprint


def list_upcoming_calendar_events(creds: Credentials, calendar_id: str, print_results=False) -> list:
    """Calls The Google API and returns a list of all events on a calendar
    
    Paramaters:
    -----------
    creds: The credentials that need to be passed from the Google Oauth2 library
    calendar_id: The ID of the calendar that you want to gather resutls from 
    print_results: A bool flag that you can set for whether you want to see the results printed in the console. 
                   For debugging purposes. 
    """    
    service = build("calendar", "v3", credentials=creds)
    
    now = datetime.now(timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId=calendar_id,
        # timeMin=now,
        # maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    events = events_result.get("items", [])
    
    if not events:
        if print_results == True:
            print("No upcoming events found.")
        return []
    
    if print_results == True:
        for event in events:        
            print(event)
    
    return events


def add_calendar_event(
        calendar_id: str, 
        uuid: str, 
        event_name: str, 
        event_date: str, 
        event_start_time: str,  
        duration: int = 60,
        ):

    dt = datetime.strptime(event_start_time ,"%H:%M")
    delta = dt + timedelta(minutes=duration)
    event_end_time = delta.time()

    event_data = {
        'summary': event_name,
        'description': uuid,
        'start': {
          'dateTime': f'{event_date}T{event_start_time}',
          'timeZone': 'America/New_York',
        },
        'end': {
          'dateTime': f'{event_date}T{event_end_time}',
          'timeZone': 'America/New_York',
        },
        'location': f"things:///show?id={uuid}",
    }
    
    service = build("calendar", "v3", credentials=creds)
    created_event = service.events().insert(
            calendarId=calendar_id,
            body=event_data,
            sendUpdates='none' # sendUpdates='none' means no notifications sent
        ).execute()
    return created_event











if __name__ == "__main__": 
    import api as things
    THINGS_CALENDAR_ID = "d80beafee68bdb1b2b26937ac30ba3a4322cf06d07d4767922e114e19ba0edcb@group.calendar.google.com"
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar.readonly'])
    # pprint(list_upcoming_calendar_events(creds, calendar_id=THINGS_CALENDAR_ID, print_results=True))

    task = things.get('chGCxv3R5QyMn4BBTkvJw')
    pprint(add_calendar_event(calendar_id=THINGS_CALENDAR_ID, uuid=task['uuid'], event_name=task['title'], event_date=task['start_date'], event_start_time=task['reminder_time']))









"""    event_info = {
        'summary': 'Charge Mouse ',
        # 'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'chGCxv3R5QyMn4BBTkvJw',
        'start': {
          'dateTime': '2015-05-28T09:00:00-07:00',
          'timeZone': 'America/Los_Angeles',
        },
        'end': {
          'dateTime': '2015-05-28T17:00:00-07:00',
          'timeZone': 'America/Los_Angeles',
        },
        # 'recurrence': [
        #   'RRULE:FREQ=DAILY;COUNT=2'
        # ],
        # 'attendees': [
        #   {'email': 'lpage@example.com'},
        #   {'email': 'sbrin@example.com'},
        # ],
        # 'reminders': {
        #   'useDefault': False,
        #   'overrides': [
        #     {'method': 'email', 'minutes': 24 * 60},
        #     {'method': 'popup', 'minutes': 10},
        #   ],
        # },
    }
    
"""