# Testing and Quality

## Test Mix

- Unit tests for local behavior and edge cases
- Table-driven tests for input/output matrices
- Integration tests for package boundaries
- Benchmarks for hot paths
- Fuzzing for parsers, codecs, and stateful edge cases when relevant

## Table-Driven Tests

```go
func TestParsePort(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    int
        wantErr bool
    }{
        {name: "ok", input: "8080", want: 8080},
        {name: "empty", input: "", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParsePort(tt.input)
            if tt.wantErr {
                if err == nil {
                    t.Fatal("expected error")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if got != tt.want {
                t.Fatalf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

## Test Hygiene

- Use `t.Helper()` in helpers.
- Use `t.TempDir()` for filesystem isolation.
- Keep benchmarks realistic and avoid benchmarking setup noise.

## Fuzzing

- Use fuzz tests for parsers, decoders, normalization logic, and state transitions that must not panic.
- Seed fuzzers with realistic edge cases, then let the engine mutate from there.

```go
func FuzzParsePort(f *testing.F) {
    f.Add("8080")
    f.Add("")
    f.Add("999999")

    f.Fuzz(func(t *testing.T, input string) {
        _, _ = ParsePort(input)
    })
}
```

## Review Heuristics

- If a bug fix lacks a regression test, ask why.
- If tests share global temp paths or process state, reliability is weak.
- If benchmarks exist without a real performance question, they are probably noise.
