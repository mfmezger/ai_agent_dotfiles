# Concurrency and Context

## Goroutines

- Launch goroutines only with a clear owner and exit condition.
- Avoid goroutine leaks by tying work to context cancellation, closed channels, or explicit shutdown.

## Context

- Pass `context.Context` explicitly as the first parameter for request-scoped or cancelable work.
- Do not store contexts in structs except for carefully justified framework integration.
- Do not use context for optional parameters.

```go
func Fetch(ctx context.Context, client *http.Client, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
    if err != nil {
        return nil, err
    }
    resp, err := client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    if resp.StatusCode < 200 || resp.StatusCode >= 300 {
        return nil, fmt.Errorf("fetch %s: unexpected status %s", url, resp.Status)
    }
    return io.ReadAll(resp.Body)
}
```

## Channels

- Use channels for ownership transfer and coordination, not as a default replacement for every data structure.
- Make close responsibility obvious.
- Prefer buffered channels only when the buffering policy is intentional.

## Coordinated Parallel Work

- Prefer `errgroup` when a set of goroutines should share cancellation and fail fast together.
- Derive the group from an existing context so cancellation propagates predictably.

```go
g, ctx := errgroup.WithContext(ctx)

for _, url := range urls {
    url := url
    g.Go(func() error {
        _, err := Fetch(ctx, client, url)
        return err
    })
}

if err := g.Wait(); err != nil {
    return fmt.Errorf("fetch group: %w", err)
}
```

## Review Heuristics

- If a goroutine can outlive the request without a reason, it may leak.
- If a channel can be closed from multiple places, ownership is unclear.
- If concurrency increases complexity without measurable benefit, simplify it.
