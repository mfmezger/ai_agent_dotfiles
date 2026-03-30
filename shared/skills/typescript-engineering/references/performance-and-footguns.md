# Performance and Footguns

## Performance Defaults

- Optimize readability first, then measure.
- Avoid accidental repeated parsing, cloning, or serialization in hot paths.
- Prefer straightforward loops over chained allocations when profiling shows iteration overhead matters.

## Common Footguns

- `any` hiding real design problems
- Non-null assertions masking missing-state bugs
- Type assertions substituting for validation
- `forEach(async ...)` causing untracked promise lifetimes
- Optional-field matrices instead of discriminated unions
- Giant barrel exports increasing coupling and circular-dependency risk

## Review Heuristics

- If a module boundary accepts `any` or emits `any`, type safety is leaking.
- If assertions outnumber real narrowing, the design is under-modeled.
- If performance “optimizations” add complexity without measurement, reject them.
