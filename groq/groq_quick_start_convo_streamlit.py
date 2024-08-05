import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY environment variable not set")
    st.stop()

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

# Set the system prompt
system_prompt = {
    "role": "system",
    "content": "You are a helpful assistant. You reply with very short answers."
}

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [system_prompt]

st.title("Groq Chatbot")

# Function to display chat messages
def display_chat_messages():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            st.write(f"**Assistant:** {message['content']}")

# Display chat messages
display_chat_messages()

# User input
user_input = st.text_input("Enter your message:", key="user_input")

# Process user input when the user presses Enter
if st.button("Send"):
    if user_input:
        # Append the user input to the chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Send the chat history to the Groq API
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=st.session_state.chat_history,
            max_tokens=2000,
            temperature=1.2
        )

        # Append the response to the chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        # Refresh the app to display the new messages
        st.experimental_rerun()
