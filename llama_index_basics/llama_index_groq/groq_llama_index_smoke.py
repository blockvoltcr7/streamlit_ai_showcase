import os
from dotenv import load_dotenv
import nest_asyncio
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader
from llama_index.core.llms import ChatMessage


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
print("Kendrick vs Drake --- single response")
response = llm.complete("Do you like Drake or Kendrick better?")
print(response)



print("Kendrick vs Drake --- continued conversation")
#stream and continue the conversation
stream_response = llm.stream_complete(
    "I think drake is way better, but some say that in california that kendrick is better. do you think people in california like kendrick more than drake? also tell me why kendrick is better at story telling."
)

for t in stream_response:
    print(t.delta, end="")


print("Kendrick vs Drake --- multiple responses")
messages = [
    ChatMessage(role="system", content="You are Kendrick."),
    ChatMessage(role="user", content="Write a verse."),
]
response = llm.chat(messages)

print(response)