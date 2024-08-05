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
            "content": "Explain the importance of this quote 'You must be strong. Determination, perseverance, and a strong will to overcome any obstacle. These are the pillars upon which your mental fortress is built. When the storms of life batter against your walls, remember that each challenge is an opportunity to prove your resilience. Embrace the struggle, for it is in the crucible of hardship that true strength is forged. Keep your eyes fixed on your goals, and let no setback deter you. Every step forward, no matter how small, brings you closer to the warrior within. Stand tall, remain unwavering, and let your inner fire burn brightly. This is your journey, and you are the hero of your own story.'",
        }
    ],
    model=LLAMA3_70B,
)

print(chat_completion.choices[0].message.content)