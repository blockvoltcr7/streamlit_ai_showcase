import os
import re
from datetime import datetime
from typing import Dict, List

import pinecone
import streamlit as st
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms.openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain_core.documents import Document
from pinecone import Pinecone as PineconeClient

# Load environment variables
load_dotenv()


# Initialize session state
def init_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "document_processed" not in st.session_state:
        st.session_state.document_processed = False
    if "metadata_template" not in st.session_state:
        st.session_state.metadata_template = {
            "source": "",
            "title": "",
            "category": "",
            "subcategory": "",
            "tags": [],
            "keywords": [],
            "description": "",
            "audience": [],
            "purpose": "",
            "document_type": "",
            "author": "",
            "location": [],
            "namespace": "",
        }


def setup_pinecone():
    try:
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        INDEX_NAME = "n8n"

        pc = PineconeClient(api_key=PINECONE_API_KEY)

        if INDEX_NAME not in pc.list_indexes().names():
            st.error(f"Index {INDEX_NAME} does not exist in Pinecone")
            return None

        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        return embeddings, INDEX_NAME
    except Exception as e:
        st.error(f"Error setting up Pinecone: {str(e)}")
        return None


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


def process_pdf(pdf_file, metadata: Dict):
    try:
        # Use original filename instead of temp filename
        original_filename = pdf_file.name
        temp_file_path = f"temp_{original_filename}"

        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as f:
            f.write(pdf_file.getvalue())

        # Load and process PDF
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        # Clean and enhance documents
        for doc in documents:
            doc.page_content = preprocess_text(doc.page_content)
            doc.metadata.update(metadata)
            doc.metadata.update(
                {
                    "timestamp": datetime.now().isoformat(),
                    "file_type": "pdf",
                    "source": original_filename,  # Add original filename as source
                }
            )

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=0, length_function=len
        )
        chunks = text_splitter.split_documents(documents)

        # Cleanup temporary file
        os.remove(temp_file_path)

        return chunks
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return None


def create_vector_store(
    documents: List[Document], embeddings, index_name: str, namespace: str = None
):
    try:
        return Pinecone.from_documents(
            documents, embeddings, index_name=index_name, namespace=namespace
        )
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None


def query_vector_store(vector_store, query: str, metadata_filter: Dict = None):
    try:
        llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        docs = vector_store.similarity_search(query, filter=metadata_filter)
        chain = load_qa_chain(llm, chain_type="stuff")
        return chain.run(input_documents=docs, question=query)
    except Exception as e:
        st.error(f"Error querying vector store: {str(e)}")
        return None


def render_metadata_form():
    st.subheader("Document Metadata")
    metadata = {}

    # Add namespace field at the top
    metadata["namespace"] = st.text_input(
        "Namespace",
        st.session_state.metadata_template["namespace"],
        help="Enter a namespace to organize your documents (optional)",
    )

    # Basic metadata fields
    metadata["title"] = st.text_input(
        "Document Title", st.session_state.metadata_template["title"]
    )
    metadata["description"] = st.text_area(
        "Description", st.session_state.metadata_template["description"]
    )
    metadata["author"] = st.text_input(
        "Author", st.session_state.metadata_template["author"]
    )

    # Categories
    metadata["category"] = st.text_input(
        "Category", st.session_state.metadata_template["category"]
    )
    metadata["subcategory"] = st.text_input(
        "Subcategory", st.session_state.metadata_template["subcategory"]
    )

    # Lists (tags, keywords, audience, location)
    metadata["tags"] = st.text_input(
        "Tags (comma-separated)", ",".join(st.session_state.metadata_template["tags"])
    ).split(",")
    metadata["keywords"] = st.text_input(
        "Keywords (comma-separated)",
        ",".join(st.session_state.metadata_template["keywords"]),
    ).split(",")
    metadata["audience"] = st.text_input(
        "Target Audience (comma-separated)",
        ",".join(st.session_state.metadata_template["audience"]),
    ).split(",")
    metadata["location"] = st.text_input(
        "Locations (comma-separated)",
        ",".join(st.session_state.metadata_template["location"]),
    ).split(",")

    # Purpose and document type
    metadata["purpose"] = st.text_area(
        "Document Purpose", st.session_state.metadata_template["purpose"]
    )
    metadata["document_type"] = st.selectbox(
        "Document Type", ["guide", "manual", "report", "article", "other"]
    )

    return metadata


def render_chat_interface(vector_store):
    st.subheader("Chat Interface")

    # Display conversation history
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your document"):
        # Add user message to conversation
        st.session_state.conversation.append({"role": "user", "content": prompt})

        # Get response from vector store
        response = query_vector_store(vector_store, prompt)

        if response:
            # Add assistant response to conversation
            st.session_state.conversation.append(
                {"role": "assistant", "content": response}
            )

            # Force refresh to show new messages
            st.rerun()


