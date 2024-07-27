import os
from together import Together

together_api_key = os.getenv('TOGETHER_API_KEY')

client = Together(api_key=together_api_key)

stream = client.chat.completions.create(
  model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
  messages=[{"role": "user", "content": "What are some fun things to do in New York?"}],
  stream=True,
)

for chunk in stream:
  print(chunk.choices[0].delta.content or "", end="", flush=True)