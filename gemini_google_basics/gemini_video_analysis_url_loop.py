# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import time
import requests
import io
import tempfile
import json # Added for JSON handling
import uuid # Added for random filename generation
from google import genai
from google.genai import types

def generate(video_urls):
    """
    Analyzes a list of videos from URLs using the Gemini API and saves the results to a JSON file.

    Args:
        video_urls (list): A list of strings, where each string is a URL to a video file.
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    all_results = [] # Store results for all videos

    for video_url in video_urls:
        print(f"--- Processing URL: {video_url} ---")
        video_filename = video_url.split("/")[-1] # Extract filename from URL
        temp_file = None
        temp_file_path = None # Initialize path
        analysis_result_text = "" # Store concatenated chunks for one video

        try:
            # Download the video from the URL
            print(f"Downloading video from {video_url}...")
            response = requests.get(video_url, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes
            video_bytes = response.content # Read the content into memory

            # Create a temporary file and write the video content to it
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_file.write(video_bytes)
            temp_file_path = temp_file.name
            temp_file.close() # Close the file handle so the API can read it
            print(f"Video saved temporarily to: {temp_file_path}")

            # Upload the temporary video file
            print(f"Uploading temporary video file {temp_file_path}...")
            # It's crucial the client can access the file path correctly
            # Ensure the path is accessible if running in different environments (e.g., containers)
            files = [
                client.files.upload(file=temp_file_path), # Upload using the file path
            ]

            # Check the file's state and wait until it's ACTIVE
            uploaded_file = files[0] # Get the uploaded file object
            print(f"File uploaded with name: {uploaded_file.name}. Checking file state...")

            max_attempts = 30  # Maximum number of attempts to check (30 * 5s = 150s)
            attempt = 1
            while attempt <= max_attempts:
                file_info = client.files.get(name=uploaded_file.name) # Use name= instead of file_id=
                file_state = file_info.state

                if file_state == "ACTIVE":
                    print("File is in ACTIVE state. Proceeding with analysis...")
                    break
                elif file_state == "PROCESSING":
                    print(f"Attempt {attempt}/{max_attempts}: File is still PROCESSING. Waiting 5 seconds...")
                    time.sleep(5)  # Wait 5 seconds before checking again
                    attempt += 1
                else:
                    # If the file is in a FAILED or other state, raise an error
                    raise Exception(f"File processing failed. State: {file_state}. Cannot proceed with analysis.")

            if attempt > max_attempts:
                raise Exception("Timeout: File did not reach ACTIVE state within the allowed time.")

            # Proceed with the analysis once the file is ACTIVE
            model = "gemini-1.5-flash" # Using 1.5 Flash
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=files[0].uri,
                            mime_type=files[0].mime_type,
                        ),
                    ],
                ),
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="""Task:

You are an advanced video scene analyst and expert AI visual prompt engineer. Analyze this video and return a structured JSON breakdown of distinct visual scenes for AI-powered video reproduction in a cinematic, high-contrast graphic-novel style.

Instructions:

Detect Unique Scenes:

Identify each visual change as a new scene (ignore timing/duration).

For Each Scene, Return:

A rich, detailed visual_description (describe subjects, environment, mood, textures).

2-4 relevant category_tags reflecting core themes/emotions.

A dynamic ai_prompt following the Artistic Style Guide below.

Strict Rules:

🚫 Do NOT mention any on-screen text.

🚫 Do NOT describe audio or background music.

Use cinematic, graphic, and emotionally charged language optimized for AI image generation.

Ensure response is pure JSON — no comments, no extra explanations.

🖌️ AI Prompt Style Guide (For ai_prompt Field):

When generating the ai_prompt, always apply these principles to stay true to the RFLKT visual identity:

"Create a high-contrast black and white monochrome illustration of [subject/action] on a solid black background. Depict bold silhouettes with selective white highlights and controlled gray shading. Apply a distinct **film grain overlay** and scattered **dust particles** across the entire image to evoke a vintage, analog atmosphere. Use cracked textures or rough ground where applicable for added grit. Ensure sharp contrasts dominate, avoiding mid-tones. Emphasize [emotion/theme] through dramatic shadows and negative space for text overlay. The style merges noir comics, sumi-e ink art, and distressed print aesthetics. Cinematic, raw, and timeless. -no signature, --no watermark, --no text"

⚡ JSON Output Format:
{
"scenes": [
{
"scene_number": 1,
"visual_description": "A lone warrior walking along a windswept ridge under a vast starry sky, viewed from behind. His cape flows dramatically in the wind, and a sword hangs at his side. Sharp white highlights trace the edges of his silhouette, while subtle gray shading defines the rocky terrain beneath his feet. The expansive black sky emphasizes solitude and purpose.",
"category_tags": ["Solitude", "Purpose", "Journey", "Resilience"],
"scene_context": "A symbolic journey toward an unknown destiny, embracing solitude and inner strength.",
"core_emotions": ["Determination", "Isolation", "Hope"],
"recommended_style": "ink_brush_minimalist",
"negative_space_position": "above",
"composition_focus": "rule-of-thirds",
"environment_elements": ["starry sky", "rocky ridge", "flowing cape", "sword"],
"action_intensity": "calm motion",
"voiceover_tone": "reflective"
}
// Additional scenes follow this structure
],
"full_transcription": "Insert the complete spoken narration of the video here, as one continuous block of text."
}

Final Note:

Ensure the response starts and ends strictly with the JSON object. No introductory text, no explanations—pure data, ready for automation."""),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="text/plain",
            )

            print("Starting video analysis...")
            response_stream = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            )
            for chunk in response_stream:
                analysis_result_text += chunk.text # Concatenate chunks

            print("Analysis complete for this video.")
            # Try to parse the result as JSON, otherwise store the raw text
            try:
                # Remove potential markdown backticks if present
                cleaned_text = analysis_result_text.strip().strip('```json').strip('```')
                parsed_result = json.loads(cleaned_text)
                all_results.append({"url": video_url, "analysis": parsed_result})
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse JSON for {video_url}. Storing raw text. Error: {e}")
                all_results.append({"url": video_url, "analysis_raw": analysis_result_text})

        except Exception as e:
            print(f"Error processing {video_url}: {e}")
            all_results.append({"url": video_url, "error": str(e)}) # Record the error

        finally:
            # Clean up the temporary file for this video
            if temp_file_path and os.path.exists(temp_file_path):
                print(f"Deleting temporary file: {temp_file_path}")
                try:
                    os.remove(temp_file_path)
                except OSError as e:
                    print(f"Error deleting temporary file {temp_file_path}: {e}")

    # After processing all URLs, write the results to a file
    if all_results:
        output_filename = f"video_analysis_results_{uuid.uuid4()}.json"
        output_filepath = os.path.join(os.getcwd(), output_filename) # Save in current dir
        print(f"Writing all results to {output_filepath}...")
        try:
            with open(output_filepath, 'w') as f:
                json.dump(all_results, f, indent=4)
            print("Results successfully written.")
        except Exception as e:
            print(f"Error writing results to file: {e}")
    else:
        print("No results were generated.")


if __name__ == "__main__":
    # --- Define the list of video URLs to process ---
    urls_to_process = [
        "https://tpfitionfrabfzlcapum.supabase.co/storage/v1/object/public/json2videoassets//rflkt-2348972.mp4",
        # Add more video URLs here if needed
        # "https://example.com/another_video.mp4",
    ]
    # --------------------------------------------------

    if not urls_to_process:
        print("No video URLs provided in the script. Exiting.")
    else:
        generate(urls_to_process)