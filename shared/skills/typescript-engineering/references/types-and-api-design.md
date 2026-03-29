# Types and API Design

## Make Invalid States Hard to Express

- Prefer discriminated unions over boolean flags or optional-field matrices.
- Prefer branded or domain-specific wrappers over naked strings for identifiers when confusion is likely.
- Prefer smaller interfaces and focused parameter objects over giant multi-purpose types.

```ts
type DraftOrder = { kind: "draft"; items: LineItem[] };
type SubmittedOrder = { kind: "submitted"; id: OrderId; items: LineItem[] };
type Order = DraftOrder | SubmittedOrder;
```

## Narrowing

- Use discriminants, `in` checks, and well-scoped user-defined type guards.
- Avoid broad type assertions that skip narrowing instead of proving it.
- Prefer exhaustive `switch` statements for discriminated unions when behavior differs by variant.

```ts
function renderOrder(order: Order): string {
  switch (order.kind) {
    case "draft":
      return `draft with ${order.items.length} items`;
    case "submitted":
      return `submitted order ${order.id}`;
    default: {
      const exhaustive: never = order;
      return exhaustive;
    }
  }
}
```

## Generics

- Use generics when there is a real relationship between inputs and outputs.
- Avoid “just in case” generic abstraction.
- Keep constraints narrow and purposeful.

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
```

## Utility Types

- Use utility types to reduce duplication, not to create opaque type puzzles.
- Prefer named intermediate types when a composed type becomes hard to read.

## API Boundaries

- Accept the narrowest shape that preserves ergonomics.
- Return stable domain shapes instead of leaking transport-layer details.
- Prefer readonly collections at boundaries when mutation is not part of the contract.

## Review Heuristics

- Replace assertions with modeling or narrowing when possible.
- Replace boolean mode flags with unions when behavior diverges materially.
- Replace over-abstracted generics with concrete types when the abstraction adds no leverage.
- If a discriminated union is handled without an exhaustive check in a critical path, expect future refactor bugs.
