import base64
import os
import time
import requests
import io
import tempfile
import json
import uuid
import datetime
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import replicate
from pydantic import BaseModel
from typing import List, Optional
from elevenlabs.client import ElevenLabs

# Import Google Gemini libraries
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Pydantic model for the structured output from OpenAI
class ImagePromptResponse(BaseModel):
    image_prompt: str

# Function to analyze video using Gemini API
def analyze_video(video_url):
    print(f"Starting video analysis process...")
    
    # Initialize Gemini client
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    
    # Extract filename from URL
    video_filename = video_url.split("/")[-1]
    
    # Download the video from the URL
    print(f"Downloading video from {video_url}...")
    response = requests.get(video_url, stream=True)
    response.raise_for_status()
    video_bytes = response.content
    
    temp_file = None
    temp_file_path = None
    
    try:
        # Create a temporary file and write the video content to it
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_file.write(video_bytes)
        temp_file_path = temp_file.name
        temp_file.close()
        print(f"Video saved temporarily to: {temp_file_path}")
        
        # Upload the temporary video file
        print(f"Uploading temporary video file to Gemini...")
        files = [
            client.files.upload(file=temp_file_path),
        ]
        
        # Check the file's state and wait until it's ACTIVE
        uploaded_file = files[0]
        # Store only the name and URI as strings
        file_name = uploaded_file.name
        file_uri = uploaded_file.uri
        
        print(f"File uploaded with name: {file_name}. Checking file state...")
        
        max_attempts = 30
        attempt = 1
        while attempt <= max_attempts:
            file_info = client.files.get(name=file_name)
            file_state = file_info.state
            
            if file_state == "ACTIVE":
                print("File is in ACTIVE state. Proceeding with analysis...")
                break
            elif file_state == "PROCESSING":
                print(f"Attempt {attempt}/{max_attempts}: File is still PROCESSING. Waiting 5 seconds...")
                time.sleep(5)
                attempt += 1
            else:
                raise Exception(f"File processing failed. State: {file_state}. Cannot proceed with analysis.")
        
        if attempt > max_attempts:
            raise Exception("Timeout: File did not reach ACTIVE state within the allowed time.")
        
        # Read the prompt from file
        # Note: In production, you might want to include this prompt directly in the code
        # or provide a fallback if the file doesn't exist
        try:
            with open("prompts/prompt_v2.txt", "r") as file:
                prompt = file.read()
        except FileNotFoundError:
            # Fallback prompt if file doesn't exist
            prompt = """Analyze this video and create a JSON response with the following structure:
{
  "scenes": [
    {
      "scene_number": 1,
      "visual_description": "Detailed visual description of what's happening in the scene",
      "category_tags": ["tag1", "tag2"],
      "scene_context": "What this scene represents in the narrative",
      "core_emotions": ["emotion1", "emotion2"],
      "recommended_style": "noir_graphic_novel or ink_brush_minimalist",
      "negative_space_position": "above or beside",
      "composition_focus": "centered-dramatic or rule-of-thirds",
      "environment_elements": ["element1", "element2", "element3"],
      "action_intensity": "still, calm motion, or dynamic action"
    }
  ],
  "full_transcription": "Full transcript of all spoken words in the video"
}
"""
        
        # Proceed with the analysis once the file is ACTIVE
        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=file_uri,
                        mime_type=files[0].mime_type,
                    ),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
            response_mime_type="text/plain",
        )
        
        print("Starting Gemini video analysis...")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
            # Optionally print each chunk as it comes in
            # print(chunk.text, end="")
        
        # Generate a unique filename with timestamp and UUID
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Ensure output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"video_analysis_results_{timestamp}_{unique_id}.json")
        
        try:
            # Clean the response text (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse the JSON and save it
            json_data = json.loads(cleaned_text)
            with open(output_file, "w") as f:
                json.dump(json_data, f, indent=2)
            print(f"\nGemini analysis saved to {output_file}")
            
            return json_data, output_file
            
        except json.JSONDecodeError:
            print("\nWarning: Could not parse response as valid JSON")
            with open(output_file, "w") as f:
                # Clean the text before writing
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                f.write(cleaned_text.strip())
            print(f"Raw response saved to {output_file}")
            
            # Try to manually fix common JSON issues and parse again
            try:
                # Common fixes for JSON issues
                fixed_text = cleaned_text.replace("'", "\"")  # Replace single quotes
                json_data = json.loads(fixed_text)
                fixed_output_file = os.path.join(output_dir, f"fixed_video_analysis_{timestamp}_{unique_id}.json")
                with open(fixed_output_file, "w") as f:
                    json.dump(json_data, f, indent=2)
                print(f"Fixed JSON saved to {fixed_output_file}")
                return json_data, fixed_output_file
            except:
                print("Could not fix JSON issues. Please check the raw output file.")
                return None, output_file
                
    finally:
        # Clean up the temporary file
        if temp_file and os.path.exists(temp_file_path):
            print(f"Deleting temporary file: {temp_file_path}")
            os.remove(temp_file_path)

