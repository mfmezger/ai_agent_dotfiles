# 🤖 AI Agent Dotfiles

Personal configuration files for AI coding agents and tools (**Claude Code** & **OpenCode**). 

> **Note**: This is a companion to my [main dotfiles repository](https://github.com/mfmezger/dotfiles), kept separate for personal use.

## 🚀 Installation

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ai_agent_dotfiles.git ~/ai_agent_dotfiles
cd ~/ai_agent_dotfiles

# 2. Install (via script)
./install.sh

# OR Manual Install (via Stow)
stow claude      # Installs to ~/.claude/
stow opencode    # Installs to ~/.config/opencode/
```

**Requirements**: [GNU Stow](https://www.gnu.org/software/stow/).

## 📂 Structure & Components

The repository uses Stow to symlink configurations to their respective home directories.

```text
~/ai_agent_dotfiles/
├── claude/ (.claude/)       # Settings, Agents, Skills, Rules for Claude Code
├── opencode/ (.config/)     # Configs, Agents, Skills, Rules for OpenCode
└── install.sh               # Setup script
```

### Key Components

- **Agents**: Specialized sub-agents (e.g., `code-roaster`, `refactorer`, `detective`) for specific coding tasks.
- **Skills**: Reusable capabilities like `karpathy-guidelines`, `generate-image`, and Jira/Confluence integration.
- **Rules**: Always-active instructions and permissions.

## 🛠️ Usage & Workflow

- **Update Configs**: Edit files in `~/ai_agent_dotfiles/` and changes are immediately reflected in your home directory (via symlinks).
- **Refresh Links**: Run `stow -R claude opencode` if you add new files.
- **Remove**: Run `stow -D claude opencode` to unlink.
- **Secrets**: Create `~/.claude.json` manually for API keys and sensitive tokens (never commit them).

## 📝 Development Guidelines

- **Shell Scripts**: Use `set -e`, 4-space indent, and meaningful names.
- **Markdown**: Use clear headings and code blocks.
- **JSON**: 2-space indent, descriptive keys.
- **Testing**: Verify syntax (`bash -n`) and test with `stow -n` (dry-run) before committing.

## 🔗 Resources

- [Claude Code Docs](https://github.com/anthropics/claude-code)
- [OpenCode Docs](https://opencode.ai/docs)
- [GNU Stow Manual](https://www.gnu.org/software/stow/manual/)

**License**: MIT.
