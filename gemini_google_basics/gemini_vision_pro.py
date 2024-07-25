import google.generativeai as genai
from dotenv import load_dotenv
import os
import streamlit as st  # Importing streamlit for Markdown

load_dotenv()
# Fetch the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

sample_file = genai.upload_file(path="../eraserio/output/sequence-diagram/sequence_diagram-1.png",
                                display_name="sequence_diagram-1.png")

st.write(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
file = genai.get_file(name=sample_file.name)
st.write(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")

# Choose a Gemini API model.
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

# Prompt the model with text and the previously uploaded image.
response = model.generate_content([sample_file, "Describe this sequence diagram, explain in a paragraph as if you are writing it in an article on medium.com. take your time and explain the flow and sequence"])
st.markdown(">" + response.text)  # Using streamlit's markdown function