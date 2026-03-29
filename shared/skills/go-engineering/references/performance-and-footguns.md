# Performance and Footguns

## Performance Defaults

- Optimize after measuring.
- Avoid needless allocations, string formatting, and interface conversions in hot paths.
- Reuse buffers where measurement justifies it.

## Common Footguns

- Interface indirection without consumer value
- Goroutines without shutdown or ownership
- Ignoring wrapped error identity
- Copying large structs accidentally
- Re-slicing or appending without understanding aliasing
- Using reflection where ordinary code is simpler

## Review Heuristics

- If a performance change adds complexity without benchmarks or profiles, reject it.
- If a package hides simple behavior behind layers of interfaces, simplify it.
- If concurrency is present but lifecycle is unclear, treat it as a bug risk.
