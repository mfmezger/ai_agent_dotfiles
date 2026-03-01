#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-write}"

if [[ "$MODE" != "write" && "$MODE" != "--check" ]]; then
  echo "Usage: $0 [--check]"
  exit 1
fi

ensure_skill_symlink() {
  local skill_name="$1"
  local target="$2"
  local rel_target="../../../shared/skills/$skill_name"

  mkdir -p "$(dirname "$target")"

  if [[ "$MODE" == "--check" ]]; then
    if [[ ! -L "$target" ]]; then
      echo "Out of sync: $target is not a symlink"
      return 1
    fi
    local actual
    actual="$(readlink "$target")"
    if [[ "$actual" != "$rel_target" ]]; then
      echo "Out of sync: $target -> $actual (expected $rel_target)"
      return 1
    fi
  else
    rm -rf "$target"
    ln -s "$rel_target" "$target"
    echo "Updated: $target"
  fi

  return 0
}

render_gemini_command() {
  local source_file="$1"
  local output_file="$2"
  local skill_name="$3"

  local description
  description="$(awk '
    BEGIN { in_frontmatter = 0 }
    /^---$/ && in_frontmatter == 0 { in_frontmatter = 1; next }
    /^---$/ && in_frontmatter == 1 { exit }
    in_frontmatter == 1 && $1 == "description:" {
      sub(/^description:[[:space:]]*/, "", $0)
      gsub(/^"|"$/, "", $0)
      print
    }
  ' "$source_file")"

  {
    echo "---"
    echo "description: ${description:-Reusable workflow command}"
    echo "---"
    echo
    awk '
      BEGIN { in_frontmatter = 0; finished_frontmatter = 0 }
      /^---$/ && in_frontmatter == 0 {
        in_frontmatter = 1
        next
      }
      /^---$/ && in_frontmatter == 1 {
        in_frontmatter = 0
        finished_frontmatter = 1
        next
      }
      finished_frontmatter == 1 { print }
    ' "$source_file" \
      | sed "1s/^# .*/# ${skill_name^} Workflow Command/" \
      | sed "s/This skill guides/This command guides/"
  } > "$output_file"
}

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

cleanup_stale_links() {
  local skills_dir="$1"
  local failed=0

  mkdir -p "$skills_dir"

  for entry in "$skills_dir"/*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    local name
    name="$(basename "$entry")"
    if [[ ! -d "$ROOT_DIR/shared/skills/$name" ]]; then
      if [[ "$MODE" == "--check" ]]; then
        echo "Stale entry: $entry"
        failed=1
      else
        rm -rf "$entry"
        echo "Removed stale: $entry"
      fi
    fi
  done

  return "$failed"
}

sync_failed=0

for source_file in "$ROOT_DIR"/shared/skills/*/SKILL.md; do
  [[ -f "$source_file" ]] || continue

  skill_dir="$(dirname "$source_file")"
  skill_name="$(basename "$skill_dir")"
  tmp_dir="$(mktemp -d)"

  if ! ensure_skill_symlink "$skill_name" \
    "$ROOT_DIR/claude/.claude/skills/$skill_name"; then
    sync_failed=1
  fi

  if ! ensure_skill_symlink "$skill_name" \
    "$ROOT_DIR/codex/.codex/skills/$skill_name"; then
    sync_failed=1
  fi

  if ! ensure_skill_symlink "$skill_name" \
    "$ROOT_DIR/gemini/.gemini/skills/$skill_name"; then
    sync_failed=1
  fi

  render_gemini_command "$source_file" "$tmp_dir/gemini.md" "$skill_name"
  if ! write_or_check_file "$tmp_dir/gemini.md" \
    "$ROOT_DIR/gemini/.gemini/commands/$skill_name.md"; then
    sync_failed=1
  fi

  rm -rf "$tmp_dir"
done

if ! cleanup_stale_links "$ROOT_DIR/claude/.claude/skills"; then
  sync_failed=1
fi
if ! cleanup_stale_links "$ROOT_DIR/codex/.codex/skills"; then
  sync_failed=1
fi
if ! cleanup_stale_links "$ROOT_DIR/gemini/.gemini/skills"; then
  sync_failed=1
fi

if [[ "$MODE" == "--check" ]]; then
  if [[ "$sync_failed" -ne 0 ]]; then
    echo "Skill sync check failed."
    exit 1
  fi
  echo "All shared skills, symlinks, and generated commands are in sync."
else
  echo "Skill sync complete."
fi
