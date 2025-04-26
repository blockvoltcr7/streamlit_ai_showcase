from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
import json
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
    
    # Use the first available model if exists
    model_id = models[0].model_id if models else "eleven_multilingual_v2"
    print(f"Using model: {model_id}")
except Exception as e:
    print(f"Error fetching models: {e}")
    # Fallback to a known model
    model_id = "eleven_multilingual_v2"
    print(f"Falling back to default model: {model_id}")

# Scene plan data
scene_plan = {
  "scenePlan": [
    {
      "sceneIndex": 1,
      "sceneStart": 0.3,
      "sceneDuration": 1.35,
      "texts": [
        {
          "caption": "He was weak",
          "textStart": 0,
          "textEnd": 0.51
        },
        {
          "caption": "couldn't do one push-up,",
          "textStart": 0.51,
          "textEnd": 1.35
        }
      ]
    },
    {
      "sceneIndex": 2,
      "sceneStart": 1.65,
      "sceneDuration": 1.17,
      "texts": [
        {
          "caption": "couldn't run a single mile",
          "textStart": 0,
          "textEnd": 0.97
        }
      ]
    },
    {
      "sceneIndex": 3,
      "sceneStart": 2.62,
      "sceneDuration": 1.42,
      "texts": [
        {
          "caption": "couldn't focus for five minutes.",
          "textStart": 0,
          "textEnd": 1.19
        }
      ]
    },
    {
      "sceneIndex": 4,
      "sceneStart": 4.88,
      "sceneDuration": 1.35,
      "texts": [
        {
          "caption": "But he started small.",
          "textStart": 0,
          "textEnd": 1.05
        }
      ]
    },
    {
      "sceneIndex": 5,
      "sceneStart": 6.96,
      "sceneDuration": 1.02,
      "texts": [
        {
          "caption": "One push-up,",
          "textStart": 0,
          "textEnd": 0.72
        }
      ]
    },
    {
      "sceneIndex": 6,
      "sceneStart": 8.58,
      "sceneDuration": 1.37,
      "texts": [
        {
          "caption": "one minute of running,",
          "textStart": 0,
          "textEnd": 1.07
        }
      ]
    },
    {
      "sceneIndex": 7,
      "sceneStart": 9.65,
      "sceneDuration": 1.45,
      "texts": [
        {
          "caption": "one page of a book.",
          "textStart": 0,
          "textEnd": 1.15
        }
      ]
    },
    {
      "sceneIndex": 8,
      "sceneStart": 11.96,
      "sceneDuration": 1.27,
      "texts": [
        {
          "caption": "Day after day,",
          "textStart": 0,
          "textEnd": 0.97
        }
      ]
    },
    {
      "sceneIndex": 9,
      "sceneStart": 13.98,
      "sceneDuration": 0.92,
      "texts": [
        {
          "caption": "he showed up.",
          "textStart": 0,
          "textEnd": 0.62
        }
      ]
    },
    {
      "sceneIndex": 10,
      "sceneStart": 15.91,
      "sceneDuration": 2.47,
      "texts": [
        {
          "caption": "The push-ups",
          "textStart": 0,
          "textEnd": 0.66
        },
        {
          "caption": "climb to 10, then 20, then 50.",
          "textStart": 0.66,
          "textEnd": 2.47
        }
      ]
    },
    {
      "sceneIndex": 11,
      "sceneStart": 19.69,
      "sceneDuration": 1.66,
      "texts": [
        {
          "caption": "The one-mile jog",
          "textStart": 0,
          "textEnd": 0.59
        },
        {
          "caption": "became five.",
          "textStart": 0.59,
          "textEnd": 1.36
        }
      ]
    },
    {
      "sceneIndex": 12,
      "sceneStart": 22.03,
      "sceneDuration": 2.56,
      "texts": [
        {
          "caption": "The pages stacked into libraries.",
          "textStart": 0,
          "textEnd": 2.26
        }
      ]
    },
    {
      "sceneIndex": 13,
      "sceneStart": 25.4,
      "sceneDuration": 3.06,
      "texts": [
        {
          "caption": "His body grew stronger, his mind sharper, his will unbreakable.",
          "textStart": 0,
          "textEnd": 2.76
        }
      ]
    },
    {
      "sceneIndex": 14,
      "sceneStart": 29.93,
      "sceneDuration": 1.96,
      "texts": [
        {
          "caption": "Now he's an absolute machine.",
          "textStart": 0,
          "textEnd": 1.66
        }
      ]
    },
    {
      "sceneIndex": 15,
      "sceneStart": 35.87,
      "sceneDuration": 1.77,
      "texts": [
        {
          "caption": "Start small, go hard,",
          "textStart": 0,
          "textEnd": 1.47
        }
      ]
    },
    {
      "sceneIndex": 16,
      "sceneStart": 38.16,
      "sceneDuration": 1.6,
      "texts": [
        {
          "caption": "finish as a legend.",
          "textStart": 0,
          "textEnd": 1.3
        }
      ]
    }
  ]
}

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

