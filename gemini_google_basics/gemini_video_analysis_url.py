# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import time
import requests
import io
import tempfile
from google import genai
from google.genai import types

def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    video_url = "https://tpfitionfrabfzlcapum.supabase.co/storage/v1/object/public/videos/mindset-rflkt/mindset_mavens_RPReplay_Final1745643177.mov"
    video_filename = video_url.split("/")[-1] # Extract filename from URL

    # Download the video from the URL
    print(f"Downloading video from {video_url}...")
    response = requests.get(video_url, stream=True)
    response.raise_for_status() # Raise an exception for bad status codes
    video_bytes = response.content # Read the content into memory

    temp_file = None
    try:
        # Create a temporary file and write the video content to it
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_file.write(video_bytes)
        temp_file_path = temp_file.name
        temp_file.close() # Close the file handle so the API can read it
        print(f"Video saved temporarily to: {temp_file_path}")

        # Upload the temporary video file
        print(f"Uploading temporary video file {temp_file_path}...")
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


        # paramaterize the prompt read the file in gemini_google_basics/prompts/prompt_default_v1.txt
        with open("../gemini_google_basics/prompts/prompt_v2.txt", "r") as file:
            prompt = file.read()

        # Proceed with the analysis once the file is ACTIVE
        model = "gemini-2.0-flash" 
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

        print("Starting video analysis...")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
            print(chunk.text, end="")
        
        # Write the JSON response to a file with a unique filename
        import json
        import uuid
        import datetime
        
        # Generate a unique filename with timestamp and UUID
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
        
        # Ensure output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"video_analysis_results_{timestamp}_{unique_id}.json")
        
        try:
            # Clean the response text by removing any markdown code block syntax if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]  # Remove ```
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]  # Remove trailing ```
            
            cleaned_text = cleaned_text.strip()  # Remove any extra whitespace
            
            json_data = json.loads(cleaned_text)
            with open(output_file, "w") as f:
                json.dump(json_data, f, indent=2)
            print(f"\nAnalysis saved to {output_file}")
        except json.JSONDecodeError:
            print("\nWarning: Could not parse response as valid JSON")
            with open(output_file, "w") as f:
                # Also clean the text before writing as raw
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                f.write(cleaned_text.strip())
            print(f"Raw response saved to {output_file}")

    finally:
        # Clean up the temporary file
        if temp_file and os.path.exists(temp_file_path):
            print(f"Deleting temporary file: {temp_file_path}")
            os.remove(temp_file_path)

if __name__ == "__main__":
    generate()