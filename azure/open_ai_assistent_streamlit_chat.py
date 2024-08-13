import os  # For accessing environment variables
import time  # For adding delays in the code
import streamlit as st  # For building the web app UI
from openai import AzureOpenAI  # For interacting with Azure OpenAI
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# Instructions to set up Azure OpenAI:
# 1. Go to the Azure Portal (https://portal.azure.com)
# 2. Create a new Azure OpenAI resource
# 3. In the resource, go to "Keys and Endpoint" 
# 4. Copy the API key and endpoint
# 5. Create a .env file in the same directory as this script
# 6. Add the following lines to the .env file:
#    AZURE_OPENAI_API_KEY=your_api_key_here
#    AZURE_OPENAI_ENDPOINT=your_endpoint_here


# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # Get the API key from environment variable
    api_version="2024-05-01-preview",  # Specify the API version
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  # Get the endpoint from environment variable
)

# Set up the Streamlit app
st.title("Azure OpenAI Test Engineer Assistant")  # Set the title of the app

# Model selection
available_models = ["gpt-4o-mini"]  # List of available models, add or remove as needed
selected_model = st.sidebar.selectbox("Select Model", available_models)  # Create a dropdown to select the model

# Initialize session state
if 'assistant' not in st.session_state or st.session_state.get('model') != selected_model:
    try:
        # Create the assistant with instructions and selected model
        st.session_state.assistant = client.beta.assistants.create(
            instructions="You are an expert test engineer in software testing.",
            model=selected_model,
            tools=[{"type": "code_interpreter"}]  # Add a code interpreter tool
        )
        st.session_state.model = selected_model  # Store the selected model in session state
    except Exception as e:
        st.error(f"Error creating assistant: {str(e)}")  # Display error if assistant creation fails
        st.stop()  # Stop the app if assistant creation fails

if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create()  # Create a new conversation thread

if 'messages' not in st.session_state:
    st.session_state.messages = []  # Initialize an empty list to store chat messages

if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # Display message with appropriate role (user or assistant)
        st.markdown(message["content"])  # Display the message content as markdown

# Chat input
if prompt := st.chat_input("What would you like to ask the test engineer?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to the conversation thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,  # ID of the conversation thread
        role="user",  # Specify the message is from the user
        content=prompt  # The user's message
    )

    # Run the assistant
    with st.spinner("Thinking..."):  # Display a spinner while the assistant is thinking
        try:
            # Create a new assistant run
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread.id,  # ID of the conversation thread
                assistant_id=st.session_state.assistant.id  # ID of the assistant
            )

            # Wait for the run to complete
            while run.status in ['queued', 'in_progress', 'cancelling']:
                time.sleep(1)  # Wait for 1 second before checking status again
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread.id,
                    run_id=run.id
                )

            if run.status == 'completed':
                # Retrieve the assistant's response
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread.id
                )
                
                # Find and display the latest assistant message
                for message in messages:
                    if message.role == "assistant":
                        for content in message.content:
                            if content.type == 'text':
                                assistant_response = content.text.value
                                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                                with st.chat_message("assistant"):
                                    st.markdown(assistant_response)
                        break  # Only display the latest assistant message
            else:
                st.error(f"Run failed with status: {run.status}")  # Display error if run failed
        except Exception as e:
            st.error(f"Error during assistant run: {str(e)}")  # Display error if exception occurred

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.title("About")
    st.sidebar.info("This is a Streamlit chat application that uses Azure OpenAI to simulate a conversation with an expert test engineer.")
    st.sidebar.info(f"Currently using model: {selected_model}")  # Display the selected model in the sidebar
