import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

#check if storage already exists
PERSIST_DIR = "./storage"


# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the data directory
data_dir = os.path.join(os.path.dirname(current_dir), "data")

if not os.path.exists(PERSIST_DIR):
    # Load data using SimpleDirectoryReader
    documents = SimpleDirectoryReader(input_dir=data_dir).load_data()
    # Create a VectorStoreIndex from the documents
    index = VectorStoreIndex.from_documents(documents)
    # Save the index to disk
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # Load the index from disk
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    
query_engine = index.as_query_engine()
response = query_engine.query("Logic is great for planning, but weak for motivation. what does this mean?")
print(response)
