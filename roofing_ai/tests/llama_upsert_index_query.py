import os

from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Get API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise ValueError("Missing required API keys in environment variables")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("n8n")

# Initialize OpenAI Embedding model and set it globally
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.embed_model = embed_model

# Initialize the PineconeVectorStore with the Pinecone index
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Create a StorageContext with the PineconeVectorStore
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load your documents
documents = SimpleDirectoryReader(
    "/Users/samisabir-idrissi/code/python/streamlit_ai_showcase/roofing_ai/tests/files/"
).load_data()

print(f"Loaded {len(documents)} documents")

# Create index with storage context
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Query the index
query_engine = index.as_query_engine()
response = query_engine.query("Do you offer warranties?")
print("\nQuery Response:")
print(response)
