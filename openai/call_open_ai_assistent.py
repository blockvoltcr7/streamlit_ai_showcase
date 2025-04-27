import os

from dotenv import load_dotenv

import openai
from openai import OpenAI  # New import

# Load environment variables
load_dotenv()

# Set up your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the Ofrom openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": "Write a one-sentence bedtime story about a unicorn."
        }
    ]
)

print(completion.choices[0].message.content)