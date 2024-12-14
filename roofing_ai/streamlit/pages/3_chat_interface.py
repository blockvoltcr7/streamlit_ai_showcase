import os
from typing import Dict

import streamlit as st
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI  # Use this for chat models
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from utils.pinecone_utils import get_active_indexes


def init_session_state():
    """Initialize chat session state."""
    if "conversation" not in st.session_state:
        st.session_state.conversation = []


def query_vector_store(vector_store, query: str, metadata_filter: Dict = None):
    """Query vector store and get response using LLM."""
    try:
        # Initialize OpenAI chat model with specific parameters
        llm = ChatOpenAI(
            temperature=0.7,  # Add some creativity
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",  # Use a valid chat model
        )

        # Get relevant documents with more context
        docs = vector_store.similarity_search(
            query, k=5, filter=metadata_filter  # Increase number of relevant docs
        )

        if not docs:
            return "I couldn't find any relevant information in the documents."

        # Create and run QA chain with specific prompt
        chain = load_qa_chain(llm, chain_type="stuff", verbose=True)

        # Add context to the question
        context_query = (
            "Based on the provided documents, " f"please answer this question: {query}"
        )

        # Get response
        response = chain.run(input_documents=docs, question=context_query)

        return response

    except Exception as e:
        st.error(f"Error querying vector store: {str(e)}")
        return None


def render_chat_interface(vector_store):
    st.subheader("Chat Interface")

    # Display conversation history
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])  # Use markdown for better formatting

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to conversation
        st.session_state.conversation.append({"role": "user", "content": prompt})

        with st.spinner("Searching documents..."):
            # Get response from vector store
            response = query_vector_store(vector_store, prompt)

            if response:
                # Add assistant response to conversation
                st.session_state.conversation.append(
                    {"role": "assistant", "content": response}
                )

                # Force refresh to show new messages
                st.rerun()


def chat_interface_page():
    st.title("Chat with Documents")
    init_session_state()

    try:
        indexes = get_active_indexes()
        if not indexes:
            st.error("No Pinecone indexes available")
            return

        # Add settings to sidebar
        with st.sidebar:
            st.header("Settings")
            selected_index = st.selectbox("Select Index", indexes)

            # Make namespace optional with a checkbox
            use_namespace = st.checkbox("Filter by Namespace")
            namespace = None
            if use_namespace:
                namespace = st.text_input(
                    "Namespace", help="Filter documents by namespace"
                )

        # Initialize vector store
        embeddings = OpenAIEmbeddings()
        vector_store = Pinecone.from_existing_index(
            index_name=selected_index,
            embedding=embeddings,
            namespace=namespace,  # Will be None by default
        )

        # Render chat interface
        render_chat_interface(vector_store)

    except Exception as e:
        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    chat_interface_page()
