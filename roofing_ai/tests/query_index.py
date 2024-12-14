"""
This script reads from a Pinecone vector store index and queries it using LlamaIndex.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import (
    ResponseMode,
    get_response_synthesizer,
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

# Load environment variables
load_dotenv()


def main():
    """Main function to demonstrate querying the Pinecone index."""
    # Get API keys
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not pinecone_api_key or not openai_api_key:
        raise ValueError("Missing required API keys in .env file")

    os.environ["OPENAI_API_KEY"] = openai_api_key

    # Initialize Pinecone and get the index
    pc = Pinecone(pinecone_api_key)
    pinecone_index = pc.Index("n8n")  # Replace "n8n" with your index name

    # Create a vector store from the Pinecone index
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
    )

    # Set the OpenAI model and temperature
    Settings.llm = OpenAI(temperature=0.6, model="gpt-4o")

    # Configure retriever with similarity search
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=3,  # Adjust this value based on your needs
    )

    # Set up response synthesizer for better answer generation
    response_synthesizer = get_response_synthesizer(response_mode=ResponseMode.COMPACT)

    # Create query engine with post-processing for better results
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[
            SimilarityPostprocessor(
                similarity_cutoff=0.7,
                filter_empty=True,
                filter_duplicates=True,
            )
        ],
        response_synthesizer=response_synthesizer,
    )

    # Query the index
    question = "what is the Patient ID"
    print(f"\nQuestion: {question}")
    response = query_engine.query(question)
    print(f"\nAnswer: {response}")


if __name__ == "__main__":
    main()
