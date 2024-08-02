import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
# Fetch the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)


# gemini-1.0-pro
# gemini-1.0-pro-001
# gemini-1.0-pro-002
# gemini-1.5-pro-001
# gemini-1.5-pro-002
# gemini-1.5-flash-001


model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Give me python code to sort a list")

# Check if the response contains a valid Part
if response.parts:
    print(response.text)
else:
    # Handle cases where no valid Part is returned
    if response.candidate.safety_ratings:
        print("Content generation was blocked due to safety filters.")
        # You can print more detailed safety ratings here
        print(response.candidate.safety_ratings)
    else:
        print("No valid content was generated.")