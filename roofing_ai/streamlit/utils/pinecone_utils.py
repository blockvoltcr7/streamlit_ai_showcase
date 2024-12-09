import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """Generate embeddings using OpenAI."""
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def init_pinecone():
    load_dotenv()
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    return Pinecone(api_key=api_key)


def get_active_indexes():
    """Get a list of active Pinecone index names."""
    pc = init_pinecone()
    indexes = pc.list_indexes()
    # Convert to list of strings (index names)
    return [index.name for index in indexes]


def get_index_stats(index_name):
    """Get statistics for a Pinecone index and convert to a dictionary."""
    pc = init_pinecone()
    index = pc.Index(index_name)
    stats = index.describe_index_stats()

    # Convert Pinecone response to dictionary
    return {
        "total_vector_count": stats.total_vector_count,
        "dimension": stats.dimension,
        "index_fullness": stats.index_fullness,
        "namespaces": {
            ns: {"vector_count": ns_stats.vector_count}
            for ns, ns_stats in stats.namespaces.items()
        },
    }


def upload_document(index_name, content, metadata, file_name):
    pc = init_pinecone()
    index = pc.Index(index_name)

    # Generate embedding (implement with your preferred embedding method)
    embedding = generate_embedding(content)

    # Create unique document ID
    doc_id = f"{file_name}_{metadata['date_last_updated']}"

    # Upload to Pinecone
    index.upsert([(doc_id, embedding, metadata)])


def format_stats(stats):
    """Format index statistics for display."""
    if not stats:
        return {}

    # Stats should already be a dictionary from get_index_stats
    formatted = {
        "Total Vectors": stats.get("total_vector_count", 0),
        "Dimension": stats.get("dimension", 0),
        "Index Fullness": f"{stats.get('index_fullness', 0):.2%}",
        "Namespaces": {},
    }

    # Format namespace information
    namespaces = stats.get("namespaces", {})
    for ns_name, ns_data in namespaces.items():
        formatted["Namespaces"][ns_name] = {
            "Vector Count": ns_data.get("vector_count", 0)
        }

    return formatted
