#!/usr/bin/env python3
"""
Generate images using Google's Gemini image generation model.
Supports both text-to-image and image-to-image generation.
Requires: google-genai, python-dotenv
Auth: GOOGLE_APPLICATION_CREDENTIALS env var pointing to service account JSON
"""

import argparse
import base64
import mimetypes
import os
import sys
import tempfile
from pathlib import Path
from typing_extensions import override

from dotenv import load_dotenv
from google import genai
from google.genai import types


def load_image_as_part(image_path: str) -> types.Part:
    """Load an image file and return it as a Gemini Part.

    Args:
        image_path: Path to the image file

    Returns:
        types.Part containing the image data
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Determine mime type
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        # Default to png if we can't determine
        mime_type = "image/png"

    # Read and encode image
    image_bytes = path.read_bytes()

    return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)


def generate_image(
    prompt: str,
    input_image: str | None = None,
    output_path: str | None = None,
    aspect_ratio: str = "16:9",
    image_size: str = "2K",
) -> str:
    """Generate an image from a text prompt and optionally an input image.

    Args:
        prompt: Text description of the image to generate or transformation to apply
        input_image: Optional path to an input image for image-to-image generation
        output_path: Where to save the image. If None, saves to temp file.
        aspect_ratio: Image aspect ratio (e.g., "16:9", "1:1", "9:16")
        image_size: Image size ("1K", "2K")

    Returns:
        Path to the saved image file
    """
    load_dotenv(override=True)

    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get(
        "CLOUDSDK_CORE_PROJECT"
    )
    if not project:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT or CLOUDSDK_CORE_PROJECT env var required"
        )

    client = genai.Client(
        vertexai=True,
        project=project,
        location="global",
    )

    model = "gemini-3-pro-image-preview"  # Image generation model

    # Build parts list - include input image if provided
    parts = []
    if input_image:
        parts.append(load_image_as_part(input_image))
    parts.append(types.Part.from_text(text=prompt))

    contents = [types.Content(role="user", parts=parts)]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["IMAGE"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            output_mime_type="image/png",
        ),
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    if response.candidates is None:
        print(
            f"DEBUG: Response has no candidates. Full response: {response}",
            file=sys.stderr,
        )
        raise RuntimeError(
            "Model returned no candidates. This could be due to safety filters or model refusal."
        )

    # Extract image from response
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type

                    # Determine file extension from mime type
                    ext = ".png"
                    if mime_type == "image/jpeg":
                        ext = ".jpg"
                    elif mime_type == "image/webp":
                        ext = ".webp"

                    # Determine output path
                    if output_path:
                        save_path = Path(output_path)
                        if save_path.suffix == "":
                            save_path = save_path.with_suffix(ext)
                    else:
                        fd, temp_path = tempfile.mkstemp(
                            suffix=ext, prefix="gemini_image_"
                        )
                        os.close(fd)
                        save_path = Path(temp_path)

                    # Decode and save
                    if isinstance(image_data, str):
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = image_data

                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    save_path.write_bytes(image_bytes)

                    print(f"Image saved to: {save_path.absolute()}")
                    return str(save_path.absolute())

    raise RuntimeError("No image found in response")


def main():
    parser = argparse.ArgumentParser(description="Generate images with Gemini")
    parser.add_argument("prompt", help="Text description of the image to generate")
    parser.add_argument(
        "-i", "--input", help="Input image path for image-to-image generation"
    )
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    parser.add_argument(
        "--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)"
    )
    parser.add_argument("--size", default="2K", choices=["1K", "2K"], help="Image size")

    args = parser.parse_args()

    try:
        path = generate_image(
            prompt=args.prompt,
            input_image=args.input,
            output_path=args.output,
            aspect_ratio=args.aspect_ratio,
            image_size=args.size,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
