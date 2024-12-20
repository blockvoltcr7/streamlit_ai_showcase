import streamlit as st
from dotenv import load_dotenv
from utils.pinecone_utils import (
    get_active_indexes,
    get_index_stats,
    process_document,
    upload_to_pinecone,
)

# Load environment variables
load_dotenv()


def reset_form():
    """Reset form state."""
    for key in list(st.session_state.keys()):
        if key != "reset_counter":
            del st.session_state[key]

    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0
    st.session_state.reset_counter += 1


def get_metadata():
    """Collect metadata from form."""
    metadata = {}

    # Core metadata fields
    metadata["title"] = st.text_input("Document Title", key="title")
    metadata["category"] = st.selectbox(
        "Category",
        ["services", "pricing", "materials", "faqs", "maintenance", "inspections"],
        key="category",
    )
    metadata["description"] = st.text_area("Description", key="description")

    # Tags and keywords
    tags = st.text_input("Tags (comma-separated)", key="tags")
    metadata["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # Author and date
    metadata["author"] = st.text_input("Author", key="author")
    metadata["date_created"] = st.date_input(
        "Date Created", key="date_created"
    ).isoformat()

    return metadata


def upload_documents_page():
    st.title("Upload Documents")

    # Get active indexes
    try:
        indexes = get_active_indexes()
        if not indexes:
            st.error("No Pinecone indexes available")
            return
    except Exception as e:
        st.error(f"Error connecting to Pinecone: {str(e)}")
        return

    # File upload with multiple file type support
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "txt", "md"],
        help="Supported formats: PDF, Text, and Markdown",
    )

    if uploaded_file:
        # Display file information
        st.write("### File Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**File Name:** {uploaded_file.name}")
            st.write(f"**File Type:** {uploaded_file.type}")
        with col2:
            st.write(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")
            # Add reset button here for when a file is uploaded
            if st.button("Clear Form", type="secondary"):
                reset_form()
                st.rerun()

        # Select index and namespace
        selected_index = st.selectbox("Select Index", indexes)

        # Get available namespaces for the selected index
        try:
            stats = get_index_stats(selected_index)
            available_namespaces = list(stats.namespaces.keys())
            # Replace empty namespace with "default" for display
            available_namespaces = [
                "default" if ns == "" else ns for ns in available_namespaces
            ]

            col1, col2 = st.columns([3, 1])
            with col1:
                if available_namespaces:
                    use_existing = st.checkbox("Use existing namespace", value=True)
                    if use_existing:
                        # Show dropdown if namespaces exist
                        namespace = st.selectbox(
                            "Select Namespace",
                            options=available_namespaces,
                            help="Select a namespace to upload to",
                            key="upload_namespace",
                        )
                        # Convert "default" back to empty string for Pinecone
                        namespace = "" if namespace == "default" else namespace
                    else:
                        # Show input field for new namespace
                        namespace = st.text_input(
                            "Create New Namespace",
                            help="Enter a name for the new namespace",
                            key="new_namespace",
                        )
                else:
                    # Show input field if no namespaces exist
                    namespace = st.text_input(
                        "Create New Namespace",
                        help="No existing namespaces found. Please create a new one.",
                        key="new_namespace",
                    )

            # Get metadata
            st.subheader("Document Metadata")
            metadata = get_metadata()

            # Upload button - only show if namespace is provided
            if namespace.strip():
                if st.button("Upload Document"):
                    try:
                        with st.spinner("Processing document..."):
                            # Process document
                            chunks = process_document(
                                uploaded_file, metadata, namespace
                            )

                            # Show chunk information
                            st.info(f"Document split into {len(chunks)} chunks")

                            with st.spinner("Uploading to Pinecone..."):
                                # Upload to Pinecone
                                vectorstore = upload_to_pinecone(
                                    chunks, selected_index, namespace
                                )

                            st.success("Document uploaded successfully!")

                            # Show document details
                            with st.expander("Document Details"):
                                st.json(
                                    {
                                        "file_name": uploaded_file.name,
                                        "chunks": len(chunks),
                                        "index": selected_index,
                                        "namespace": (
                                            "default" if namespace == "" else namespace
                                        ),
                                        "metadata": metadata,
                                    }
                                )

                            # Show upload another button
                            if st.button("Upload Another Document"):
                                reset_form()
                                st.rerun()

                    except Exception as e:
                        st.error(f"Error uploading document: {str(e)}")
                        st.exception(e)  # Show detailed error in development
            else:
                st.error("Please enter a namespace before uploading")

        except Exception as e:
            st.error(f"Error fetching namespaces: {str(e)}")


if __name__ == "__main__":
    upload_documents_page()
