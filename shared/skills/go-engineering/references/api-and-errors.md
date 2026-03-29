# API Design and Errors

## Errors

- Return errors explicitly.
- Wrap errors with `%w` so callers can use `errors.Is` and `errors.As`.
- Use sentinel errors sparingly and only for meaningful branching behavior.

```go
var ErrNotFound = errors.New("not found")

func Load(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read %s: %w", path, err)
    }
    return data, nil
}
```

Use `errors.Is` and `errors.As` at call sites instead of string matching:

```go
data, err := Load(path)
if err != nil {
    if errors.Is(err, fs.ErrNotExist) {
        return nil, ErrNotFound
    }

    var pathErr *fs.PathError
    if errors.As(err, &pathErr) {
        return nil, fmt.Errorf("path failure on %s: %w", pathErr.Path, err)
    }

    return nil, err
}
```

## Concrete Types vs Interfaces

- Accept interfaces when the caller already has one.
- Return concrete types when the implementation details are stable and useful.
- Avoid defining interfaces on the producer side without consumer pressure.

## Zero Values and Constructors

- Make zero values valid when possible.
- Use constructors when dependencies, invariants, or background resources are required.

## Review Heuristics

- If an interface has one implementation and no consumer need, remove it.
- If error messages omit the operation or identifier, diagnostics are weak.
- If sentinels proliferate without real branching use, the error model is too loose.
