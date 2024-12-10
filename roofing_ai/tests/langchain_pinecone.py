import os

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


def create_document_search(texts, embeddings, index_name):
    return LangchainPinecone.from_texts(
        [t.page_content for t in texts], embeddings, index_name=index_name
    )


def process_text_file(file_path):
    # Open and read the text file
    with open(file_path, "r") as file_data:
        file_content = file_data.read()

    # Set up the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=0,
        length_function=len,
    )

    # Split the text into chunks
    return text_splitter.create_documents([file_content])


def process_pdf_file(pdf_path):
    # Load PDF file
    loader = PyPDFLoader(pdf_path)
    file_content = loader.load()

    # Split the content
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=0,
        length_function=len,
    )

    return text_splitter.split_documents(file_content)


def query_document(docsearch, query_text):
    # Set up the LLM model
    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

    # Perform similarity search
    docs = docsearch.similarity_search(query_text)

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

    print(query_document(pdf_docsearch, "Do you offer free roof inspections?"))
    print(query_document(pdf_docsearch, "How often should I get my roof inspected?"))


if __name__ == "__main__":
    main()
