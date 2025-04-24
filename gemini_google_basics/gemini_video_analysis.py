# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
import time
from google import genai
from google.genai import types

def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Upload the video file
    print("Uploading video file...")
    files = [
        client.files.upload(file="rflkt-2348972.mp4"),
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
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()