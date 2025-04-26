# Deploying Gemini Video Analysis API to Render.com

This document outlines how to convert the `gemini_video_analysis_url_loop.py` script into a FastAPI application and deploy it to Render.com.

## Part 1: Converting the Script to FastAPI

### Project Structure

Create a project with the following structure:

```
gemini-video-api/
├── main.py               # FastAPI application
├── requirements.txt      # Dependencies
├── .env.example          # Example environment variables (don't commit real secrets)
└── README.md             # Instructions
```

### FastAPI Implementation

In `main.py`, implement the FastAPI application:

```python
import base64
import os
import time
import requests
import tempfile
import json
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Gemini Video Analysis API",
    description="API for analyzing videos using Google's Gemini 1.5 Flash model",
    version="1.0.0"
)

# Security configuration
API_KEY_NAME = "X-API-Secret"
API_KEY = os.environ.get("API_SECRET")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Pydantic models for request and response
class VideoRequest(BaseModel):
    urls: List[str]

class VideoAnalysisResult(BaseModel):
    url: str
    status: str
    analysis: Optional[dict] = None
    error_message: Optional[str] = None

# Dependency for API key validation
async def get_api_key(api_key_header: str = Header(None, alias=API_KEY_NAME)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
    return api_key_header

# Core functionality from the original script
def analyze_video(video_url):
    """
    Analyzes a video using Google's Gemini model.
    Returns a dictionary with analysis results or error information.
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    temp_file = None
    temp_file_path = None
    analysis_result_text = ""

    try:
        # Download the video from the URL
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        video_bytes = response.content

        # Create a temporary file and write the video content to it
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_file.write(video_bytes)
        temp_file_path = temp_file.name
        temp_file.close()

        # Upload the temporary video file
        files = [
            client.files.upload(file=temp_file_path),
        ]

        # Check the file's state and wait until it's ACTIVE
        uploaded_file = files[0]
        max_attempts = 30
        attempt = 1
        
        while attempt <= max_attempts:
            file_info = client.files.get(name=uploaded_file.name)
            file_state = file_info.state

            if file_state == "ACTIVE":
                break
            elif file_state == "PROCESSING":
                time.sleep(5)
                attempt += 1
            else:
                raise Exception(f"File processing failed. State: {file_state}")

        if attempt > max_attempts:
            raise Exception("Timeout: File did not reach ACTIVE state within the allowed time.")

        # Proceed with the analysis
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

        # Collect the complete response
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        for chunk in response_stream:
            analysis_result_text += chunk.text

        # Try to parse the result as JSON
        cleaned_text = analysis_result_text.strip().strip('```json').strip('```')
        parsed_result = json.loads(cleaned_text)
        return {"status": "success", "analysis": parsed_result}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}

    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass

# API endpoint
@app.post("/analyze_videos", response_model=List[VideoAnalysisResult])
async def analyze_videos(request: VideoRequest, api_key: str = Depends(get_api_key)):
    """
    Analyze a list of videos using the Gemini AI model
    
    - Requires an API key in the X-API-Secret header
    - Accepts a JSON list of video URLs
    - Returns analysis results for each video
    """
    results = []
    
    for url in request.urls:
        result = analyze_video(url)
        results.append({"url": url, **result})
    
    return results

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)},
    )

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
```

### Requirements

Create a `requirements.txt` file:

```
fastapi==0.103.1
uvicorn==0.23.2
google-generativeai==0.3.1
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.4.2
python-multipart==0.0.6
```

### Environment Variables

Create an `.env.example` file:

```
# API configuration
API_SECRET=your_api_secret_here

# Gemini API configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

## Part 2: Deploying to Render.com

Follow these steps to deploy your FastAPI application to Render.com:

1. **Push your code to GitHub**
   - Create a new GitHub repository
   - Push your code to the repository

2. **Create a new Web Service on Render**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New" and select "Web Service"
   - Connect your GitHub repository
   - Select the repository for deployment

3. **Configure the Web Service**
   - **Name**: Choose a name for your service 
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   - In the "Environment" section, add these variables:
     - `API_SECRET`: Your chosen API secret key
     - `GEMINI_API_KEY`: Your Google Gemini API key

5. **Deploy Your Service**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

Your FastAPI Gemini Video Analysis API will be available at `https://your-service-name.onrender.com`.

## Testing the Deployed API

Use a tool like cURL or Postman to test the API:

```bash
curl -X POST \
  https://your-service-name.onrender.com/analyze_videos \
  -H 'X-API-Secret: your_api_secret_here' \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": [
      "https://example.com/video1.mp4",
      "https://example.com/video2.mp4"
    ]
  }'
```

## Deployment Tips

1. **Scaling**: Render's free tier has limitations. For production use, consider upgrading to a paid plan.

2. **Timeout**: Video analysis can be time-intensive. Render might timeout for long-running requests on the free tier. Consider implementing background processing for production.

3. **Monitoring**: Use Render's built-in logs to debug issues.

4. **Custom Domains**: Set up a custom domain for your API in Render's dashboard if needed.

5. **Continuous Deployment**: Render automatically deploys new versions when you push to your repository.

## Useful Render Commands

Render's platform handles most deployment tasks automatically, but you can use their CLI for advanced operations:

```bash
# Install Render CLI (if needed)
npm install -g @render/cli

# Login to Render
render login

# View logs for your service
render logs your-service-name
```

---

By following this guide, you'll have successfully converted the Gemini video analysis script into a secure, deployable FastAPI application on Render.com. 