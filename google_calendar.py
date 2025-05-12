# Standar Library
from datetime import datetime, timedelta
import logging
import os.path
import json
import uuid
import sys

# Third part libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local Modules
import keys

# --- Configuration ---
# IMPORTANT: If modifying SCOPES, delete the file token.json.
# Need 'calendar.events' scope to create events.
# Use 'calendar' for full read/write access to calendars and events.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'credentials.json' # The file downloaded from Google Cloud Console
TOKEN_FILE = 'token.json'             # Stores user's access/refresh tokens


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


def get_upcoming_events(service, calendar_id: str, max_results=1000) -> dict:
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
        # now = datetime.today().date().isoformat() + 'Z'  # 'Z' indicates UTC time
        now = datetime.today().date().isoformat() + 'T00:00:00Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
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
                 event_start_time: str,
                 duration: int = keys.DEFAULT_DURATION
                 ) -> dict:
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
    
    dt = datetime.strptime(event_start_time ,"%H:%M")
    delta = dt + timedelta(minutes=duration)
    event_end_time = delta.time()

    event_data = {
        'summary': event_name,
        'description': task_uuid,
        'start': {
          'dateTime': f'{event_date}T{event_start_time}:00',
          'timeZone': 'America/New_York',
        },
        'end': {
          'dateTime': f'{event_date}T{event_end_time}',
          'timeZone': 'America/New_York',
        },
        'location': f"things:///show?id={task_uuid}",
    }

    try:
        logging.info(f"\nCreating event on calendar: {calendar_id}")
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event_data,
            sendUpdates='none' # sendUpdates='none' means no notifications sent to attendees
        ).execute()

        logging.info(f"""\n\n---- Event Created ----
\tSummary: {created_event.get('summary')}
\tID: {created_event.get('id')}"
\tStatus: {created_event.get('status')}
\tLink: {created_event.get('htmlLink')}
----------------------\n""")
        
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
                 event_start_time: str,
                 duration: int = keys.DEFAULT_DURATION
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
    
    dt = datetime.strptime(event_start_time ,"%H:%M")
    delta = dt + timedelta(minutes=duration)
    event_end_time = delta.time()
    
    event_body = {
        'summary': event_name,
        'description': task_uuid,
        'start': {
          'dateTime': f'{event_date}T{event_start_time}:00',
          'timeZone': 'America/New_York',
        },
        'end': {
          'dateTime': f'{event_date}T{event_end_time}',
          'timeZone': 'America/New_York',
        },
        'location': f"things:///show?id={task_uuid}",
    }
    

    try:
        logging.info(f"\nUpdating event {event_id} on calendar: {calendar_id}")
        # Using patch for partial updates
        updated_event = service.events().patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body,
            sendUpdates='none' # sendUpdates='none' means no notifications sent to attendees
        ).execute()

        logging.info(f"""\n\n---- Event Updated ----
\tSummary: {updated_event.get('summary')}
\tID: {updated_event.get('id')}
\tStatus: {updated_event.get('status')}
\tLink: {updated_event.get('htmlLink')}
-----------------------\n""")
        
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
                 ):
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
        logging.info(f"\nAttempting to delete event {event_id} from calendar: {calendar_id}")
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates='none' # sendUpdates='none' means no notifications sent to attendees
        ).execute()

        logging.info(f"""\n\n---- Event Deleted ----
Event ID: {event_id} successfully deleted."
-----------------------\n")""")
        
        return True

    except HttpError as error:
        logging.error(f'An API error occurred while deleting event: {error}')
        if error.resp.status == 403:
            logging.errort("Error 403: Ensure you have write permissions for this calendar.")
            logging.error("You might need to delete token.json and re-authenticate.")
        elif error.resp.status == 404:
            logging.error(f"Error 404: Event with ID '{event_id}' not found on calendar '{calendar_id}'.")
        return False
    except Exception as e:
        logging.error(f'An unexpected error occurred during event deletion: {e}')
        return False



