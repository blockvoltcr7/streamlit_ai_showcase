"""
Batch video analysis to CSV (Gemini).

- Iterates over all videos in a given folder (one creator).
- Uploads each video, waits until ACTIVE, and asks Gemini to return a single CSV row per video.
- Aggregates all rows into one CSV file saved at ./outputs/<creator>/<creator>_analysis.csv

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
import csv
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
# Base Prompt (CSV output)
# -------------------------
BASE_ANALYSIS_PROMPT = """
You are a Senior Short-Form Content Strategist. Analyze this single video and return EXACTLY ONE CSV row (no header, no code fences, no extra text) with the following columns in order:

video_filename,
likes,
saves,
number_of_comments,
shares,
hook_analysis,
visual_style,
call_to_action,
key_insights,
format_type,
estimated_topic,
detected_language,
posting_time_if_visible,
views_if_visible

Rules:
- Return ONLY one line of CSV, comma-separated. Do NOT include a header, code fences, language hints (e.g., ```csv), or any extra text before/after the row.
- Numeric columns (likes, saves, number_of_comments, shares, views_if_visible) must be plain digits only (e.g., 1234) or left empty if unknown. Never include commas, units, or text in numeric fields.
- ALL non-numeric text columns must be enclosed in double quotes. If the text itself contains double quotes, escape them by doubling (e.g., He said ""hi"").
- For text fields (hook_analysis, visual_style, call_to_action, key_insights), be concise but specific.
- If a value is unknown or not visible, leave that field empty (i.e., two consecutive commas).
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
# Core: analyze single video -> CSV row (string)
# -------------------------
def analyze_video_to_csv_row(
    client: genai.Client,
    video_path: Path,
    model: str,
    base_prompt: str,
    extra_input: Optional[str] = None,
    stream_to_stdout: bool = True,
) -> str:
    """
    Uploads a video, waits until ACTIVE, asks Gemini for ONE CSV row,
    optionally streams output, and returns the aggregated CSV line as a string.
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

    print("Starting analysis (streaming CSV row)...")
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

    # Combined CSV row text
    csv_text = "".join(chunks).strip()

    # Basic sanitization: remove code fences or accidental headers
    if csv_text.startswith("```"):
        csv_text = csv_text.strip("`\n ")
        # Strip a leading 'csv' language hint if present
        if csv_text.lower().startswith("csv\n"):
            csv_text = csv_text.split("\n", 1)[1]
        if csv_text.lower().startswith("csv "):
            csv_text = csv_text[4:]
    # Ensure it's a single line
    csv_text = " ".join(csv_text.splitlines())
    return csv_text

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
    csv_path = outdir / f"{creator}_analysis.csv"
    print(f"Aggregated CSV will be written to: {csv_path.resolve()}")

    # Prepare CSV header (we control this locally and ask the model to return only rows)
    header = [
        "video_filename",
        "likes",
        "saves",
        "number_of_comments",
        "shares",
        "hook_analysis",
        "visual_style",
        "call_to_action",
        "key_insights",
        "format_type",
        "estimated_topic",
        "detected_language",
        "posting_time_if_visible",
        "views_if_visible",
    ]

    # Create/overwrite and write header
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for idx, v in enumerate(videos, 1):
        print(f"\n[{idx}/{len(videos)}] Processing {v.name} ...")
        try:
            row_text = analyze_video_to_csv_row(
                client=client,
                video_path=v,
                model=model,
                base_prompt=BASE_ANALYSIS_PROMPT,
                extra_input=extra_input,
                stream_to_stdout=True,
            )
            # Append the row to the CSV file
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                f.write(row_text + "\n")
            print(f"[OK] Appended CSV row for → {v.name}")
        except Exception as e:
            print(f"[ERROR] {v.name}: {e}")
            continue
        time.sleep(0.8)

# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Batch Gemini video analysis to CSV (one row per video).")
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