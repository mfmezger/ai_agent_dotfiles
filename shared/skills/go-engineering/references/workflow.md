# Workflow, Packages, and Modules

## Package Shape

- Keep packages small and cohesive.
- Avoid `util` or `common` dumping grounds.
- Export the smallest API that serves consumers.
- Keep application wiring near `main`, not spread through leaf packages.

## Modules

- Prefer one module unless multiple modules solve a real distribution problem.
- Keep `go.mod` tidy and dependencies deliberate.

## Concrete Types First

- Start with structs and functions.
- Add interfaces where callers need substitution, not where implementers want indirection.
- Keep interfaces small and behavior-based.

```go
type Clock interface {
    Now() time.Time
}
```

## API Shape

- Make zero values useful when it does not hide required initialization.
- Prefer constructors when invariants or dependencies matter.
- Keep exported fields rare; prefer methods that preserve invariants.

## Review Heuristics

- Challenge speculative interfaces.
- Challenge package splits that increase import churn without clarifying ownership.
- Challenge exported identifiers that only internal code uses.
