# API and Type Design

## Make Invalid States Unrepresentable

- Prefer enums over stringly typed modes.
- Prefer newtypes over raw `String`, `u64`, or `PathBuf` when values have domain meaning.
- Prefer dedicated structs over passing many loosely related parameters.

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Mode {
    DryRun,
    Apply,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UserId(String);
```

## Ownership at Boundaries

- Accept borrowed data where the caller likely already owns it:
  - `&str` over `&String`
  - `&[T]` over `&Vec<T>`
  - `impl AsRef<Path>` for path-like arguments
- Return owned data when values outlive the input or cross abstraction boundaries.
- Make cloning explicit and justified.

## Visibility

- Keep fields private by default.
- Expose constructors, smart constructors, and methods that maintain invariants.
- Use `pub(crate)` for internal sharing before reaching for `pub`.

## Smart Constructors

Validate at the boundary instead of scattering checks:

```rust
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum ParseError {
    #[error("name must not be empty")]
    Empty,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NonEmptyName(String);

impl NonEmptyName {
    pub fn parse(value: impl Into<String>) -> Result<Self, ParseError> {
        let value = value.into();
        if value.trim().is_empty() {
            return Err(ParseError::Empty);
        }
        Ok(Self(value))
    }
}
```

## Traits

- Use traits to express stable behavioral contracts, not to hide concrete types prematurely.
- Prefer generic parameters for static dispatch when the caller benefits from inlining and type information.
- Prefer trait objects when heterogeneous storage or dynamic dispatch is the actual need.
- Keep traits small. Large “god traits” are hard to implement and harder to evolve.

## Serde-Facing Types

- Keep transport structs separate from domain types when validation or invariants differ.
- Parse external data into typed domain models as early as possible.
- Avoid leaking wire-format concerns deep into core logic.

## Review Heuristics

- Replace booleans with enums when the meaning is non-obvious.
- Replace repeated validation with newtypes or smart constructors.
- Replace wide public surfaces with tighter methods and fewer exposed fields.