# Function to generate and save audio for a caption
def generate_audio_for_caption(scene_index, caption_index, caption_text):
    print(f"Generating audio for scene {scene_index}, caption {caption_index}: '{caption_text}'")
    
    # Generate audio
    audio = client.text_to_speech.convert(
        text=caption_text,
        voice_id="a9ldg2iPgaBn4VcYMJ4x",  # You can change this to another voice ID if you prefer
        model_id=model_id,  # Use the dynamically selected model ID
        output_format="mp3_44100_128",
    )
    
    # Create a filename based on scene and caption indices
    file_name = f"scene_{scene_index:02d}_caption_{caption_index:02d}.mp3"
    save_file_path = os.path.join(audio_dir, file_name)
    
    # Convert generator to bytes and write to file
    audio_bytes = b''.join(chunk for chunk in audio)
    with open(save_file_path, "wb") as f:
        f.write(audio_bytes)
    
    # Calculate the audio duration
    duration = get_audio_duration(save_file_path)
    duration_str = f"{duration:.2f} seconds" if duration is not None else "unknown"
    
    print(f"Audio saved to: {save_file_path} (Duration: {duration_str})")
    
    # Add a small delay to avoid rate limiting
    time.sleep(0.5)
    
    return save_file_path, duration

# Create a list to store the paths to all generated audio files
generated_files = []

# Process each scene in the scene plan
for scene in scene_plan["scenePlan"]:
    scene_index = scene["sceneIndex"]
    
    print(f"\nProcessing scene {scene_index}")
    
    # Process each caption in the scene
    for caption_index, text_item in enumerate(scene["texts"], 1):
        caption_text = text_item["caption"]
        
        # Generate and save audio for this caption
        audio_path, duration = generate_audio_for_caption(scene_index, caption_index, caption_text)
        generated_files.append({
            "scene_index": scene_index,
            "caption_index": caption_index,
            "caption_text": caption_text,
            "audio_path": audio_path,
            "planned_duration": text_item["textEnd"] - text_item["textStart"],
            "actual_duration": duration if duration is not None else None
        })

print(f"\nGenerated {len(generated_files)} audio files.")

# Calculate total duration of all caption audio files
if mutagen_available:
    total_actual_duration = sum(item["actual_duration"] for item in generated_files if item["actual_duration"] is not None)
    print(f"Total actual duration of all caption audio files: {total_actual_duration:.2f} seconds")

# Optionally, create a combined text of all captions for a single audio file
full_script = " ".join([text_item["caption"] for scene in scene_plan["scenePlan"] for text_item in scene["texts"]])
print("\nGenerating audio for full script...")

audio = client.text_to_speech.convert(
    text=full_script,
    voice_id="a9ldg2iPgaBn4VcYMJ4x",
    model_id=model_id,  # Use the dynamically selected model ID
    output_format="mp3_44100_128",
)

# Save the full script audio
full_script_file_path = os.path.join(audio_dir, "full_script.mp3")
audio_bytes = b''.join(chunk for chunk in audio)
with open(full_script_file_path, "wb") as f:
    f.write(audio_bytes)

# Calculate duration of the full script
full_script_duration = get_audio_duration(full_script_file_path)
full_script_duration_str = f"{full_script_duration:.2f} seconds" if full_script_duration is not None else "unknown"
print(f"Full script audio saved to: {full_script_file_path} (Duration: {full_script_duration_str})")

# Save a summary of generated files
summary_path = os.path.join(audio_dir, "audio_summary.json")
with open(summary_path, "w") as f:
    json.dump({
        "individual_files": generated_files,
        "full_script": {
            "path": full_script_file_path,
            "duration": full_script_duration
        },
        "total_individual_duration": total_actual_duration if mutagen_available else None
    }, f, indent=2)

print(f"Audio summary saved to: {summary_path}")

# Compare the planned vs actual durations
if mutagen_available:
    print("\nPlanned vs Actual Durations:")
    print("---------------------------")
    for item in generated_files:
        planned = item["planned_duration"]
        actual = item["actual_duration"]
        if actual is not None:
            difference = actual - planned
            percent_diff = (difference / planned) * 100 if planned > 0 else 0
            print(f"Scene {item['scene_index']}, Caption {item['caption_index']}: Planned={planned:.2f}s, Actual={actual:.2f}s, Diff={difference:.2f}s ({percent_diff:.1f}%)")