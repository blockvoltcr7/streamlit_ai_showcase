import os
from dotenv import load_dotenv
import openai
from openai import OpenAI  # New import

# Load environment variables
load_dotenv()

# Set up your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

# Initialize the OpenAI client
client = OpenAI()  # New client initialization

# Define the payload using the new client method
response = client.chat.completions.create(  # Updated API call
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a LLM?"}
    ]
)

# Check for errors (this may not be necessary with the new client)
# response.raise_for_status()  # Remove this line if using the new client

# Print the response
response_text = response.choices[0].message.content  # Access content directly

# Print the response text
print(response_text)  # This will print only the message content