import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)

LLAMA3_405b = "llama-3.1-405b-reasoning";
LLAMA3_8B_8192 = "llama3-8b-8192";
LLAMA3_70B = "llama3-70b-8192";
# LLAMA3_8B_8192 = "llama-3.1-405b-reasoning";
# LLAMA3_8B_8192 = "llama-3.1-405b-reasoning";
# LLAMA3_8B_8192 = "llama-3.1-405b-reasoning";
# LLAMA3_8B_8192 = "llama-3.1-405b-reasoning";

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model=LLAMA3_70B,
)

print(chat_completion.choices[0].message.content)