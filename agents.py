from calendar_tools import (
    list_calendar_list,
    list_calendar_events,
    create_calendar,
    create_event,
    update_event,
    delete_event,
    get_free_busy
)
from datetime import datetime, timedelta
import json

class GoogleCalendarAgent:
    def __init__(self):
        self.name = "Google Calendar Agent"
        self.calendars = []
        self.current_calendar = 'primary'
        self.update_calendar_list()
    
    def update_calendar_list(self, max_results=50):
        """Update the list of available calendars."""
        self.calendars = list_calendar_list(max_results)
        return self.calendars
    
    def list_events(self, calendar_id=None, max_results=20, days_ahead=30):
        """List events from a calendar."""
        calendar_id = calendar_id or self.current_calendar
        time_min = datetime.utcnow().isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events = list_calendar_events(
            calendar_id=calendar_id,
            max_results=max_results,
            time_min=time_min,
            time_max=time_max
        )
        
        # Format events for display
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            formatted_events.append({
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'start': start,
                'end': end,
                'status': event.get('status')
            })
        
        return formatted_events
    
    def create_calendar(self, summary, description=''):
        """Create a new calendar."""
        result = create_calendar(summary, description)
        if result:
            self.update_calendar_list()
        return result
    
    def add_event(self, event_details, calendar_id=None):
        """Add a new event to the calendar."""
        calendar_id = calendar_id or self.current_calendar
        return create_event(calendar_id, event_details)
    
    def modify_event(self, event_id, event_details, calendar_id=None):
        """Update an existing event."""
        calendar_id = calendar_id or self.current_calendar
        return update_event(calendar_id, event_id, event_details)
    
    def remove_event(self, event_id, calendar_id=None):
        """Delete an event."""
        calendar_id = calendar_id or self.current_calendar
        return delete_event(calendar_id, event_id)
    
    def check_availability(self, time_min, time_max, calendar_ids=None):
        """Check availability across multiple calendars."""
        if not calendar_ids:
            calendar_ids = [self.current_calendar]
        
        items = [{'id': cal_id} for cal_id in calendar_ids]
        return get_free_busy(time_min, time_max, items)
    
    def find_calendar_by_name(self, name):
        """Find a calendar by its name/summary."""
        for cal in self.calendars:
            if cal.get('summary') == name:
                return cal
        return None

# Example usage
if __name__ == "__main__":
    agent = GoogleCalendarAgent()
    
    # Example: List all calendars
    print("Available calendars:")
    for cal in agent.calendars:
        print(f"- {cal['summary']} (ID: {cal['id']})")
    
    # Example: List upcoming events
    print("\nUpcoming events:")
    events = agent.list_events(max_results=5)
    for event in events:
        print(f"- {event['summary']} from {event['start']} to {event['end']}")
