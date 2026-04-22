#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-write}"
SHARED_CONTEXT="$ROOT_DIR/shared/context/default-coding-guidelines.md"

if [[ "$MODE" != "write" && "$MODE" != "--check" ]]; then
  echo "Usage: $0 [--check]"
  exit 1
fi

write_or_check_file() {
  local generated_file="$1"
  local target_file="$2"

  mkdir -p "$(dirname "$target_file")"

  if [[ "$MODE" == "--check" ]]; then
    if [[ ! -f "$target_file" ]]; then
      echo "Missing target: $target_file"
      return 1
    fi
    if ! cmp -s "$generated_file" "$target_file"; then
      echo "Out of sync: $target_file"
      return 1
    fi
  else
    cp "$generated_file" "$target_file"
    echo "Updated: $target_file"
  fi

  return 0
}

render_notes() {
  local tool="$1"

  case "$tool" in
    claude)
      cat <<'EOF'
## Tool Notes

- Project-specific guidance should live in each project's `.claude/CLAUDE.md`.

@RTK.md
EOF
      ;;
    codex)
      cat <<'EOF'
## Tool Notes

- Project-specific guidance should live in repository `AGENTS.md` files.
EOF
      ;;
    pi)
      cat <<'EOF'
## Tool Notes

- Project-specific guidance should live in repository `AGENTS.md` files.
EOF
      ;;
    gemini)
      cat <<'EOF'
## Tool Notes

- Project-specific guidance should live in repository `GEMINI.md` files.
EOF
      ;;
    *)
      echo "Unknown tool: $tool"
      return 1
      ;;
  esac
}

render_context() {
  local tool="$1"
  local output_file="$2"
  local title
  local intro

  case "$tool" in
    claude)
      title="# Claude Code User-Level Guidelines"
      intro="This file provides global context and guidelines that apply across all projects."
      ;;
    codex)
      title="# Codex CLI User-Level Guidelines"
      intro="This file provides global instructions and preferences that apply across all projects."
      ;;
    pi)
      title="# pi User-Level Guidelines"
      intro="This file provides global context and guidelines that apply across all projects."
      ;;
    gemini)
      title="# Gemini CLI User-Level Guidelines"
      intro="This file provides global context and guidelines that apply across all projects."
      ;;
    *)
      echo "Unknown tool: $tool"
      return 1
      ;;
  esac

  {
    printf '%s\n\n' "$title"
    printf '%s\n\n' "$intro"
    printf '<!-- Generated from `shared/context/default-coding-guidelines.md` via `./scripts/sync-contexts.sh`. -->\n\n'
    cat "$SHARED_CONTEXT"
    printf '\n\n'
    render_notes "$tool"
    printf '\n'
  } > "$output_file"
}

sync_failed=0

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

render_context claude "$tmp_dir/CLAUDE.md"
if ! write_or_check_file "$tmp_dir/CLAUDE.md" "$ROOT_DIR/claude/.claude/CLAUDE.md"; then
  sync_failed=1
fi

render_context codex "$tmp_dir/AGENTS.codex.md"
if ! write_or_check_file "$tmp_dir/AGENTS.codex.md" "$ROOT_DIR/codex/.codex/AGENTS.md"; then
  sync_failed=1
fi

render_context pi "$tmp_dir/AGENTS.pi.md"
if ! write_or_check_file "$tmp_dir/AGENTS.pi.md" "$ROOT_DIR/pi/.pi/agent/AGENTS.md"; then
  sync_failed=1
fi

render_context gemini "$tmp_dir/GEMINI.md"
if ! write_or_check_file "$tmp_dir/GEMINI.md" "$ROOT_DIR/gemini/.gemini/GEMINI.md"; then
  sync_failed=1
fi

if [[ "$MODE" == "--check" ]]; then
  if [[ "$sync_failed" -ne 0 ]]; then
    echo "Context sync check failed."
    exit 1
  fi
  echo "All shared context files are in sync."
else
  echo "Context sync complete."
fi
