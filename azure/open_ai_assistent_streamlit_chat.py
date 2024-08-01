import os
import time
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key= os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

# Streamlit app
st.title("Azure OpenAI Test Engineer Assistant")

# Model selection
available_models = ["gpt-4o"]  # Add or remove models as needed
selected_model = st.sidebar.selectbox("Select Model", available_models)

# Initialize session state
if 'assistant' not in st.session_state or st.session_state.get('model') != selected_model:
    try:
        st.session_state.assistant = client.beta.assistants.create(
            instructions="You are an expert test engineer in software testing.",
            model=selected_model,
            tools=[{"type": "code_interpreter"}]
        )
        st.session_state.model = selected_model
    except Exception as e:
        st.error(f"Error creating assistant: {str(e)}")
        st.stop()

if 'thread' not in st.session_state:
    st.session_state.thread = client.beta.threads.create()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to ask the test engineer?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=prompt
    )

    # Run the assistant
    with st.spinner("Thinking..."):
        try:
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread.id,
                assistant_id=st.session_state.assistant.id
            )

            # Wait for the run to complete
            while run.status in ['queued', 'in_progress', 'cancelling']:
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread.id,
                    run_id=run.id
                )

            if run.status == 'completed':
                # Retrieve and display the assistant's response
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread.id
                )
                
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
                st.error(f"Run failed with status: {run.status}")
        except Exception as e:
            st.error(f"Error during assistant run: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.title("About")
    st.sidebar.info("This is a Streamlit chat application that uses Azure OpenAI to simulate a conversation with an expert test engineer.")
    st.sidebar.info(f"Currently using model: {selected_model}")