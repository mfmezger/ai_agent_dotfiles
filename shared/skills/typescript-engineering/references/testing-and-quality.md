# Testing and Quality

## Test Mix

- Unit tests for pure logic, parsing, and edge cases
- Integration tests for module boundaries and public behavior
- Component tests for interactive TSX behavior
- End-to-end tests only where the user workflow matters

## Good Targets

- Runtime validation failures
- Union narrowing and impossible-state prevention
- Error propagation and async failure behavior
- Serialization and deserialization boundaries
- Public API behavior across representative inputs

## Mocks and Fixtures

- Prefer realistic fixtures over deeply coupled mocks.
- Mock infrastructure boundaries, not every helper.
- Keep fixtures typed so they fail when contracts drift.

## Review Heuristics

- If a type-level invariant has no runtime test where it matters, coverage is incomplete.
- If tests rely on `as any`, they are probably bypassing the exact behavior that needs verification.
- If snapshots are huge, assert more intentionally.
