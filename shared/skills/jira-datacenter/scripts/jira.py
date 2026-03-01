#!/usr/bin/env python3
"""
Jira Data Center REST API client.

Supports Personal Access Token (PAT) or basic auth.
Uses Jira REST API v2 for Data Center/Server compatibility.
"""

import json
import os
import sys
from typing import Optional

import requests
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Jira Data Center CLI")
console = Console()


class JiraClient:
    """Jira Data Center API client."""

    def __init__(self):
        load_dotenv()

        self.base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        if not self.base_url:
            raise typer.BadParameter("JIRA_BASE_URL environment variable required")

        self.api_url = f"{self.base_url}/rest/api/2"

        pat = os.environ.get("JIRA_PAT")
        if pat:
            self.session = requests.Session()
            self.session.headers["Authorization"] = f"Bearer {pat}"
        else:
            username = os.environ.get("JIRA_USERNAME")
            password = os.environ.get("JIRA_PASSWORD")
            if not username or not password:
                raise typer.BadParameter(
                    "Set JIRA_PAT or both JIRA_USERNAME and JIRA_PASSWORD"
                )
            self.session = requests.Session()
            self.session.auth = (username, password)

        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["Accept"] = "application/json"

    def _request(self, method: str, endpoint: str, **kwargs) -> dict | list | None:
        """Make API request and handle errors."""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            if response.status_code == 204:
                return None
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                if "errorMessages" in error_data:
                    error_msg = "; ".join(error_data["errorMessages"])
                elif "errors" in error_data:
                    error_msg = "; ".join(f"{k}: {v}" for k, v in error_data["errors"].items())
            except (ValueError, AttributeError):
                pass
            raise typer.Exit(1) from typer.echo(f"Error: {error_msg}", err=True)

    def get_issue(self, issue_key: str, fields: list[str] | None = None,
                  expand: list[str] | None = None) -> dict:
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)
        return self._request("GET", f"issue/{issue_key}", params=params)

    def search_issues(self, jql: str, max_results: int = 50,
                      fields: list[str] | None = None) -> dict:
        data = {"jql": jql, "maxResults": max_results}
        if fields:
            data["fields"] = fields
        return self._request("POST", "search", json=data)

    def create_issue(self, project: str, issue_type: str, summary: str,
                     description: str | None = None, priority: str | None = None,
                     assignee: str | None = None, labels: list[str] | None = None,
                     components: list[str] | None = None) -> dict:
        fields = {
            "project": {"key": project},
            "issuetype": {"name": issue_type},
            "summary": summary,
        }
        if description:
            fields["description"] = description
        if priority:
            fields["priority"] = {"name": priority}
        if assignee:
            fields["assignee"] = {"name": assignee}
        if labels:
            fields["labels"] = labels
        if components:
            fields["components"] = [{"name": c} for c in components]
        return self._request("POST", "issue", json={"fields": fields})

    def update_issue(self, issue_key: str, fields: dict | None = None,
                     update: dict | None = None) -> None:
        data = {}
        if fields:
            data["fields"] = fields
        if update:
            data["update"] = update
        self._request("PUT", f"issue/{issue_key}", json=data)

    def get_transitions(self, issue_key: str) -> list[dict]:
        result = self._request("GET", f"issue/{issue_key}/transitions")
        return result.get("transitions", [])

    def transition_issue(self, issue_key: str, transition_id: str,
                         comment: str | None = None) -> None:
        data = {"transition": {"id": transition_id}}
        if comment:
            data["update"] = {"comment": [{"add": {"body": comment}}]}
        self._request("POST", f"issue/{issue_key}/transitions", json=data)

    def add_comment(self, issue_key: str, body: str) -> dict:
        return self._request("POST", f"issue/{issue_key}/comment", json={"body": body})

    def assign_issue(self, issue_key: str, username: str | None) -> None:
        self._request("PUT", f"issue/{issue_key}/assignee", json={"name": username})

    def get_projects(self) -> list[dict]:
        return self._request("GET", "project")


