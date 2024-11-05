"""
Initialize and run a question-answering system using LlamaIndex and Gemini.

This script sets up a document retrieval and question-answering pipeline using
LlamaIndex and the Gemini language model. It loads documents, creates a vector
store index, and uses a retriever to find relevant documents for a given query.

Parameters:
    None

Returns:
    None

Raises:
    ValueError: If the GEMINI_API_KEY is not found in environment variables.
    Exception: For any other errors that occur during execution.

The script performs the following steps:
1. Loads environment variables and sets up the Gemini API key.
2. Initializes the Gemini language model.
3. Loads documents from a specified directory.
4. Creates a vector store index from the documents.
5. Sets up a retriever to find similar documents.
6. Creates a query engine using the retriever.
7. Generates a response to a predefined question.
8. Prints the generated response.

Note: This script requires the necessary environment variables to be set,
including the GEMINI_API_KEY.
"""
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
    response = query_engine.query("what are the benefits of testing ai systems?")


    # Print the generated text
    print("Generated text:")
    print(response)

except Exception as e:
    print(f"An error occurred: {str(e)}")
