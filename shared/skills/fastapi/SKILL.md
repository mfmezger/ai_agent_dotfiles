---
name: fastapi
description: "FastAPI application design and implementation conventions. Use this skill when building, updating, or reviewing FastAPI services, routers, dependencies, request/response schemas, streaming endpoints, or API tests. Trigger on FastAPI-specific work such as path operation design, dependency injection, response models, `Annotated` parameters, `fastapi` CLI usage, SQLModel-backed APIs, or refactoring older FastAPI code to current patterns."
---

# FastAPI Conventions

Assume the general Python tooling conventions from the `python-stack` skill. This skill only covers FastAPI-specific patterns.

## App Layout

Prefer a small, explicit structure:

```text
src/<package>/
  main.py
  routers/
    __init__.py
    items.py
  dependencies.py
  schemas.py
  models.py
  settings.py
```

- Keep the ASGI app in `main.py`
- Group path operations into routers by bounded area
- Put shared dependency helpers in `dependencies.py`
- Keep request/response schemas separate from persistence models when that improves clarity

## Running the App

Prefer the FastAPI CLI over invoking Uvicorn directly.

```bash
uv run fastapi dev src/<package>/main.py
uv run fastapi run src/<package>/main.py
```

If the project has a stable app entrypoint, prefer configuring it in `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "src.<package>.main:app"
```

## Path Operations

Use one HTTP operation per function. Do not collapse multiple methods into a single handler.

Use `Annotated` for request parameters and dependencies:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

router = APIRouter(prefix="/items", tags=["items"])

ItemId = Annotated[int, Path(ge=1)]
SearchQuery = Annotated[str | None, Query(max_length=100)]


@router.get("/{item_id}")
async def get_item(item_id: ItemId, q: SearchQuery = None) -> dict[str, str | int | None]:
    return {"item_id": item_id, "q": q}
```

- Prefer reusable type aliases for common dependencies and parameter declarations
- Do not use `...` as a required marker in FastAPI parameters or Pydantic fields
- Do not use `@app.api_route(..., methods=[...])` unless there is a strong reason

## Request and Response Models

Declare response types deliberately.

- Prefer a concrete return type when the returned value already matches the public schema
- Use `response_model=` when the runtime return value differs from the public schema
- Treat response models as a data-exposure boundary; never return raw internal models that contain secrets or extra fields
- Prefer regular Pydantic models or standard typed containers over `RootModel`

Example:

```python
from pydantic import BaseModel


class ItemOut(BaseModel):
    id: int
    name: str


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: ItemId) -> dict[str, object]:
    return {"id": item_id, "name": "example", "internal_flag": True}
```

## Routers and Dependencies

Put router metadata on the router itself, not on `include_router()`:

```python
router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(require_session)],
)
```

- Apply shared dependencies at the router level when every route needs them
- Use dependency functions for external resources, auth, request-scoped state, and cleanup via `yield`
- Keep dependencies small and composable; do not bury business logic in them

## Sync vs Async

Use `async def` only when the whole call path is async-safe and awaited correctly.

- Use `async def` for async database drivers, async HTTP clients, and other non-blocking libraries
- Use plain `def` for blocking libraries or when in doubt
- Do not call blocking code from an async path operation or dependency

This is stricter than "I/O-bound means async". The deciding factor is whether the libraries you call are actually async.

## Persistence

When building a typical FastAPI CRUD service, prefer SQLModel first because it fits the rest of this stack well.

- Use SQLModel for straightforward application models and CRUD APIs
- Fall back to SQLAlchemy when advanced ORM mapping or separation from Pydantic models is more important
- Keep API schemas separate from DB models once the shapes start to diverge

## Settings and Lifespan

- Use `pydantic-settings` for app configuration
- Prefer FastAPI lifespan handlers for startup/shutdown wiring instead of older event patterns when possible
- Construct expensive shared clients once during lifespan or via well-scoped dependencies, not inside each request handler

## Testing

Use `pytest` with FastAPI's testing tools.

- Use `TestClient` for sync tests
- Use `httpx.AsyncClient` for async integration tests
- Override dependencies in tests instead of patching deep internals when possible
- Test both happy-path and validation/error responses

## Streaming and Background Work

- Use `StreamingResponse` for byte streams
- Use Server-Sent Events only when the user explicitly needs push-style updates
- Keep background work explicit; use `BackgroundTasks` only for small in-process tasks, not for durable job processing

## Review Heuristics

When reviewing FastAPI code, look for:

- Missing or weak response models
- Blocking work inside async handlers
- Dependencies that hide too much business logic
- Routers assembled inconsistently
- Raw ORM models leaking through the API boundary
- Old parameter style without `Annotated`

## Sources

- Official FastAPI repository: https://github.com/fastapi/fastapi
