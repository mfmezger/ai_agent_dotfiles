# Performance and Memory

## Default Posture

- Optimize correctness and clarity first, then profile.
- Remove avoidable allocations and cloning in hot paths.
- Use the type system and ownership model to express zero-copy paths where they help.

## Common Wins

- Pre-allocate with `Vec::with_capacity`, `String::with_capacity`, or `HashMap::with_capacity` when sizes are known.
- Accept slices and iterators instead of forcing owned collections.
- Use `Cow<'a, str>` or `Cow<'a, [T]>` when ownership is conditional.
- Box large enum variants when aggregate type size matters.
- Prefer stack-friendly or small-buffer structures only when measurement justifies them.

## API Choices That Affect Performance

- `&str` over `String` for borrowed input
- `&[u8]` over `Vec<u8>` for borrowed binary input
- `impl AsRef<Path>` for flexible path parameters
- Iterators for transformations instead of allocating intermediate collections unnecessarily

## Layout and Allocation

- Be aware of enum and struct size when values are stored in large collections.
- Avoid repeated format/parse/clone churn in loops.
- Reuse buffers where it materially reduces allocation pressure.

## Measure, Then Change

- Use `criterion` for comparisons.
- Use profiling tools before claiming a bottleneck.
- Confirm the bottleneck is on a user-visible or cost-relevant path.

## Review Heuristics

- If cloning appears in a hot loop, question it.
- If a function takes ownership but only reads, question it.
- If optimization adds complexity without measurement, reject it.
