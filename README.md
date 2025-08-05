# Google Calendar Agent

A Python-based agent for managing Google Calendar operations through the Google Calendar API.

## Features

- List all available calendars
- View events from any calendar
- Create new calendars
- Add, update, and delete events
- Check calendar availability
- Manage multiple calendars

## Prerequisites

1. Python 3.7 or higher
2. Google Cloud Platform (GCP) project with the Google Calendar API enabled
3. OAuth 2.0 credentials (client_secret.json) from the Google Cloud Console

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your `client_secret.json` file in the project root directory
4. Run the agent:
   ```bash
   python agents.py
   ```

## Usage

### Basic Usage

```python
from agents import GoogleCalendarAgent

# Initialize the agent
agent = GoogleCalendarAgent()

# List all calendars
calendars = agent.update_calendar_list()
for cal in calendars:
    print(f"- {cal['summary']} (ID: {cal['id']})")

# List upcoming events
events = agent.list_events(max_results=5)
for event in events:
    print(f"- {event['summary']} from {event['start']} to {event['end']}")

# Create a new event
event_details = {
    'summary': 'Meeting with Team',
    'location': 'Office',
    'description': 'Weekly team sync',
    'start': {
        'dateTime': '2023-10-01T10:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2023-10-01T11:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
}

created_event = agent.add_event(event_details)
print(f"Created event: {created_event.get('htmlLink')}")
```

## Authentication

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials as `client_secret.json` and place it in the project root

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
