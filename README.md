# AI Agent Dotfiles

Personal configs for AI coding agents: Claude Code, OpenCode, Codex CLI,
Gemini CLI, and pi.

## Install

Requirements: [GNU Stow](https://www.gnu.org/software/stow/).

```bash
git clone https://github.com/mfmezger/ai_agent_dotfiles.git ~/ai_agent_dotfiles
cd ~/ai_agent_dotfiles
./install.sh
```

Manual install:

```bash
stow claude opencode codex gemini pi
```

If `~/.pi` already contains local config/state, the installer may prompt before
stowing repo-managed pi files.

## Common Commands

```bash
# Regenerate shared skills/context targets
./scripts/sync-skills.sh
./scripts/sync-contexts.sh

# Check generated files are current
./scripts/sync-skills.sh --check
./scripts/sync-contexts.sh --check

# Refresh symlinks after adding files
stow -R claude opencode codex gemini pi

# Unlink configs
stow -D claude opencode codex gemini pi
```

## Repository Layout

```text
claude/     # ~/.claude config
opencode/   # ~/.config/opencode config
codex/      # ~/.codex config
gemini/     # ~/.gemini config
pi/         # ~/.pi config, themes, and pi agent settings
shared/     # Canonical shared skills and context
scripts/    # Sync helpers
```

## Editing Guidelines

- Edit shared skills in `shared/skills/<skill>/SKILL.md`.
- Edit shared always-on guidance in `shared/context/default-coding-guidelines.md`.
- Run the sync scripts after changing shared content.
- Never commit secrets or local credentials.

## License

MIT
