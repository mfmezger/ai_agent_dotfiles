# Workflow and Project Shape

## Crate Shape

- Keep binaries thin. Put reusable logic in `lib.rs` or dedicated modules.
- Split by responsibility, not by pattern repetition. Avoid `utils.rs` dumping grounds.
- Prefer one obvious entrypoint per concern: parsing, validation, domain logic, I/O, persistence.
- Keep public API surface narrow. Start private, then widen intentionally.

## Dependency Choices

- Prefer the standard library until a crate removes real complexity.
- Add crates for clear leverage:
  - `thiserror` for library-facing typed errors
  - `anyhow` for application boundaries and operator-facing failures
  - `serde` for serialization
  - `tokio` for async I/O concurrency
  - `tracing` and `tracing-subscriber` for diagnostics
  - `tempfile` for atomic writes and isolated tests
  - `criterion` for benchmarks when hot paths matter
  - `proptest` for property-based tests on invariants

## Binary Pattern

Use a thin `main()` that delegates to `run()`:

```rust
fn main() {
    if let Err(err) = run() {
        eprintln!("{err:#}");
        std::process::exit(1);
    }
}

fn run() -> anyhow::Result<()> {
    // parse config / args
    // initialize tracing once
    // call domain logic
    Ok(())
}
```

- Initialize tracing once in the binary, not in libraries.
- Return rich errors from `run()`. Convert them to user-facing output at the process boundary.

## Tracing

- Use `tracing` for structured diagnostics instead of ad hoc `println!` debugging in production code.
- Include stable fields such as IDs, paths, operation names, and durations.
- Log at boundaries. Avoid noisy logs in tight loops unless diagnosing a specific issue.

```rust
use tracing::{error, info};

info!(path = %path.display(), "loading config");
error!(error = %err, "configuration failed");
```

## File I/O Safety

- Create parent directories before writing.
- Use atomic writes for config, cache, state, or generated files that must not be partially written.
- Prefer `tempfile` plus `persist()` over writing directly to the target path.

```rust
use std::fs;
use std::io::Write;

fn write_atomic(path: &std::path::Path, contents: &[u8]) -> anyhow::Result<()> {
    let parent = path.parent().ok_or_else(|| anyhow::anyhow!("missing parent directory"))?;
    fs::create_dir_all(parent)?;

    let mut temp = tempfile::NamedTempFile::new_in(parent)?;
    temp.write_all(contents)?;
    temp.flush()?;
    temp.persist(path)?;
    Ok(())
}
```

## Review Heuristics

- Challenge duplicated parsing, validation, and conversion logic.
- Challenge broad `pub` visibility.
- Challenge application logic hiding in `main.rs`.
- Challenge direct file writes when interruption could corrupt state.
