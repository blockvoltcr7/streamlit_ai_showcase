import os
from google.cloud import texttospeech

# Correct the path to your Google Cloud service account key
credentials_path = os.path.abspath("../google_cloud_keys/ssi-automations-827bdc794623.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Create a Text-to-Speech client
client = texttospeech.TextToSpeechClient()

# Get the list of voices
voices_response = client.list_voices()

# Iterate over the voices in the response
for voice in voices_response.voices:
    print(f"Name: {voice.name}")
    print(f"Language Code: {voice.language_codes}")
    print(f"Gender: {voice.ssml_gender}")
    print(f"Naturalness: {voice.natural_sample_rate_hertz}")
    print("-" * 20)
    
# Construct the request
synthesis_input = texttospeech.SynthesisInput(text="We all have to battle our demons, it tests our resilience and determination. Each of us, at some point in our lives, faces challenges that seem insurmountable. It is during these times that the principles of Stoicism offer us a guiding light, a beacon of hope that helps us navigate through the storm.")

# Select the voice (with language code)
voice = texttospeech.VoiceSelectionParams(
    name="en-US-Standard-A",  # Choose a voice (see documentation for options)
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    language_code="en-US"  # Add the language code here
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