# OpenAI client setup
def get_openai_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Function to generate an image prompt from a scene
def generate_image_prompt(scene, client):
    # Build the prompt based on the template
    prompt = f"""You are a world-class visual prompt engineer
---
### 🎬 INPUT DATA
- **visual_description:** {scene['visual_description']}
- **scene_context:** {scene['scene_context']}
- **core_emotions:** {scene['core_emotions']}
- **category_tags:** {scene['category_tags']}
- **recommended_style:** {scene['recommended_style']}
- **negative_space_position:** {scene['negative_space_position']}
- **composition_focus:** {scene['composition_focus']}
- **environment_elements:** {scene['environment_elements']}
- **action_intensity:** {scene['action_intensity']}
> ⚡ *Note:* Fields like `symbolic_motifs`, `tone_keywords`, `camera_angle`, etc., are removed to align with your current input structure.
---
### 🎨 BASE STYLE GUIDE PROMPT TEMPLATE YOU MUST USE
Always **embed** this core artistic direction into every prompt:
"Create a high-contrast black and white monochrome illustration of [describe main subject and action] on a solid black background.
Depict figure(s) or object(s) using bold silhouettes, enhanced with selective white highlights and controlled gray shading to define critical elements like [muscle tone, facial expressions, clothing folds, or motion bursts].
Incorporate textures using charcoal shading, pencil sketching, or woodcut-style cross-hatching to add depth, grit, and a handcrafted feel—without losing dramatic contrast.
Use minimal white strokes or gradients to subtly suggest [environment context: e.g., storm clouds, rocky terrain, ring ropes], ensuring the background remains predominantly pure black for maximum impact.
Avoid excessive mid-tones—focus on sharp, deliberate contrasts for a graphic-novel or classic woodcut appearance.
Emphasize [core emotions/themes: e.g., resilience, determination, solitude, intensity] through dynamic composition, lighting, and shadow play.
Leave intentional negative space [above/beside] the subject for a motivational quote overlay.
The style merges influences from noir comics, sumi-e ink art, pencil-on-black-canvas realism, and traditional woodcut illustrations. Cinematic, raw, powerful, and timeless. -no signature, --no watermark, --no text"
---
### 🛠️ TASKS
1. **Scene Fusion**:
   - Seamlessly merge:
     - `visual_description`
     - `scene_context`
     - Key `environment_elements`
   - Ensure it forms a vivid, cinematic narrative in **2-3 sentences**.
2. **Evoke Atmosphere**:
   - Subtly **weave in emotional tone** by referencing:
     - 2 emotions from `core_emotions` or `category_tags`.
     - Reflect mood without listing tags—focus on **feeling**.
3. **Technical Detailing**:
   - Apply:
     - `composition_focus` (e.g., "use rule-of-thirds for dynamic framing")
     - `negative_space_position` (e.g., "leave space above for text overlay")
     - Mention **action_intensity** to define motion or stillness.
     - Reference `recommended_style` subtly to guide visual flair.
4. **Wording Optimization**:
   - Limit prompt to **minimum of 150 WORDS OR MORE**.
   - Ensure cinematic flow, descriptive power, and technical clarity.
   - Embed **base style guide** naturally—avoid copy-pasting.
5. **End Prompt**:
   - Always conclude with:  
   `-no signature --no watermark --no text`
---
### 🚫 OUTPUT RULES
- Return **only** the finalized **single-line prompt**.
- No JSON, no extra text, no comments.
"""

    try:
        # Call OpenAI to generate the image prompt
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",  # Adjust model as needed
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate the optimized image prompt based on the provided scene."}
            ],
            response_format=ImagePromptResponse,
        )
        
        # Return the generated image prompt
        return completion.choices[0].message.parsed.image_prompt
    except Exception as e:
        print(f"Error generating image prompt: {e}")
        return None

