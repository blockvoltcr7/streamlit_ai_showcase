from openai import OpenAI
import os

# Get the API key from the environment variable
ngc_api_key = os.getenv('NGC_API_KEY')

if ngc_api_key is None:
    raise ValueError("API key not found. Please set the NGC_API_KEY environment variable.")

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = ngc_api_key
)

completion = client.chat.completions.create(
  model="mistralai/mistral-7b-instruct-v0.2",
  messages=[{"role":"user","content":"write me a poem about marvel super hero ironman when i dies from saving the world in 5 verses"}],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")