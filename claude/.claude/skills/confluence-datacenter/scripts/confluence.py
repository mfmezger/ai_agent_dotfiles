#!/usr/bin/env python3
"""
Confluence Data Center REST API client.

Supports Personal Access Token (PAT) or basic auth.
Compatible with Confluence Data Center/Server 6.x and later.
"""

import html
import json
import os
import re
from pathlib import Path
from typing import Optional

import requests
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Confluence Data Center CLI")
console = Console()


class ConfluenceClient:
    """Confluence Data Center API client."""

    def __init__(self):
        load_dotenv()

        self.base_url = os.environ.get("CONFLUENCE_BASE_URL", "").rstrip("/")
        if not self.base_url:
            raise typer.BadParameter("CONFLUENCE_BASE_URL environment variable required")

        self.api_url = f"{self.base_url}/rest/api"

        pat = os.environ.get("CONFLUENCE_PAT")
        if pat:
            self.session = requests.Session()
            self.session.headers["Authorization"] = f"Bearer {pat}"
        else:
            username = os.environ.get("CONFLUENCE_USERNAME")
            password = os.environ.get("CONFLUENCE_PASSWORD")
            if not username or not password:
                raise typer.BadParameter(
                    "Set CONFLUENCE_PAT or both CONFLUENCE_USERNAME and CONFLUENCE_PASSWORD"
                )
            self.session = requests.Session()
            self.session.auth = (username, password)

        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["Accept"] = "application/json"

    def _request(self, method: str, endpoint: str, **kwargs) -> dict | list | None:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            if response.status_code == 204:
                return None
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            return {"content": response.text}

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
            except (ValueError, AttributeError):
                pass
            console.print(f"[red]Error:[/red] {error_msg}")
            raise typer.Exit(1)

    def _upload(self, endpoint: str, file_path: Path) -> dict:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = {"X-Atlassian-Token": "no-check"}
        if "Authorization" in self.session.headers:
            headers["Authorization"] = self.session.headers["Authorization"]

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = self.session.post(url, files=files, headers=headers, auth=self.session.auth)
            response.raise_for_status()
            return response.json()

    def get_page(self, page_id: str | None = None, space_key: str | None = None,
                 title: str | None = None) -> dict:
        if page_id:
            params = {"expand": "body.storage,version,space,ancestors"}
            return self._request("GET", f"content/{page_id}", params=params)
        elif space_key and title:
            params = {"spaceKey": space_key, "title": title, "expand": "body.storage,version,space"}
            result = self._request("GET", "content", params=params)
            results = result.get("results", [])
            if not results:
                raise typer.BadParameter(f"Page '{title}' not found in space '{space_key}'")
            return results[0]
        else:
            raise typer.BadParameter("Provide page_id or both --space and --title")

    def search(self, cql: str, max_results: int = 25, content_type: str | None = None) -> dict:
        params = {"cql": cql, "limit": max_results, "expand": "space,version"}
        if content_type:
            params["cql"] = f"type = {content_type} AND ({cql})"
        return self._request("GET", "content/search", params=params)

    def create_page(self, space_key: str, title: str, body: str,
                    parent_id: str | None = None, body_format: str = "storage") -> dict:
        data = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {body_format: {"value": body, "representation": body_format}}
        }
        if parent_id:
            data["ancestors"] = [{"id": parent_id}]
        return self._request("POST", "content", json=data)

    def update_page(self, page_id: str, body: str | None = None, title: str | None = None,
                    body_format: str = "storage", minor_edit: bool = False) -> dict:
        current = self.get_page(page_id)
        current_version = current.get("version", {}).get("number", 0)

        data = {
            "type": "page",
            "title": title or current.get("title", ""),
            "version": {"number": current_version + 1, "minorEdit": minor_edit}
        }
        if body:
            data["body"] = {body_format: {"value": body, "representation": body_format}}
        return self._request("PUT", f"content/{page_id}", json=data)

    def delete_page(self, page_id: str) -> None:
        self._request("DELETE", f"content/{page_id}")

    def get_children(self, page_id: str, max_results: int = 50) -> dict:
        return self._request("GET", f"content/{page_id}/child/page",
                           params={"expand": "version", "limit": max_results})

    def get_spaces(self, space_type: str | None = None) -> dict:
        params = {"limit": 100, "expand": "description.plain"}
        if space_type:
            params["type"] = space_type
        return self._request("GET", "space", params=params)

    def get_attachments(self, page_id: str) -> dict:
        return self._request("GET", f"content/{page_id}/child/attachment", params={"expand": "version"})

    def upload_attachment(self, page_id: str, file_path: Path) -> dict:
        return self._upload(f"content/{page_id}/child/attachment", file_path)

    def export_pdf(self, page_id: str) -> bytes:
        url = f"{self.base_url}/spaces/flyingpdf/pdfpageexport.action"
        response = self.session.get(url, params={"pageId": page_id})
        response.raise_for_status()
        return response.content


