import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from pinecone import Pinecone
from PyPDF2 import PdfReader
from tqdm import tqdm

from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI and Pinecone
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Name of your Pinecone index
INDEX_NAME = "n8n"
pinecone_index = pinecone_client.Index(INDEX_NAME)


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validates that all required metadata fields are present.

    Args:
        metadata (Dict[str, Any]): Metadata to validate

    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    required_fields = [
        "title",
        "category",
        "description",
        "keywords",
        "author",
        "date_last_updated",
    ]

    missing_fields = [field for field in required_fields if not metadata.get(field)]

    if missing_fields:
        raise ValueError(
            f"Missing required metadata fields: {', '.join(missing_fields)}"
        )

    return True


def create_chunk_metadata(
    base_metadata: Dict[str, Any], chunk_id: int, total_chunks: int, chunk_content: str
) -> Dict[str, Any]:
    """
    Creates metadata for a chunk, inheriting from base document metadata.

    Args:
        base_metadata (Dict[str, Any]): Original document metadata
        chunk_id (int): Index of the chunk
        total_chunks (int): Total number of chunks
        chunk_content (str): Content of the chunk

    Returns:
        Dict[str, Any]: Complete chunk metadata
    """
    # Create a deep copy of the base metadata
    chunk_metadata = base_metadata.copy()

    # Add chunk-specific metadata
    chunk_metadata.update(
        {
            "chunk_id": chunk_id,
            "chunk_total": total_chunks,
            "content": chunk_content,
            "is_chunk": True,
            "parent_document": base_metadata["title"],
            "chunk_position": f"{chunk_id + 1} of {total_chunks}",
            "document_type": "document_chunk",
        }
    )

    return chunk_metadata


def read_pdf(file_path: str) -> str:
    """Reads and extracts text from a PDF file."""
    reader = PdfReader(file_path)
    text = " ".join(page.extract_text() for page in reader.pages)
    return text


def read_file(file_path: str) -> str:
    """Read content from a file based on its extension."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Handle different file types
    if path.suffix.lower() == ".pdf":
        return read_pdf(file_path)
    elif path.suffix.lower() in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    """
    Chunks text into smaller segments of a specified token length.

    Args:
        text (str): The text to chunk
        max_tokens (int): Maximum number of tokens per chunk

    Returns:
        List[str]: List of text chunks
    """
    # Simple word-based chunking
    words = text.split()
    chunks = [
        " ".join(words[i : i + max_tokens]) for i in range(0, len(words), max_tokens)
    ]
    return chunks


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generates an embedding for the given text using OpenAI.

    Args:
        text (str): Text to embed
        model (str): OpenAI embedding model to use

    Returns:
        List[float]: The embedding vector
    """
    response = openai_client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def add_document_to_pinecone(file_path: str, metadata: Dict[str, Any]) -> List[str]:
    """
    Reads, chunks, embeds, and uploads a document to Pinecone with consistent metadata.

    Args:
        file_path (str): Path to the document
        metadata (dict): Base document metadata

    Returns:
        List[str]: List of chunk IDs created
    """
    # Validate base metadata
    validate_metadata(metadata)

    # Read the document
    content = read_file(file_path)

    # Chunk the content
    chunks = chunk_text(content)
    chunk_ids = []

    print(f"\nProcessing document: {metadata['title']}")
    print(f"Total chunks to process: {len(chunks)}")

    # Process each chunk with progress bar
    for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
        # Create chunk-specific metadata
        chunk_metadata = create_chunk_metadata(
            base_metadata=metadata,
            chunk_id=i,
            total_chunks=len(chunks),
            chunk_content=chunk,
        )

        # Create a unique ID for the chunk
        chunk_id = f"{metadata['title']}_{metadata.get('date_last_updated', '')}_{i}"
        chunk_ids.append(chunk_id)

        # Generate the embedding
        embedding = get_embedding(chunk)

        # Add to Pinecone
        pinecone_index.upsert([(chunk_id, embedding, chunk_metadata)])

    print(f"\nSuccessfully added {len(chunks)} chunks to Pinecone index '{INDEX_NAME}'")
    return chunk_ids


def query_pinecone(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Queries the Pinecone index using OpenAI embeddings.

    Args:
        query (str): Query text
        top_k (int): Number of results to return

    Returns:
        Dict[str, Any]: Query results with matches and metadata
    """
    # Generate query embedding
    query_embedding = get_embedding(query)

    # Query the Pinecone index
    results = pinecone_index.query(
        vector=query_embedding, top_k=top_k, include_metadata=True
    )

    return results


if __name__ == "__main__":
    # Use absolute path to the PDF file
    file_path = "/Users/samisabir-idrissi/code/python/streamlit_ai_showcase/roofing_ai/tests/files/common-questions-roofing.pdf"

    # Define document metadata
    metadata = {
        "title": "Common Roofing Questions",
        "category": "roofing",
        "description": "A comprehensive guide answering common questions about roofing",
        "keywords": ["roofing", "maintenance", "repair", "installation"],
        "author": "Roofing Experts",
        "date_last_updated": "2024-03-19",
        "source": "Roofing Documentation",
        "language": "en",
        "version": "1.0",
    }

    try:
        # Add the document to Pinecone
        chunk_ids = add_document_to_pinecone(file_path, metadata)
        print(f"\nDocument processing complete:")
        print(f"- Total chunks created: {len(chunk_ids)}")
        print(f"- First chunk ID: {chunk_ids[0]}")
        print(f"- Last chunk ID: {chunk_ids[-1]}")

        # Test query
        test_query = "What are common roofing problems?"
        print(f"\nTesting search with query: '{test_query}'")
        results = query_pinecone(test_query)

        print("\nSearch Results:")
        for i, match in enumerate(results.matches, 1):
            print(f"\nResult #{i}:")
            print(f"Score: {match.score:.4f}")
            print(f"Chunk: {match.metadata['chunk_position']}")
            print(f"Content Preview: {match.metadata['content'][:200]}...")

    except Exception as e:
        print(f"\nError processing document: {str(e)}")
        raise
