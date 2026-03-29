---
description: Standard Python engineering stack and tooling conventions. Use this skill whenever starting a new Python project, setting up dependencies, configuring linting/testing/CI, choosing between frameworks or libraries, or when the user asks about Python project structure, tooling choices, or best practices. Also trigger when the user mentions any of these tools: uv, uvx, ruff, ty, pytest, FastAPI, SQLModel, SQLAlchemy, Pydantic, Typer, loguru, prek, or pre-commit in a Python context.
---


# Python Engineering Stack

Standard tooling and conventions for Python projects. When making recommendations or scaffolding projects, prefer these tools over alternatives unless the user explicitly requests otherwise.

## Python Version

Use **Python 3.13** or **3.14**. Target the latest stable release for new projects.

## Package and Dependency Management

**uv** is the standard package and dependency manager. It replaces pip, Poetry, and Conda.

- Use `uv init` to scaffold new projects
- Use `uv add <package>` to add dependencies (not `pip install`)
- Use `uv sync` to install from lockfile
- Use `uv run` to execute scripts/commands in the project environment
- Use `uvx` to run CLI tools without installing them (e.g., `uvx ruff check`, `uvx ty`)
- `pyproject.toml` is the single source of truth for project metadata and dependencies

## Coding Standards

### MUST DO

- Type hints for all function signatures and class attributes
- Use `X | None` instead of `Optional[X]` (Python 3.10+)
- PEP 8 compliance (enforced via ruff)
- Comprehensive docstrings in Google style for public APIs
- Test coverage exceeding 90% with pytest
- Async/await for I/O-bound operations
- Dataclasses over manual `__init__` methods (or Pydantic models when validation is needed)
- Context managers for resource handling

### MUST NOT DO

- Skip type annotations on public APIs
- Use mutable default arguments
- Mix sync and async code improperly
- Ignore ty errors in strict mode
- Use bare `except:` clauses
- Hardcode secrets or configuration (use pydantic-settings)
- Use deprecated stdlib modules (use `pathlib` not `os.path`)

## Code Quality

### File Paths — pathlib

Always use `pathlib.Path` for file and directory operations. Do not use `os.path` or string manipulation for paths.

### Console Output — Rich

Use **Rich** for terminal output, including formatted text, tables, and progress bars. Use `rich.progress` as the default for progress indicators.

### Logging — Loguru

Use **Loguru** for application logging. Prefer structured, contextual logs over ad hoc `print()` debugging.

- Add `loguru` as a dependency when the project needs logging
- Create module-level loggers with `from loguru import logger`
- Bind contextual fields for request IDs, user IDs, job IDs, and similar metadata
- Use stdlib `logging` only when required by a framework or library integration

### Data Validation — Pydantic

Use Pydantic models for all data validation and serialization. Prefer Pydantic v2 APIs.

### Linting and Formatting — Ruff

Ruff is the standard linter and formatter (replaces Black, isort, flake8, pylint).

- Configure in `ruff.toml` (not `pyproject.toml`)
- Use `ruff check` for linting, `ruff format` for formatting
- Typical `ruff.toml`:

```toml
target-version = "py313"
line-length = 120

[lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "RUF"]
```

### Static Type Checking — ty

ty is the standard type checker.

### Pre-commit — prek

**prek** is the standard pre-commit framework (replaces `pre-commit`). It uses the same `.pre-commit-config.yaml` format but is faster and written in Rust.

- Install with `uvx prek install`
- Uses the same `.pre-commit-config.yaml` config file
- A typical config includes hooks for ruff (lint + format) and ty
- Reference example: [conversational-agent-langchain/.pre-commit-config.yaml](https://github.com/mfmezger/conversational-agent-langchain/blob/migrate-precommit-to-prek-7280253721743533025/.pre-commit-config.yaml)

## Testing

**pytest** is the standard testing framework.

- Place tests in a `tests/` directory
- Use `uv run pytest` to run tests
- Use fixtures, parametrize, and clear test naming (`test_<what>_<condition>_<expected>`)

### Snapshot Testing — inline-snapshot

Use **inline-snapshot** for snapshot/golden-master testing. Snapshots live directly in the test source code, not in separate files.

```python
from inline_snapshot import snapshot

def test_example():
    assert 1 + 1 == snapshot(2)
```

- Write tests with empty `snapshot()` calls, then run `pytest --inline-snapshot=create` to fill them in
- Run `pytest --inline-snapshot=fix` to update stale snapshots after code changes
- Review changes with `git diff` before committing

### HTTP Recording — pytest-recording

Use **pytest-recording** (built on VCR.py) to record and replay HTTP interactions in tests, avoiding live API calls in CI.

- Mark tests with `@pytest.mark.vcr` to record/replay HTTP cassettes
- Cassettes are stored in `tests/cassettes/` by default
- Re-record with `pytest --vcr-record=all`

## Git Workflow

### Commit Messages — Conventional Commits

Follow the Conventional Commits format: `<type>(<scope>): <summary>`

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`.

See the `/commit` skill for the full commit workflow.

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
from pydantic import SettingsConfigDict
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
uv add ruff pytest inline-snapshot pytest-recording pydantic rich loguru
# For API projects:
uv add fastapi uvicorn sqlmodel pydantic-settings
# Set up prek:
uvx prek install
```
