# Home.py
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from utils.pinecone_utils import init_pinecone

# Load environment variables
load_dotenv()


def main():
    st.set_page_config(
        page_title="Document Vector Store Manager", page_icon="📚", layout="wide"
    )

    st.title("Document Vector Store Manager")
    st.write(
        """
    Welcome to the Document Vector Store Manager. This application allows you to:
    
    - Upload documents with metadata to Pinecone
    - View and manage existing indexes
    - Search and retrieve documents
    """
    )

    # Initialize Pinecone connection
    try:
        init_pinecone()
        st.success("Successfully connected to Pinecone")
    except Exception as e:
        st.error(f"Failed to connect to Pinecone: {str(e)}")


if __name__ == "__main__":
    main()
