import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from PyPDF2 import PdfReader
from utils.metadata_utils import get_metadata_template, validate_metadata
from utils.pinecone_utils import get_active_indexes, upload_document


def reset_form():
    """Reset all form inputs and clear the uploaded file."""
    # Clear file uploader
    st.session_state["uploaded_file"] = None

    # Clear all form inputs from session state
    for key in list(st.session_state.keys()):
        if key != "reset_counter":  # Keep the reset counter
            del st.session_state[key]

    # Increment reset counter to force a rerun
    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0
    st.session_state.reset_counter += 1


def read_file_content(uploaded_file):
    """Read content from uploaded file based on its type."""
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        # Handle PDF files
        pdf_reader = PdfReader(uploaded_file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        return text_content
    else:
        # Handle text files (txt, md)
        return uploaded_file.getvalue().decode("utf-8")


def document_upload_page():
    st.title("Upload Documents")

    # Add reset button at the top
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Reset Form", type="secondary"):
            reset_form()
            st.rerun()

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a document", type=["txt", "md", "pdf"], key="uploaded_file"
    )

    if uploaded_file:
        # Display file details
        st.write(f"File name: {uploaded_file.name}")
        st.write(f"File size: {uploaded_file.size} bytes")
        st.write(f"File type: {uploaded_file.type}")

        # Index selection
        try:
            indexes = get_active_indexes()
            if not indexes:
                st.error("No Pinecone indexes available. Please create an index first.")
                return
            selected_index = st.selectbox("Select Index", indexes)
        except Exception as e:
            st.error(f"Error getting Pinecone indexes: {str(e)}")
            return

        # Metadata input
        st.subheader("Document Metadata")
        metadata = {}

        # Core Attributes
        with st.expander("Core Attributes", expanded=True):
            metadata["title"] = st.text_input("Document Title", uploaded_file.name)
            metadata["category"] = st.selectbox(
                "Category",
                [
                    "services",
                    "pricing",
                    "materials",
                    "faqs",
                    "maintenance",
                    "inspections",
                ],
            )
            metadata["subcategory"] = st.text_input("Subcategory")
            tags_input = st.text_input(
                "Tags",
                help="Enter tags separated by commas (e.g., 'roofing,inspection,maintenance')",
            )
            # Split tags on commas and clean up
            metadata["tags"] = [
                tag.strip() for tag in tags_input.split(",") if tag.strip()
            ]
            metadata["keywords"] = st.text_area(
                "Keywords (one per line, min 3)", help="Enter SEO-friendly keywords"
            ).split("\n")
            metadata["description"] = st.text_area(
                "Description",
                help="Provide a comprehensive description of the document",
            )
            metadata["audience"] = st.multiselect(
                "Target Audience",
                [
                    "residential homeowners",
                    "commercial property managers",
                    "contractors",
                    "architects",
                ],
            )
            metadata["content_snippet"] = st.text_area(
                "Content Preview", help="A brief preview of the document's content"
            )

        # Functional Attributes
        with st.expander("Functional Attributes"):
            metadata["purpose"] = st.text_input(
                "Document Purpose", help="What is the main purpose of this document?"
            )
            metadata["question_intent"] = st.text_area(
                "Question Intent (one per line)",
                help="What questions does this document answer?",
            ).split("\n")
            metadata["document_type"] = st.selectbox(
                "Document Type",
                ["text", "markdown", "pdf", "guide", "manual", "specification"],
            )
            metadata["location"] = st.multiselect(
                "Geographic Coverage",
                ["USA", "California", "Los Angeles", "San Francisco", "San Diego"],
            )

        # Technical Attributes
        with st.expander("Technical Attributes"):
            metadata["date_created"] = st.date_input("Date Created").isoformat()
            metadata["date_last_updated"] = st.date_input("Last Updated").isoformat()
            metadata["author"] = st.text_input("Author")

            # Related documents as a structured list
            st.subheader("Related Documents")
            num_related = st.number_input(
                "Number of related documents", min_value=0, max_value=5, value=0
            )
            metadata["related_documents"] = []

            for i in range(num_related):
                with st.container():
                    related_doc = {
                        "title": st.text_input(f"Document {i+1} Title"),
                        "purpose": st.text_input(f"Document {i+1} Purpose"),
                        "link": st.text_input(f"Document {i+1} Link"),
                    }
                    metadata["related_documents"].append(related_doc)

        if st.button("Upload Document"):
            try:
                # Clean empty lists and strings
                for key in metadata:
                    if isinstance(metadata[key], list):
                        metadata[key] = [x.strip() for x in metadata[key] if x.strip()]
                    elif isinstance(metadata[key], str):
                        metadata[key] = metadata[key].strip()

                # Validate metadata
                if validate_metadata(metadata):
                    # Read file content based on file type
                    content = read_file_content(uploaded_file)

                    # Upload to Pinecone
                    upload_document(
                        selected_index, content, metadata, file_name=uploaded_file.name
                    )

                    st.success("Document uploaded successfully!")
                    st.json(metadata)  # Display the final metadata for verification

                    # Add option to reset after successful upload
                    if st.button("Upload Another Document"):
                        reset_form()
                        st.rerun()

            except Exception as e:
                st.error(f"Error uploading document: {str(e)}")
                st.exception(e)  # This will show the full traceback in development


if __name__ == "__main__":
    document_upload_page()
