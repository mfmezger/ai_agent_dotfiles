# 🤖 AI Agent Dotfiles

Personal configuration files for AI coding agents and tools (**Claude Code**,
**OpenCode**, **Codex CLI**, and **Gemini CLI**).

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
stow codex       # Installs to ~/.codex/
stow gemini      # Installs to ~/.gemini/
```

**Requirements**: [GNU Stow](https://www.gnu.org/software/stow/).

## ▶️ Start Here (First Run)

This repo is a dotfiles/config repo, so "starting the project" means installing
the symlinks into your home directory and validating the tools can read them.

```bash
# 1) Enter the repo
cd ~/ai_agent_dotfiles

# 2) Install symlinks
./install.sh

# 3) Sync shared skills (recommended)
./scripts/sync-skills.sh
stow -R claude codex gemini

# 4) Verify configs are linked
ls -la ~/.claude/
ls -la ~/.config/opencode/
ls -la ~/.codex/
ls -la ~/.gemini/
```

After that, start using your agent CLIs as normal (for example `codex --help`,
`opencode --help`, or `gemini --help`) and they will load the installed config.

## 📂 Structure & Components

The repository uses Stow to symlink configurations to their respective home directories.

```text
~/ai_agent_dotfiles/
├── claude/ (.claude/)       # Settings, Agents, Skills, Rules for Claude Code
├── opencode/ (.config/)     # Configs, Agents, Skills, Rules for OpenCode
├── codex/ (.codex/)         # Skills and config for Codex CLI
├── gemini/ (.gemini/)       # Custom commands for Gemini CLI
└── install.sh               # Setup script
```

### Key Components

- **Agents**: Specialized sub-agents (e.g., `code-roaster`, `refactorer`, `detective`) for specific coding tasks.
- **Skills**: Reusable capabilities like `karpathy-guidelines`, `generate-image`, and Jira/Confluence integration.
- **Rules**: Always-active instructions and permissions.

## 🛠️ Usage & Workflow

- **Update Configs**: Edit files in `~/ai_agent_dotfiles/` and changes are immediately reflected in your home directory (via symlinks).
- **Refresh Links**: Run `stow -R claude opencode codex gemini` if you add new
  files.
- **Remove**: Run `stow -D claude opencode codex gemini` to unlink.
- **Secrets**: Create `~/.claude.json` manually for API keys and sensitive tokens (never commit them).

## 📍 Skill/Command Locations

- **Codex CLI skills**: Put skill folders in `~/.codex/skills/` globally, or in
  `./.codex/skills/` for a project-specific skill.
- **Gemini CLI custom commands**: Put markdown command files in
  `~/.gemini/commands/` globally, or in `./.gemini/commands/` for project-only
  commands.

## 🔄 Cross-Agent Skill Sync

To keep the same skill behavior across Claude, Codex, and Gemini:

- Edit canonical skills in `shared/skills/<skill-name>/SKILL.md`
- Sync links and generated commands with:

```bash
./scripts/sync-skills.sh
```

- Validate everything is in sync:

```bash
./scripts/sync-skills.sh --check
```

Managed targets:

- `claude/.claude/skills/<skill-name>` -> symlink to `shared/skills/<skill-name>`
- `codex/.codex/skills/<skill-name>` -> symlink to `shared/skills/<skill-name>`
- `gemini/.gemini/skills/<skill-name>` -> symlink to `shared/skills/<skill-name>`
- `gemini/.gemini/commands/<skill-name>.md` -> generated command file

### Apply Synced Skills Locally

```bash
# 1) Update per-tool links and generated command files
./scripts/sync-skills.sh

# 2) Restow into your home directory
stow -R claude codex gemini

# 3) Verify links
ls -la ~/.claude/skills/github/SKILL.md
ls -la ~/.codex/skills/github/SKILL.md
ls -la ~/.gemini/commands/github.md

# Optional: ensure no old misplaced path remains
ls -la ~/skills
```

## 📝 Development Guidelines

- **Shell Scripts**: Use `set -e`, 4-space indent, and meaningful names.
- **Markdown**: Use clear headings and code blocks.
- **JSON**: 2-space indent, descriptive keys.
- **Testing**: Verify syntax (`bash -n`) and test with `stow -n` (dry-run) before committing.

## 🔗 Resources

- [Claude Code Docs](https://github.com/anthropics/claude-code)
- [OpenCode Docs](https://opencode.ai/docs)
- [Codex CLI Docs](https://developers.openai.com/codex/)
- [Gemini CLI Docs](https://github.com/google-gemini/gemini-cli)
- [GNU Stow Manual](https://www.gnu.org/software/stow/manual/)

**License**: MIT.
