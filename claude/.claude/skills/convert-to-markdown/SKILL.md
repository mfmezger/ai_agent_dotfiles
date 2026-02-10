---
name: convert-to-markdown
description: This skill should be used when the user asks to "convert a document to markdown", "extract text from PDF", "convert Word/PowerPoint/Excel to markdown", or needs to transform documents into markdown format.
version: 0.1.0
---

# Document to Markdown Converter

Convert various document formats to Markdown using markitdown and pandoc.

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | .pdf | Text + OCR hybrid mode available |
| Word | .docx | Full support |
| PowerPoint | .pptx | Extracts text from slides |
| Excel | .xlsx | Converts tables |
| HTML | .html, .htm | Full support |
| EPUB | .epub | Via pandoc |
| Images | .jpg, .png, .gif, .webp | OCR extraction |
| Google Docs | URL | Public docs, exports as docx |

## Usage

```bash
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py INPUT
```

### Options

| Flag | Description |
|------|-------------|
| `-o, --output PATH` | Output path (default: input.md next to original) |
| `--mode auto\|ocr\|text` | Extraction mode (default: auto) |
| `--hybrid` | PDF only: run both text + OCR, merge results |

### Examples

```bash
# Basic conversion (saves as document.md)
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py document.pdf

# Force OCR mode for scanned document
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py scanned.pdf --mode ocr

# Hybrid extraction for PDFs with mixed content
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py report.pdf --hybrid

# Convert Word document
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py report.docx

# Convert public Google Doc
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py "https://docs.google.com/document/d/DOCUMENT_ID/edit"

# Specify output location
uvx --with markitdown python ~/.claude/skills/convert-to-markdown/scripts/convert.py slides.pptx -o notes.md
```

## Mode Details

- **auto**: Smart detection - uses OCR for images, text extraction for documents
- **text**: Pure text extraction, faster but misses image content
- **ocr**: Force OCR on everything, slower but catches all visual content
- **hybrid** (PDF only): Runs both text and OCR extraction, merges results for best coverage

## Google Docs

For Google Docs conversion:
- Document must be publicly accessible (or "Anyone with link can view")
- Provide the full URL: `https://docs.google.com/document/d/DOC_ID/edit`
- Script exports as docx, then converts to markdown

## Output

- Default: Creates `filename.md` next to the original file
- Use `-o` to specify a different location
- Prints the output path when complete

## Requirements

- **markitdown**: Installed automatically via uvx
- **pandoc**: Must be installed on system (for epub, odt, rst, tex formats)
  ```bash
  brew install pandoc  # macOS
  ```
