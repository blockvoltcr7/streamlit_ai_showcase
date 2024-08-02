"""
This script reads documents from the data folder, loads them into a VectorStoreIndex,
and then queries the index with a question to return a response.
"""
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
os.environ["OPENAI_API_KEY"] = api_key

# Set the OpenAI model and temperature
Settings.llm = OpenAI(temperature=0.2, model="gpt-4o-mini")

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the data directory
data_dir = os.path.join(os.path.dirname(current_dir), "data")
# Load data using SimpleDirectoryReader
documents = SimpleDirectoryReader(input_dir=data_dir).load_data()


index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Logic is great for planning, but weak for motivation. what does this mean?")

print(response)