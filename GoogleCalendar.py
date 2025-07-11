# Standar Library
from datetime import datetime, timedelta
import logging
import os.path
import json
# import uuid
import sys

# Third part libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local Modules
import config

# --- Configuration ---
# IMPORTANT: If modifying SCOPES, delete the file token.json.
# Need 'calendar.events' scope to create events.
# Use 'calendar' for full read/write access to calendars and events.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'credentials.json' # The file downloaded from Google Cloud Console
TOKEN_FILE = 'token.json'             # Stores user's access/refresh tokens


def _create_endtime(start_date: str, start_time: str, duration: int) -> datetime:
    start_datetime = datetime.combine(date=datetime.fromisoformat(start_date).date(), 
                                      time=datetime.strptime(start_time, "%H:%M").time())
    end_datetime = start_datetime + timedelta(minutes=duration)
    
    return f"{end_datetime.date()}T{end_datetime.time()}"


def authenticate_google_calendar():
    """Handle the authentication with the account"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except ValueError as e:
            logging.error(f"Error loading token file: {e}")
            # Check if it's a scope mismatch error
            try:
                with open(TOKEN_FILE, 'r') as token_file:
                    token_data = json.load(token_file)
                    if set(token_data.get('scopes', [])) != set(SCOPES):
                        logging.error("Detected scope mismatch. Please delete token.json and re-run.")
                    else:
                         logging.warning(f"Please delete {TOKEN_FILE} and try again.")
            except Exception: # Handle file reading errors etc.
                 logging.error(f"Please delete {TOKEN_FILE} and try again.")
            creds = None # Ensure creds is None if loading fails
        except Exception as e: # Catch other potential file issues
            logging.error(f"Unexpected error loading token file: {e}")
            logging.error(f"Consider deleting {TOKEN_FILE} and trying again.")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logging.info("Credentials expired, refreshing...")
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Error refreshing token: {e}")
                logging.error(f"Need to re-authenticate. Deleting {TOKEN_FILE} if it exists.")
                if os.path.exists(TOKEN_FILE):
                    try:
                        os.remove(TOKEN_FILE)
                        logging.info(f"{TOKEN_FILE} deleted.")
                    except OSError as oe:
                         logging.error(f"Error deleting {TOKEN_FILE}: {oe}")
                creds = None # Force re-authentication
        else:
            # Only run the flow if credentials file exists
            if not os.path.exists(CREDENTIALS_FILE):
                 logging.error(f"Error: Credentials file '{CREDENTIALS_FILE}' not found.")
                 logging.error("Please download it from Google Cloud Console and place it here.")
                 sys.exit(1) # Exit if credentials file is missing

            logging.error(f"No valid token found or refresh failed, starting authentication flow...")
            logging.error(f"Required Scopes: {SCOPES}")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            # Run local server flow for Desktop app type
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        if creds:
            try:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                logging.info(f"Credentials saved to {TOKEN_FILE}")
            except Exception as e:
                logging.error(f"Error saving token file: {e}")

    if not creds:
         logging.error("Failed to obtain credentials.")
         sys.exit(1) # Exit if authentication failed

    try:
        # Build the service object
        service = build('calendar', 'v3', credentials=creds)
        logging.info("Google Calendar API service created successfully.")
        return service
    except HttpError as error:
        logging.error(f'An error occurred building the service: {error}')
        return None
    except Exception as e:
        logging.error(f'An unexpected error occurred during service build: {e}')
        return None


def get_upcoming_events(service, calendar_id: str, max_results=1000) -> dict | None:
    """
    Fetches and prints the next 'max_results' events from the user's primary calendar.

    Args:
        service: Authorized Google Calendar API service instance.
        max_results: The maximum number of events to retrieve.
    """
    if not service:
        logging.error("Calendar service is not available for listing events.")
        return
    
    try:
        # today = datetime.today().date().isoformat() + 'T00:00:00Z'  # 'Z' indicates UTC time
        time_min = f"{datetime.today().date() - timedelta(days=7)}T00:00:00Z"  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result

    except HttpError as error:
        logging.error(f'An API error occurred while listing events: {error}')
        if error.resp.status == 403:
            logging.error("Error 403: Check if the Calendar API is enabled and your scopes grant read access.")
        elif error.resp.status == 401:
             logging.error("Error 401: Invalid Credentials. Try deleting token.json and re-authenticating.")
    except Exception as e:
        logging.error(f'An unexpected error occurred during event fetch: {e}')



def create_event(service, 
                 calendar_id: str, 
                 event_name: str,
                 task_uuid: str,
                 event_date: str,
                 event_start_time: str = ...,
                 all_day: bool = False,
                 duration: int = config.DEFAULT_DURATION
                 ) -> dict | None:
    """
    Creates a new event on the specified calendar.

    Args:
        service: Authorized Google Calendar API service instance.
        calendar_id: ID of the target calendar (e.g., 'primary').
        event_body: A dictionary representing the event resource.
                    See: https://developers.google.com/calendar/v3/reference/events#resource

    Returns:
        The created event resource dictionary, or None if creation failed.
    """
    if not service:
        logging.error("Calendar service is not available for creating events.")
        return None

    if all_day == True:
        event_body = {
            'summary': event_name,
            'description': task_uuid,
            'start': {
                'date': event_date,
                'timeZone': 'America/New_York',
            },
            'end': {
                'date': event_date,
                'timeZone': 'America/New_York',
            },
            'location': f"things:///show?id={task_uuid}",
        }
    else:
        event_body = {
            'summary': event_name,
            'description': task_uuid,
            'start': {
                'dateTime': f'{event_date}T{event_start_time}:00',
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': _create_endtime(event_date, event_start_time, duration),
                'timeZone': 'America/New_York',
            },
            'location': f"things:///show?id={task_uuid}",
        }

    try:
        logging.debug(f"\nCreating event on calendar: {calendar_id}")
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event_body,
            sendUpdates='none' # sendUpdates='none' means no notifications sent to attendees
        ).execute()

        logging.info(f"""\n\n{' EVENT CREATED ':-^54}
