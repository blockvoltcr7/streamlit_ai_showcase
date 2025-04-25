from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
import json
import time

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY,
)

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

# Function to generate and save audio for a caption
def generate_audio_for_caption(scene_index, caption_index, caption_text):
    print(f"Generating audio for scene {scene_index}, caption {caption_index}: '{caption_text}'")
    
    # Generate audio
    audio = client.text_to_speech.convert(
        text=caption_text,
        voice_id="a9ldg2iPgaBn4VcYMJ4x",  # You can change this to another voice ID if you prefer
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    
    # Create a filename based on scene and caption indices
    file_name = f"scene_{scene_index:02d}_caption_{caption_index:02d}.mp3"
    save_file_path = os.path.join(audio_dir, file_name)
    
    # Convert generator to bytes and write to file
    audio_bytes = b''.join(chunk for chunk in audio)
    with open(save_file_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"Audio saved to: {save_file_path}")
    
    # Add a small delay to avoid rate limiting
    time.sleep(0.5)
    
    return save_file_path

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
        audio_path = generate_audio_for_caption(scene_index, caption_index, caption_text)
        generated_files.append({
            "scene_index": scene_index,
            "caption_index": caption_index,
            "caption_text": caption_text,
            "audio_path": audio_path
        })

print(f"\nGenerated {len(generated_files)} audio files.")

# Optionally, create a combined text of all captions for a single audio file
full_script = " ".join([text_item["caption"] for scene in scene_plan["scenePlan"] for text_item in scene["texts"]])
print("\nGenerating audio for full script...")

audio = client.text_to_speech.convert(
    text=full_script,
    voice_id="a9ldg2iPgaBn4VcYMJ4x",
    model_id="eleven_flash_v2.5",
    output_format="mp3_44100_128",
)

# Save the full script audio
full_script_file_path = os.path.join(audio_dir, "full_script.mp3")
audio_bytes = b''.join(chunk for chunk in audio)
with open(full_script_file_path, "wb") as f:
    f.write(audio_bytes)

print(f"Full script audio saved to: {full_script_file_path}")

# Save a summary of generated files
summary_path = os.path.join(audio_dir, "audio_summary.json")
with open(summary_path, "w") as f:
    json.dump(generated_files, f, indent=2)

print(f"Audio summary saved to: {summary_path}")