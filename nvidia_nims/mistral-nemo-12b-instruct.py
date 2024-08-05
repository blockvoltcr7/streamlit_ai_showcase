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
  api_key = api_key
)

completion = client.chat.completions.create(
  model="nv-mistralai/mistral-nemo-12b-instruct",
  messages=[{"role":"user","content":"write a code for streamlit for a login page"}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")

