# 🤖 AI Agent Dotfiles

Personal configuration files for AI coding agents and tools. This repository contains settings, skills, agents, and preferences for:

- **Claude Code** - Anthropic's official CLI for Claude
- **OpenCode** - AI-powered coding agent for the terminal

> **Note**: This is a companion to my [main dotfiles repository](https://github.com/mfmezger/dotfiles). These configs are kept separate as they're only used on personal machines, not at work.

## Quick Install

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/ai_agent_dotfiles.git ~/ai_agent_dotfiles

# Run the installer
cd ~/ai_agent_dotfiles
./install.sh
```

## What Gets Installed

The installer uses [GNU Stow](https://www.gnu.org/software/stow/) to create symlinks:

| Package    | Symlinks To           | Contains                                     |
| ---------- | --------------------- | -------------------------------------------- |
| `claude`   | `~/.claude/`          | Settings, agents, skills, rules, keybindings |
| `opencode` | `~/.config/opencode/` | Config, rules, permissions                   |

## Structure

```
~/ai_agent_dotfiles/
├── claude/
│   └── .claude/
│       ├── settings.json          # User preferences (model, plugins, permissions)
│       ├── CLAUDE.md              # User-level context and guidelines
│       ├── agents/                # Custom agents
│       │   ├── code-roaster.md   # Comprehensive code critique agent
│       │   ├── refactorer.md     # SOLID + DRY + KISS refactoring planner
│       │   ├── detective.md      # Code smell and best practices detector
│       │   └── vault-organizer.md # Documentation/notes organizer agent
│       ├── skills/                # Custom skills
│       │   ├── karpathy-guidelines/       # Coding best practices
│       │   ├── convert-to-markdown/       # Document → Markdown converter
│       │   ├── google-workspace-convert/  # Google Docs/Sheets ↔ Markdown
│       │   ├── generate-image/            # Gemini image generation
│       │   ├── jira-datacenter/           # Jira Data Center REST client
│       │   └── confluence-datacenter/     # Confluence Data Center REST client
│       └── .gitignore             # Ignore cache/session files
│
├── opencode/
│   └── .config/
│       └── opencode/
│           ├── opencode.json      # Main config with permissions
│           ├── agents/            # Custom agents
│           │   ├── code-roaster.md  # Comprehensive code critique agent
│           │   ├── refactorer.md    # SOLID + DRY + KISS refactoring planner
│           │   └── detective.md     # Code smell and best practices detector
│           ├── skills/            # Custom skills (invokable)
│           │   └── karpathy-guidelines/  # Coding best practices skill
│           ├── rules/             # Custom rules (always loaded)
│           │   ├── karpathy-guidelines.md  # Coding best practices
│           │   └── permissions.md
│           ├── README.md          # OpenCode config docs
│           └── .gitignore         # Ignore node_modules, cache, etc.
│
├── install.sh                     # Installation script
└── README.md                      # This file
```

## Manual Installation

If you prefer manual setup:

```bash
cd ~/ai_agent_dotfiles

# Install Claude Code configs
stow claude

# Install OpenCode configs
stow opencode
```

## Configuration Overview

### Claude Code (`~/.claude/`)

- **settings.json** - Model selection, enabled plugins, permissions
- **CLAUDE.md** - User-level memory/context with Karpathy guidelines
- **agents/** - Custom subagents for specialized tasks
  - `code-roaster.md` - Comprehensive code quality critique agent
  - `refactorer.md` - SOLID + DRY + KISS refactoring planner with actionable plans
  - `detective.md` - Code smell and best practices detector (Python, Go, Rust)
  - `vault-organizer.md` - Documentation and notes organization agent
- **skills/** - Reusable commands and reference material
  - `karpathy-guidelines/` - Coding best practices skill
  - `convert-to-markdown/` - Convert PDF, DOCX, PPTX, images to Markdown
  - `google-workspace-convert/` - Google Docs/Sheets/Slides to/from Markdown
  - `generate-image/` - AI image generation via Gemini (text-to-image, image-to-image)
  - `jira-datacenter/` - Jira Data Center REST API client (issues, JQL, transitions)
  - `confluence-datacenter/` - Confluence Data Center REST API client (pages, CQL, attachments)
- **rules/** - User-level coding conventions and workflows
- **keybindings.json** - Custom keyboard shortcuts (create if needed)
- **skills/** - Reusable commands and reference material
  <<<<<<< HEAD
- `karpathy-guidelines/` - Coding best practices skill
- **rules/** - User-level coding conventions and workflows
- **keybindings.json** - Custom keyboard shortcuts (create if needed)
  ||||||| c0b82d6
  - `karpathy-guidelines/` - Coding best practices skill
- **rules/** - User-level coding conventions and workflows
- # **keybindings.json** - Custom keyboard shortcuts (create if needed)
  - `karpathy-guidelines/` - Coding best practices skill
  - `convert-to-markdown/` - Convert PDF, DOCX, PPTX, images to Markdown
  - `google-workspace-convert/` - Google Docs/Sheets/Slides to/from Markdown
  - `generate-image/` - AI image generation via Gemini (text-to-image, image-to-image)
  - `jira-datacenter/` - Jira Data Center REST API client (issues, JQL, transitions)
  - `confluence-datacenter/` - Confluence Data Center REST API client (pages, CQL, attachments)
    > > > > > > > 8eb4c09144072ce1e653734b9c896f8d5e33b78e

### OpenCode (`~/.config/opencode/`)

- **opencode.json** - Permissions, instructions, global config
- **agents/** - Custom AI subagents
  - `code-roaster.md` - Comprehensive code quality critique agent
  - `refactorer.md` - SOLID + DRY + KISS refactoring planner with actionable plans
  - `detective.md` - Code smell and best practices detector (Python, Go, Rust)
- **skills/** - Invokable skills
- `karpathy-guidelines/` - Coding best practices skill (can be invoked)
- **rules/** - Modular instruction files (always loaded)
  - `karpathy-guidelines.md` - Coding best practices (always active)
- `permissions.md` - Permission reference
- `commands/**, **modes/**, **plugins/\*\* - Other extensions (create as needed)

## Custom Agents

### code-roaster

Comprehensive, no-holds-barred critique of your entire codebase. Delivers brutal honesty about code quality, architecture, design patterns, and implementation issues across all levels - from architectural decisions down to individual problematic lines.

**Use when:**

- After major refactoring to identify remaining issues
- Before code reviews to find problems preemptively
- When technical debt has accumulated and you need a reality check
- When you want unfiltered feedback on code quality

### refactorer

Analyzes code for violations of SOLID, DRY, and KISS principles and creates detailed, actionable refactoring plans without executing changes. Specializes in Python and Go/Rust ecosystems with language-specific patterns.

**Use when:**

- Before major refactoring efforts to identify structural issues
- When technical debt needs systematic assessment
- When code has grown organically and needs architectural review
- When you want a prioritized roadmap for improving code quality

**Key Features:**

- Identifies SOLID principle violations (SRP, OCP, LSP, ISP, DIP)
- Detects DRY violations (code duplication)
- Finds KISS violations (over-engineering)
- Creates step-by-step refactoring plans with risk assessment
- Provides before/after code examples
- Includes testing requirements and rollback strategies
- Integrates Karpathy guidelines for surgical changes

### detective

Identifies code smells, best practices violations, and test smells across Python, Go, and Rust codebases with language-specific guidance. Covers security vulnerabilities, performance issues, and test quality problems.

**Use when:**

- When you need a comprehensive code quality audit
- Before major releases to catch code smells
- When performance issues are suspected
- When security review is needed
- When test quality needs improvement
- When onboarding new developers and setting quality standards

**Key Features:**

- Detects Martin Fowler's classic code smells
- Language-specific anti-patterns for Python, Go, and Rust
- Security vulnerability detection (hardcoded credentials, SQL injection, etc.)
- Performance smell identification (N+1 queries, memory leaks, etc.)
- Test smell analysis (brittle tests, missing assertions, test pollution)
- Prioritized recommendations with severity ratings
- Detailed code examples showing fixes

## Code Style Guidelines

When creating custom agents, skills, or rules, follow these style conventions:

### Shell Scripts (.sh, .bash, .zsh)

- Indentation: 4 spaces
- Shebang: `#!/bin/bash` at top of file
- Always use `set -e` for error handling
- Use descriptive variable names in UPPER_CASE
- Comment with `#` prefix
- Use functions for complex logic
- Exit immediately on command failure with `set -e`

### Markdown (.md) - Agents, Skills, Rules

- Use clear, descriptive titles
- Structure with headings (`##`, `###`)
- Use code blocks for examples: `bash or `json
- Keep line length reasonable (< 120 chars when possible)
- Use bullet lists for enumerations
- Include usage examples and expected output

### JSON Configuration (.json)

- Indentation: 2 spaces
- Trailing commas allowed (for readability)
- Use descriptive keys
- Keep permissions organized logically
- Comment JSON with "instructions" array referencing rules files

### General Rules

- Encoding: UTF-8
- Line endings: LF (Unix-style)
- Trim trailing whitespace
- Always insert final newline
- Use meaningful filenames (lowercase with hyphens for agents/skills)

## Sensitive Data

⚠️ **Important**: The `~/.claude.json` file may contain:

- OAuth tokens
- MCP server configurations with API keys
- Trust settings

This file is **NOT** included in this repository for security reasons.

### Setting up .claude.json

Create `~/.claude.json` manually for:

- MCP server configurations
- Theme preferences
- OAuth settings

Example structure:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@my/mcp-server"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

**Use environment variables** for sensitive data, never hardcode API keys!

## Updating Configs

Since stow creates symlinks, changes work in both directions:

```bash
# Edit in your home directory
vim ~/.claude/settings.json

# Changes are automatically reflected in the repo
cd ~/ai_agent_dotfiles
git status  # Shows the modified file
```

## Adding New Skills/Agents

### Claude Code

```bash
# Create a new skill
mkdir -p ~/ai_agent_dotfiles/claude/.claude/skills/my-skill
vim ~/ai_agent_dotfiles/claude/.claude/skills/my-skill/SKILL.md

# Create a new agent
vim ~/ai_agent_dotfiles/claude/.claude/agents/my-agent.md
```

### OpenCode

```bash
# Add an agent
mkdir -p ~/ai_agent_dotfiles/opencode/.config/opencode/agents
vim ~/ai_agent_dotfiles/opencode/.config/opencode/agents/my-agent.md
```

## Stow Tips & Notes

GNU Stow creates symlinks from package directories to home directory:

- **Use `--no-folding`** for packages with scripts folders (not needed for ai_agent_dotfiles)
- **Dry run mode**: `stow -n <package>` - preview changes before applying
- **Restow**: `stow -R <package>` - refresh all symlinks for a package
- **Unstow**: `stow -D <package>` - remove all symlinks for a package
- **Conflicts**: Occur when files exist at target location - backup and remove before stowing
- **Multiple packages**: Can stow multiple at once: `stow claude opencode`

### Conflict Resolution

If stow reports conflicts:

```bash
# Backup existing file
mv ~/.claude/settings.json ~/.claude/settings.json.bak

# Restow
stow -R claude
```

## Testing & Development

When working with AI agent configurations, test changes safely:

### Shell Testing

Test shell scripts by running them in a safe environment:

```bash
# Check syntax
bash -n install.sh

# Test in dry-run mode where supported
stow -n <package>
```

### Pre-commit Hooks

Always run linting/typechecking before committing:

```bash
# Check what commands are available
cd ~/ai_agent_dotfiles

# If using pre-commit hooks
pre-commit run --all-files
```

### Verification

After making changes:

1. Test Claude Code with new settings: `claude --help` or run a simple task
2. Verify OpenCode permissions work by having it read files
3. Check that all agents/skills are accessible
4. Ensure symlinks are correct: `ls -la ~/.claude ~/.config/opencode`

## Restowing (After Updates)

If you add new files, refresh the symlinks:

```bash
cd ~/ai_agent_dotfiles
stow -R claude opencode
```

## Removing

To unlink configs:

```bash
cd ~/ai_agent_dotfiles
stow -D claude opencode
```

## Git Workflow

```bash
cd ~/ai_agent_dotfiles

# Check what changed
git status

# Commit your configs
git add .
git commit -m "Update Claude Code settings"
git push
```

### Commit Message Format

Follow conventional commits (or use commitizen if configured):

- `feat:` - New feature
- `fix:` - Bug fix
- `chore:` - Maintenance tasks
- `docs:` - Documentation changes
- `style:` - Code style changes (no functional change)
- `refactor:` - Code refactoring
- `config:` - Configuration updates

### If Using Commitizen

```bash
cz commit     # Create a commit with conventional format
cz bump       # Bump version based on commits
pcr           # Run pre-commit hooks on all files
pcu           # Update pre-commit hooks
```

## Why Separate from Main Dotfiles?

- **Work/Personal Separation** - Main dotfiles used at work, these only on personal machines
- **Different Update Cadence** - AI tool configs change more frequently
- **Privacy** - Can keep this private while sharing main dotfiles
- **Focus** - Cleaner organization for AI-specific tooling

## Resources

- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [OpenCode Documentation](https://opencode.ai/docs)
- [GNU Stow Manual](https://www.gnu.org/software/stow/manual/)

## License

MIT - Feel free to fork and adapt for your own use!
