# React and TSX

## Props and State

- Model props as narrow contracts, not pass-through bags.
- Keep state minimal and derived data computed from source state.
- Prefer unions for component modes instead of optional-prop combinations that permit impossible states.

## Hooks

- Keep hooks focused and predictable.
- Avoid storing values in state when they can be derived from props or other state.
- Type event handlers explicitly when inference is unclear.

```tsx
import { useState } from "react";
import type { FormEvent } from "react";

function SearchBox({ onSubmit }: { onSubmit(query: string): void }) {
  const [query, setQuery] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(query);
  }

  return <form onSubmit={handleSubmit}>...</form>;
}
```

## Context

- Keep context values small and stable.
- Avoid putting every mutable concern into one global context object.
- Expose domain hooks instead of leaking raw context shapes everywhere.

## Review Heuristics

- If a component accepts too many unrelated props, split the responsibility.
- If render logic branches on many booleans, reconsider the state model.
- If hook return values are hard to name or reason about, the hook API is too broad.
