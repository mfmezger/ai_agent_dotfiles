---
description: This skill should be used when the user asks to "get Jira issue", "create Jira ticket", "search Jira", "update issue status", or needs to interact with Jira Data Center/Server instances.
---

# Jira Data Center

Interact with Jira Data Center/Server instances via REST API.

## Features

| Command     | Description                             |
| ----------- | --------------------------------------- |
| get         | Get issue details by key                |
| search      | Search issues using JQL                 |
| create      | Create a new issue                      |
| update      | Update issue fields                     |
| transition  | Change issue status                     |
| comment     | Add a comment to an issue               |
| assign      | Assign issue to a user                  |
| projects    | List available projects                 |
| transitions | List available transitions for an issue |

## Prerequisites

Environment variables (can be in `.env` file):

- `JIRA_BASE_URL` - Your Jira instance URL (e.g., `https://jira.company.com`)
- `JIRA_PAT` - Personal Access Token (preferred)

OR for basic auth:

- `JIRA_BASE_URL` - Your Jira instance URL
- `JIRA_USERNAME` - Your username
- `JIRA_PASSWORD` - Your password

### Creating a Personal Access Token

1. Go to your Jira profile (click avatar → Profile)
2. Navigate to Personal Access Tokens
3. Click "Create token"
4. Give it a name and set expiry
5. Copy the token to `JIRA_PAT`

## Usage

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py COMMAND [OPTIONS]
```

## Commands

### Get Issue

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py get PROJ-123
```

Options:

- `--fields FIELD1,FIELD2` - Specific fields to return (default: all)
- `--comments` - Include comments
- `--json` - Output as JSON

### Search Issues (JQL)

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py search "project = PROJ AND status = Open"
```

Options:

- `--max N` - Maximum results (default: 50)
- `--fields FIELD1,FIELD2` - Fields to include
- `--json` - Output as JSON

### Create Issue

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py create \
  --project PROJ \
  --type Bug \
  --summary "Issue title" \
  --description "Detailed description"
```

Options:

- `--project KEY` - Project key (required)
- `--type TYPE` - Issue type: Bug, Task, Story, Epic, etc. (required)
- `--summary TEXT` - Issue summary/title (required)
- `--description TEXT` - Issue description
- `--priority NAME` - Priority: Highest, High, Medium, Low, Lowest
- `--assignee USERNAME` - Assign to user
- `--labels LABEL1,LABEL2` - Comma-separated labels
- `--components COMP1,COMP2` - Comma-separated component names

### Update Issue

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py update PROJ-123 \
  --summary "New title" \
  --description "Updated description"
```

Options:

- `--summary TEXT` - New summary
- `--description TEXT` - New description
- `--priority NAME` - New priority
- `--labels LABEL1,LABEL2` - Replace labels
- `--add-labels LABEL` - Add labels
- `--remove-labels LABEL` - Remove labels

### Transition Issue (Change Status)

```bash
# List available transitions
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py transitions PROJ-123

# Transition to new status
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py transition PROJ-123 "In Progress"
```

### Add Comment

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py comment PROJ-123 "This is my comment"
```

### Assign Issue

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py assign PROJ-123 username
```

Use `-` to unassign:

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py assign PROJ-123 -
```

### List Projects

```bash
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py projects
```

## Examples

```bash
# Get issue with comments
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py get PROJ-123 --comments

# Search for my open issues
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py search "assignee = currentUser() AND status != Done"

# Create a bug with priority
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py create \
  --project PROJ \
  --type Bug \
  --summary "Login fails with special characters" \
  --description "Steps to reproduce:\n1. Enter username with @\n2. Click login\n3. Error appears" \
  --priority High \
  --labels security,login

# Move issue to In Progress
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py transition PROJ-123 "In Progress"

# Add a comment
uvx --with requests --with python-dotenv --with typer --with rich \
  python ~/.claude/skills/jira-datacenter/scripts/jira.py comment PROJ-123 "Fixed in commit abc123"
```

## Output

- Default output is human-readable formatted text
- Use `--json` flag for machine-readable JSON output
- Issue URLs are included for easy navigation

## API Version

This skill uses Jira REST API v2 (`/rest/api/2/`), which is compatible with:

- Jira Data Center 7.x and later
- Jira Server 7.x and later
