"""
This script reads documents from the data folder, loads them into a VectorStoreIndex,
and then queries the index with a question to return a response.
"""

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from dotenv import load_dotenv
import os

def main():
    """Main function to demonstrate reading documents, loading them into a VectorStoreIndex,
    and querying the index with a question to return a response.
    """
    # Load the OpenAI API Key into the environment variable named OPENAI_API_KEY
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    os.environ["OPENAI_API_KEY"] = api_key

    # Set the OpenAI model and temperature
    Settings.llm = OpenAI(temperature=0.2, model="gpt-4o-mini")

    # Load data using SimpleDirectoryReader
    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)

    # Print the number of documents
    print(f"Number of documents: {len(documents)}")
    print(f"Display a document in the Index: {documents[25].text}")
    print("---------------------------------------------")

    # Configure retriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=10)

    # The response synthesizer is used to turn the response data into a human-readable format
    response_synthesizer = get_response_synthesizer(response_mode=ResponseMode.COMPACT)

    # The query engine is used to query the index and generate a response
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[
            SimilarityPostprocessor(
                similarity_cutoff=0.7,  # filter nodes with similarity score below the cutoff
                filter_empty=True,  # filter empty nodes
                filter_duplicates=True,  # filter duplicate nodes
                filter_similar=True,  # filter similar nodes
            )
        ],
        response_synthesizer=response_synthesizer,
    )

    # Query the index and print the response
    question = "What are the Potential Benefits of Social Media Use Among Children and Adolescents?"
    response = query_engine.query(question)
    print(response)

if __name__ == "__main__":
    main()
