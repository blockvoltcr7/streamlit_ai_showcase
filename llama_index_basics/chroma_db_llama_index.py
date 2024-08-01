# Description: This Code is used to create a ChromaDB vectorindex and upload the documents to the index.
# After that, it queries the index with LlamaIndex and returns the response.

# Install the required packages
# pipenv install chromadb
# pipenv install llama_index.vector_stores.chroma
# pip install llama-index-llms-gemini

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext 
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv
import os

load_dotenv()   
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

# set maximum context window size
context_window = 4096
# set number of output tokens - this is done to limit the output size
num_output = 500
"""
Settings.llm = OpenAI(temperature=0.5,
    model="gpt-3.5-turbo",
    max_tokens=num_output,
    context_window=context_window)
"""
Settings.llm = Gemini(
    temperature=0.5,
    model="models/gemini-1.5-flash-001",
    max_tokens=num_output,
    context_window=context_window)


documents = SimpleDirectoryReader("./data").load_data()

# print the number of documents
print(f"Number of documents: {len(documents)}")

# initialize client, setting path to save data
db = chromadb.PersistentClient(path="./chroma_db")

# create collection
chroma_collection = db.get_or_create_collection("quickstart")

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# create your index
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

# create a query engine and query
query_engine = index.as_query_engine()
response = query_engine.query("What The Potential Benefits of Social Media Use Among Children and Adolescents?")
print(response)