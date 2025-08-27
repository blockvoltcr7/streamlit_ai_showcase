"""Video growth-phase analysis using Gemini.

Refactored to follow the same conventions/patterns as `gemini_video_analysis.py`:
 - Explicit video file upload with polling until ACTIVE
 - Streaming response output
 - Clear status prints
 - Parameterized helper for optional extra user input

Usage:
  export GEMINI_API_KEY=your_key
  python gemini_video_analysis_content.py

Optional:
  from gemini_video_analysis_content import generate
  generate(video_path="carter-video-1.mp4", extra_input="Focus on hook evolution.")
"""

import os
import time
from typing import Optional
from google import genai
from google.genai import types



MODEL = "gemini-2.5-flash"
VIDEO_PATH = "ai-self-help-wisdom-tech.mp4"

BASE_ANALYSIS_PROMPT = """
Analyze this screen recording of a creator's last 30 Instagram posts to identify content patterns and performance metrics. I need specific data to fill out a content analysis framework.

Please provide:

## CONTENT TOPICS ANALYSIS
- List the top 3-5 most common topics/themes across all 30 posts
- Count how many posts fall into each topic category
- Note any topic patterns or shifts over time

## FORMAT PERFORMANCE
- Count how many posts are: Reels, Static Posts, Carousels, IGTV
- Which format appears most frequently?
- Note any obvious performance differences between formats (based on visible engagement)

## ENGAGEMENT PATTERNS
- For posts where engagement numbers are visible, note the likes/comments/views
- Identify the 3-5 highest performing posts and their topics/formats
- Calculate average engagement if enough data is visible
- Note any posts that seem to have significantly higher or lower engagement

## POSTING FREQUENCY
- How many posts were made in the time period shown?
- Are there patterns in posting frequency (daily, every few days, clusters)?
- Any gaps or periods of increased activity?

## PERFORMANCE INSIGHTS
- Which days of the week appear most frequently for posts?
- Do certain topics consistently get higher engagement?
- Are there any obvious patterns in what works vs what doesn't?

## VISUAL/STYLE CONSISTENCY
- How consistent is the visual style across posts?
- Any changes in production quality or aesthetic?
- Consistent use of text overlays, colors, or branding elements?

suggest a return format and think hard about the output we should return
"""


def _wait_for_active(client: genai.Client, file_name: str, max_attempts: int = 30, interval_sec: int = 5):
    """Poll the file status until ACTIVE or raise on timeout/failure."""
    attempt = 1
    while attempt <= max_attempts:
        info = client.files.get(name=file_name)
        state = info.state
        if state == "ACTIVE":
            print("File is ACTIVE. Proceeding...")
            return info
        if state == "PROCESSING":
            print(f"Attempt {attempt}/{max_attempts}: still PROCESSING – waiting {interval_sec}s...")
            time.sleep(interval_sec)
            attempt += 1
            continue
        raise RuntimeError(f"File entered unexpected state: {state}")
    raise TimeoutError("Timed out waiting for file to become ACTIVE")


def generate(video_path: str = VIDEO_PATH, extra_input: Optional[str] = None, model: str = MODEL):
    """Run growth-phase analysis on the provided video.

    Args:
        video_path: Path to the mp4 file to upload.
        extra_input: Optional additional instruction appended as a separate user part.
        model: Gemini model name.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in environment")

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    client = genai.Client(api_key=api_key)

    print(f"Uploading video: {video_path} ...")
    uploaded = client.files.upload(file=video_path)
    print(f"Uploaded file name: {uploaded.name} (state={uploaded.state})")
    file_info = _wait_for_active(client, uploaded.name)

    # Build prompt contents
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=file_info.uri,
                    mime_type=file_info.mime_type,
                ),
            ],
        ),
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=BASE_ANALYSIS_PROMPT)],
        ),
    ]

    if extra_input:
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=extra_input.strip())],
            )
        )

    tools = [types.Tool(googleSearch=types.GoogleSearch())]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        tools=tools,
    )

    print("Starting growth-phase content analysis (streaming)...")
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    ):
        # Stream incremental text pieces
        if chunk.text:
            print(chunk.text, end="")
    print()  # final newline


if __name__ == "__main__":
    generate()
