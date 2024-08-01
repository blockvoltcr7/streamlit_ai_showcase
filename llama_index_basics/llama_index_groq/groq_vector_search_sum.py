# Import necessary libraries
from llama_index.core import VectorStoreIndex
import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import SimpleDirectoryReader
from llama_index.core import SummaryIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import RouterQueryEngine

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
print("Script directory:", script_dir)

# Construct the full path to the PDF files
# These PDFs contain information about Kendrick Lamar, Drake, and their beef
kendrick_pdf = os.path.join(script_dir, "testdata", "kendrick.pdf")
drake_pdf = os.path.join(script_dir, "testdata", "drake.pdf")
both_pdf = os.path.join(script_dir, "testdata", "drake_kendrick_beef.pdf")

# Load the documents using SimpleDirectoryReader
# This step reads the content of the PDFs and prepares them for processing
docs_kendrick = SimpleDirectoryReader(input_files=[kendrick_pdf]).load_data()
docs_drake = SimpleDirectoryReader(input_files=[drake_pdf]).load_data()
docs_both = SimpleDirectoryReader(input_files=[both_pdf]).load_data()

# Create a VectorStoreIndex from the documents
# This index allows for efficient similarity-based searches
index = VectorStoreIndex.from_documents(docs_both)

# Create a query engine from the index
# similarity_top_k=3 means it will return the top 3 most relevant results
query_engine = index.as_query_engine(similarity_top_k=3)

# Perform a query about "family matters"
response = query_engine.query("Tell me about family matters")
print(str(response))

# Create a SummaryIndex from the documents
# This index is optimized for generating summaries of the content
summary_index = SummaryIndex.from_documents(docs_both)
summary_engine = summary_index.as_query_engine()

# Use the summary engine to ask who won the beef
response = summary_engine.query(
    "Given your assessment of this article, who won the beef?"
)
print(str(response))

# Create a vector search tool
# This tool is useful for finding specific facts in the documents
vector_tool = QueryEngineTool(
    index.as_query_engine(),
    metadata=ToolMetadata(
        name="vector_search",
        description="Useful for searching for specific facts.",
    ),
)

# Create a summary tool
# This tool is useful for summarizing entire documents or large sections
summary_tool = QueryEngineTool(
    index.as_query_engine(response_mode="tree_summarize"),
    metadata=ToolMetadata(
        name="summary",
        description="Useful for summarizing an entire document.",
    ),
)

# Initialize Groq language models
# These are powerful language models that can understand and generate human-like text
llm = Groq(model="llama3-8b-8192")  # 8 billion parameter model
llm_70b = Groq(model="llama3-70b-8192")  # 70 billion parameter model

# Create a RouterQueryEngine
# This engine can choose between the vector search and summary tools based on the query
query_engine = RouterQueryEngine.from_defaults(
    [vector_tool, summary_tool], select_multi=False, verbose=True, llm=llm_70b
)

# Use the router query engine to ask about a specific song
response = query_engine.query(
    "If Drake could do one thing to win the beef against Kendrick, what should it be?"
)

print("-----------------")
print(response)