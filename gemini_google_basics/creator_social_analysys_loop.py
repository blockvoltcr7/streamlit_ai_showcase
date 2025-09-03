"""
Batch video analysis to Markdown (Gemini).

- Iterates over all videos in a given folder (one creator).
- Uploads each video, waits until ACTIVE, and asks Gemini to return Markdown.
- Streams the model's output to stdout while also capturing it as a string.
- Writes one Markdown file per input video under ./outputs/<creator>/.

Usage:
  export GEMINI_API_KEY=your_key
  python gemini_video_analysis_markdown.py \
    --folder ./videos/creator_alex \
    --creator alex \
    --model gemini-2.5-flash

Optional:
  --extra "Focus on hooks and CTAs."
"""

import os
import time
import argparse
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
# Base Prompt
# -------------------------
BASE_ANALYSIS_PROMPT = """
You are a Senior Short-Form Content Strategist. Analyze this video post for creator research.

Return your entire analysis in well-structured **Markdown**, using informative section headings. Include any structure you deem helpful for strategy work (e.g., hooks, pacing, editing notes, captions/hashtag observations, CTA critique, cloneable patterns, A/B test ideas, risks/pitfalls). If a detail is unknown from the video, simply skip it—do not fabricate.

Do NOT return JSON—only Markdown.
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
# Core: analyze single video -> Markdown string
# -------------------------
def analyze_video_to_markdown(
    client: genai.Client,
    video_path: Path,
    model: str,
    base_prompt: str,
    extra_input: Optional[str] = None,
    stream_to_stdout: bool = True
) -> str:
    """
    Uploads a video, waits until ACTIVE, asks Gemini for Markdown,
    streams output, and returns the aggregated Markdown string.
    """
    print(f"\nUploading: {video_path.name}")
    uploaded = client.files.upload(file=str(video_path))
    print(f"Uploaded file name: {uploaded.name} (state={uploaded.state})")

    file_info = _wait_for_active(client, uploaded.name)

    parts = [
        types.Part.from_uri(file_uri=file_info.uri, mime_type=file_info.mime_type),
        types.Part.from_text(text=base_prompt.strip()),
    ]
    if extra_input:
        parts.append(types.Part.from_text(text=extra_input.strip()))

    contents = [types.Content(role="user", parts=parts)]

    # Optional tools (kept from your pattern)
    tools = [types.Tool(googleSearch=types.GoogleSearch())]
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        tools=tools,
    )

    print("Starting analysis (streaming Markdown)...")
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
    return "".join(chunks)

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
    print(f"Outputs will be written to: {outdir.resolve()}")

    for idx, v in enumerate(videos, 1):
        print(f"\n[{idx}/{len(videos)}] Processing {v.name} ...")
        try:
            md = analyze_video_to_markdown(
                client=client,
                video_path=v,
                model=model,
                base_prompt=BASE_ANALYSIS_PROMPT,
                extra_input=extra_input,
                stream_to_stdout=True,
            )
            # Write one .md per video
            outfile = outdir / f"{v.stem}.md"
            outfile.write_text(md, encoding="utf-8")
            print(f"[OK] Wrote Markdown → {outfile.name}")
        except Exception as e:
            print(f"[ERROR] {v.name}: {e}")
            # Continue to next file
            continue
        # Small delay to be gentle with the API
        time.sleep(0.8)

# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Batch Gemini video analysis to Markdown (one .md per video).")
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