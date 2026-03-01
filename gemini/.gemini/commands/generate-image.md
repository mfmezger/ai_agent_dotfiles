---
description: This skill should be used when the user asks to "generate an image", "create a picture", "make an image of", "edit this image", "transform this photo", or needs AI-generated visual content using Google's Gemini image generation model.
---

# Image Generation with Gemini

Generate images using Google's Gemini image generation model via Vertex AI. Supports both text-to-image and image-to-image generation.

## Prerequisites

Environment variables (can be in `.env` file in working directory):

- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON file
- `GOOGLE_CLOUD_PROJECT` - GCP project ID

## Usage

Run the generation script using `uvx`:

```bash
# Text-to-image generation
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "PROMPT"

# Image-to-image generation (with input image)
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "PROMPT" -i /path/to/input/image.png
```

### Options

| Flag                | Description                               | Default   |
| ------------------- | ----------------------------------------- | --------- |
| `-i, --input PATH`  | Input image for image-to-image generation | None      |
| `-o, --output PATH` | Where to save the image                   | Temp file |
| `--aspect-ratio`    | "16:9", "1:1", "9:16"                     | "16:9"    |
| `--size`            | "1K" or "2K"                              | "2K"      |

### Examples

```bash
# Basic text-to-image - saves to temp file, prints path
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "A serene mountain landscape at sunset"

# Save to specific location
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "A cute robot" -o ./robot.png

# Square format
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "Abstract art" --aspect-ratio 1:1

# High resolution
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "Detailed cityscape" --size 2K

# Image-to-image: Transform an existing image
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "Make this scene nighttime with stars" -i ./daytime_photo.jpg

# Image-to-image: Add elements to an image
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "Add a rainbow in the sky" -i ./landscape.png -o ./landscape_with_rainbow.png

# Image-to-image: Style transfer
uvx --with google-genai --with python-dotenv python ~/.claude/skills/generate-image/scripts/generate.py "Convert to watercolor painting style" -i ./photo.jpg
```

## Workflow

1. Run the script with user's prompt (and optionally an input image)
2. Script prints the saved image path
3. Use Read tool to view the generated image
4. Move/copy to user-specified location if requested

## Error Handling

- Missing env vars: Script errors with clear message about which variable is needed
- Input image not found: Script errors if the specified input image path doesn't exist
- Generation failure: Script returns non-zero exit code with error details
