import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()


def init_pinecone():

    # Get Pinecone API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in .env file")

    return Pinecone(api_key=api_key)


def delete_all_vectors(index_name: str):
    """Delete all vectors from the specified index."""
    try:
        pc = init_pinecone()
        index = pc.Index(index_name)

        # Delete all vectors
        index.delete(delete_all=True)
        print(f"All contents of index '{index_name}' have been deleted.")

        # Verify deletion
        stats = index.describe_index_stats()
        print("\nIndex stats after deletion:")
        print(stats)

    except Exception as e:
        print(f"Error deleting vectors: {str(e)}")


def delete_by_namespace(index_name: str, namespace: str):
    """Delete all vectors in a specific namespace."""
    try:
        pc = init_pinecone()
        index = pc.Index(index_name)

        # Delete vectors in namespace
        index.delete(delete_all=True, namespace=namespace)
        print(f"All vectors in namespace '{namespace}' have been deleted.")

        # Verify deletion
        stats = index.describe_index_stats()
        print("\nIndex stats after deletion:")
        print(stats)

    except Exception as e:
        print(f"Error deleting namespace: {str(e)}")


def delete_by_metadata(index_name: str, metadata_filter: dict):
    """Delete vectors matching specific metadata criteria."""
    try:
        pc = init_pinecone()
        index = pc.Index(index_name)

        # Delete vectors matching filter
        index.delete(filter=metadata_filter)
        print(f"Vectors matching filter {metadata_filter} have been deleted.")

        # Verify deletion
        stats = index.describe_index_stats()
        print("\nIndex stats after deletion:")
        print(stats)

    except Exception as e:
        print(f"Error deleting by metadata: {str(e)}")


def delete_by_ids(index_name: str, ids: list):
    """Delete vectors with specific IDs."""
    try:
        pc = init_pinecone()
        index = pc.Index(index_name)

        # Delete specific vectors
        index.delete(ids=ids)
        print(f"Vectors with IDs {ids} have been deleted.")

        # Verify deletion
        stats = index.describe_index_stats()
        print("\nIndex stats after deletion:")
        print(stats)

    except Exception as e:
        print(f"Error deleting by IDs: {str(e)}")


def main():
    INDEX_NAME = "n8n"

    # Print initial stats
    pc = init_pinecone()
    index = pc.Index(INDEX_NAME)
    print("Initial index stats:")
    print(index.describe_index_stats())
    print("\n" + "=" * 50 + "\n")

    # Example usage - uncomment the operation you want to perform

    # 1. Delete all vectors
    # delete_all_vectors(INDEX_NAME)

    # 2. Delete by namespace
    delete_by_namespace(INDEX_NAME, "faq")

    # 3. Delete by metadata filter
    # metadata_filter = {"category": "roofing"}
    # delete_by_metadata(INDEX_NAME, metadata_filter)

    # 4. Delete specific IDs
    # vector_ids = ["doc1", "doc2"]
    # delete_by_ids(INDEX_NAME, vector_ids)


if __name__ == "__main__":
    main()
