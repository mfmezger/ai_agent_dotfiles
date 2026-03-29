# Common Footguns

## UTF-8 String Slicing

- Do not slice strings by arbitrary byte offsets such as `s[..50]`.
- Rust strings are UTF-8; byte slicing can panic or corrupt assumptions.
- Prefer `.chars().take(n).collect::<String>()` or boundary-aware truncation helpers.

## TOCTOU Races

- Do not check then act on files when one atomic operation exists.
- Prefer creating directories directly and handling the result.
- Prefer atomic write patterns with temp files and rename/persist semantics.

## Path Handling

- Do not convert `Path` to `String` just to pass it around.
- Keep `Path` and `PathBuf` in domain logic.
- Use `display()` only for user-facing formatting.

## Panic-Driven Error Handling

- Do not `unwrap()` ordinary I/O, parse, env-var, or network failures.
- Keep panics for invariants and tests.

## Async Lock Misuse

- Do not hold `MutexGuard` or `RwLockWriteGuard` across unrelated `.await` points.
- Do not use `tokio::spawn` for CPU-bound work.

## Overusing `String`, `Vec`, and `Box<dyn Error>`

- Accept borrowed forms where possible.
- Return typed errors from libraries.
- Use dynamic error erasure only at application boundaries or plugin points.

## Unnecessary `unsafe`

- Do not reach for `unsafe` to fight the borrow checker.
- Exhaust safe refactors first: smaller scopes, ownership transfers, helper functions, or different data structures.
- If `unsafe` remains necessary, document invariants with `// SAFETY:` and test them indirectly through public behavior.

## Review Heuristics

- If code relies on lossy conversions, panics on routine failures, or byte-slices text, expect latent bugs.
- If a fix “works” by cloning everywhere or adding `unsafe`, the design likely needs rework.
