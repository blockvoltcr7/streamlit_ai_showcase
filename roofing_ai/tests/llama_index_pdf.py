# Standard library imports
import os
import re
from pathlib import Path

# Third-party imports
import pdfplumber
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Initialize OpenAI and Pinecone
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # API key for OpenAI
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # API key for Pinecone
INDEX_NAME = "n8n"  # Name of the Pinecone index

# Initialize Pinecone with the provided API key and environment
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# Name of your Pinecone index
INDEX_NAME = "n8n"
pinecone_index = pinecone_client.Index(INDEX_NAME)

# Initialize VectorStore and embedding model
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
embedding_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)


def clean_text(text: str) -> str:
    """Cleans text by removing special characters and normalizing spaces.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # Remove non-ASCII characters
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace
    text = re.sub(r"(?<=[a-zA-Z])-\s+(?=[a-zA-Z])", "", text)  # Fix hyphenated words
    return text.strip()


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts and cleans text from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted and cleaned text.
    """
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )
    return clean_text(text)  # Clean the extracted text


def chunk_text(text: str, max_tokens: int = 500) -> list:
    """Chunk text into smaller segments, preserving sentence boundaries.

    Args:
        text (str): The text to chunk.
        max_tokens (int): The maximum number of tokens per chunk.

    Returns:
        list: A list of text chunks.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)  # Split by sentence
    chunks, current_chunk = [], []  # Initialize chunks and current chunk
    current_length = 0  # Track the current length of the chunk

    for sentence in sentences:
        sentence_length = len(sentence.split())  # Calculate the length of the sentence
        if (
            current_length + sentence_length > max_tokens
        ):  # Check if adding the sentence exceeds max tokens
            chunks.append(" ".join(current_chunk))  # Add the current chunk to the list
            current_chunk, current_length = [], 0  # Reset current chunk and length
        current_chunk.append(sentence)  # Add the sentence to the current chunk
        current_length += sentence_length  # Update the current length

    if current_chunk:  # Add any remaining sentences as a chunk
        chunks.append(" ".join(current_chunk))

    return chunks  # Return the list of chunks


def ingest_pdf_to_pinecone(file_path: str, metadata: dict):
    """Ingest a PDF document into Pinecone."""
    # Step 1: Extract text
    raw_text = extract_text_from_pdf(file_path)
    if not raw_text:
        raise ValueError(f"No extractable text found in {file_path}")

    # Step 2: Chunk text
    chunks = chunk_text(raw_text)
    chunks = [chunk for chunk in chunks if chunk.strip()]  # Remove empty chunks

    print(f"\nProcessing document: {metadata['title']}")
    print(f"Total chunks to process: {len(chunks)}")

    # Step 3: Embed and upload chunks
    for i, chunk in enumerate(tqdm(chunks, desc="Uploading chunks")):
        if not chunk.strip():  # Skip empty chunks
            continue

        # Prepare metadata for each chunk
        chunk_metadata = metadata.copy()
        chunk_metadata.update(
            {
                "chunk_id": i,
                "chunk_total": len(chunks),
                "text": chunk,  # Add the text content to metadata - this is crucial!
                "is_chunk": True,
            }
        )

        # Generate embedding for the chunk
        embedding = embedding_model.get_text_embedding(chunk)

        # Create a unique ID for this chunk
        chunk_id = f"{metadata['title']}_chunk_{i}"

        # Upsert the chunk into Pinecone
        try:
            pinecone_index.upsert(vectors=[(chunk_id, embedding, chunk_metadata)])
        except Exception as e:
            print(f"Error upserting chunk {i}: {str(e)}")
            continue

    print(f"Successfully added {len(chunks)} chunks to Pinecone index '{INDEX_NAME}'")


if __name__ == "__main__":
    # Path to the PDF file
    file_path = "/Users/samisabir-idrissi/code/python/streamlit_ai_showcase/roofing_ai/tests/files/common-questions-roofing.pdf"

    # Metadata for the document
    metadata = {
        "title": "Common Roofing Questions",
        "category": "roofing",
        "description": "A comprehensive guide answering common questions about roofing.",
        "keywords": ["roofing", "maintenance", "repair", "installation"],
        "author": "Roofing Experts",
        "date_last_updated": "2024-12-09",
        "source": "Roofing Documentation",
        "language": "en",
        "version": "1.0",
    }

    try:
        ingest_pdf_to_pinecone(file_path, metadata)  # Ingest the PDF document
    except Exception as e:
        print(f"Error during ingestion: {str(e)}")  # Handle any errors during ingestion