# Function to generate an image using Replicate
def generate_image(image_prompt, scene_number):
    try:
        # Call Replicate to generate the image
        output = replicate.run(
            "black-forest-labs/flux-1.1-pro-ultra",
            input={
                "raw": False,
                "prompt": image_prompt,
                "aspect_ratio": "9:16",
                "output_format": "jpg",
                "safety_tolerance": 2,
                "image_prompt_strength": 0.1
            }
        )
        
        # Replicate typically returns a URL or list of URLs
        if isinstance(output, list) and len(output) > 0:
            image_url = output[0]
            # Make sure the URL is a string
            if hasattr(image_url, 'url'):
                image_url = image_url.url
            if not isinstance(image_url, str):
                image_url = str(image_url)
        else:
            # Make sure output is a string
            if hasattr(output, 'url'):
                image_url = output.url
            elif not isinstance(output, str):
                image_url = str(output)
            else:
                image_url = output
        
        return image_url
    except Exception as e:
        print(f"Error generating image for scene {scene_number}: {e}")
        return None

# Function to download and save an image
def download_image(url, scene_number):
    try:
        # Create output directory if it doesn't exist
        output_dir = "output_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # Download the image
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Generate a unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"scene_{scene_number}_{timestamp}.jpg")
        
        # Save the image
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Image saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error downloading image for scene {scene_number}: {e}")
        return None

