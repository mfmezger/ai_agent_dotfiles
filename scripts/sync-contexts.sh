#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-write}"
SHARED_CONTEXT="$ROOT_DIR/shared/context/default-coding-guidelines.md"

if [[ "$MODE" != "write" && "$MODE" != "--check" ]]; then
  echo "Usage: $0 [--check]"
  exit 1
fi

if [[ ! -f "$SHARED_CONTEXT" ]]; then
  echo "Error: Shared context source not found at $SHARED_CONTEXT"
  exit 1
fi

write_or_check_file() {
  local generated_file="$1"
  local target_file="$2"

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
    mkdir -p "$(dirname "$target_file")"
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
- Invoke `/karpathy-guidelines` skill to explicitly apply stricter coding discipline.
EOF
      ;;
    opencode|codex|pi)
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
      echo "Unknown tool: $tool" >&2
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
    opencode)
      title="# OpenCode User-Level Guidelines"
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
      echo "Unknown tool: $tool" >&2
      return 1
      ;;
  esac

  {
    printf '%s\n\n' "$title"
    printf '%s\n\n' "$intro"
    printf '<!-- Generated from `shared/context/default-coding-guidelines.md` via `./scripts/sync-contexts.sh`. -->\n\n'
    awk 1 "$SHARED_CONTEXT"
    printf '\n'
    render_notes "$tool"
    printf '\n'
  } > "$output_file"
}

sync_failed=0

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

tool_targets=(
  "claude:claude/.claude/CLAUDE.md"
  "opencode:opencode/.config/opencode/AGENTS.md"
  "codex:codex/.codex/AGENTS.md"
  "pi:pi/.pi/agent/AGENTS.md"
  "gemini:gemini/.gemini/GEMINI.md"
)

for entry in "${tool_targets[@]}"; do
  tool="${entry%%:*}"
  target="${entry#*:}"
  temp_file="$tmp_dir/${tool}-$(basename "$target")"

  render_context "$tool" "$temp_file"
  if ! write_or_check_file "$temp_file" "$ROOT_DIR/$target"; then
    sync_failed=1
  fi
done

if [[ "$MODE" == "--check" ]]; then
  if [[ "$sync_failed" -ne 0 ]]; then
    echo "Context sync check failed."
    exit 1
  fi
  echo "All shared context files are in sync."
else
  echo "Context sync complete."
fi
