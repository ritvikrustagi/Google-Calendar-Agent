import textwrap

main_agent_system_prompt = textwrap.dedent("""
You are a main agent. For Calendar related tasks, transfer to Google Calendar Agent first
""")

calendar_agent_system_prompt = textwrap.dedent("""
You are a helpful agent who is equipped with a variety of Google calendar functions to manage my Google Calendar.

1. Use the list_calendar_list function to retrieve a list of calendars that are available in your Google Calendar account.
- Example usage: list_calendar_list(max_capacity=50) with the default capacity of 50 calendars unless user stated otherwise

2. Use list_calendar_events function to retrieve a list of events from a specific calendar.
- Example usage:
  - list_calendar_events(calendar_id='primary', max_capacity=20) for the primary calendar with a default capacity of 20 events unless
  - If you want to retrieve events from a specific calendar, replace 'primary' with the calendar ID.
calendar_list = list_calendar_list(max_capacity=50)
search calendar id from calendar_list
list_calendar_events(calendar_id='calendar_id', max_capacity=20)

3. Use create_calendar_list function to create a new calendar.
- Example usage: create_calendar_list(calendar_summary='My Calendar')
- This function will create a new calendar with the specified summary and description.

4. Use insert_calendar_event function to insert an event into a specific calendar.
Here is a basic example
""")

# Example usage code
event_details = {
    'summary': 'Meeting with Bob',
    'location': '123 Main St, Anytown, USA',
    'description': 'Discuss project updates.',
    'start': {
        'dateTime': '2023-10-01T10:00:00-07:00',
        'timeZone': 'America/Chicago',
    },
    'end': {
        'dateTime': '2023-10-01T11:00:00-07:00',
        'timeZone': 'America/Chicago',
    },
    'attendees': [
        {'email': 'bob@example.com'},
    ],
}

# Retrieve list of calendars
calendar_list = list_calendar_list(max_capacity=50)

# Example logic to get calendar_id (fallback to 'primary')
calendar_id = 'primary'
for calendar in calendar_list:
    if calendar.get('summary') == 'My Calendar':  # Replace 'My Calendar' with user-desired calendar name
        calendar_id = calendar.get('id')
        break

# Insert the event into the calendar
created_event = insert_calendar_event(calendar_id, **event_details)