def enhance_transcript_with_openai(transcript, scenes, openai_client=None):
    """
    Use OpenAI to enhance a transcript with ElevenLabs voice controls based on scene information.
    
    Args:
        transcript (str): The original transcript
        scenes (list): List of scene dictionaries containing emotional and visual context
        openai_client: Optional OpenAI client instance, will create one if not provided
        
    Returns:
        str: Enhanced transcript with ElevenLabs control tags
    """
    # Create OpenAI client if not provided
    if openai_client is None:
        openai_client = get_openai_client()
    
    # Create the prompt template with the controls documentation
    prompt = """
# Task: Enhance Voice Transcript with ElevenLabs Controls

You will be provided with a transcript and scene descriptions. Your task is to enhance the transcript with ElevenLabs voice controls to create a more emotionally resonant and natural-sounding voiceover.

## Scene Information
{scenes_json}

## Original Transcript
{transcript}

## ElevenLabs Voice Controls Documentation

### Pause Controls
- Use <break time="Xs" /> syntax for natural pauses (where X is seconds, max 3s)
- Examples:
  * <break time="0.5s" /> (short pause)
  * <break time="1s" /> (medium pause)
  * <break time="2s" /> (long pause)
- Limit to 2-3 break tags per paragraph to avoid instability
- Alternative pause methods: use dashes (-) for short pauses or ellipses (...) for hesitation

### Emphasis Controls
- Use CAPITAL LETTERS for strongly emphasized words
- Use partial CAPitalization for specific syllable emphasis
- Place "quotation marks" around phrases for moderate emphasis
- For specific words that need precise pronunciation:
  * <phoneme alphabet="ipa" ph="pronunciation">word</phoneme> (for IPA phonetic alphabet)
  * <phoneme alphabet="cmu-arpabet" ph="pronunciation">word</phoneme> (for CMU Arpabet)

### Pacing and Delivery
- Write in narrative style to naturally control pacing
- Use punctuation strategically (commas, periods) to control rhythm
- Multiple dashes (-- --) can create extended pauses
- Use question marks for rising intonation
- Use exclamation marks sparingly for excitement

### Limitations
- Avoid excessive break tags in a single passage
- Each voice responds differently to controls
- Only Eleven English V1 and Turbo V2 models fully support all SSML tags
- Break tags may cause some voices to add filler sounds ("uh", "ah")

## Guidelines for Enhancement
1. Start with a short break (0.5-1s)
2. Match emphasis to the emotional context of each scene
3. Use pauses between scenes or major transitions
4. Add emphasis to key words that match the core emotions of each scene
5. Consider the action_intensity when deciding on pacing
6. Keep the same words and meaning as the original transcript
7. Format the enhanced transcript as a single text block with appropriate controls
8. Ensure the enhanced transcript flows naturally when read aloud

## Your Task
Create an enhanced version of the transcript using appropriate ElevenLabs controls.
    """
    
    # Format the prompt with scenes and transcript
    formatted_prompt = prompt.format(
        scenes_json=json.dumps(scenes, indent=2),
        transcript=transcript
    )
    
    print(f"Enhancing transcript with OpenAI: {formatted_prompt}")
    
    try:
        # Call OpenAI API to enhance the transcript
        completion = openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # Use the most capable model
            messages=[
                {"role": "system", "content": "You are an expert in voice scripting and ElevenLabs text-to-speech controls."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.7  # Adjust for creativity vs determinism
        )
        
        # Extract the enhanced transcript from the response
        enhanced_transcript = completion.choices[0].message.content.strip()
        
        # If the response contains markdown code blocks, extract the content
        import re
        code_block_pattern = r"```(?:.*?\n)?(.*?)```"
        code_blocks = re.findall(code_block_pattern, enhanced_transcript, re.DOTALL)
        if code_blocks:
            # Use the first code block as the enhanced transcript
            enhanced_transcript = code_blocks[0].strip()
        
        return enhanced_transcript
    
    except Exception as e:
        print(f"Error enhancing transcript with OpenAI: {e}")
        import traceback
        traceback.print_exc()
        # Return the original transcript if enhancement fails
        return transcript

def generate_voiceover(transcript, scenes=None, voice_id="a9ldg2iPgaBn4VcYMJ4x", output_filename=None, enhance=False):
    """
    Generate a voiceover using ElevenLabs API.
    
    Args:
        transcript (str): The transcript to convert to speech
        scenes (list): Optional list of scene dictionaries for enhancement
        voice_id (str): ElevenLabs voice ID
        output_filename (str): Optional filename for the output audio file
        enhance (bool): Whether to enhance the transcript with OpenAI
        
    Returns:
        str: Path to the saved audio file
    """
    try:
        # Enhance the transcript with OpenAI if requested and scenes are provided
        if enhance and scenes:
            print("Enhancing transcript with OpenAI...")
            openai_client = get_openai_client()
            text_to_process = enhance_transcript_with_openai(transcript, scenes, openai_client)
            print("Transcript enhanced with ElevenLabs controls")
            # Save enhanced transcript for reference
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            enhanced_file = os.path.join("output", f"enhanced_transcript_{timestamp}.txt")
            with open(enhanced_file, "w") as f:
                f.write(text_to_process)
            print(f"Enhanced transcript saved to: {enhanced_file}")
        else:
            text_to_process = transcript
            print("Using original transcript without enhancement")
        
        # Create output directory if it doesn't exist
        audio_dir = os.path.join(os.getcwd(), 'audio')
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        # Generate a default filename if not provided
        if not output_filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"voiceover_{timestamp}.mp3"
        
        # Ensure filename has .mp3 extension
        if not output_filename.endswith('.mp3'):
            output_filename += '.mp3'
        
        output_file_path = os.path.join(audio_dir, output_filename)
        
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))
        
        # Use specified model or default to a known model
        try:
            # Choose an appropriate model
            if enhance:
                model_id = "eleven_multilingual_v2"  # Use multilingual for enhanced transcripts
            else:
                model_id = "eleven_flash_v2_5"  # Use flash for regular transcripts
            print(f"Using model: {model_id}")
        except Exception as e:
            print(f"Error fetching models: {e}")
            model_id = "eleven_flash_v2_5"
            print(f"Falling back to default model: {model_id}")
        print(f"Generating audio with ElevenLabs...")
        
        # Generate audio
        audio = client.text_to_speech.convert(
            text=text_to_process,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128",
        )
        
        # Save the audio file
        audio_bytes = b''.join(chunk for chunk in audio)
        with open(output_file_path, "wb") as f:
            f.write(audio_bytes)
        
        print(f"Audio saved to: {output_file_path}")
        
        # Calculate and display duration if mutagen is available
        try:
            from mutagen.mp3 import MP3
            audio = MP3(output_file_path)
            duration = audio.info.length
            print(f"Audio duration: {duration:.2f} seconds")
        except (ImportError, Exception) as e:
            print(f"Unable to calculate audio duration: {e}")
        
        return output_file_path
    
    except Exception as e:
        print(f"Error generating voiceover: {e}")
        import traceback
        traceback.print_exc()
        return None