\tSummary: {created_event.get('summary')}
\tGoogle Calendar ID: {created_event.get('id')}
\tStatus: {created_event.get('status')}
\tThings UUID: {task_uuid}
{'-' * 54}\n""")
        
        return created_event

    except HttpError as error:
        logging.error(f'An API error occurred while creating event: {error}')
        if error.resp.status == 403:
             logging.error("Error 403: Ensure you have write permissions for this calendar.")
             logging.error(f"Current scopes: {SCOPES}. Required: Write access like '.../auth/calendar.events'")
             logging.error("You might need to delete token.json and re-authenticate.")
        elif error.resp.status == 404:
             logging.error(f"Error 404: Calendar with ID '{calendar_id}' not found.")
        elif error.resp.status == 400:
             logging.error(f"Error 400: Bad Request. Check the structure of your event_body:\n{json.dumps(event_data, indent=2)}")
        return None
    except Exception as e:
        logging.error(f'An unexpected error occurred during event creation: {e}')
        return None



def update_event(service,
                 calendar_id: str,
                 event_id: str,
                 event_name: str,
                 task_uuid: str,
                 event_date: str,
                 event_start_time: str = ...,
                 all_day: bool = False,
                 duration: int = config.DEFAULT_DURATION
                 ) -> dict | None:
    """
    Updates an existing event on the specified calendar.

    Args:
        service: Authorized Google Calendar API service instance.
        calendar_id: ID of the target calendar (e.g., 'primary').
        event_id: The ID of the event to update.
        event_body: A dictionary containing the fields to update.
                    See: https://developers.google.com/calendar/v3/reference/events#resource

    Returns:
        The updated event resource dictionary, or None if update failed.
    """
    if not service:
        logging.error("Calendar service is not available for updating events.")
        return None
    
    if all_day == True:
        event_body = {
            'summary': event_name,
            'description': task_uuid,
            'start': {
                'date': event_date,
                'timeZone': 'America/New_York',
            },
            'end': {
                'date': event_date,
                'timeZone': 'America/New_York',
            },
            'location': f"things:///show?id={task_uuid}",
        }
    else:
        event_body = {
            'summary': event_name,
            'description': task_uuid,
            'start': {
                'dateTime': f'{event_date}T{event_start_time}:00',
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': _create_endtime(event_date, event_start_time, duration),
                'timeZone': 'America/New_York',
            },
            'location': f"things:///show?id={task_uuid}",
        }
        

    try:
        logging.debug(f"\nUpdating event {event_id} on calendar: {calendar_id}")
        # Using patch for partial updates
        updated_event = service.events().patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body,
            sendUpdates='none' # sendUpdates='none' means no notifications sent to attendees
        ).execute()

        logging.info(f"""\n\n{' EVENT UPDATED ':-^54}
\tSummary: {updated_event.get('summary')}
\tGoogle Calendar ID: {updated_event.get('id')}
\tStatus: {updated_event.get('status')}
\tThings UUID: {task_uuid}
{'-' * 54}\n""")
        
        return updated_event

    except HttpError as error:
        logging.error(f'An API error occurred while updating event: {error}')
        if error.resp.status == 403:
             logging.error("Error 403: Ensure you have write permissions for this calendar.")
             # print(f"Current scopes: {SCOPES}. Required: Write access like '.../auth/calendar.events'") # Assuming SCOPES is defined
             logging.error("You might need to delete token.json and re-authenticate.")
        elif error.resp.status == 404:
             logging.error(f"Error 404: Event with ID '{event_id}' not found on calendar '{calendar_id}'.")
        elif error.resp.status == 400:
             logging.error(f"Error 400: Bad Request. Check the structure of your event_body:\n{json.dumps(event_body, indent=2)}")
        return None
    except Exception as e:
        logging.error(f'An unexpected error occurred during event update: {e}')
        return None



def delete_event(service,
                 calendar_id: str,
                 event_id: str
                 ) -> bool:
    """
    Deletes an existing event from the specified calendar.

    Args:
        service: Authorized Google Calendar API service instance.
        calendar_id: ID of the target calendar (e.g., 'primary').
        event_id: The ID of the event to delete.

    Returns:
        True if the event was successfully deleted, False otherwise.
    """
    if not service:
        logging.error("Calendar service is not available for deleting events.")
        return False

    if not event_id:
        logging.warning("Event ID is required for deleting an event.")
        return False

    try:
        logging.debug(f"\nAttempting to delete event {event_id} from calendar: {calendar_id}")
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates='none' # sendUpdates='none' means no notifications sent to attendees
        ).execute()

        logging.info(f"""\n\n{' EVENT DELETED ':-^54}
\tEvent ID: {event_id}
{'-' * 54}\n""")
        
        return True

    except HttpError as error:
        logging.error(f'An API error occurred while deleting event: {error}')
        if error.resp.status == 403:
            logging.error("Error 403: Ensure you have write permissions for this calendar.")
            logging.error("You might need to delete token.json and re-authenticate.")
        elif error.resp.status == 404:
            logging.error(f"Error 404: Event with ID '{event_id}' not found on calendar '{calendar_id}'.")
        return False
    except Exception as e:
        logging.error(f'An unexpected error occurred during event deletion: {e}')
        return False

