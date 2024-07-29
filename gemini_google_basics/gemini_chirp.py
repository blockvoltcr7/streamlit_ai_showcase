import os
from google.cloud import texttospeech

# Set up your environment variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service_account_key.json"

# Create a Text-to-Speech client
client = texttospeech.TextToSpeechClient()

# Construct the request
synthesis_input = texttospeech.SynthesisInput(text="Hello, world!")

# Select the voice
voice = texttospeech.VoiceSelectionParams(
    name="en-US-Standard-A",  # Choose a voice (see documentation for options)
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
)

# Set the audio configuration
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
)

# Perform the text-to-speech request
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# Save the audio file
with open("output.mp3", "wb") as out:
    out.write(response.audio_content)

print("Audio content written to file 'output.mp3'")
