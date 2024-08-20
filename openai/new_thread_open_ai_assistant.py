import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Function to create a new thread
def create_new_thread():
    thread = client.beta.threads.create()
    return thread

# Function to add a message to the thread
def add_message_to_thread(thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    return message

# Function to create and run a new run on the thread
def create_and_run_thread(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run

# Function to retrieve the latest message from a thread
def get_latest_message(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0] if messages.data else None

# Main execution
if __name__ == "__main__":
    # Assistant ID
    assistant_id = "asst_zxXTrOWVPsT7fapLS82c7J4X"
    
    # Create a new thread
    thread = create_new_thread()
    print(f"Created new thread with ID: {thread.id}")
    
    # Add a message to the thread
    user_message = "Hello, I'd like to ask about the latest updates to the API."
    add_message_to_thread(thread.id, user_message)
    print(f"Added message to thread: {user_message}")
    
    # Create and start a run
    run = create_and_run_thread(thread.id, assistant_id)
    print(f"Started run with ID: {run.id}")
    
    # Wait for the run to complete (you might want to implement a proper polling mechanism here)
    import time
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == 'completed':
            break
        time.sleep(1)
    
    # Retrieve and print the latest message (which should be the assistant's response)
    latest_message = get_latest_message(thread.id)
    if latest_message:
        print(f"Latest message: {latest_message.content[0].text.value}")
    else:
        print("No messages found in the thread.")