def delete_vectors_by_namespace(index, namespace: str):
    try:
        # Add confirmation message based on namespace
        if namespace:
            confirm_msg = f"Deleting all vectors in namespace '{namespace}'"
        else:
            confirm_msg = "Deleting all vectors in default namespace"

        st.info(confirm_msg)

        index.delete(delete_all=True, namespace=namespace)

        success_msg = f"Successfully deleted all vectors from {'default namespace' if not namespace else f'namespace {namespace}'}"
        st.success(success_msg)
        return True
    except Exception as e:
        st.error(f"Error deleting namespace: {str(e)}")
        return False


def delete_vectors_by_metadata(index, metadata_filter: dict):
    try:
        index.delete(filter=metadata_filter)
        st.success(f"Vectors matching filter {metadata_filter} have been deleted.")
        return True
    except Exception as e:
        st.error(f"Error deleting by metadata: {str(e)}")
        return False


def delete_vectors_by_ids(index, ids: list):
    try:
        index.delete(ids=ids)
        st.success(f"Vectors with IDs {ids} have been deleted.")
        return True
    except Exception as e:
        st.error(f"Error deleting by IDs: {str(e)}")
        return False


def render_vector_store_management(pc, index_name: str):
    st.header("Vector Store Management")

    index = pc.Index(index_name)

    # Show current index stats
    with st.expander("Index Statistics"):
        stats = index.describe_index_stats()
        st.json(stats)

    # Namespace deletion section
    st.subheader("Delete by Namespace")

    # Initialize session state for confirmation
    if "show_confirm" not in st.session_state:
        st.session_state.show_confirm = False

    namespace = st.text_input(
        "Enter namespace to delete", help="Leave empty to delete from default namespace"
    )

    # First delete button
    if st.button("Delete Namespace", type="primary"):
        st.session_state.show_confirm = True

    # Show confirmation button if first button was clicked
    if st.session_state.show_confirm:
        st.warning(
            f"Are you sure you want to delete namespace '{namespace if namespace else 'default'}'?"
        )
        if st.button("Confirm Delete", type="primary"):
            namespace_to_delete = namespace if namespace else ""
            if delete_vectors_by_namespace(index, namespace_to_delete):
                st.session_state.document_processed = False
                st.session_state.show_confirm = False  # Reset confirmation state
                st.rerun()
        if st.button("Cancel"):
            st.session_state.show_confirm = False
            st.rerun()

    # Add a divider
    st.divider()

    # Other deletion options
    st.subheader("Other Delete Options")
    delete_option = st.selectbox(
        "Select Delete Operation",
        [
            "Select Operation",
            "Delete by Metadata",
            "Delete by IDs",
        ],
    )

    if delete_option == "Delete by Metadata":
        st.write("Enter metadata filter criteria:")
        filter_key = st.text_input("Metadata Key")
        filter_value = st.text_input("Metadata Value")
        if st.button("Delete by Metadata"):
            if filter_key and filter_value:
                metadata_filter = {filter_key: filter_value}
                delete_vectors_by_metadata(index, metadata_filter)
                st.rerun()
            else:
                st.warning("Please enter both key and value")

    elif delete_option == "Delete by IDs":
        ids_input = st.text_area("Enter vector IDs (one per line)")
        if st.button("Delete IDs"):
            if ids_input:
                ids = [id.strip() for id in ids_input.split("\n") if id.strip()]
                delete_vectors_by_ids(index, ids)
                st.rerun()
            else:
                st.warning("Please enter at least one ID")


def main():
    st.title("Document Q&A System")
    init_session_state()

    # Setup Pinecone and embeddings
    setup_result = setup_pinecone()
    if not setup_result:
        st.stop()
    embeddings, index_name = setup_result

    # Add tabs for different functionalities
    tab1, tab2 = st.tabs(["Document Processing", "Vector Store Management"])

    with tab1:
        # Document upload section
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file:
            # Metadata configuration section
            metadata = render_metadata_form()

            # Process document button
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    chunks = process_pdf(uploaded_file, metadata)
                    if not chunks:
                        st.error("Failed to process document")
                        st.stop()

                    vector_store = create_vector_store(
                        chunks,
                        embeddings,
                        index_name,
                        namespace=metadata.get("namespace"),
                    )
                    if not vector_store:
                        st.error("Failed to create vector store")
                        st.stop()

                    st.session_state.document_processed = True
                    st.success("Document processed successfully!")
                    st.session_state.vector_store = vector_store
                    st.rerun()

        # Chat interface (only shown after document is processed)
        if st.session_state.document_processed:
            st.markdown("---")
            render_chat_interface(st.session_state.vector_store)

    with tab2:
        # Vector store management interface
        pc = PineconeClient(api_key=os.getenv("PINECONE_API_KEY"))
        render_vector_store_management(pc, index_name)


if __name__ == "__main__":
    main()
