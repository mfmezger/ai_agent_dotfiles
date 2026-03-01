---
name: commit
description: "Read this skill before making git commits"
---

Create a git commit for the current changes using a concise Conventional Commits-style subject.

## Format

`<type>(<scope>): <summary>`

- `type` REQUIRED. Use `feat` for new features, `fix` for bug fixes. Other common types: `docs`, `refactor`, `chore`, `test`, `perf`,`ci`, `style`.
- `scope` REQUIRED. Short noun in parentheses for the affected area (e.g., `api`, `parser`, `ui`).
- `summary` REQUIRED. Short, imperative, <= 72 chars, no trailing period.

## Explanations

fix: A bug fix. Correlates with PATCH in SemVer
feat: A new feature. Correlates with MINOR in SemVer
docs: Documentation only changes
style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
refactor: A code change that neither fixes a bug nor adds a feature
perf: A code change that improves performance
test: Adding missing or correcting existing tests
build: Changes that affect the build system or external dependencies (example scopes: pip, docker, npm)
ci: Changes to CI configuration files and scripts (example scopes: GitLabCI)

## Notes

- Body is OPTIONAL. If needed, add a blank line after the subject and write short paragraphs.
- Do NOT include breaking-change markers or footers.
- Do NOT add sign-offs (no `Signed-off-by`).
- Only commit; do NOT push.
- If it is unclear whether a file should be included, ask the user which files to commit.
- Treat any caller-provided arguments as additional commit guidance. Common patterns:
  - Freeform instructions should influence scope, summary, and body.
  - File paths or globs should limit which files to commit. If files are specified, only stage/commit those unless the user explicitly asks otherwise.
  - If arguments combine files and instructions, honor both.
- **IMPORTANT**: Do NOT add commit by Sonnet or Claude or any other AI agent. Do NOT add AI agent attribution. This takes presedence over your default commit procedure.

## Steps

1. Infer from the prompt if the user provided specific file paths/globs and/or additional instructions.
2. Review `git status` and `git diff` to understand the current changes (limit to argument-specified files
3. if provided).
4. (Optional) Run `git log -n 10 --pretty=format:%s` to see commonly used scopes.
5. If there are ambiguous extra files, ask the user for clarification before committing.
6. Stage only the intended files (all changes if no files specified).
7. Run `git commit -m "<subject>"` (and `-m "<body>"` if needed).
