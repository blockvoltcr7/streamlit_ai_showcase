import os
import uuid
from typing import IO
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import boto3
from botocore.exceptions import NoCredentialsError

load_dotenv()

# ElevenLabs setup
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# AWS S3 setup
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def text_to_speech_stream(text: str) -> IO[bytes]:
    """
    Converts text to speech and returns an audio stream.

    Args:
        text (str): The text content to convert to speech.

    Returns:
        IO[bytes]: An audio stream of the converted speech.
    """
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    return response

def upload_audiostream_to_s3(audio_stream: IO[bytes]) -> str:
    """
    Uploads an audio stream to S3 bucket.

    Args:
        audio_stream (IO[bytes]): The audio stream to upload.

    Returns:
        str: The S3 file name of the uploaded file.
    """
    s3_file_name = f"{uuid.uuid4()}.mp3"
    try:
        s3_client.upload_fileobj(audio_stream, S3_BUCKET, s3_file_name)
        print(f"Upload Successful: {s3_file_name}")
        return s3_file_name
    except NoCredentialsError:
        print("Credentials not available")
        return ""

def generate_presigned_url(file_name: str) -> str:
    """
    Generates a presigned URL for the S3 file.

    Args:
        file_name (str): The name of the file in S3 bucket.

    Returns:
        str: The presigned URL for the file.
    """
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET,
                                                            'Key': file_name},
                                                    ExpiresIn=3600)
        return response
    except NoCredentialsError:
        print("Credentials not available")
        return ""

def main(text: str):
    audio_stream = text_to_speech_stream(text)
    s3_file_name = upload_audiostream_to_s3(audio_stream)
    signed_url = generate_presigned_url(s3_file_name)

    print(f"Signed URL to access the file: {signed_url}")

if __name__ == "__main__":
    main("This is a test of the ElevenLabs API.")