# Function to process all scenes
def process_scenes(json_data):
    # Store all generated image URLs
    image_urls = []
    downloaded_files = []
    image_prompts = []
    
    # Initialize OpenAI client
    openai_client = get_openai_client()
    
    # Process each scene
    for i, scene in enumerate(json_data["scenes"]):
        scene_number = scene["scene_number"]
        print(f"\nProcessing Scene {scene_number}...")
        
        # Step 1: Generate the image prompt
        print("Generating image prompt...")
        image_prompt = generate_image_prompt(scene, openai_client)
        
        if image_prompt:
            print(f"Generated image prompt ({len(image_prompt)} chars)")
            image_prompts.append({"scene": scene_number, "prompt": image_prompt})
            
            # Step 2: Generate the image
            print("Generating image with Replicate...")
            image_url = generate_image(image_prompt, scene_number)
            
            if image_url:
                # Ensure URL is a string before adding to the results
                if not isinstance(image_url, str):
                    if hasattr(image_url, 'url'):
                        image_url = image_url.url
                    else:
                        image_url = str(image_url)
                
                print(f"Image generated: {image_url}")
                image_urls.append({"scene": scene_number, "url": image_url})
                
                # Step 3: Download the image
                print("Downloading image...")
                filename = download_image(image_url, scene_number)
                if filename:
                    downloaded_files.append({"scene": scene_number, "file": filename})
        
        # Add some delay to avoid rate limiting
        time.sleep(1)
    
    return {
        "image_prompts": image_prompts,
        "image_urls": image_urls,
        "downloaded_files": downloaded_files
    }
    

# Main execution function
def main():
    try:
        # Set up command line arguments
        parser = argparse.ArgumentParser(description='RFLKT Automation Content Creation Pipeline')
        parser.add_argument('--video_url', type=str, 
                            default="https://tpfitionfrabfzlcapum.supabase.co/storage/v1/object/public/videos/testing/2025-04-25-16246.mp4",
                            help='URL of the video to process')
        parser.add_argument('--enhance_transcript', action='store_true', 
                            help='Enable transcript enhancement with OpenAI (default: False)')
        parser.add_argument('--generate_voiceover', action='store_true',
                            help='Generate voiceover from transcript (default: False)')
        
        args = parser.parse_args()
        
        # Step 1: Analyze the video with Gemini
        video_url = args.video_url
        
        print(f"Starting end-to-end pipeline for video: {video_url}")
        json_data, analysis_file = analyze_video(video_url)
        
        if not json_data:
            print("Video analysis failed. Exiting.")
            return
        
        # Step 2: Process all scenes to generate images
        print("\nStarting image generation process for all scenes...")
        results = process_scenes(json_data)
        
        # Step 3: Generate voiceover from transcript only if flag is enabled
        if args.generate_voiceover and "full_transcription" in json_data:
            print("\nStarting voiceover generation process...")
            transcript = json_data["full_transcription"]
            
            # Generate the audio with enhanced transcript if enabled
            audio_file = generate_voiceover(
                transcript=transcript,
                scenes=json_data["scenes"],
                voice_id="a9ldg2iPgaBn4VcYMJ4x",  # You can change to your preferred voice
                enhance=args.enhance_transcript  # Use command line arg for enhancement
            )
            
            if audio_file:
                # Add audio file to results
                results["audio_file"] = audio_file
        elif args.generate_voiceover:
            print("\nNo transcript found in the video analysis data. Cannot generate voiceover.")
        else:
            print("\nVoiceover generation skipped (use --generate_voiceover to enable).")
        
        # Step 4: Save the complete results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join("output", f"complete_pipeline_results_{timestamp}.json")
        
        # Deep copy the results to ensure we don't modify the original objects
        import copy
        serializable_results = copy.deepcopy(results)
        
        # Ensure image_urls are all strings
        for url_obj in serializable_results.get('image_urls', []):
            if 'url' in url_obj and not isinstance(url_obj['url'], str):
                url_obj['url'] = str(url_obj['url'])
        
        # Add the analysis file to the results
        full_results = {
            "video_url": video_url,
            "analysis_file": str(analysis_file),  # Convert to string to ensure JSON serialization
            "generated_results": serializable_results
        }
        
        # Custom JSON encoder to handle any non-serializable objects
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                try:
                    return super().default(obj)
                except TypeError:
                    return str(obj)
        
        with open(results_file, 'w') as f:
            json.dump(full_results, f, indent=2, cls=CustomJSONEncoder)
            
        print(f"\nProcess completed. Generated {len(results['image_urls'])} images.")
        print(f"Complete results saved to {results_file}")
            
    except Exception as e:
        print(f"Error in main process: {e}")
        # Print more details for debugging
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()