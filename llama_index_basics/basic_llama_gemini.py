from llama_index.llms.gemini import Gemini
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the Google API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

os.environ["GOOGLE_API_KEY"] = api_key

# Initialize the Gemini model
llm = Gemini(model="models/gemini-1.5-flash-001")

try:
    # Generate a response
    resp = llm.complete("Write a poem about a magic backpack")
    
    # Print the generated text
    print("Generated poem:")
    print(resp.text)
    
    # You can access other attributes of the response if needed
    # print("Model used:", resp.model_name)
    # print("Finish reason:", resp.finish_reason)

except Exception as e:
    print(f"An error occurred: {str(e)}")