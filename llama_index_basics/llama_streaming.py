import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
os.environ["OPENAI_API_KEY"] = api_key

# Set the OpenAI model
Settings.llm = OpenAI(model="gpt-4o-mini")


# Example of streaming a conversation
def stream_conversation():
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Tell me a joke. write 1000 words"),
    ]

    # Start streaming the conversation
    stream_response = Settings.llm.stream_chat(messages)

    for message in stream_response:
        print(message.delta, end="")


if __name__ == "__main__":
    stream_conversation()
