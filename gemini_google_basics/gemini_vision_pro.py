from google import genai
from dotenv import load_dotenv
import os
import streamlit as st  # Importing streamlit for Markdown

load_dotenv()
# Fetch the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

# Upload the file
sample_file = client.files.upload(
    file="../eraserio/output/flowchart-diagram/bug-ticketing-process.png",
    display_name="bug-ticketing-process.png"
)

st.write(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
file = client.files.get(name=sample_file.name)
st.write(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")

# Choose a Gemini model
model = "gemini-1.5-pro-latest"

# Prompt the model with text and the previously uploaded image
contents = [
    {
        "role": "user",
        "parts": [
            {
                "file_data": {
                    "file_uri": sample_file.uri,
                    "mime_type": sample_file.mime_type
                }
            },
            {
                "text": "Describe this diagram, explain in a paragraph as if you are writing it in an article on medium.com. take your time and explain the flow and sequence"
            }
        ]
    }
]

response = client.generate_content(
    model=model,
    contents=contents
)

st.markdown(">" + response.text)  # Using streamlit's markdown function