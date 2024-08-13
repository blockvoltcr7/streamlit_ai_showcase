import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv  # For loading environment variables from .env file
load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2024-05-01-preview"
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

print("client api key is: ", api_key)
print("endpoint is : ", azure_endpoint)
print("Creating assistant...")

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

# Create an assistant
assistant = client.beta.assistants.create(
    name="Data Visualization",
    instructions=f"You are a helpful AI assistant who makes interesting visualizations based on data." 
    f"You have access to a sandboxed environment for writing and testing code."
    f"When you are asked to create a visualization you should follow these steps:"
    f"1. Write the code."
    f"2. Anytime you write new code display a preview of the code to show your work."
    f"3. Run the code to confirm that it runs."
    f"4. If the code is successful display the visualization."
    f"5. If the code is unsuccessful display the error message and try to revise the code and rerun going through the steps from above again.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o-mini" #You must replace this value with the deployment name for your model.
)

print(assistant.model_dump_json(indent=2))

# Create a thread
thread = client.beta.threads.create()
print(thread)

# Add a user question to the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Create a visualization of a sinewave"
)

thread_messages = client.beta.threads.messages.list(thread.id)
print(thread_messages.model_dump_json(indent=2))