# RFLKT Automation Content Creation - Command Line Usage

This document explains the command line arguments available for the `rflkt_mvp.py` script and how to use them effectively.

## Available Command Line Arguments

The script accepts the following command line arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--video_url` | string | *Required* | URL of the video to process (required) |
| `--generate_voiceover` | flag | `False` | Enable voiceover generation from transcript |
| `--enhance_transcript` | flag | `False` | Enable transcript enhancement with ElevenLabs controls (only relevant when voiceover is enabled) |
| `--no_reword` | flag | `False` | Disable transcript rewording (rewording is enabled by default) |

## Basic Usage

### Process a Video

The `--video_url` argument is required for all operations:

```bash
python rflkt_automation_content_creation/rflkt_mvp.py --video_url https://example.com/path/to/your/video.mp4
```

### Generate a Voiceover

To enable voiceover generation:

```bash
python rflkt_mvp.py --video_url https://example.com/path/to/your/video.mp4 --generate_voiceover
```

By default, this will reword the transcript to create a unique voiceover while preserving the same meaning and length.

### Generate a Voiceover Without Rewording

If you want to use the exact original transcript without rewording:

```bash
python rflkt_mvp.py --video_url https://example.com/path/to/your/video.mp4 --generate_voiceover --no_reword
```

### Generate an Enhanced Voiceover with rewording the transcript

To generate a voiceover with ElevenLabs voice controls (for better quality with pauses, emphasis, etc.):

This will both reword the transcript (by default) and add voice controls.


```bash
python rflkt_mvp.py --video_url https://example.com/path/to/your/video.mp4 --generate_voiceover --enhance_transcript
```


## Transcript Processing

The script provides two independent transcript processing features:

1. **Transcript Rewording** (enabled by default)
   - Uses OpenAI to subtly reword the transcript while preserving meaning and length
   - Creates a unique voiceover each time the script runs
   - Disable with `--no_reword` if you want to use the exact original wording

2. **Voice Control Enhancement** (opt-in with `--enhance_transcript`)
   - Adds ElevenLabs voice controls like pauses, emphasis, and intonation
   - Improves the natural sound and emotional impact of the voiceover
   - Based on the emotional context from scene analysis

These features can be used independently or together:
- Reword only: Default behavior with `--generate_voiceover`
- Enhance only: `--generate_voiceover --enhance_transcript --no_reword`
- Both: `--generate_voiceover --enhance_transcript` (default)
- Neither: `--generate_voiceover --no_reword` (uses original transcript exactly)

## Output

The script generates:

1. Scene analysis JSON file in the `output/analysis` directory
2. Generated images in the `output/images` directory
3. Voiceover audio file in the `output/audio` directory (when `--generate_voiceover` is enabled)
4. Enhanced and/or reworded transcript files in the `output/analysis` directory (when those features are enabled)
5. Complete pipeline results JSON file in the output directory

## Requirements

Ensure all required API keys are set in your `.env` file:
- `GEMINI_API_KEY` - For video analysis
- `OPENAI_API_KEY` - For image prompt generation and transcript processing
- `ELEVENLABS_API_KEY` - For voiceover generation
- Replicate API key in your environment - For image generation 