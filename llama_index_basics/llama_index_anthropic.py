import os
from dotenv import load_dotenv
from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

tokenizer = Anthropic().tokenizer
Settings.tokenizer = tokenizer

# Load environment variables
load_dotenv()

# Set up API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Set up Anthropic tokenizer
anthropic_tokenizer = Anthropic().tokenizer
Settings.tokenizer = anthropic_tokenizer

# Initialize LLMs
anthropic_llm = Anthropic(model="claude-3-opus-20240229", api_key=ANTHROPIC_API_KEY)
response = anthropic_llm.complete("j.cole started his career at what age?")
print(response)
llm = Anthropic(model="claude-3-opus-20240229")

resp = llm.complete("what is a test plan in software testing?")
print(resp)