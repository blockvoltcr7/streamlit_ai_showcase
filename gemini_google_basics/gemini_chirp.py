import google.generativeai as genai
from google.generativeai import GenerationConfig, GenerativeModel, TextGenerationConfig
from dotenv import load_dotenv
import os
import wave

load_dotenv()

# Fetch the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

model = GenerativeModel("gemini-pro")
text = "Hello, world! This is a test of text-to-speech."

generation_config = TextGenerationConfig(
    voice="en-US-Standard-A",  # Choose a voice
    language="en-US"
)

response = model.generate_content(
    prompt=text,
    generation_config=generation_config
)

#verify response is 200 status code
print(response.status_code)

# # Process the audio data
# audio_data = b''
# for chunk in response:
#     if hasattr(chunk, 'audio'):
#         audio_data += chunk.audio

# # Save the audio data to a WAV file
# output_file = "output.wav"
# with wave.open(output_file, 'wb') as wav_file:
#     wav_file.setnchannels(1)  # Mono audio
#     wav_file.setsampwidth(2)  # 16-bit audio
#     wav_file.setframerate(24000)  # Sample rate (you may need to adjust this)
#     wav_file.writeframes(audio_data)

# print(f"Audio saved to {output_file}")