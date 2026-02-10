#!/usr/bin/env python3
"""
Convert Google Workspace files (Docs, Sheets, Slides) to/from Markdown.

Uses Google Drive API with service account authentication.
Requires: GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT env vars.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from markitdown import MarkItDown


# Google Workspace MIME types and their export formats
WORKSPACE_TYPES = {
    "application/vnd.google-apps.document": {
        "name": "Google Doc",
        "export_mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "extension": ".docx",
    },
    "application/vnd.google-apps.spreadsheet": {
        "name": "Google Sheet",
        "export_mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "extension": ".xlsx",
    },
    "application/vnd.google-apps.presentation": {
        "name": "Google Slides",
        "export_mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "extension": ".pptx",
    },
    "application/vnd.google-apps.drawing": {
        "name": "Google Drawing",
        "export_mime": "image/png",
        "extension": ".png",
    },
}

# Scopes needed for Drive API (read + write)
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def extract_file_id(url_or_id: str) -> str:
    """Extract Google Drive file ID from URL or return as-is if already an ID."""
    if "/" not in url_or_id and len(url_or_id) > 20:
        return url_or_id

    patterns = [
        r"/document/d/([a-zA-Z0-9_-]+)",
        r"/spreadsheets/d/([a-zA-Z0-9_-]+)",
        r"/presentation/d/([a-zA-Z0-9_-]+)",
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"/drawings/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract file ID from: {url_or_id}")


def extract_folder_id(url_or_id: str) -> str | None:
    """Extract Google Drive folder ID from URL."""
    if not url_or_id:
        return None

    if "/" not in url_or_id and len(url_or_id) > 20:
        return url_or_id

    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)

    return url_or_id


def get_drive_service():
    """Build and return Google Drive API service."""
    load_dotenv()

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS env var required")

    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )

    return build("drive", "v3", credentials=credentials)


def get_file_info(service, file_id: str) -> dict:
    """Get file metadata from Google Drive."""
    try:
        return service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,owners,shared"
        ).execute()
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            raise ValueError(
                f"File not found. Make sure the file is shared with your service account email. "
                f"File ID: {file_id}"
            )
        raise


def export_workspace_file(service, file_id: str, mime_type: str, output_path: Path) -> None:
    """Export a Google Workspace file to the specified format."""
    request = service.files().export_media(fileId=file_id, mimeType=mime_type)

    with open(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%", file=sys.stderr)


def download_regular_file(service, file_id: str, output_path: Path) -> None:
    """Download a regular (non-Workspace) file from Google Drive."""
    request = service.files().get_media(fileId=file_id)

    with open(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%", file=sys.stderr)


def convert_to_markdown(file_path: Path, enable_ocr: bool = False) -> str:
    """Convert a file to markdown using markitdown."""
    md = MarkItDown(enable_vision=enable_ocr)
    result = md.convert(str(file_path))
    return result.text_content


def markdown_to_docx(md_path: Path, docx_path: Path) -> None:
    """Convert markdown to docx using pandoc."""
    result = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "docx", "-o", str(docx_path), str(md_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {result.stderr}")


def upload_to_gdoc(
    service,
    file_path: Path,
    name: str,
    folder_id: str | None = None,
) -> dict:
    """Upload a file to Google Drive and convert to Google Docs format."""
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.document",
    }

    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(
        str(file_path),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,webViewLink",
    ).execute()

    return file


def convert_workspace_file(
    url_or_id: str,
    output_path: str | None = None,
    enable_ocr: bool = False,
) -> str:
    """
    Convert a Google Workspace file to Markdown.

    Args:
        url_or_id: Google Drive URL or file ID
        output_path: Where to save markdown (default: current dir with file name)
        enable_ocr: Enable OCR for image content

    Returns:
        Path to the saved markdown file
    """
    file_id = extract_file_id(url_or_id)
    print(f"File ID: {file_id}", file=sys.stderr)

    service = get_drive_service()

    # Get file info
    file_info = get_file_info(service, file_id)
    file_name = file_info["name"]
    mime_type = file_info["mimeType"]

    print(f"File: {file_name}", file=sys.stderr)
    print(f"Type: {mime_type}", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Handle Google Workspace files (need export)
        if mime_type in WORKSPACE_TYPES:
            type_info = WORKSPACE_TYPES[mime_type]
            print(f"Exporting {type_info['name']} as {type_info['extension']}...", file=sys.stderr)

            export_path = tmpdir_path / f"{file_name}{type_info['extension']}"
            export_workspace_file(service, file_id, type_info["export_mime"], export_path)

        # Handle regular files (direct download)
        else:
            ext_map = {
                "application/pdf": ".pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
                "text/html": ".html",
                "text/plain": ".txt",
                "image/png": ".png",
                "image/jpeg": ".jpg",
            }
            ext = ext_map.get(mime_type, "")
            if not ext:
                ext = Path(file_name).suffix or ".bin"

            export_path = tmpdir_path / f"{file_name}{ext if not file_name.endswith(ext) else ''}"
            print(f"Downloading file...", file=sys.stderr)
            download_regular_file(service, file_id, export_path)

        # Convert to markdown
        print("Converting to Markdown...", file=sys.stderr)
        md_content = convert_to_markdown(export_path, enable_ocr=enable_ocr)

    # Determine output path
    if output_path:
        out = Path(output_path)
    else:
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
        out = Path.cwd() / f"{safe_name}.md"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md_content)

    print(f"Converted to: {out.absolute()}")
    return str(out.absolute())


def create_gdoc_from_markdown(
    md_path: str,
    doc_name: str | None = None,
    folder_id: str | None = None,
) -> str:
    """
    Create a Google Doc from a Markdown file.

    Args:
        md_path: Path to the markdown file
        doc_name: Name for the Google Doc (default: markdown filename)
        folder_id: Google Drive folder ID to upload to (optional)

    Returns:
        URL of the created Google Doc
    """
    md_file = Path(md_path)
    if not md_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    if not doc_name:
        doc_name = md_file.stem

    print(f"Converting {md_file.name} to Google Doc...", file=sys.stderr)

    service = get_drive_service()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Convert markdown to docx first
        docx_path = Path(tmpdir) / f"{doc_name}.docx"
        print("Converting Markdown to DOCX...", file=sys.stderr)
        markdown_to_docx(md_file, docx_path)

        # Upload and convert to Google Doc
        print("Uploading to Google Drive...", file=sys.stderr)
        result = upload_to_gdoc(service, docx_path, doc_name, folder_id)

    url = result.get("webViewLink", f"https://docs.google.com/document/d/{result['id']}/edit")
    print(f"Created Google Doc: {url}")
    return url


def list_shared_files(limit: int = 20) -> None:
    """List files accessible to the service account."""
    service = get_drive_service()

    results = service.files().list(
        pageSize=limit,
        fields="files(id, name, mimeType, owners)",
    ).execute()

    files = results.get("files", [])

    if not files:
        print("No files found. Share files with your service account email to access them.")
        return

    print(f"\nAccessible files ({len(files)}):\n")
    for f in files:
        type_name = WORKSPACE_TYPES.get(f["mimeType"], {}).get("name", f["mimeType"])
        print(f"  {f['name']}")
        print(f"    ID: {f['id']}")
        print(f"    Type: {type_name}")
        print()


def get_service_account_email() -> str:
    """Get the service account email for sharing instructions."""
    load_dotenv()
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        return "SERVICE_ACCOUNT_EMAIL"

    import json
    with open(creds_path) as f:
        creds = json.load(f)
    return creds.get("client_email", "SERVICE_ACCOUNT_EMAIL")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Google Workspace files to/from Markdown",
        epilog="Supports: Google Docs, Sheets, Slides, Drawings, and uploaded files"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # to-markdown command
    to_md_parser = subparsers.add_parser("to-markdown", aliases=["tomd", "download"], help="Convert Google file to Markdown")
    to_md_parser.add_argument("input", help="Google Drive URL or file ID")
    to_md_parser.add_argument("-o", "--output", help="Output path (default: current dir)")
    to_md_parser.add_argument("--ocr", action="store_true", help="Enable OCR for image content")

    # to-gdoc command
    to_gdoc_parser = subparsers.add_parser("to-gdoc", aliases=["togdoc", "upload"], help="Create Google Doc from Markdown")
    to_gdoc_parser.add_argument("input", help="Path to Markdown file")
    to_gdoc_parser.add_argument("-n", "--name", help="Name for the Google Doc (default: filename)")
    to_gdoc_parser.add_argument("-f", "--folder", help="Google Drive folder ID or URL to upload to")

    # list command
    list_parser = subparsers.add_parser("list", help="List accessible files")
    list_parser.add_argument("-n", "--limit", type=int, default=20, help="Max files to list")

    # info command
    info_parser = subparsers.add_parser("info", help="Show service account info for sharing")

    args = parser.parse_args()

    if args.command in ("to-markdown", "tomd", "download"):
        try:
            convert_workspace_file(
                url_or_id=args.input,
                output_path=args.output,
                enable_ocr=args.ocr,
            )
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command in ("to-gdoc", "togdoc", "upload"):
        try:
            folder_id = extract_folder_id(args.folder) if args.folder else None
            create_gdoc_from_markdown(
                md_path=args.input,
                doc_name=args.name,
                folder_id=folder_id,
            )
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "list":
        try:
            list_shared_files(args.limit)
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "info":
        email = get_service_account_email()
        print(f"\nService Account Email: {email}")
        print(f"\nTo give access to a file:")
        print(f"  1. Open the file in Google Drive")
        print(f"  2. Click 'Share'")
        print(f"  3. Add: {email}")
        print(f"  4. Give 'Viewer' access (or 'Editor' for upload)")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
