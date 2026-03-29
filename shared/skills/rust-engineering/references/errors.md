# Error Handling

## Error Model

- Libraries:
  - Prefer typed errors with `thiserror`.
  - Preserve source errors with `#[from]` and `#[source]`.
  - Document important failure cases with a `# Errors` section on public fallible APIs.
- Applications:
  - Prefer `anyhow::Result` at the outer boundary.
  - Add context with `.context(...)` or `.with_context(...)`.
  - Keep user-facing messages actionable.

## `thiserror` for Libraries

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("failed to read config from {path}")]
    Read {
        path: std::path::PathBuf,
        #[source]
        source: std::io::Error,
    },
    #[error("invalid config value for {field}: {reason}")]
    InvalidField { field: &'static str, reason: String },
}
```

## `anyhow` for Applications

```rust
use anyhow::{Context, Result};

fn load_port(path: &std::path::Path) -> Result<u16> {
    let raw = std::fs::read_to_string(path)
        .with_context(|| format!("failed to read {}", path.display()))?;
    let port = raw
        .trim()
        .parse::<u16>()
        .with_context(|| format!("invalid port in {}", path.display()))?;
    Ok(port)
}
```

## Defaults

- Use `?` for propagation.
- Use `Option` only when absence is expected and non-diagnostic.
- Convert `Option` to `Result` at boundaries that need actionable failure information.
- Avoid `Box<dyn Error>` in libraries unless dynamic polymorphism is the point.

## `unwrap()` and `expect()`

- Do not use `unwrap()` in production paths.
- Use `expect()` only for invariants that indicate programmer error, not environmental failure.
- Tests and one-off setup code may use `expect()` when the message makes the invariant obvious.

## Error Message Style

- Make messages specific and actionable.
- Include the path, key, operation, or identifier that failed.
- Prefer lowercase messages without trailing punctuation inside error values.

## Path and File Failure Handling

- Keep paths as `Path` or `PathBuf`, not lossy strings.
- Use `%path.display()` for presentation only.
- Preserve source errors so callers can distinguish missing files, permission errors, parse failures, and validation failures.

## Review Heuristics

- If callers need branching behavior, use typed errors.
- If the code sits at the process boundary, context-rich `anyhow` is usually enough.
- If the code panics on ordinary I/O or parse failure, the error model is wrong.