def watch_calendar(service, calendar_id, webhook_url, channel_token=None):
    """
    Subscribes to push notifications for a given calendar.

    Args:
        service: Authorized Google Calendar API service instance.
        calendar_id: ID of the calendar to watch (e.g., 'primary').
        webhook_url: The HTTPS URL where Google should send notifications.
                     MUST be publicly accessible and registered in Google Cloud Console
                     if using certain Google Cloud services.
        channel_token: (Optional) A secret token you provide, which Google
                       will include in the X-Goog-Channel-Token header of
                       notifications, allowing your webhook to verify the source.

    Returns:
        The watch response dictionary containing 'id', 'resourceId', 'expiration', etc.,
        or None if the watch request failed.
    """
    if not service:
        print("Calendar service is not available for watching.")
        return None
    if not webhook_url.lower().startswith("https"):
        print("Error: Webhook URL must use HTTPS.")
        return None

    # Generate a unique ID for this channel
    channel_id = str(uuid.uuid4())
    print(f"Attempting to watch calendar '{calendar_id}' with channel ID: {channel_id}")
    print(f"Notifications will be sent to: {webhook_url}")

    watch_body = {
        "id": channel_id,        # A unique identifier for the channel
        "type": "web_hook",      # The channel type
        "address": webhook_url,  # Your HTTPS webhook URL
    }

    # Add the verification token if provided
    if channel_token:
        watch_body["token"] = channel_token
        print(f"Using channel verification token.")


    try:
        watch_response = service.events().watch(
            calendarId=calendar_id,
            body=watch_body
        ).execute()

        print("\n--- Watch Request Successful ---")
        expiration_ms = int(watch_response.get('expiration', 0))
        if expiration_ms > 0:
            # Convert milliseconds timestamp to human-readable UTC date
            expiration_dt = datetime.utcfromtimestamp(expiration_ms / 1000)
            print(f"Channel ID: {watch_response.get('id')}")
            print(f"Resource ID: {watch_response.get('resourceId')}") # Should match the calendar resource being watched
            print(f"Expiration (UTC): {expiration_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Watch details: {json.dumps(watch_response, indent=2)}")
        print("-----------------------------\n")

        # IMPORTANT: Your webhook at webhook_url must now handle incoming POSTs
        #            including a 'sync' message to confirm setup.

        return watch_response

    except HttpError as error:
        print(f'An API error occurred during watch request: {error}')
        # Common errors: 400 (Bad request - check body), 401 (auth), 404 (calendar not found)
        #               500 series (Google internal errors)
        # A 403 might mean the webhook URL domain isn't authorized/verified in your GCP project.
        print(f"Response content: {error.content}")
        return None
    except Exception as e:
        print(f'An unexpected error occurred during watch request: {e}')
        return None



def stop_channel(service, channel_id, resource_id) -> bool:
    """Stops push notifications on a specific channel."""
    if not service:
        print("Calendar service is not available for stopping channel.")
        return False
    try:
        print(f"Attempting to stop channel ID: {channel_id}, Resource ID: {resource_id}")
        body = {
            'id': channel_id,
            'resourceId': resource_id
        }
        service.channels().stop(body=body).execute()
        print("Channel stopped successfully.")
        return True
    except HttpError as error:
        print(f"An API error occurred trying to stop the channel: {error}")
        # A 404 might mean the channel already expired or doesn't exist
        return False
    except Exception as e:
        print(f"An unexpected error occurred stopping the channel: {e}")
        return False



# --- Main Execution ---
if __name__ == '__main__':
    print("----------------------------------------------------")
    print("Google Calendar API Interaction Script")
    print("----------------------------------------------------")

    # --- Step 1: Authenticate ---
    # IMPORTANT: If you changed SCOPES above, DELETE token.json first!
    print("\n--- Step 1: Authentication ---")
    calendar_service = authenticate_google_calendar()

    if calendar_service:
        print("\nAuthentication Successful.")

        # --- Step 2: List Upcoming Events ---
        print("\n--- Step 2: Listing Upcoming Events ---")
        get_upcoming_events(calendar_service, max_results=5) # List fewer for demo

        # --- Step 3: Create a New Event ---
        print("\n--- Step 3: Creating a Sample Event ---")

        # Define the event body
        # Use IANA Time Zone Database names (e.g., 'America/New_York', 'Europe/London')
        # Find yours: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # Let's create an event for tomorrow at 10 AM in the specified timezone
        tz = "America/New_York" # CHANGE THIS TO YOUR TIMEZONE if needed
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        start_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 10, 0, 0) # 10:00 AM
        end_time = start_time + datetime.timedelta(hours=1) # Event duration 1 hour

        # Format for API (ISO 8601) - Note: Python < 3.9 doesn't easily add tzinfo here
        # We will rely on the 'timeZone' field in the request body for the API to interpret correctly
        # For robustness with older Python, you might construct the string manually with offset
        # or use the 'pytz' library. The API generally handles dateTime + timeZone well.
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()

        sample_event_body = {
            'summary': 'Demo Event via Python Script',
            'location': 'My Computer',
            'description': f'This event was created automatically by a Python script.\nScript run time: {datetime.datetime.now()}',
            'start': {
                'dateTime': start_iso,
                'timeZone': tz,
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': tz,
            },
            # Optional: Add attendees
            # 'attendees': [
            #     {'email': 'friend@example.com'},
            # ],
             # Optional: Add reminders (popup 10 min before, email 1 hour before)
             'reminders': {
                 'useDefault': False,
                 'overrides': [
                     {'method': 'popup', 'minutes': 10},
                     {'method': 'email', 'minutes': 60},
                 ],
             },
             # Optional: Add a Google Meet link
             # Requires enabling "Hangouts Meet" support in your API project? (might just work)
             # 'conferenceData': {
             #     'createRequest': { 'requestId': f"sample{datetime.datetime.now().timestamp()}" }
             # }
        }

        print(f"Attempting to create event '{sample_event_body['summary']}' for tomorrow.")
        # Create event on the user's primary calendar
        created_event_details = create_event(calendar_service, 'primary', sample_event_body)

        if created_event_details:
            print("Sample event creation process completed.")
        else:
            print("Sample event creation failed.")

    else:
        print("\nCould not get Calendar service. Exiting.")

    print("\n----------------------------------------------------")
    print("Script finished.")
    print("----------------------------------------------------")