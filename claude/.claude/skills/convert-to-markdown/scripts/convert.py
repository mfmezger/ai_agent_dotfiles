#!/usr/bin/env python3
"""
Convert documents to Markdown format.
Supports: PDF, DOCX, PPTX, XLSX, HTML, EPUB, images, Google Docs (via URL)

Uses markitdown as primary converter, pandoc as fallback.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from markitdown import MarkItDown


# Formats best handled by pandoc
PANDOC_FORMATS = {".epub", ".org", ".rst", ".tex", ".latex", ".odt", ".rtf"}

# Formats markitdown handles well
MARKITDOWN_FORMATS = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm", ".jpg", ".jpeg", ".png", ".gif", ".webp"}


def run_pandoc(input_path: Path) -> str | None:
    """Run pandoc to convert a file to markdown."""
    try:
        result = subprocess.run(
            ["pandoc", "-t", "markdown", "-o", "-", str(input_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return result.stdout
        print(f"Pandoc warning: {result.stderr}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("Pandoc not found, skipping pandoc conversion", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("Pandoc timed out", file=sys.stderr)
        return None


def run_markitdown(input_path: Path, enable_ocr: bool = False) -> str | None:
    """Run markitdown to convert a file to markdown."""
    try:
        md = MarkItDown(enable_vision=enable_ocr)
        result = md.convert(str(input_path))
        return result.text_content
    except Exception as e:
        print(f"Markitdown error: {e}", file=sys.stderr)
        return None


def extract_text_pdftotext(input_path: Path) -> str | None:
    """Extract text from PDF using pdftotext (poppler)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(input_path), "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def merge_extractions(text_content: str | None, ocr_content: str | None) -> str:
    """Merge text and OCR extractions intelligently."""
    if not text_content and not ocr_content:
        return ""
    if not text_content:
        return ocr_content or ""
    if not ocr_content:
        return text_content

    # If OCR content is significantly longer, it likely caught more content
    # (images, scanned pages, etc.)
    text_len = len(text_content.strip())
    ocr_len = len(ocr_content.strip())

    # If they're similar, prefer text extraction (cleaner formatting)
    if ocr_len <= text_len * 1.2:
        return text_content

    # OCR caught more - combine them
    # Use OCR as base, it likely has more complete content
    return f"{ocr_content}\n\n---\n\n## Additional Text Extraction\n\n{text_content}"


def download_gdoc(url: str, output_dir: Path) -> Path | None:
    """Download a Google Doc as docx for conversion."""
    # Extract document ID from URL
    patterns = [
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
    ]

    doc_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            doc_id = match.group(1)
            break

    if not doc_id:
        print(f"Could not extract Google Doc ID from URL: {url}", file=sys.stderr)
        return None

    # Export URL for docx format
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=docx"

    output_path = output_dir / f"gdoc_{doc_id}.docx"

    try:
        # Try using curl
        result = subprocess.run(
            ["curl", "-L", "-o", str(output_path), export_url],
            capture_output=True,
            timeout=60,
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return output_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("Could not download Google Doc. Make sure the document is publicly accessible.", file=sys.stderr)
    return None


def convert_file(
    input_path: str,
    output_path: str | None = None,
    mode: str = "auto",
    hybrid: bool = False,
) -> str:
    """
    Convert a document to markdown.

    Args:
        input_path: Path to input file or Google Docs URL
        output_path: Where to save markdown. If None, saves next to original.
        mode: "auto", "ocr", or "text"
        hybrid: If True for PDFs, run both text and OCR extraction and merge

    Returns:
        Path to the saved markdown file
    """
    # Handle Google Docs URLs
    if input_path.startswith(("http://", "https://")) and "docs.google.com" in input_path:
        with tempfile.TemporaryDirectory() as tmpdir:
            downloaded = download_gdoc(input_path, Path(tmpdir))
            if not downloaded:
                raise RuntimeError("Failed to download Google Doc")

            # Recursively convert the downloaded file
            md_content = convert_file_content(downloaded, mode, hybrid)

            # For URLs, we need an output path
            if not output_path:
                output_path = f"gdoc_{Path(downloaded).stem}.md"

            out = Path(output_path)
            out.write_text(md_content)
            print(f"Converted to: {out.absolute()}")
            return str(out.absolute())

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    md_content = convert_file_content(path, mode, hybrid)

    # Determine output path
    if output_path:
        out = Path(output_path)
    else:
        out = path.with_suffix(".md")

    out.write_text(md_content)
    print(f"Converted to: {out.absolute()}")
    return str(out.absolute())


def convert_file_content(path: Path, mode: str, hybrid: bool) -> str:
    """Convert file and return markdown content."""
    suffix = path.suffix.lower()

    # Route to appropriate converter
    if suffix in PANDOC_FORMATS:
        content = run_pandoc(path)
        if content:
            return content
        # Fallback to markitdown
        content = run_markitdown(path)
        if content:
            return content
        raise RuntimeError(f"Failed to convert {path}")

    # PDF with hybrid mode
    if suffix == ".pdf" and hybrid:
        print("Running hybrid extraction (text + OCR)...", file=sys.stderr)
        text_content = run_markitdown(path, enable_ocr=False)
        ocr_content = run_markitdown(path, enable_ocr=True)
        return merge_extractions(text_content, ocr_content)

    # Standard markitdown conversion
    enable_ocr = mode == "ocr" or (mode == "auto" and suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"})
    content = run_markitdown(path, enable_ocr=enable_ocr)

    if content:
        return content

    # Fallback to pandoc
    content = run_pandoc(path)
    if content:
        return content

    raise RuntimeError(f"Failed to convert {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert documents to Markdown",
        epilog="Supports: PDF, DOCX, PPTX, XLSX, HTML, EPUB, images, Google Docs URLs"
    )
    parser.add_argument("input", help="Path to file or Google Docs URL")
    parser.add_argument("-o", "--output", help="Output path (default: same location as input with .md extension)")
    parser.add_argument(
        "--mode",
        choices=["auto", "ocr", "text"],
        default="auto",
        help="Extraction mode: auto (smart detection), ocr (force OCR), text (text only)"
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="For PDFs: run both text and OCR extraction, merge results"
    )

    args = parser.parse_args()

    try:
        convert_file(
            input_path=args.input,
            output_path=args.output,
            mode=args.mode,
            hybrid=args.hybrid,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
