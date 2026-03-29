# Workflow, Tooling, and Project Shape

## Project Shape

- Keep domain logic independent of frameworks where practical.
- Split by responsibility, not by file suffix or “helpers” dumping grounds.
- Keep entrypoints thin. Parse input, initialize dependencies, then call typed domain logic.
- Export intentionally. Start with local modules, then widen only what other modules actually need.

## `tsconfig` Defaults

- Enable `strict`.
- Prefer `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` when the project can support them.
- Prefer modern module settings that match the runtime and bundler instead of legacy compatibility defaults.
- Keep path aliases sparse and obvious.

## Modules

- Prefer the module system already established by the repo or runtime. For new projects, prefer modern ESM-compatible settings when the runtime and toolchain support them cleanly.
- Keep imports type-only when appropriate:

```ts
import type { User } from "./types";
```

- Do not use barrel exports as the default for every folder. Re-export intentionally at stable package boundaries.

## Naming and Co-location

- Co-locate types with the module they serve when the type is not broadly shared.
- Extract shared types only when multiple modules actually benefit.
- Name domain concepts by meaning, not transport shape.

## Boundary Pattern

```ts
export async function run(rawConfig: unknown): Promise<void> {
  const config = parseConfig(rawConfig);
  await execute(config);
}
```

- Parse and validate early.
- Keep `unknown` at the boundary, not in the core.

## Tooling

- Run the project type checker as a required gate, not a best-effort task.
- Use the repo’s formatter and linter instead of inventing local style.
- Prefer fast feedback loops: per-file tests when possible, full typecheck before finalization.

## Review Heuristics

- Challenge broad exports.
- Challenge duplicated type definitions and transport/domain mixing.
- Challenge `tsconfig` relaxations that hide real design problems.
