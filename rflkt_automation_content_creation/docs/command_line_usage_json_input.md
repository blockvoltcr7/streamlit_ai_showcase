# RFLKT Automation Content Creation - Command Line Usage

This document describes how to use the RFLKT Automation Content Creation pipeline (`rflkt_mvp_json.py`) from the command line.

## Overview

The RFLKT Automation Content Creation pipeline processes JSON input to:
1. Generate high-contrast black and white monochrome illustrations based on scene descriptions
2. Enhance and reword transcripts (optional)
3. Generate voiceovers from transcripts using ElevenLabs (optional)

All outputs are saved to a unique timestamped directory for each run.

## Prerequisites

Before using this script, ensure you have the following environment variables set:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key (if generating voiceovers)

Required Python packages:
- openai
- replicate
- pydantic
- elevenlabs
- requests
- python-dotenv

## Command Line Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--json_file` | Path to JSON file with scene data | Either this or `--json_string` is required |
| `--json_string` | JSON string with scene data | Either this or `--json_file` is required |
| `--enhance_transcript` | Enable transcript enhancement with OpenAI | Optional (default: False) |
| `--generate_voiceover` | Generate voiceover from transcript | Optional (default: False) |
| `--no_reword` | Disable transcript rewording | Optional (default: False - rewording is enabled) |
| `--voice_id` | ElevenLabs voice ID to use | Optional (default: a9ldg2iPgaBn4VcYMJ4x) |

## Input JSON Format

The input JSON should have the following structure:

```json
{
  "full_transcript": "The complete transcript text for voiceover generation",
  "scenes": [
    {
      "scene_number": 1,
      "images": [
        {
          "image_number": 1,
          "visual_description": "Description of what should be in the image",
          "scene_context": "Context about the scene",
          "core_emotions": ["emotion1", "emotion2"],
          "scene_narrative": "Narrative description of the scene",
          "emotional_atmosphere": "Description of the emotional atmosphere",
          "technical_directives": "Technical details for image composition",
          "environment_elements": ["element1", "element2"]
        }
      ]
    }
  ]
}
```

## Usage Examples

### Process a JSON file and generate images only

```bash
python rflkt_mvp_json.py --json_file path/to/input.json
```

### Process a JSON file, generate images, and create a voiceover

```bash
python rflkt_mvp_json.py --json_file path/to/input.json --generate_voiceover
```

### Process a JSON string with enhanced transcript and voiceover

```bash
python rflkt_mvp_json.py --json_string '{"full_transcript": "This is the transcript text", "scenes": [...]}' --generate_voiceover --enhance_transcript
```

### Process a JSON file with a custom ElevenLabs voice

```bash
python rflkt_mvp_json.py --json_file path/to/input.json --generate_voiceover --voice_id your_voice_id_here
```

## Output

The script creates a unique output directory for each run with the format:
```
output_YYYYMMDD_HHMMSS_UUID/
├── analysis/        # Contains input JSON, processing results, and transcript files
├── images/          # Contains generated images
└── audio/           # Contains generated voiceover files
```

A complete results summary is saved to:
```
output_YYYYMMDD_HHMMSS_UUID/complete_pipeline_results.json
```

## Error Handling

- If both `--json_file` and `--json_string` are provided, the script will exit with an error
- If neither `--json_file` nor `--json_string` is provided, the script will exit with an error
- If `--generate_voiceover` is specified but no transcript is found in the JSON data, the script will skip voiceover generation
