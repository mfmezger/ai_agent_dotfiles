---
name: google-workspace-convert
description: This skill should be used when the user asks to "convert a Google Doc to markdown", "download Google Sheets as markdown", "create a Google Doc from markdown", or needs to convert between Google Workspace files and Markdown format.
version: 0.1.0
---

# Google Workspace Converter

Convert Google Workspace files (Docs, Sheets, Slides) to Markdown and vice versa.

Uses Google Drive API with service account authentication.

## Supported Formats

| Format | To Markdown | From Markdown |
|--------|-------------|---------------|
| Google Docs | Yes | Yes |
| Google Sheets | Yes | No |
| Google Slides | Yes | No |
| Google Drawings | Yes | No |
| Uploaded files (PDF, DOCX, etc.) | Yes | - |

## Prerequisites

Environment variables (can be in `.env` file):
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON
- `GOOGLE_CLOUD_PROJECT` - GCP project ID

Service account needs:
- Google Drive API enabled in the GCP project
- Files shared with the service account email (use `info` command to get email)

## Commands

### Download: Google Workspace → Markdown

```bash
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  to-markdown "GOOGLE_DRIVE_URL_OR_ID"
```

Options:
- `-o, --output PATH` - Output path (default: current dir)
- `--ocr` - Enable OCR for image content

### Upload: Markdown → Google Doc

```bash
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  to-gdoc notes.md
```

Options:
- `-n, --name NAME` - Name for the Google Doc (default: filename)
- `-f, --folder ID` - Google Drive folder ID to upload to

### List Accessible Files

```bash
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  list
```

### Get Service Account Email

```bash
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  info
```

## Examples

```bash
# Convert Google Doc to Markdown
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  to-markdown "https://docs.google.com/document/d/1ABC123/edit"

# Convert with OCR for embedded images
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  to-markdown "https://docs.google.com/document/d/1ABC123/edit" --ocr

# Create Google Doc from Markdown
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  to-gdoc ./meeting-notes.md --name "Meeting Notes 2024"

# Upload to specific folder
uvx --with markitdown --with google-auth --with google-api-python-client --with python-dotenv \
  python ~/.claude/skills/google-workspace-convert/scripts/convert.py \
  to-gdoc ./report.md --folder "https://drive.google.com/drive/folders/1XYZ789"
```

## Sharing Files with Service Account

1. Run the `info` command to get the service account email
2. Open the Google file/folder in your browser
3. Click "Share"
4. Add the service account email
5. Give "Viewer" access (or "Editor" if uploading to a folder)

## Output

- **to-markdown**: Creates `filename.md` in current directory (or specified path)
- **to-gdoc**: Returns the URL of the created Google Doc
