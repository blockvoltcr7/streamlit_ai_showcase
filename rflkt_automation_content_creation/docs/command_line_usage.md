# RFLKT Automation Content Creation - Command Line Usage

This document explains the command line arguments available for the `rflkt_mvp.py` script and how to use them effectively.

## Available Command Line Arguments

The script accepts the following command line arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--video_url` | string | `https://tpfitionfrabfzlcapum.supabase.co/storage/v1/object/public/videos/testing/2025-04-25-16246.mp4` | URL of the video to process |
| `--generate_voiceover` | flag | `False` | Enable voiceover generation from transcript |
| `--enhance_transcript` | flag | `False` | Enable transcript enhancement with OpenAI (only relevant when voiceover is enabled) |

## Basic Usage

### Process a Video with Default Settings

This will process the default video without generating a voiceover:

```bash
python rflkt_automation_content_creation/rflkt_mvp.py
```

### Process a Custom Video

To process a specific video:

```bash
python rflkt_automation_content_creation/rflkt_mvp.py --video_url https://example.com/path/to/your/video.mp4
```

### Generate a Voiceover

To enable voiceover generation:

```bash
python rflkt_automation_content_creation/rflkt_mvp.py --generate_voiceover
```

### Generate an Enhanced Voiceover

To generate a voiceover with OpenAI-enhanced transcript (for better quality with pauses, emphasis, etc.):

```bash
python rflkt_automation_content_creation/rflkt_mvp.py --generate_voiceover --enhance_transcript
```

### Full Example with All Options

```bash
python rflkt_automation_content_creation/rflkt_mvp.py --video_url https://example.com/path/to/your/video.mp4 --generate_voiceover --enhance_transcript
```

## Notes on Voiceover Enhancement

When the `--enhance_transcript` flag is used:

1. The script will use OpenAI to enhance the transcript with ElevenLabs voice control tags
2. These enhancements include appropriate pauses, emphasis, and pacing based on the emotional context of each scene
3. The enhanced transcript is saved to the output directory for reference
4. The ElevenLabs API will use the enhanced transcript to generate more natural-sounding audio
5. Note that using this option will consume OpenAI API credits
6. The multilingual model (`eleven_multilingual_v2`) is used for enhanced transcripts to better handle the control tags

## Output

The script generates:

1. Scene analysis JSON file in the `output` directory
2. Generated images in the `output_images` directory
3. Voiceover audio file in the `audio` directory (when `--generate_voiceover` is enabled)
4. Enhanced transcript file in the `output` directory (when `--enhance_transcript` is enabled)
5. Complete pipeline results JSON file in the `output` directory

## Requirements

Ensure all required API keys are set in your `.env` file:
- `GEMINI_API_KEY` - For video analysis
- `OPENAI_API_KEY` - For image prompt generation and transcript enhancement
- `ELEVENLABS_API_KEY` - For voiceover generation
- Replicate API key in your environment - For image generation 