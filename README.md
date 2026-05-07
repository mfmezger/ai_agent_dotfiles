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

```text
claude/     # ~/.claude config
opencode/   # ~/.config/opencode config
codex/      # ~/.codex config
gemini/     # ~/.gemini config
pi/         # ~/.pi config, themes, and pi agent settings
shared/     # Canonical shared skills and context
scripts/    # Sync helpers
```

## Skills

### Git and GitHub

| Name | Short description |
| --- | --- |
| `commit` | Commit local changes with Conventional Commits. |
| `github-pr` | Commit, push, and open or update GitHub pull requests. |
| `github-pr-feedback` | Triage PR review feedback into actionable and non-actionable items. |

### Documents and Files

| Name | Short description |
| --- | --- |
| `convert-to-markdown` | Convert PDFs, Office files, and other documents to Markdown. |
| `doc-coauthoring` | Co-author documentation through context gathering, drafting, and reader testing. |
| `docx` | Create, read, edit, and format Word documents. |
| `google-workspace-convert` | Convert between Google Workspace files and Markdown. |
| `pptx` | Create, read, edit, and reorganize PowerPoint presentations. |
| `xlsx` | Create, read, edit, clean, and convert spreadsheet files. |

### Engineering

| Name | Short description |
| --- | --- |
| `fastapi` | Build and review FastAPI services, routers, schemas, and tests. |
| `go-engineering` | Write, debug, refactor, and review idiomatic Go code. |
| `mcp-builder` | Build high-quality MCP servers for external service integrations. |
| `python-stack` | Apply Python project, tooling, testing, and packaging conventions. |
| `rust-engineering` | Write, debug, refactor, and review idiomatic Rust code. |
| `typescript-engineering` | Write, debug, refactor, and review type-safe TypeScript. |

### Integrations and Media

| Name | Short description |
| --- | --- |
| `confluence-datacenter` | Search, read, create, and update Confluence Data Center pages. |
| `generate-image` | Generate or edit images with Gemini image generation. |
| `jira-datacenter` | Search, read, create, and update Jira Data Center issues. |

### Reachy Mini

| Name | Short description |
| --- | --- |
| `reachy-mini-ai-integration` | Build LLM-driven Reachy Mini robot apps. |
| `reachy-mini-control-loops` | Design real-time Reachy Mini control loops. |
| `reachy-mini-create-app` | Create new Reachy Mini Python apps and publish them. |
| `reachy-mini-debugging` | Troubleshoot Reachy Mini connectivity, daemon, motion, and import issues. |
| `reachy-mini-deep-dive-docs` | Find advanced Reachy Mini SDK, API, and source references. |
| `reachy-mini-interaction-patterns` | Design Reachy Mini antenna, head-motion, and robot-native interactions. |
| `reachy-mini-motion-philosophy` | Choose between `goto_target` and `set_target` motion patterns. |
| `reachy-mini-rest-api` | Control Reachy Mini through REST and WebSocket APIs. |
| `reachy-mini-safe-torque` | Safely enable and disable Reachy Mini motor torque. |
| `reachy-mini-setup-environment` | Prepare local tools and resources for Reachy Mini development. |
| `reachy-mini-symbolic-motion` | Define rhythmic Reachy Mini motion symbolically. |
| `reachy-mini-testing-apps` | Test Reachy Mini apps in simulation and on hardware. |

### Skill Maintenance

| Name | Short description |
| --- | --- |
| `karpathy-guidelines` | Keep coding changes simple, surgical, and goal-driven. |
| `skill-creator` | Create, improve, and evaluate skills. |

## License

MIT
