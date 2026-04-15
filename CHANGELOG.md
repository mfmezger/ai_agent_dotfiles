## v0.4.0 (2026-04-15)

### Feat

- **skills**: add Reachy Mini, Rust, FastAPI, Python, Go, and TypeScript skills
- **skills**: centralize shared skills and sync mappings across Claude, Codex, Gemini, and pi
- **github-pr**: rename the GitHub skill to `github-pr`
- **gemini**: symlink shared skills into Gemini CLI
- **opencode**: symlink new shared skills and link the commit skill
- **codex**: allow GitHub CLI in default rules
- **pi**: track portable pi settings in the repo

### Fix

- **install**: handle Stow conflicts more reliably
- **skills**: prefix Reachy Mini skill names consistently
- **rust-engineering**: address review feedback

## v0.3.0 (2026-02-12)

### Feat

- **opencode**: link commit skill from claude config
- **commit**: adding a skill for commiting
- **linking**: opencode skills now are linked to the claude skills to avoid duplication
- **claudeskills**: adding claude skills for confluence and jira
- Add refactorer and detective agents

### Fix

- **generate-image**: force reload of environment variables

## v0.2.0 (2026-02-07)

### Feat

- consolidate AI agent configs from old dotfiles
- **init**: first version
