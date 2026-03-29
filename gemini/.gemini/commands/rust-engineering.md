---
description: Comprehensive Rust engineering guidance for coding agents. Use when writing, reviewing, refactoring, or debugging Rust code; designing crate APIs; resolving ownership, borrowing, lifetime, or trait issues; implementing async/concurrent code with Tokio; improving error handling, testing, performance, memory layout, or file I/O safety; or reviewing Rust pull requests for idioms and footguns. Trigger on Rust, Cargo, rustc, clippy, rustfmt, ownership, lifetimes, traits, enums, tokio, anyhow, thiserror, serde, criterion, and borrow-checker errors.
---


# Rust Engineering

Produce Rust that is safe, explicit, and maintainable under review. Default to stable language features, minimal `unsafe`, narrow APIs, and code that passes formatting, linting, and tests.

## Workflow

1. Identify the artifact.
   Library: optimize for explicit API boundaries, typed errors, docs, and semver-safe design.
   Application or CLI: optimize for operability, context-rich errors, tracing, and clear failure modes.
2. Model types before writing control flow.
   Prefer enums, newtypes, and private fields over ad hoc strings, flags, or loosely related values.
3. Choose ownership deliberately.
   Accept borrowed inputs where practical, return owned outputs when crossing boundaries, and make cloning explicit.
4. Choose the failure model early.
   Libraries usually use `thiserror`; applications usually use `anyhow` at the outer boundary and typed errors internally when helpful.
5. Choose the concurrency model deliberately.
   Use synchronous code unless async is justified by I/O concurrency needs. When async is justified, use Tokio and design cancellation, timeouts, and shutdown explicitly.
6. Verify before finalizing.
   Run `cargo fmt --check`, `cargo clippy --all-targets --all-features`, and relevant tests. Address warnings instead of normalizing them.

## Load References By Need

| Need | Reference |
|---|---|
| Project setup, crate structure, CLI patterns, tracing | `references/workflow.md` |
| Error model, `thiserror` vs `anyhow`, context, path/file failure handling | `references/errors.md` |
| Ownership, API boundaries, newtypes, traits, visibility, serde-facing types | `references/api-and-types.md` |
| Tokio, cancellation, timeouts, shared state, task spawning, async traits | `references/async-and-concurrency.md` |
| Unit/integration/doc/property tests, benchmarks, temp files, review checklist | `references/testing-and-quality.md` |
| Allocation control, data layout, slices, `Cow`, boxing, profiling | `references/performance-and-memory.md` |
| Common footguns and review traps | `references/footguns.md` |

## Default Standards

- Keep `main.rs` and public entrypoints thin; move logic into modules or `lib.rs`.
- Keep struct fields private by default. Expose behavior, not raw state.
- Prefer `&str`, `&[T]`, iterators, and generic bounds over overly concrete argument types.
- Return `Result` for expected failures. Reserve panics for invariant violations and test scaffolding.
- Document every `unsafe` block with a `// SAFETY:` comment describing the invariants.
- Prefer stable language features. Use macros or nightly-only ideas only with a clear reason.
- Prefer typed domain models over magic strings and boolean flags.
- Treat Clippy findings as design feedback, not noise.

## Code Review Checklist

- Are invalid states made unrepresentable with types?
- Are ownership and cloning choices intentional?
- Are error messages actionable and context-rich?
- Is async justified, and are blocking operations kept off the runtime?
- Are file writes atomic where corruption would matter?
- Are string/path operations preserving correctness instead of forcing lossy conversions?
- Are tests covering error paths, edge cases, and externally visible behavior?
- Is there any avoidable `unsafe`, panic, or allocation churn?

## Sources and Influences

This skill synthesizes ideas from the following public Rust skill work rather than copying any one source directly:

- `rust-agentic-skills` by UdapY: https://udapy.github.io/rust-agentic-skills/
- `rust-skills` by leonardomso: https://agent-skills.md/skills/leonardomso/rust-skills/rust-skills
- Mirror for `rust-skills` by leonardomso: https://skills.sh/leonardomso/rust-skills/rust-skills

Use those sources for attribution and broader context; use this skill's references for the repo-specific, agent-oriented structure.
