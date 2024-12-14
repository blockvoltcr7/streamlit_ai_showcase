import os
import re
from datetime import datetime

import langchain
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import (
    OnlinePDFLoader,
    PyPDFLoader,
    UnstructuredPDFLoader,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms.openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain_core.documents import Document
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Initialize OpenAI and Pinecone
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # API key for OpenAI
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # API key for Pinecone
INDEX_NAME = "n8n"  # Name of the Pinecone index


def setup_pinecone(index_name):
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Verify index exists
    if index_name not in pc.list_indexes().names():
        raise ValueError(f"Index {index_name} does not exist")

    # Set up OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    return embeddings


def preprocess_text(text: str) -> str:
    """
    Clean and preprocess extracted text.

    Args:
        text (str): Raw text to process

    Returns:
        str: Cleaned and preprocessed text
    """
    # Replace common artifacts
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = text.replace("\xa0", " ")  # Replace non-breaking spaces
    text = text.replace("\u200b", "")  # Remove zero-width spaces

    # Fix spacing issues
    text = re.sub(r"\s+", " ", text)

    # Fix common PDF artifacts
    text = re.sub(r"(?<=[a-z])-\s+(?=[a-z])", "", text)  # Fix hyphenation
    text = re.sub(r"([a-z])- ([a-z])", r"\1\2", text)  # Fix broken words
    text = re.sub(r"([a-z])_([a-z])", r"\1\2", text)  # Fix underscores between words

    # Clean up punctuation
    text = re.sub(r"\s+([.,!?])", r"\1", text)

    return text.strip()


def create_document_search(texts, embeddings, index_name):
    """
    Create document search with metadata in Pinecone vector store.

    Args:
        texts: List of Document objects
        embeddings: OpenAI embeddings
        index_name: Name of Pinecone index
    """
    # Create documents with metadata
    documents = []
    for i, text in enumerate(texts):
        # Extract existing metadata from the text object if it exists
        existing_metadata = getattr(text, "metadata", {})

        metadata = {
            **existing_metadata,
            "source": text.metadata.get("source", "roofing_pdf"),
            "page": text.metadata.get("page", 0),
            "chunk_id": i,
            "title": "Roof Inspections",
            "category": "services",
            "subcategory": "inspections",
            "tags": ["roofing", "inspection", "maintenance", "roof care"],
            "keywords": [
                "roof inspections",
                "leak prevention",
                "roof maintenance",
                "professional roof inspections",
                "inspection checklist",
                "roof inspection cost",
            ],
            "description": "A comprehensive guide to roof inspections, including benefits, steps, and pricing.",
            "audience": ["residential homeowners", "commercial property managers"],
            "purpose": "Educate users on the importance of regular roof inspections",
            "question_intent": [
                "What is included in a roof inspection?",
                "How much does a roof inspection cost?",
                "How often should I inspect my roof?",
                "Why are roof inspections important?",
            ],
            "document_type": "markdown",
            "date_created": "2023-11-15",
            "date_last_updated": "2024-12-01",
            "author": "Roofing Team",
            "location": ["USA", "California", "Los Angeles"],
            "related_docs": ["repairs.md", "pricing.md"],
            "related_titles": ["Roof Repairs", "Roof Pricing Overview"],
            "content_snippet": "Roof inspections are critical for identifying leaks and maintaining roof integrity.",
        }

        # Create new Document with cleaned text and metadata
        doc = Document(
            page_content=preprocess_text(text.page_content), metadata=metadata
        )
        documents.append(doc)

    # Create vector store with documents and metadata
    return LangchainPinecone.from_documents(
        documents, embeddings, index_name=index_name, namespace="default"
    )


def process_pdf_file(pdf_path):
    # Load PDF file
    loader = PyPDFLoader(pdf_path)
    file_content = loader.load()

    # Clean the text content and enhance metadata
    for doc in file_content:
        doc.page_content = preprocess_text(doc.page_content)
        # Add or update metadata
        doc.metadata.update(
            {
                "source": pdf_path,
                "file_type": "pdf",
                "timestamp": datetime.now().isoformat(),
            }
        )

    # Split the content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
        length_function=len,
    )

    chunks = text_splitter.split_documents(file_content)
    print(f"Split {len(file_content)} documents into {len(chunks)} chunks")
    return chunks


def query_document(docsearch, query_text, metadata_filter=None):
    """
    Query documents with optional metadata filtering

    Args:
        docsearch: Pinecone vector store instance
        query_text: Query string
        metadata_filter: Dictionary of metadata filters
    """
    # Set up the LLM model
    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

    # Perform similarity search with metadata filter
    docs = docsearch.similarity_search(query_text, filter=metadata_filter)

    # Run the QA chain
    chain = load_qa_chain(llm, chain_type="stuff")
    return chain.run(input_documents=docs, question=query_text)


def main():
    # Example usage
    index_name = "n8n"

    # Setup Pinecone and create document search
    embeddings = setup_pinecone(index_name)

    # Process PDF file - fix the path to be relative to the tests directory
    pdf_docs = process_pdf_file("files/common-questions-roofing.pdf")
    pdf_docsearch = create_document_search(pdf_docs, embeddings, index_name)

    # Query with metadata filter
    metadata_filter = {
        "document_type": "roofing_guide",
        "source": "files/common-questions-roofing.pdf",
    }

    result = query_document(
        pdf_docsearch,
        "How much does a roof replacement cost?",
        metadata_filter=metadata_filter,
    )
    print(result)


if __name__ == "__main__":
    main()