def get_client() -> JiraClient:
    try:
        return JiraClient()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def get(
    issue_key: str = typer.Argument(..., help="Issue key (e.g., PROJ-123)"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated fields"),
    comments: bool = typer.Option(False, "--comments", "-c", help="Include comments"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Get issue details by key."""
    client = get_client()

    field_list = fields.split(",") if fields else None
    expand = ["renderedFields"]
    if comments:
        expand.append("comments")

    issue = client.get_issue(issue_key, fields=field_list, expand=expand)

    if output_json:
        console.print_json(json.dumps(issue))
        return

    f = issue.get("fields", {})
    console.print(f"\n[bold blue]{issue_key}[/bold blue]: {f.get('summary', 'N/A')}")
    console.print(f"URL: {client.base_url}/browse/{issue_key}")
    console.print(f"Type: {f.get('issuetype', {}).get('name', 'N/A')}  "
                  f"Status: [green]{f.get('status', {}).get('name', 'N/A')}[/green]  "
                  f"Priority: {f.get('priority', {}).get('name', 'N/A')}")

    assignee = f.get("assignee")
    console.print(f"Assignee: {assignee.get('displayName') if assignee else 'Unassigned'}")

    if f.get("labels"):
        console.print(f"Labels: {', '.join(f['labels'])}")

    if f.get("description"):
        console.print(f"\n[bold]Description:[/bold]\n{f['description']}")

    if comments:
        comment_list = f.get("comment", {}).get("comments", [])
        if comment_list:
            console.print(f"\n[bold]Comments ({len(comment_list)}):[/bold]")
            for c in comment_list:
                author = c.get("author", {}).get("displayName", "Unknown")
                created = c.get("created", "")[:10]
                console.print(f"\n[dim]{created}[/dim] [bold]{author}[/bold]:")
                console.print(c.get("body", ""))


@app.command()
def search(
    jql: str = typer.Argument(..., help="JQL query string"),
    max_results: int = typer.Option(50, "--max", "-m", help="Maximum results"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated fields"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Search issues using JQL."""
    client = get_client()

    field_list = fields.split(",") if fields else None
    results = client.search_issues(jql, max_results=max_results, fields=field_list)

    if output_json:
        console.print_json(json.dumps(results))
        return

    issues = results.get("issues", [])
    total = results.get("total", 0)

    console.print(f"\nFound [bold]{total}[/bold] issues (showing {len(issues)})\n")

    table = Table(show_header=True)
    table.add_column("Key", style="blue")
    table.add_column("Type")
    table.add_column("Status", style="green")
    table.add_column("Assignee")
    table.add_column("Summary")

    for issue in issues:
        f = issue.get("fields", {})
        assignee = f.get("assignee")
        table.add_row(
            issue.get("key", ""),
            f.get("issuetype", {}).get("name", ""),
            f.get("status", {}).get("name", ""),
            assignee.get("displayName", "") if assignee else "Unassigned",
            f.get("summary", "")[:50],
        )

    console.print(table)


@app.command()
def create(
    project: str = typer.Option(..., "--project", "-p", help="Project key"),
    issue_type: str = typer.Option(..., "--type", "-t", help="Issue type (Bug, Task, Story, etc.)"),
    summary: str = typer.Option(..., "--summary", "-s", help="Issue summary/title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Description"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Priority name"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Assignee username"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Comma-separated labels"),
    components: Optional[str] = typer.Option(None, "--components", help="Comma-separated components"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Create a new issue."""
    client = get_client()

    label_list = labels.split(",") if labels else None
    component_list = components.split(",") if components else None

    result = client.create_issue(
        project=project,
        issue_type=issue_type,
        summary=summary,
        description=description,
        priority=priority,
        assignee=assignee,
        labels=label_list,
        components=component_list,
    )

    if output_json:
        console.print_json(json.dumps(result))
        return

    key = result.get("key", "")
    console.print(f"\n[green]Created:[/green] [bold blue]{key}[/bold blue]")
    console.print(f"URL: {client.base_url}/browse/{key}")


@app.command()
def update(
    issue_key: str = typer.Argument(..., help="Issue key"),
    summary: Optional[str] = typer.Option(None, "--summary", "-s", help="New summary"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description"),
    priority: Optional[str] = typer.Option(None, "--priority", help="New priority"),
    labels: Optional[str] = typer.Option(None, "--labels", "-l", help="Replace labels"),
    add_labels: Optional[str] = typer.Option(None, "--add-labels", help="Add labels"),
    remove_labels: Optional[str] = typer.Option(None, "--remove-labels", help="Remove labels"),
):
    """Update issue fields."""
    client = get_client()

    fields = {}
    update_ops = {}

    if summary:
        fields["summary"] = summary
    if description:
        fields["description"] = description
    if priority:
        fields["priority"] = {"name": priority}
    if labels:
        fields["labels"] = labels.split(",")

    if add_labels:
        update_ops["labels"] = [{"add": l} for l in add_labels.split(",")]
    if remove_labels:
        update_ops.setdefault("labels", [])
        update_ops["labels"].extend([{"remove": l} for l in remove_labels.split(",")])

    client.update_issue(
        issue_key,
        fields=fields if fields else None,
        update=update_ops if update_ops else None
    )
    console.print(f"[green]Updated:[/green] {issue_key}")


@app.command()
def transitions(
    issue_key: str = typer.Argument(..., help="Issue key"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """List available transitions for an issue."""
    client = get_client()
    trans = client.get_transitions(issue_key)

    if output_json:
        console.print_json(json.dumps(trans))
        return

    console.print(f"\nAvailable transitions for [bold blue]{issue_key}[/bold blue]:\n")
    for t in trans:
        console.print(f"  [{t['id']}] {t['name']} -> {t.get('to', {}).get('name', 'N/A')}")


@app.command()
def transition(
    issue_key: str = typer.Argument(..., help="Issue key"),
    status: str = typer.Argument(..., help="Target status name or transition ID"),
    comment: Optional[str] = typer.Option(None, "--comment", "-c", help="Add comment"),
):
    """Transition issue to a new status."""
    client = get_client()
    trans = client.get_transitions(issue_key)

    transition_id = None
    for t in trans:
        if t["id"] == status or t["name"].lower() == status.lower():
            transition_id = t["id"]
            break

    if not transition_id:
        available = ", ".join(t["name"] for t in trans)
        console.print(f"[red]Error:[/red] Transition '{status}' not found. Available: {available}")
        raise typer.Exit(1)

    client.transition_issue(issue_key, transition_id, comment=comment)
    console.print(f"[green]Transitioned:[/green] {issue_key} -> {status}")


@app.command()
def comment(
    issue_key: str = typer.Argument(..., help="Issue key"),
    body: str = typer.Argument(..., help="Comment text"),
):
    """Add a comment to an issue."""
    client = get_client()
    client.add_comment(issue_key, body)
    console.print(f"[green]Added comment to:[/green] {issue_key}")


@app.command()
def assign(
    issue_key: str = typer.Argument(..., help="Issue key"),
    username: str = typer.Argument(..., help="Username (or '-' to unassign)"),
):
    """Assign issue to a user."""
    client = get_client()
    user = None if username == "-" else username
    client.assign_issue(issue_key, user)

    if user:
        console.print(f"[green]Assigned:[/green] {issue_key} -> {user}")
    else:
        console.print(f"[green]Unassigned:[/green] {issue_key}")


@app.command()
def projects(
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """List available projects."""
    client = get_client()
    proj_list = client.get_projects()

    if output_json:
        console.print_json(json.dumps(proj_list))
        return

    console.print("\n[bold]Available projects:[/bold]\n")
    table = Table(show_header=True)
    table.add_column("Key", style="blue")
    table.add_column("Name")

    for p in proj_list:
        table.add_row(p.get("key", ""), p.get("name", ""))

    console.print(table)


if __name__ == "__main__":
    app()
