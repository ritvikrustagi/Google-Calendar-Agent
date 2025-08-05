import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from agents import GoogleCalendarAgent
import json
from datetime import datetime, timedelta

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

def get_llm_response(user_input, calendar_state):
    """Get response from OpenAI's API with calendar context."""
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
        st.session_state.messages = []
    
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
        with st.spinner('Thinking...'):
            response = get_llm_response(prompt, calendar_state)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the chat
        st.rerun()

if __name__ == "__main__":
    main()
