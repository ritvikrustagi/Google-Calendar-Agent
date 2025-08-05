from google_apis import create_service
import os
from datetime import datetime, timedelta

def get_calendar_service():
    """Initialize and return the Google Calendar service."""
    API_NAME = 'calendar'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    client_secret_file = os.path.join(os.getcwd(), 'client_secret.json')
    return create_service(client_secret_file, API_NAME, API_VERSION, *SCOPES)

def list_calendar_list(max_results=50):
    """Retrieve a list of calendars."""
    service = get_calendar_service()
    try:
        return service.calendarList().list(maxResults=max_results).execute().get('items', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def list_calendar_events(calendar_id='primary', max_results=20, time_min=None, time_max=None):
    """Retrieve events from a specific calendar."""
    service = get_calendar_service()
    
    # Set default time range if not provided
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    if not time_min:
        time_min = now
    if not time_max:
        time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
    
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def create_calendar(calendar_summary, calendar_description=''):
    """Create a new calendar."""
    service = get_calendar_service()
    calendar = {
        'summary': calendar_summary,
        'description': calendar_description,
        'timeZone': 'UTC'
    }
    
    try:
        created_calendar = service.calendars().insert(body=calendar).execute()
        return created_calendar
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def create_event(calendar_id, event_details):
    """Create a new event in the specified calendar."""
    service = get_calendar_service()
    
    try:
        event = service.events().insert(calendarId=calendar_id, body=event_details).execute()
        return event
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def update_event(calendar_id, event_id, event_details):
    """Update an existing event."""
    service = get_calendar_service()
    
    try:
        event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_details
        ).execute()
        return event
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def delete_event(calendar_id, event_id):
    """Delete an event."""
    service = get_calendar_service()
    
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def get_free_busy(time_min, time_max, items):
    """Get free/busy information for a set of calendars."""
    service = get_calendar_service()
    
    body = {
        'timeMin': time_min,
        'timeMax': time_max,
        'timeZone': 'UTC',
        'items': items
    }
    
    try:
        return service.freebusy().query(body=body).execute()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None