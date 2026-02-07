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

| Package | Symlinks To | Contains |
|---------|-------------|----------|
| `claude` | `~/.claude/` | Settings, agents, skills, rules, keybindings |
| `opencode` | `~/.config/opencode/` | Config, rules, permissions |

## Structure

```
~/ai_agent_dotfiles/
├── claude/
│   └── .claude/
│       ├── settings.json          # User preferences
│       ├── CLAUDE.md              # User-level context and guidelines
│       ├── agents/                # Custom agents
│       │   └── code-roaster.md   # Comprehensive code critique agent
│       ├── skills/                # Custom skills
│       │   └── karpathy-guidelines/  # Coding best practices
│       ├── rules/                 # User-level rules (empty for now)
│       └── .gitignore             # Ignore cache/session files
│
├── opencode/
│   └── .config/
│       └── opencode/
│           ├── opencode.json      # Main config with permissions
│           ├── agents/            # Custom agents
│           │   └── code-roaster.md  # Comprehensive code critique agent
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

- **settings.json** - Model selection, enabled plugins
- **CLAUDE.md** - User-level memory/context with Karpathy guidelines
- **agents/** - Custom subagents for specialized tasks
  - `code-roaster.md` - Comprehensive code quality critique agent
- **skills/** - Reusable commands and reference material
  - `karpathy-guidelines/` - Coding best practices skill
- **rules/** - User-level coding conventions and workflows
- **keybindings.json** - Custom keyboard shortcuts (create if needed)

### OpenCode (`~/.config/opencode/`)

- **opencode.json** - Permissions, instructions, global config
- **agents/** - Custom AI subagents
  - `code-roaster.md` - Comprehensive code quality critique agent
- **skills/** - Invokable skills
  - `karpathy-guidelines/` - Coding best practices skill (can be invoked)
- **rules/** - Modular instruction files (always loaded)
  - `karpathy-guidelines.md` - Coding best practices (always active)
  - `permissions.md` - Permission reference
- **commands/**, **modes/**, **plugins/** - Other extensions (create as needed)

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
