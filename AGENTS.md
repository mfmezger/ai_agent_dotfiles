# AI Agent Dotfiles - Agent Guidelines

This is a dotfiles repository for AI coding tools (Claude Code, OpenCode), not a software project with build/test artifacts.

## Installation & Setup

### Installation Commands
```bash
# Full installation (runs install.sh)
./install.sh

# Manual installation using stow
stow claude      # Install Claude Code configs to ~/.claude/
stow opencode    # Install OpenCode configs to ~/.config/opencode/

# Update symlinks after adding new files
stow -R claude opencode

# Unlink configs
stow -D claude opencode
```

### Prerequisites
- GNU Stow (macOS: `brew install stow`, Linux: `sudo apt install stow`)
- Bash for install.sh script

## Code Style Guidelines

### Shell Scripts (install.sh)
- Shebang: `#!/usr/bin/env bash`
- Use `set -e` for error handling
- Color output using ANSI codes (RED, GREEN, YELLOW, BLUE, NC)
- Function naming: `lowercase_with_underscores`
- Indentation: 2 spaces
- Quotes around all variable expansions: `"$variable"`
- Use `[[` for tests instead of `[`
- Exit on errors: functions return non-zero to indicate failure

### Configuration Files (JSON, Markdown)
- JSON: 2-space indentation, no trailing commas
- Markdown: Use GitHub Flavored Markdown, line length ~80-100 chars
- Paths in comments use absolute paths starting with `~` for user home
- Code blocks specify language for syntax highlighting

### Project-Specific Conventions

#### Directory Structure
```
claude/.claude/
├── settings.json       # User preferences
├── CLAUDE.md          # User-level context
├── agents/            # Custom agents (.md files)
├── skills/            # Skills (directories with SKILL.md)
└── rules/             # User-level rules (.md files)

opencode/.config/opencode/
├── opencode.json      # Main config with permissions
├── agents/            # Custom agents (.md files)
├── skills/            # Skills (directories with SKILL.md)
├── rules/             # Custom rules (.md files)
└── README.md          # Config documentation
```

#### File Naming
- Agent files: `kebab-case.md` (e.g., `code-roaster.md`)
- Skill directories: `kebab-case/` containing `SKILL.md`
- Rule files: `kebab-case.md`
- Config files: lowercase or camelCase as appropriate to format

#### Content Guidelines for Agents/Skills/Rules
- **Agents**: Subagents for specialized tasks. Include purpose, when to invoke, and tool access.
- **Skills**: Invokable commands/reference material. Include metadata YAML block (name, description, license).
- **Rules**: Always-loaded instructions. Include clear behavioral guidelines.
- Use Markdown with code blocks, lists, and clear section headers
- Link to external resources where appropriate

## Testing & Validation

### Manual Validation
```bash
# Verify symlinks created correctly
ls -la ~/.claude/
ls -la ~/.config/opencode/

# Verify configs are valid JSON
cat ~/.claude/settings.json | python -m json.tool
cat ~/.config/opencode/opencode.json | python -m json.tool

# Test tools work
claude --version    # If Claude Code CLI available
opencode --help     # If OpenCode CLI available
```

### Adding New Configs
1. Create file in appropriate subdirectory (claude/.claude/ or opencode/.config/opencode/)
2. Restow: `stow -R <package>`
3. Verify symlink: `ls -la ~/.<target>/new-file`
4. Test if applicable (launch Claude/OpenCode and verify config loaded)

## Important Constraints

- **No build commands**: This is a config repo, not a code project
- **No package managers**: No npm, pip, go mod, cargo, etc. unless documenting tool setup
- **No tests**: Configs validated by manual testing and tool validation
- **Sensitive data never committed**: `.claude.json` and similar credential files excluded via .gitignore
- **Use environment variables** for any secrets in config examples

## File Editing Guidelines

### Surgical Changes
- Only edit config files as requested
- Don't reformat unrelated config sections
- Preserve existing JSON structure, keys, and values unless modifying them
- Keep comments in Markdown files explaining "why", not "what"
- Match existing indentation and spacing

### When Adding New Skills/Agents
1. Check existing files for patterns
2. Include required metadata in skills (YAML block at top)
3. Provide clear instructions on when/how to invoke
4. Add to README.md if documenting new capabilities
5. Restow and verify symlinks work

## References

- [GNU Stow Manual](https://www.gnu.org/software/stow/manual/)
- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [OpenCode Documentation](https://opencode.ai/docs)
