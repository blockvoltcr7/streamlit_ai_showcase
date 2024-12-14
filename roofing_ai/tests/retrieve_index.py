import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone

# Get the path to the .env file in the root directory
root_dir = Path(__file__).parent.parent  # Go up one level to reach project root
env_path = root_dir / ".env"

print("Checking if .env exists:", env_path.exists())
print("env_path:", env_path)

# Load environment variables from the specific .env file
if not env_path.exists():
    raise FileNotFoundError(f"Could not find .env file at {env_path}")

load_dotenv(dotenv_path=env_path)

# Set the Pinecone API key
api_key = os.getenv("PINECONE_API_KEY")
print("api_key is", api_key)
if not api_key:
    raise ValueError("PINECONE_API_KEY not found in .env file")

print("API Key found:", bool(api_key))

pc = Pinecone(api_key)
index = pc.Index("n8n")
print(index)

# Retrieve and print all active indexes
active_indexes = pc.list_indexes()
print("Active Pinecone Indexes:")
for index in active_indexes:
    print(index)