def markdown_to_storage(markdown: str) -> str:
    """Convert markdown to Confluence storage format."""
    try:
        import subprocess
        result = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html"],
            input=markdown, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: basic conversion
    text = markdown
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


def storage_to_markdown(storage: str) -> str:
    """Convert Confluence storage format to markdown."""
    try:
        from markitdown import MarkItDown
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
            f.write(storage)
            f.flush()
            md = MarkItDown()
            result = md.convert(f.name)
            Path(f.name).unlink()
            return result.text_content
    except ImportError:
        pass

    # Fallback
    text = storage
    text = re.sub(r'<h1[^>]*>(.+?)</h1>', r'# \1', text)
    text = re.sub(r'<h2[^>]*>(.+?)</h2>', r'## \1', text)
    text = re.sub(r'<h3[^>]*>(.+?)</h3>', r'### \1', text)
    text = re.sub(r'<strong>(.+?)</strong>', r'**\1**', text)
    text = re.sub(r'<em>(.+?)</em>', r'*\1*', text)
    text = re.sub(r'<code>(.+?)</code>', r'`\1`', text)
    text = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.+?)</a>', r'[\2](\1)', text)
    text = re.sub(r'<li>(.+?)</li>', r'- \1', text)
    text = re.sub(r'</?[uo]l[^>]*>', '', text)
    text = re.sub(r'<p>(.+?)</p>', r'\1\n\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def get_client() -> ConfluenceClient:
    try:
        return ConfluenceClient()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("get")
def get_page(
    page_id: Optional[str] = typer.Argument(None, help="Page ID"),
    space: Optional[str] = typer.Option(None, "--space", "-s", help="Space key"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Page title"),
    output_format: str = typer.Option("markdown", "--format", "-f",
                                       help="Output format: markdown, html, storage"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Get page content by ID or title."""
    client = get_client()

    if not page_id and not (space and title):
        console.print("[red]Error:[/red] Provide page_id or both --space and --title")
        raise typer.Exit(1)

    page = client.get_page(page_id=page_id, space_key=space, title=title)

    if output_json:
        console.print_json(json.dumps(page))
        return

    pid = page.get("id", "")
    ptitle = page.get("title", "")
    pspace = page.get("space", {}).get("key", "")

    console.print(f"\n[bold blue]{ptitle}[/bold blue]")
    console.print(f"ID: {pid}  Space: {pspace}")
    console.print(f"URL: {client.base_url}/pages/viewpage.action?pageId={pid}\n")

    body = page.get("body", {}).get("storage", {}).get("value", "")
    if output_format == "markdown":
        console.print(storage_to_markdown(body))
    elif output_format == "html":
        console.print(re.sub(r'>\s+<', '>\n<', body))
    else:
        console.print(body)


@app.command()
def search(
    cql: str = typer.Argument(..., help="CQL query"),
    max_results: int = typer.Option(25, "--max", "-m", help="Maximum results"),
    content_type: Optional[str] = typer.Option(None, "--type", "-t",
                                                help="Content type: page, blogpost, comment"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Search content using CQL."""
    client = get_client()
    results = client.search(cql, max_results=max_results, content_type=content_type)

    if output_json:
        console.print_json(json.dumps(results))
        return

    items = results.get("results", [])
    total = results.get("totalSize", len(items))

    console.print(f"\nFound [bold]{total}[/bold] results (showing {len(items)})\n")

    table = Table(show_header=True)
    table.add_column("ID", style="dim")
    table.add_column("Space", style="blue")
    table.add_column("Title")
    table.add_column("Type")

    for item in items:
        table.add_row(
            item.get("id", ""),
            item.get("space", {}).get("key", ""),
            item.get("title", ""),
            item.get("type", ""),
        )

    console.print(table)


@app.command()
def create(
    space: str = typer.Option(..., "--space", "-s", help="Space key"),
    title: str = typer.Option(..., "--title", "-t", help="Page title"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="Page content"),
    body_file: Optional[Path] = typer.Option(None, "--body-file", help="Read body from file"),
    parent: Optional[str] = typer.Option(None, "--parent", "-p", help="Parent page ID"),
    input_format: str = typer.Option("markdown", "--format", "-f",
                                      help="Body format: markdown, html, storage"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Create a new page."""
    client = get_client()

    content = body
    if body_file:
        content = body_file.read_text()
    if not content:
        console.print("[red]Error:[/red] Provide --body or --body-file")
        raise typer.Exit(1)

    if input_format == "markdown":
        content = markdown_to_storage(content)
        body_format = "storage"
    else:
        body_format = input_format

    result = client.create_page(space, title, content, parent_id=parent, body_format=body_format)

    if output_json:
        console.print_json(json.dumps(result))
        return

    pid = result.get("id", "")
    console.print(f"\n[green]Created:[/green] [bold]{title}[/bold]")
    console.print(f"ID: {pid}")
    console.print(f"URL: {client.base_url}/pages/viewpage.action?pageId={pid}")


@app.command()
def update(
    page_id: str = typer.Argument(..., help="Page ID"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="New content"),
    body_file: Optional[Path] = typer.Option(None, "--body-file", help="Read body from file"),
    input_format: str = typer.Option("markdown", "--format", "-f",
                                      help="Body format: markdown, html, storage"),
    minor: bool = typer.Option(False, "--minor", help="Mark as minor edit"),
):
    """Update a page."""
    client = get_client()

    content = body
    if body_file:
        content = body_file.read_text()

    body_format = input_format
    if content and input_format == "markdown":
        content = markdown_to_storage(content)
        body_format = "storage"

    client.update_page(page_id, body=content, title=title, body_format=body_format, minor_edit=minor)
    console.print(f"[green]Updated:[/green] {page_id}")


@app.command()
def delete(
    page_id: str = typer.Argument(..., help="Page ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a page."""
    client = get_client()

    if not force:
        page = client.get_page(page_id)
        title = page.get("title", "Unknown")
        confirm = typer.confirm(f"Delete page '{title}' (ID: {page_id})?")
        if not confirm:
            console.print("Cancelled")
            raise typer.Exit(0)

    client.delete_page(page_id)
    console.print(f"[green]Deleted:[/green] {page_id}")


@app.command()
def children(
    page_id: str = typer.Argument(..., help="Parent page ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """List child pages."""
    client = get_client()
    result = client.get_children(page_id)

    if output_json:
        console.print_json(json.dumps(result))
        return

    items = result.get("results", [])
    console.print(f"\n[bold]Child pages ({len(items)}):[/bold]\n")

    for item in items:
        console.print(f"  [bold]{item.get('title', 'N/A')}[/bold]")
        console.print(f"    ID: {item.get('id', '')}")


@app.command()
def spaces(
    space_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter: global, personal"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """List available spaces."""
    client = get_client()
    result = client.get_spaces(space_type=space_type)

    if output_json:
        console.print_json(json.dumps(result))
        return

    items = result.get("results", [])
    console.print(f"\n[bold]Spaces ({len(items)}):[/bold]\n")

    table = Table(show_header=True)
    table.add_column("Key", style="blue")
    table.add_column("Name")
    table.add_column("Type")

    for s in items:
        table.add_row(s.get("key", ""), s.get("name", ""), s.get("type", ""))

    console.print(table)


@app.command()
def attachments(
    page_id: str = typer.Argument(..., help="Page ID"),
    upload: Optional[Path] = typer.Option(None, "--upload", "-u", help="File to upload"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """List or upload attachments."""
    client = get_client()

    if upload:
        if not upload.exists():
            console.print(f"[red]Error:[/red] File not found: {upload}")
            raise typer.Exit(1)

        result = client.upload_attachment(page_id, upload)

        if output_json:
            console.print_json(json.dumps(result))
        else:
            console.print(f"[green]Uploaded:[/green] {upload.name}")
        return

    result = client.get_attachments(page_id)

    if output_json:
        console.print_json(json.dumps(result))
        return

    items = result.get("results", [])
    console.print(f"\n[bold]Attachments ({len(items)}):[/bold]\n")

    for att in items:
        console.print(f"  {att.get('title', 'N/A')}")
        console.print(f"    ID: {att.get('id', '')}")


@app.command("export")
def export_page(
    page_id: str = typer.Argument(..., help="Page ID"),
    output_format: str = typer.Option("markdown", "--format", "-f",
                                       help="Export format: pdf, markdown"),
    output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
):
    """Export page to file."""
    client = get_client()

    if output_format == "pdf":
        content = client.export_pdf(page_id)
        output.write_bytes(content)
        console.print(f"[green]Exported to:[/green] {output}")

    elif output_format == "markdown":
        page = client.get_page(page_id)
        body = page.get("body", {}).get("storage", {}).get("value", "")
        md_content = storage_to_markdown(body)
        output.write_text(md_content)
        console.print(f"[green]Exported to:[/green] {output}")

    else:
        console.print(f"[red]Error:[/red] Unsupported format: {output_format}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
