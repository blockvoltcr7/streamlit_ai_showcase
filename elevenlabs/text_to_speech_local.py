import os
import uuid
from io import BytesIO
from typing import IO
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs


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
        voice_id="txaks9Y4DguQLag5WHgP",  # custom mental health voice
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

    print("Streaming audio data...")

    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    audio_stream.seek(0)
    return audio_stream

def save_audiostream_to_file(audio_stream: IO[bytes]) -> str:
    """
    Saves an audio stream to a file in the project's root directory.

    Args:
        audio_stream (IO[bytes]): The audio stream to save.

    Returns:
        str: The file path where the audio file has been saved.
    """
    file_name = f"kratos{uuid.uuid4()}.mp3"
    save_file_path = os.path.join(os.getcwd(), '..', 'audio', file_name)
    print(f"Saving audio file to: {save_file_path}")
    
    with open(save_file_path, "wb") as f:
        f.write(audio_stream.getvalue())

    print(f"A new audio file was saved successfully at {save_file_path}")
    return save_file_path

def main(text: str):
    audio_stream = text_to_speech_stream(text)
    file_path = save_audiostream_to_file(audio_stream)
    print(f"Audio file saved at: {file_path}")
    
    

if __name__ == "__main__":
    
    text  = """

We all have to battle our demons, it tests our resilience and determination.
Each of us, at some point in our lives, faces challenges that seem insurmountable.
It is during these times that the principles of Stoicism offer us a guiding light, a beacon of hope that
helps us navigate through the storm.

    """
    main(text)