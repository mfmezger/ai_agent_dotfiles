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

## Repository Layout

Top-level tool directories are GNU Stow packages. The `shared/` directory is the
canonical source for reusable content that gets linked or generated into those
packages.

```text
claude/     # stows to ~/.claude
opencode/   # stows to ~/.config/opencode
codex/      # stows to ~/.codex
gemini/     # stows to ~/.gemini
pi/         # stows to ~/.pi
shared/     # canonical shared skills and global context
scripts/    # install/sync helpers
```

Important shared paths:

```text
shared/context/default-coding-guidelines.md  # source for user-level guidance
shared/skills/<skill>/SKILL.md               # source for reusable skills
```

Generated or linked targets include:

```text
claude/.claude/skills/                       # symlinks to shared/skills
codex/.codex/skills/                         # symlinks to shared/skills
gemini/.gemini/skills/                       # symlinks to shared/skills
gemini/.gemini/commands/                     # generated from shared skills
opencode/.config/opencode/skills/            # symlinks through Claude skills
pi/.pi/agent/skills/                         # symlinks to shared/skills
```

Edit shared assets at the source, then regenerate/check derived files:

```bash
./scripts/sync-skills.sh
./scripts/sync-contexts.sh

./scripts/sync-skills.sh --check
./scripts/sync-contexts.sh --check
```

## Skills

Canonical skills live in `shared/skills/`.

### Git and GitHub

| Name | Short description |
| --- | --- |
| `commit` | Create concise Conventional Commits. |
| `github-pr` | Commit, push, and open or update GitHub pull requests. |
| `github-pr-feedback` | Triage PR review feedback into actionable and non-actionable items. |

### Documents, Files, and Reporting

| Name | Short description |
| --- | --- |
| `convert-to-markdown` | Convert PDFs, Office files, and other documents to Markdown. |
| `doc-coauthoring` | Co-author docs through context gathering, drafting, and reader testing. |
| `docx` | Create, read, edit, and format Word documents. |
| `google-workspace-convert` | Convert between Google Workspace files and Markdown. |
| `html-reporting` | Produce self-contained HTML reports, specs, dashboards, and prototypes. |
| `pptx` | Create, read, edit, and reorganize PowerPoint presentations. |
| `xlsx` | Create, read, edit, clean, and convert spreadsheet files. |

### Engineering

| Name | Short description |
| --- | --- |
| `building-pydantic-ai-agents` | Build Pydantic AI agents: tools, structured output, streaming, and tests. |
| `fastapi` | Build and review FastAPI services, routers, schemas, and tests. |
| `go-engineering` | Write, debug, refactor, and review idiomatic Go code. |
| `mcp-builder` | Build high-quality MCP servers for external service integrations. |
| `python-stack` | Apply Python project, tooling, testing, and packaging conventions. |
| `rust-engineering` | Write, debug, refactor, and review idiomatic Rust code. |
| `typescript-engineering` | Write, debug, refactor, and review type-safe TypeScript. |

### Integrations and Media

| Name | Short description |
| --- | --- |
| `agent-registry` | Manage Google Cloud Agent Registry services, endpoints, and MCP servers. |
| `confluence-datacenter` | Search, read, create, and update Confluence Data Center pages. |
| `generate-image` | Generate or edit images with Gemini image generation. |
| `jira-datacenter` | Search, read, create, and update Jira Data Center issues. |

### Agent and Skill Maintenance

| Name | Short description |
| --- | --- |
| `karpathy-guidelines` | Keep coding changes simple, surgical, and goal-driven. |
| `skill-creator` | Create, improve, and evaluate skills. |
| `tidy-first` | Separate structural refactors from behavioral changes. |

## License

MIT
