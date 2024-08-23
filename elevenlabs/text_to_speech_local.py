import os
import uuid
from io import BytesIO
from typing import IO
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import streamlit as st

load_dotenv()

# ElevenLabs setup
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech_stream(text: str) -> IO[bytes]:
    """
    Converts text to speech and returns the audio data as a byte stream.

    Args:
        text (str): The text content to be converted into speech.

    Returns:
        IO[bytes]: A BytesIO stream containing the audio data.
    """
    response = client.text_to_speech.convert(
        voice_id="6FVMQT8QZi7fP00BUvK9",  # custom mental health voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=1.0,
            similarity_boost=1.0,
            style=.80,
            use_speaker_boost=True,
        ),
    )

    st.write("Generating audio...")

    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    audio_stream.seek(0)
    return audio_stream

def save_audiostream_to_file(audio_stream: IO[bytes]) -> str:
    """
    Saves an audio stream to a file in the project's audio directory.

    Args:
        audio_stream (IO[bytes]): The audio stream to save.

    Returns:
        str: The file path where the audio file has been saved.
    """
    file_name = f"kratos{uuid.uuid4()}.mp3"
    save_file_path = os.path.join(os.getcwd(), '..', 'audio', file_name)
    st.write(f"Saving audio file to: {save_file_path}")
    
    with open(save_file_path, "wb") as f:
        f.write(audio_stream.getvalue())

    st.success(f"Audio file saved successfully at {save_file_path}")
    return save_file_path

def main():
    st.title("Text-to-Speech with ElevenLabs")
    
    # Text input
    text = st.text_area("Enter the text you want to convert to speech:", height=200)
    
    # Generate button
    if st.button("Generate Speech"):
        if text:
            try:
                audio_stream = text_to_speech_stream(text)
                file_path = save_audiostream_to_file(audio_stream)
                
                # Play the generated audio
                st.audio(file_path, format="audio/mp3")
                
                # Provide download link
                with open(file_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Audio",
                        data=file,
                        file_name="generated_speech.mp3",
                        mime="audio/mp3"
                    )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to convert to speech.")

if __name__ == "__main__":
    main()