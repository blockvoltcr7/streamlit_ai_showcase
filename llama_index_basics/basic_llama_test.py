import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

# Set up OpenAI API key
API_KEY = os.getenv("OPENAI_API_KEY")

response = OpenAI(model = "gpt-3.5-turbo", api_key = API_KEY).complete(prompt="Create a Python function that calculates the sum of two numbers", max_tokens=100)

print(response)