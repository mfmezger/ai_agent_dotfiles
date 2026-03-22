---
name: python-stack
description: "Standard Python engineering stack and tooling conventions. Use this skill whenever starting a new Python project, setting up dependencies, configuring linting/testing/CI, choosing between frameworks or libraries, or when the user asks about Python project structure, tooling choices, or best practices. Also trigger when the user mentions any of these tools: uv, ruff, ty, pytest, FastAPI, SQLModel, SQLAlchemy, Pydantic, Typer, commitizen, or pre-commit in a Python context."
---

# Python Engineering Stack

Standard tooling and conventions for Python projects. When making recommendations or scaffolding projects, prefer these tools over alternatives unless the user explicitly requests otherwise.

## Package and Dependency Management

**uv** is the standard package and dependency manager. It replaces pip, Poetry, and Conda.

- Use `uv init` to scaffold new projects
- Use `uv add <package>` to add dependencies (not `pip install`)
- Use `uv sync` to install from lockfile
- Use `uv run` to execute scripts/commands in the project environment
- `pyproject.toml` is the single source of truth for project metadata and dependencies

## Code Quality

### Data Validation — Pydantic

Use Pydantic models for all data validation and serialization. Prefer Pydantic v2 APIs.

### Linting and Formatting — Ruff

Ruff is the standard linter and formatter (replaces Black, isort, flake8, pylint).

- Configure in `pyproject.toml` under `[tool.ruff]`
- Use `ruff check` for linting, `ruff format` for formatting
- Typical config:

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]
```

### Static Type Checking — ty

ty is the standard type checker.

### Pre-commit

pre-commit is the standard framework for enforcing checks before committing. A typical `.pre-commit-config.yaml` includes hooks for ruff (lint + format) and ty.

## Testing

**pytest** is the standard testing framework.

- Place tests in a `tests/` directory
- Use `uv run pytest` to run tests
- Use fixtures, parametrize, and clear test naming (`test_<what>_<condition>_<expected>`)

## Git and CI/CD Workflow

### Commit Messages — Conventional Commits via Commitizen

- Follow Conventional Commits format: `<type>(<scope>): <summary>`
- Use **Commitizen** (`cz commit`) to enforce this standard
- Configure in `pyproject.toml`:

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version_provider = "pep621"
update_changelog_on_bump = true
```

## API Frameworks

**FastAPI** is the standard framework for REST services.

- Use Pydantic models for request/response schemas
- Use dependency injection for shared resources
- Structure with routers for modularity

## ORM

| Need | Tool |
|---|---|
| ORM for FastAPI projects | **SQLModel** (combines Pydantic + SQLAlchemy) |
| ORM with advanced features or decoupled from Pydantic | **SQLAlchemy** |

Prefer SQLModel for new FastAPI projects. Fall back to SQLAlchemy when you need advanced ORM features or want to decouple from Pydantic.

## Configuration Management

**Pydantic Settings** (`pydantic-settings`) is the standard for configuration and settings management. Use `BaseSettings` with environment variable loading.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")
```

## CLI Frameworks

When a CLI is needed:

- **Typer** — recommended (built on Click, uses type hints)
- **Click** — standard alternative

## Quick Reference: New Project Setup

```bash
uv init my-project
cd my-project
uv add ruff pytest pydantic
# For API projects:
uv add fastapi uvicorn sqlmodel pydantic-settings
# Set up pre-commit:
uv add --dev pre-commit commitizen
uv run pre-commit install
```
