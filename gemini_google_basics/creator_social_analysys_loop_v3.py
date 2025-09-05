"""
Batch video analysis to JSON (Gemini).

- Iterates over all videos in a given folder (one creator).
- Uploads each video, waits until ACTIVE, and asks Gemini to return a single JSON object per video.
- Aggregates all objects into one JSON array saved at ./outputs/<creator>/<creator>_analysis.json

Usage:
  export GEMINI_API_KEY=your_key
  python creator_social_analysys_loop_v2.py \
    --folder ./videos/creator_alex \
    --creator alex \
    --model gemini-2.5-flash

Optional:
  --extra "Focus on hooks and CTAs."
"""

import os
import time
import argparse
import json
import re
from pathlib import Path
from typing import Optional, List

from google import genai
from google.genai import types

# -------------------------
# Defaults
# -------------------------
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
VIDEO_EXTS = {".mp4", ".mov", ".m4v"}
OUTPUT_ROOT = Path("./outputs")

# -------------------------
# Base Prompt (JSON output)
# -------------------------
BASE_ANALYSIS_PROMPT = """
You are a Senior Short-Form Content Strategist. Analyze this single video and return EXACTLY ONE JSON object (no prose, no markdown fences) with the following keys:

{
  "video_filename": string,
  "likes": number | null,
  "saves": number | null,
  "number_of_comments": number | null,
  "shares": number | null,
  "hook_analysis": string,
  "visual_style": string,
  "call_to_action": string,
  "key_insights": string,
  "format_type": string,
  "estimated_topic": string,
  "detected_language": string,
  "posting_time_if_visible": string | null,
  "views_if_visible": number | null
}

Rules:
- Output ONLY valid JSON for a single object. No code fences (e.g., ```json), no explanations, no trailing commas.
- Use numbers (no commas or units). If a number is unknown, use null.
- Keep text fields concise but specific.
"""

# -------------------------
# Helpers
# -------------------------
def _require_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in environment")
    return api_key

def _is_video_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in VIDEO_EXTS

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

def _list_videos(folder: Path) -> List[Path]:
    files = [p for p in sorted(folder.iterdir()) if _is_video_file(p)]
    if not files:
        raise FileNotFoundError(f"No video files found in: {folder}")
    return files

def _ensure_creator_outdir(creator: str) -> Path:
    outdir = OUTPUT_ROOT / creator
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir

# -------------------------
# Core: analyze single video -> JSON dict
# -------------------------
def analyze_video_to_json(
    client: genai.Client,
    video_path: Path,
    model: str,
    base_prompt: str,
    extra_input: Optional[str] = None,
    stream_to_stdout: bool = True,
) -> dict:
    """
    Uploads a video, waits until ACTIVE, asks Gemini for ONE JSON object,
    optionally streams output, and returns it parsed as a Python dict.
    """
    print(f"\nUploading: {video_path.name}")
    uploaded = client.files.upload(file=str(video_path))
    print(f"Uploaded file name: {uploaded.name} (state={uploaded.state})")

    file_info = _wait_for_active(client, uploaded.name)

    # Prepend video filename context to ensure the first column can be filled reliably
    video_context = f"The video filename is: {video_path.name}."

    parts = [
        types.Part.from_uri(file_uri=file_info.uri, mime_type=file_info.mime_type),
        types.Part.from_text(text=(video_context + "\n\n" + base_prompt.strip())),
    ]
    if extra_input:
        parts.append(types.Part.from_text(text=extra_input.strip()))

    contents = [types.Content(role="user", parts=parts)]

    tools = [types.Tool(googleSearch=types.GoogleSearch())]
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        tools=tools,
    )

    print("Starting analysis (streaming JSON)...")
    chunks: List[str] = []
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    ):
        if chunk.text:
            chunks.append(chunk.text)
            if stream_to_stdout:
                print(chunk.text, end="")
    print()  # newline

    # Combine and sanitize
    raw_text = "".join(chunks).strip()
    # Remove code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`\n ")
        # Remove a leading language hint like 'json' if present
        if raw_text.lower().startswith("json\n"):
            raw_text = raw_text.split("\n", 1)[1]
        if raw_text.lower().startswith("json "):
            raw_text = raw_text[5:]

    # Try to extract a JSON object substring heuristically
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        raise ValueError("Model did not return a JSON object.")
    json_str = match.group(0)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # Attempt a second pass by collapsing whitespace/newlines
        compact = " ".join(json_str.splitlines())
        data = json.loads(compact)
    # Ensure filename is set
    data.setdefault("video_filename", video_path.name)
    return data

# -------------------------
# Batch runner
# -------------------------
def run_folder(
    folder: Path,
    creator: str,
    model: str = DEFAULT_MODEL,
    extra_input: Optional[str] = None
):
    api_key = _require_api_key()
    client = genai.Client(api_key=api_key)

    videos = _list_videos(folder)
    outdir = _ensure_creator_outdir(creator)

    print(f"Found {len(videos)} videos in {folder}")
    json_path = outdir / f"{creator}_analysis.json"
    print(f"Aggregated JSON will be written to: {json_path.resolve()}")

    results: List[dict] = []

    for idx, v in enumerate(videos, 1):
        print(f"\n[{idx}/{len(videos)}] Processing {v.name} ...")
        try:
            obj = analyze_video_to_json(
                client=client,
                video_path=v,
                model=model,
                base_prompt=BASE_ANALYSIS_PROMPT,
                extra_input=extra_input,
                stream_to_stdout=True,
            )
            results.append(obj)
            # Write the array incrementally (safe on long runs)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"[OK] Appended JSON object for → {v.name}")
        except Exception as e:
            print(f"[ERROR] {v.name}: {e}")
            continue
        time.sleep(0.8)

# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Batch Gemini video analysis to JSON (one object per video).")
    parser.add_argument("--folder", type=str, required=True, help="Path to the creator's folder of videos.")
    parser.add_argument("--creator", type=str, required=True, help="Creator handle/name used for output folder.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Gemini model (default: {DEFAULT_MODEL})")
    parser.add_argument("--extra", type=str, default=None, help="Optional extra instruction appended to the prompt.")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found or not a directory: {folder}")

    run_folder(
        folder=folder,
        creator=args.creator,
        model=args.model,
        extra_input=args.extra
    )

if __name__ == "__main__":
    main()