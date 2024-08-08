import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# Fetch the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

your_file = genai.upload_file(path='../audio/ai-agents-mark-jen.mp3')
prompt = "Listen carefully to the following audio file. provide a full summary of the audio. be detailed and then elaborate on ai agents and their role in the future of work."
model = genai.GenerativeModel('models/gemini-1.5-flash')
response = model.generate_content([prompt, your_file])
print(response.text)
     