from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the Google API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

os.environ["GOOGLE_API_KEY"] = api_key

# Initialize the Gemini model
llm = Gemini(model="models/gemini-1.5-flash-001")

try:
    # Load documents from a directory
    documents = SimpleDirectoryReader('./data/istqb').load_data()
    
    # Create a vector store index
    index = VectorStoreIndex.from_documents(documents)
    
    # the retriever is setup to retrieve the most similar document to the query
    retriever = VectorIndexRetriever(index=index, similarity_top_k=10,)

    query_engine = RetrieverQueryEngine(retriever=retriever)
    
    # Generate a response
    response = query_engine.query("What are the Test Levels for AI-Based Systems")

    
    # Print the generated text
    print("Generated text:")
    print(response)
    
except Exception as e:
    print(f"An error occurred: {str(e)}")