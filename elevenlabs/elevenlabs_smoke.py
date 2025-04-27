from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
import time

try:
    from mutagen.mp3 import MP3
    mutagen_available = True
except ImportError:
    print("Warning: mutagen library not found. Audio duration calculation will be skipped.")
    print("Install with: pip install mutagen")
    mutagen_available = False

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY,
)

# Get available models to use a valid model ID
print("Fetching available models...")
try:
    models = client.models.get_all()
    print("Available models:")
    for model in models:
        print(f"- {model.model_id}: {model.name}")
    
    # Use specified model
    model_id = "eleven_flash_v2_5"
    print(f"Using model: {model_id}")
except Exception as e:
    print(f"Error fetching models: {e}")
    # Fallback to a known model
    model_id = "eleven_flash_v2_5"
    print(f"Falling back to default model: {model_id}")

# Create audio directory if it doesn't exist
audio_dir = os.path.join(os.getcwd(), 'audio')
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Function to calculate audio duration in seconds
def get_audio_duration(file_path):
    if not mutagen_available:
        return None
    
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        print(f"Error calculating duration for {file_path}: {e}")
        return None

# Simple text to speech test
test_text = "Hello world! This is a simple text to speech test using Eleven Labs."
print(f"\nGenerating audio for: '{test_text}'")

# Generate audio
audio = client.text_to_speech.convert(
    text=test_text,
    voice_id="a9ldg2iPgaBn4VcYMJ4x",
    model_id=model_id,
    output_format="mp3_44100_128",
)

# Save the audio file
output_file_path = os.path.join(audio_dir, "hello_world.mp3")
audio_bytes = b''.join(chunk for chunk in audio)
with open(output_file_path, "wb") as f:
    f.write(audio_bytes)

# Calculate and display duration
duration = get_audio_duration(output_file_path)
duration_str = f"{duration:.2f} seconds" if duration is not None else "unknown"
print(f"Audio saved to: {output_file_path} (Duration: {duration_str})")

# Optionally play the audio (uncomment if needed)
# elevenlabs.play(audio)