# Guide: Using `creator_social_analysys_loop.py`

Batch-analyze a folder of videos and output one Markdown report per video.

## Folder structure

Place everything under `gemini_google_basics/`. You already created `videos/`.

- **Required**
  - `gemini_google_basics/`
    - `creator_social_analysys_loop.py`
    - `videos/`               ← put your input videos here
    - `outputs/`              ← created automatically on first run
- **Recommended (per-creator organization)**
  - `gemini_google_basics/videos/`
    - `creator_alex/`
      - `video1.mp4`
      - `video2.mov`
    - `creator_bailey/`
      - `clip_a.m4v`

Supported video extensions: `.mp4`, `.mov`, `.m4v`.

## Prerequisites

- Python environment with the dependencies from the repo `requirements.txt` installed (notably `google-genai`).
- Environment variables:
  - `GEMINI_API_KEY` (required)
  - `GEMINI_MODEL` (optional; defaults to `gemini-2.5-flash`)

Example:
```bash
export GEMINI_API_KEY="YOUR_API_KEY"
# optionally:
export GEMINI_MODEL="gemini-2.5-flash"
```

## How it works (high level)

- Iterates all videos in the `--folder` you pass.
- For each video:
  - Uploads to Gemini and polls until the file is `ACTIVE`.
  - Streams analysis to stdout as it’s generated.
  - Saves the full Markdown to `./outputs/<creator>/<video-stem>.md`.

Core functions: `analyze_video_to_markdown()` and `run_folder()` in `gemini_google_basics/creator_social_analysys_loop.py`.

## Run commands

Run from inside `gemini_google_basics/` so relative paths resolve correctly.

- **Single creator folder**
```bash
python creator_social_analysys_loop.py \
  --folder ./videos/creator_alex \
  --creator alex
```

- **Specify a model**
```bash
python creator_social_analysys_loop.py \
  --folder ./videos/creator_alex \
  --creator alex \
  --model gemini-2.5-flash
```

- **Add extra prompt instructions**
```bash
python creator_social_analysys_loop.py \
  --folder ./videos/creator_alex \
  --creator alex \
  --extra "Focus on hooks and CTAs."
```

## Outputs

- Per-video Markdown is written to: `./outputs/<creator>/<video-stem>.md`
- Example:
  - Input: `./videos/creator_alex/opening_hook.mov`
  - Output: `./outputs/alex/opening_hook.md`

## Tips

- **Working directory**: Always run from `gemini_google_basics/`.
- **Re-runs**: If re-running often, consider cleaning existing `.md` files or add an `--overwrite` flag in the future.
- **Prompt**: The included prompt is a strategist-style Markdown report. If you prefer the research-heavy prompt from `gemini_video_analysis_content.py`, copy its `BASE_ANALYSIS_PROMPT` into this script.

## Troubleshooting

- **“GEMINI_API_KEY not set”**: Export the key as shown above.
- **“No video files found”**: Ensure the folder exists and files end with `.mp4/.mov/.m4v`.
- **Stuck on PROCESSING**: Large files may need more time; increase `max_attempts` or `interval_sec` in `_wait_for_active()`.

---

Note: The script filename uses `analysys` (intentional to match the file in this repo). If you rename the file to `creator_social_analysis_loop.py`, update your commands accordingly.
