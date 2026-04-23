# 🤖 AI Agent Dotfiles

Personal configuration files for AI coding agents and tools (**Claude Code**,
**OpenCode**, **Codex CLI**, **Gemini CLI**, and the **pi coding agent**).

> **Note**: This is a companion to my [main dotfiles repository](https://github.com/mfmezger/dotfiles), kept separate for personal use.

## 🚀 Installation

```bash
# 1. Clone
git clone https://github.com/mfmezger/ai_agent_dotfiles.git ~/ai_agent_dotfiles
cd ~/ai_agent_dotfiles

# 2. Install (via script)
./install.sh

# OR Manual Install (via Stow)
stow claude      # Installs to ~/.claude/
stow opencode    # Installs to ~/.config/opencode/
stow codex       # Installs to ~/.codex/
stow gemini      # Installs to ~/.gemini/
stow pi          # Installs to ~/.pi/
```

**Requirements**: [GNU Stow](https://www.gnu.org/software/stow/).

> **Note**: If you already use pi, you may already have a real
> `~/.pi/agent/settings.json` file. Stow will not overwrite existing files.
> The installer now detects this and offers to back up `~/.pi` before
> continuing.

## ▶️ Start Here (First Run)

This repo is a dotfiles/config repo, so "starting the project" means installing
the symlinks into your home directory and validating the tools can read them.

```bash
# 1) Enter the repo
cd ~/ai_agent_dotfiles

# 2) Install symlinks
./install.sh

# If pi already has local state/config, the installer may prompt to back up
# ~/.pi before stowing the repo-managed settings.json symlink.

# 3) Sync shared skills and default context files (recommended)
./scripts/sync-skills.sh
./scripts/sync-contexts.sh
stow -R claude opencode codex gemini pi

# 4) Verify configs are linked
ls -la ~/.claude/
ls -la ~/.config/opencode/
ls -la ~/.codex/
ls -la ~/.gemini/
ls -la ~/.pi/agent/
```

After that, start using your agent CLIs as normal (for example `codex --help`,
`opencode --help`, or `gemini --help`) and they will load the installed config.

## 📂 Structure & Components

The repository uses Stow to symlink configurations to their respective home directories.

```text
~/ai_agent_dotfiles/
├── claude/ (.claude/)       # Settings, context, agents, skills, rules for Claude Code
├── opencode/ (.config/)     # Global context, configs, agents, skills, and rules for OpenCode
├── codex/ (.codex/)         # Global context, skills, and rules for Codex CLI
├── gemini/ (.gemini/)       # Global context, skills, and custom commands for Gemini CLI
├── pi/ (.pi/)               # Global context, settings, themes, and skills for pi
├── shared/                  # Canonical shared skills and context sources
└── install.sh               # Setup script
```

### Key Components

- **Context files**: Always-loaded global instructions such as `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
- **Agents**: Specialized sub-agents (e.g., `code-roaster`, `refactorer`, `detective`) for specific coding tasks.
- **Skills**: Reusable capabilities like `karpathy-guidelines`, `generate-image`, and Jira/Confluence integration.
- **Rules**: Always-active instructions and permissions.

## 🛠️ Usage & Workflow

- **Update Configs**: Edit files in `~/ai_agent_dotfiles/` and changes are immediately reflected in your home directory (via symlinks).
- **Refresh Links**: Run `stow -R claude opencode codex gemini pi` if you add
  new files.
- **Remove**: Run `stow -D claude opencode codex gemini pi` to unlink.
- **Secrets**: Create `~/.claude.json` manually for API keys and sensitive tokens (never commit them).

## 📍 Skill, Command, and Context Locations

- **Shared context source**: Edit the canonical always-on guidance in
  `shared/context/default-coding-guidelines.md`.
- **Claude global context**: `claude/.claude/CLAUDE.md` stows to
  `~/.claude/CLAUDE.md`.
- **OpenCode global context**: `opencode/.config/opencode/AGENTS.md` stows to
  `~/.config/opencode/AGENTS.md`.
- **Codex global context**: `codex/.codex/AGENTS.md` stows to
  `~/.codex/AGENTS.md`.
- **Gemini global context**: `gemini/.gemini/GEMINI.md` stows to
  `~/.gemini/GEMINI.md`.
- **pi global context**: `pi/.pi/agent/AGENTS.md` stows to
  `~/.pi/agent/AGENTS.md`.
- **pi skills**: This repo configures pi via `~/.pi/agent/settings.json` to load
  canonical shared skills from `~/ai_agent_dotfiles/shared/skills/` using a
  home-relative path so it is portable across your machines.
- **pi config**: Track pi settings in `pi/.pi/agent/settings.json`, which stows
  to `~/.pi/agent/settings.json`.
- **pi themes**: Custom pi themes live in `pi/.pi/agent/themes/` and stow to
  `~/.pi/agent/themes/`. The current tracked custom theme is `mayu`, selected
  via `pi/.pi/agent/settings.json`.
- **Codex CLI skills**: Put skill folders in `~/.codex/skills/` globally, or in
  `./.codex/skills/` for a project-specific skill.
- **Gemini CLI custom commands**: Put markdown command files in
  `~/.gemini/commands/` globally, or in `./.gemini/commands/` for project-only
  commands.

## 🔄 Cross-Agent Skill and Context Sync

To keep shared skills and default coding guidance aligned across agents:

- Edit canonical skills in `shared/skills/<skill-name>/SKILL.md`
- Edit canonical always-on context in `shared/context/default-coding-guidelines.md`
- Sync generated files with:

```bash
./scripts/sync-skills.sh
./scripts/sync-contexts.sh
```

- Validate everything is in sync:

```bash
./scripts/sync-skills.sh --check
./scripts/sync-contexts.sh --check
```

Managed targets:

- `shared/context/default-coding-guidelines.md` -> source for generated global context files
- `claude/.claude/CLAUDE.md` -> generated global Claude context
- `opencode/.config/opencode/AGENTS.md` -> generated global OpenCode context
- `codex/.codex/AGENTS.md` -> generated global Codex context
- `gemini/.gemini/GEMINI.md` -> generated global Gemini context
- `pi/.pi/agent/AGENTS.md` -> generated global pi context
- `pi/.pi/agent/settings.json` -> `~/.pi/agent/settings.json` (loads shared pi skills from `~/ai_agent_dotfiles/shared/skills`)
- `pi/.pi/agent/themes/<theme>.json` -> `~/.pi/agent/themes/<theme>.json`
- `claude/.claude/skills/<skill-name>` -> symlink to `shared/skills/<skill-name>`
- `codex/.codex/skills/<skill-name>` -> symlink to `shared/skills/<skill-name>`
- `gemini/.gemini/skills/<skill-name>` -> symlink to `shared/skills/<skill-name>`
- `gemini/.gemini/commands/<skill-name>.md` -> generated command file

### Apply Synced Resources Locally

```bash
# 1) Update per-tool links and generated files
./scripts/sync-skills.sh
./scripts/sync-contexts.sh

# 2) Restow into your home directory
stow -R claude opencode codex gemini pi

# 3) Verify links
ls -la ~/.claude/CLAUDE.md
ls -la ~/.config/opencode/AGENTS.md
ls -la ~/.codex/AGENTS.md
ls -la ~/.gemini/GEMINI.md
ls -la ~/.pi/agent/AGENTS.md
ls -la ~/.claude/skills/github-pr/SKILL.md
ls -la ~/.codex/skills/github-pr/SKILL.md
ls -la ~/.gemini/commands/github-pr.md
ls -la ~/.pi/agent/themes/mayu.json

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
- [pi Coding Agent Docs](https://github.com/badlogic/pi-mono)
- [GNU Stow Manual](https://www.gnu.org/software/stow/manual/)

**License**: MIT.
