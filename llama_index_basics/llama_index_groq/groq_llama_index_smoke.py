import os
from dotenv import load_dotenv
import nest_asyncio
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader

# Print current working directory
print("Current working directory:", os.getcwd())

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
print("Script directory:", script_dir)

# Construct the full path to the PDF files
kendrick_pdf = os.path.join(script_dir, "testdata", "kendrick.pdf")
drake_pdf = os.path.join(script_dir, "testdata", "drake.pdf")
both_pdf = os.path.join(script_dir, "testdata", "drake_kendrick_beef.pdf")

print("Kendrick PDF path:", kendrick_pdf)
print("Drake PDF path:", drake_pdf)
print("Both PDF path:", both_pdf)


nest_asyncio.apply()
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

os.environ["GROQ_API_KEY"] = api_key

# Load the documents
docs_kendrick = SimpleDirectoryReader(input_files=[kendrick_pdf]).load_data()
docs_drake = SimpleDirectoryReader(input_files=[drake_pdf]).load_data()
docs_both = SimpleDirectoryReader(input_files=[both_pdf]).load_data()

# Set up the models
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Groq(model="llama3-8b-8192")
llm_70b = Groq(model="llama3-70b-8192")

# Configure settings
Settings.llm = llm
Settings.embed_model = embed_model

# Test the LLM
response = llm.complete("Do you like Drake or Kendrick better?")
print(response)