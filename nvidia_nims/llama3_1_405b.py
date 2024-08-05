from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("NGC_API_KEY")
if api_key is None:
    raise ValueError("NGC_API_KEY environment variable is not set")


client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv("NGC_API_KEY")
)

completion = client.chat.completions.create(
  model="meta/llama-3.1-405b-instruct",
  messages=[{"role":"user","content":"act as a dynasty warrior. You are Lu Bu preparing to conquor a dynasty. give your victory speech"}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")

