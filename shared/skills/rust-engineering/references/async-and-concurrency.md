# Async and Concurrency

## When to Use Async

- Use async when coordinating many concurrent I/O operations.
- Do not use async by default for simple CPU-bound or single-step programs.
- Prefer synchronous code until async clearly simplifies concurrency or throughput.

## Tokio Defaults

- Use Tokio as the default runtime when async is justified.
- Keep blocking file I/O, compression, CPU-heavy parsing, and similar work off the async executor.
- Use `spawn_blocking` for blocking work.

```rust
let parsed = tokio::task::spawn_blocking(move || parse_large_file(bytes)).await??;
```

## Timeouts and Cancellation

- Add timeouts around external I/O and shutdown-sensitive operations.
- Design explicit cancellation or shutdown paths for background tasks.
- Always handle `JoinHandle` results.

```rust
use std::time::Duration;

let response = tokio::time::timeout(Duration::from_secs(5), client.fetch())
    .await
    .map_err(|_| Error::Timeout)??;
```

## Shared State

- Prefer message passing when practical.
- Use `Arc<T>` for shared immutable state.
- Use `Arc<Mutex<T>>` or `Arc<RwLock<T>>` only when shared mutable state is justified.
- Never hold an async lock across expensive work or unrelated `.await` points.

## Spawning

- Use `tokio::spawn` for async tasks that are non-blocking and `Send`.
- Do not use `tokio::spawn` for CPU-bound work just because it is concurrent.
- Bound task growth. Unbounded spawning is a production failure mode.

## Async Traits

- Prefer native trait methods and concrete async functions where that keeps the design simple.
- Use `async fn` in traits on stable Rust when the trait is internal and the tradeoffs are acceptable.
- Use `async-trait` only when it solves a real ergonomics problem and the allocation/object-safety tradeoffs are acceptable.

## Review Heuristics

- If the code uses async but performs mostly blocking work, simplify it or isolate the blocking work.
- If background tasks lack shutdown, timeout, or join handling, the design is incomplete.
- If shared mutable state dominates the design, reconsider channels or ownership boundaries.
