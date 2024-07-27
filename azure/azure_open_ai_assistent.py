import os
import time
import json
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AzureOpenAI(
    api_key= os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

assistant = client.beta.assistants.create(
    instructions="you are an expert test engineer in software testing.",
    model="gpt-4o", 
    tools=[{"type":"code_interpreter"}]
    )

# Create a thread
thread = client.beta.threads.create()

# Add a user question to the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="create a python pytest script that calculates the sum of two numbers"
)

# Run the thread
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)

# Looping until the run completes or fails
while run.status in ['queued', 'in_progress', 'cancelling']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

if run.status == 'completed':
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    # Extract and print only the value from the response
    for message in messages:
        if message.role == "assistant":
            for content in message.content:
                if content.type == 'text':
                    print(content.text.value)
elif run.status == 'requires_action':
    # The assistant requires calling some functions
    # and submit the tool outputs back to the run
    pass
else:
    print(f"Run failed with status: {run.status}")

