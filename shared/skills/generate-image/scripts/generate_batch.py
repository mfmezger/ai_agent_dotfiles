# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "python-dotenv",
#     "typer",
# ]
# ///
"""Batch image generation using Google's Gemini model.

Generates multiple images in parallel with configurable concurrency.

Usage:
    uv run generate_batch.py "A sunset over mountains" "A robot in a garden"
    uv run generate_batch.py --from-file prompts.txt -o ./images
    uv run generate_batch.py --max-concurrent 2 "prompt1" "prompt2" "prompt3"
"""

import asyncio
import base64
import mimetypes
import os
import sys
import tempfile
from pathlib import Path

import typer
from dotenv import load_dotenv
from google import genai
from google.genai import types

app = typer.Typer(help="Generate multiple images in parallel using Gemini.")


def _build_config(aspect_ratio: str, image_size: str) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["IMAGE"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            output_mime_type="image/png",
        ),
    )


def _load_image_as_part(image_path: str) -> types.Part:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "image/png"
    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type)


def _extract_image(response, save_path: Path) -> Path:
    if response.candidates is None:
        raise RuntimeError("Model returned no candidates (safety filters or model refusal).")

    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type

                    ext = ".png"
                    if mime_type == "image/jpeg":
                        ext = ".jpg"
                    elif mime_type == "image/webp":
                        ext = ".webp"

                    if save_path.suffix == "":
                        save_path = save_path.with_suffix(ext)

                    if isinstance(image_data, str):
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = image_data

                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    save_path.write_bytes(image_bytes)
                    return save_path

    raise RuntimeError("No image found in response")


async def _generate_one(
    client: genai.Client,
    index: int,
    prompt: str,
    output_path: Path,
    input_image: str | None,
    aspect_ratio: str,
    image_size: str,
    semaphore: asyncio.Semaphore,
) -> tuple[int, str, Path | None, str | None]:
    """Generate a single image. Returns (index, prompt, path_or_none, error_or_none)."""
    async with semaphore:
        try:
            parts: list[types.Part] = []
            if input_image:
                parts.append(_load_image_as_part(input_image))
            parts.append(types.Part.from_text(text=prompt))

            contents = [types.Content(role="user", parts=parts)]
            config = _build_config(aspect_ratio, image_size)

            response = await client.aio.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=contents,
                config=config,
            )

            saved = _extract_image(response, output_path)
            return (index, prompt, saved, None)
        except Exception as e:
            return (index, prompt, None, str(e))


def _resolve_output_path(output_dir: Path | None, index: int, prompt: str) -> Path:
    """Build output file path for a given prompt index."""
    # Sanitize prompt into a short filename slug
    slug = prompt[:40].strip().replace(" ", "_")
    slug = "".join(c for c in slug if c.isalnum() or c in "_-")
    filename = f"{index:03d}_{slug}.png"

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / filename

    fd, temp_path = tempfile.mkstemp(suffix=".png", prefix=f"gemini_batch_{index:03d}_")
    os.close(fd)
    return Path(temp_path)


async def _run_batch(
    prompts: list[str],
    output_dir: Path | None,
    input_image: str | None,
    aspect_ratio: str,
    image_size: str,
    max_concurrent: int,
) -> None:
    load_dotenv(override=True)

    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("CLOUDSDK_CORE_PROJECT")
    if not project:
        typer.echo("Error: GOOGLE_CLOUD_PROJECT or CLOUDSDK_CORE_PROJECT env var required", err=True)
        raise typer.Exit(1)

    client = genai.Client(vertexai=True, project=project, location="global")
    semaphore = asyncio.Semaphore(max_concurrent)

    total = len(prompts)
    typer.echo(f"Generating {total} image(s) with max {max_concurrent} concurrent requests...\n")

    tasks = [
        _generate_one(
            client=client,
            index=i,
            prompt=prompt,
            output_path=_resolve_output_path(output_dir, i, prompt),
            input_image=input_image,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            semaphore=semaphore,
        )
        for i, prompt in enumerate(prompts)
    ]

    succeeded = 0
    failed = 0

    for coro in asyncio.as_completed(tasks):
        index, prompt, path, error = await coro
        short_prompt = prompt[:60] + ("..." if len(prompt) > 60 else "")
        if error:
            failed += 1
            typer.echo(f"  FAIL [{index + 1}/{total}] \"{short_prompt}\"\n         {error}", err=True)
        else:
            succeeded += 1
            typer.echo(f"  OK   [{index + 1}/{total}] \"{short_prompt}\"\n         -> {path}")

    typer.echo(f"\nDone: {succeeded} succeeded, {failed} failed out of {total} total.")
    if failed > 0:
        raise typer.Exit(1)


@app.command()
def generate(
    prompts: list[str] = typer.Argument(default=None, help="One or more text prompts to generate images for."),
    from_file: Path = typer.Option(None, "--from-file", "-f", help="Read prompts from a text file (one per line)."),
    output_dir: Path = typer.Option(None, "--output-dir", "-o", help="Directory to save images. Defaults to temp files."),
    input_image: str = typer.Option(None, "--input-image", "-i", help="Input image path for image-to-image generation (applied to all prompts)."),
    aspect_ratio: str = typer.Option("16:9", "--aspect-ratio", "-a", help="Aspect ratio: 16:9, 1:1, 9:16"),
    image_size: str = typer.Option("2K", "--size", "-s", help="Image size: 1K or 2K"),
    max_concurrent: int = typer.Option(4, "--max-concurrent", "-c", help="Max parallel requests (semaphore limit)."),
) -> None:
    """Generate multiple images in parallel using Google Gemini."""
    all_prompts: list[str] = []

    if from_file:
        if not from_file.exists():
            typer.echo(f"Error: File not found: {from_file}", err=True)
            raise typer.Exit(1)
        lines = from_file.read_text().strip().splitlines()
        all_prompts.extend(line.strip() for line in lines if line.strip() and not line.startswith("#"))

    if prompts:
        all_prompts.extend(prompts)

    if not all_prompts:
        typer.echo("Error: No prompts provided. Pass prompts as arguments or use --from-file.", err=True)
        raise typer.Exit(1)

    asyncio.run(
        _run_batch(
            prompts=all_prompts,
            output_dir=output_dir,
            input_image=input_image,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            max_concurrent=max_concurrent,
        )
    )


if __name__ == "__main__":
    app()
