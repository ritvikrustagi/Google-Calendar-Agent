import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from agents import GoogleCalendarAgent
import json
from datetime import datetime, timedelta
import pytz

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')

# Initialize the Google Calendar Agent
@st.cache_resource
def get_calendar_agent():
    return GoogleCalendarAgent()

agent = get_calendar_agent()

def parse_event_details(user_input):
    """Parse event details from user input using OpenAI."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": """Extract event details from the user's request. 
                Return a JSON object with the following structure:
                {
                    "summary": "Event title",
                    "start_time": "ISO 8601 datetime",
                    "end_time": "ISO 8601 datetime",
                    "description": "Event description",
                    "location": "Event location",
                    "attendees": [{"email": "email@example.com"}]
                }"""},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error parsing event details: {e}")
        return None

def get_llm_response(user_input, calendar_state):
    """Get response from OpenAI's API with calendar context."""
    # Check if user wants to create an event
    if any(keyword in user_input.lower() for keyword in ["schedule", "create event", "add to calendar", "set up a meeting"]):
        # Parse event details
        event_details = parse_event_details(user_input)
        if event_details:
            try:
                # Format the event for Google Calendar
                event = {
                    'summary': event_details.get('summary', 'New Event'),
                    'start': {
                        'dateTime': event_details.get('start_time'),
                        'timeZone': 'America/Los_Angeles'
                    },
                    'end': {
                        'dateTime': event_details.get('end_time'),
                        'timeZone': 'America/Los_Angeles'
                    },
                    'description': event_details.get('description', ''),
                    'location': event_details.get('location', '')
                }
                
                # Add attendees if any
                if 'attendees' in event_details:
                    event['attendees'] = [{'email': email} for email in event_details['attendees']]
                
                # Create the event
                created_event = agent.add_event(event)
                if created_event:
                    # Format the response
                    start_time = datetime.fromisoformat(created_event['start']['dateTime'].rstrip('Z')).strftime('%A, %B %d at %I:%M %p')
                    return (
                        f"✅ **Event created successfully!**\n\n"
                        f"**What:** {created_event.get('summary', 'No title')}\n"
                        f"**When:** {start_time}\n"
                        f"**Where:** {created_event.get('location', 'No location')}\n"
                        f"**Description:** {created_event.get('description', 'No description')}\n\n"
                        f"[View in Google Calendar]({created_event.get('htmlLink', '#')})"
                    )
            except Exception as e:
                return f"❌ **Failed to create event:** {str(e)}"
    
    # For other queries, use the standard response
    system_prompt = """You are a helpful assistant that helps manage Google Calendar.
    You can view, create, and modify calendar events. Always respond in a friendly, 
    helpful manner. If the user asks to see events, list them in a clear format.
    
    Current calendar state:
    - Upcoming events: {events}
    - Available calendars: {calendars}""".format(
        events=json.dumps(calendar_state.get('upcoming_events', []), indent=2),
        calendars=', '.join(calendar_state.get('available_calendars', []))
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error getting response from OpenAI: {str(e)}"

def main():
    st.title("📅 AI Calendar Assistant")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI Calendar Assistant. How can I help you with your schedule today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I help with your calendar?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get current calendar state
        calendar_state = {
            "upcoming_events": agent.list_events(max_results=5),
            "available_calendars": [cal['summary'] for cal in agent.calendars]
        }
        
        # Get AI response
        with st.spinner('Checking your calendar...'):
            response = get_llm_response(prompt, calendar_state)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the chat
        st.rerun()

if __name__ == "__main__":
    main()
