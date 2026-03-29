# Testing and Quality

## Verification Commands

Run the smallest relevant set, then the full gate before finalizing:

```bash
cargo fmt --check
cargo clippy --all-targets --all-features
cargo test
```

Add as needed:

```bash
cargo test --doc
cargo test <name>
cargo bench
```

## Test Mix

- Unit tests for local invariants and branch behavior
- Integration tests for public behavior and end-to-end flows
- Doc tests for public examples
- Property-based tests for invariants and parser/state-machine edge cases
- Benchmarks only for code that matters to latency or throughput

## Good Test Targets

- Error paths, not just happy paths
- Boundary values and empty inputs
- Parsing and validation failures
- Idempotency and round-trip properties
- Concurrency shutdown and timeout behavior

## Temp Files and Directories

- Use `tempfile` for isolated tests.
- Avoid shared hard-coded paths in `/tmp`.
- Use atomic-write helpers in tests the same way production code does.

## Property-Based Testing

Use `proptest` when logic has invariants worth exploring across many generated inputs:

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn reversing_twice_returns_original(s in ".*") {
        let reversed: String = s.chars().rev().collect();
        let restored: String = reversed.chars().rev().collect();
        prop_assert_eq!(s, restored);
    }
}
```

## Benchmarking

- Use `criterion` for microbenchmarks and hot-path comparisons.
- Benchmark realistic workloads, not toy inputs.
- Profile before optimizing and confirm the optimization actually matters.

## Review Heuristics

- If a bug fix lacks a regression test, ask why.
- If a parser or state machine lacks malformed-input tests, coverage is incomplete.
- If tests depend on global temp paths, real clocks, or network access without a reason, reliability is weak.
