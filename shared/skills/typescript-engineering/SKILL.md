---
name: typescript-engineering
description: Comprehensive TypeScript engineering guidance for coding agents. Use when writing, reviewing, refactoring, or debugging TypeScript or TSX code; designing public APIs; fixing tsconfig or strict-mode issues; resolving generic, union, narrowing, async, module, or type-inference problems; improving runtime validation, testability, and performance; or reviewing TypeScript pull requests for safety and maintainability. Trigger on TypeScript, ts, tsx, tsconfig, tsc, generics, discriminated unions, type guards, Zod, NodeNext, ESM, and strict mode.
---

# TypeScript Engineering

Produce TypeScript that is explicit at boundaries, narrow in surface area, and strict enough that refactors fail fast. Prefer inference inside small scopes, explicit types at module boundaries, runtime validation for external data, and simple control flow over clever type tricks.

## Workflow

1. Identify the boundary.
   Library: optimize for stable public types, portability, and narrow exports.
   Application: optimize for operability, runtime validation, and maintainable module boundaries.
2. Model data before behavior.
   Prefer discriminated unions, branded/domain types, and small interfaces over optional-field soup.
3. Decide where trust begins.
   Treat network, env, file, CLI, and user input as `unknown` until validated.
4. Keep types and implementation aligned.
   Prefer deriving types from values and functions over duplicating parallel definitions.
5. Use async intentionally.
   Model failure and cancellation explicitly; avoid floating promises and hidden concurrency.
6. Verify before finalizing.
   Run the project’s formatter, linter, type checker, and tests. Treat type errors as design feedback.

## Load References By Need

| Need | Reference |
|---|---|
| Project shape, tsconfig, modules, exports, tooling | `references/workflow.md` |
| Boundary validation, error handling, async and promises | `references/runtime-and-errors.md` |
| API design, unions, narrowing, generics, utility types | `references/types-and-api-design.md` |
| React/TSX state, props, hooks, and event typing | `references/react-and-tsx.md` |
| Testing, mocks, fixtures, snapshots, review checklist | `references/testing-and-quality.md` |
| Performance, allocation, iteration, and common footguns | `references/performance-and-footguns.md` |

## Default Standards

- Enable strict mode and keep it on.
- Prefer `unknown` over `any` at trust boundaries.
- Validate external data at runtime before treating it as domain data.
- Prefer discriminated unions over boolean mode flags and optional-field matrices.
- Keep exports intentional. Avoid giant barrel files that hide ownership and increase coupling.
- Return typed domain values from core logic; isolate framework types at the edges.
- Use `Promise<void>` and `await` intentionally. Do not leave floating promises.
- Prefer stable, readable types over maximally clever conditional-type machinery.

## Code Review Checklist

- Are untrusted inputs validated before use?
- Are unions discriminated cleanly and narrowed safely?
- Are generic constraints actually helping, or just obscuring the code?
- Are async failures, cancellation, and promise lifetimes explicit?
- Are public exports and types narrower than the implementation internals?
- Is React state or prop modeling preserving invariants instead of pushing checks into render logic?
- Is the code relying on `any`, assertions, or non-null operators where better modeling would remove them?

## Sources and Influences

This skill synthesizes ideas from the following public TypeScript skill work rather than copying any one source directly:

- alinaqi `typescript`: https://agent-skills.md/skills/alinaqi/claude-bootstrap/typescript
- Metabase `typescript-write`: https://agent-skills.md/skills/metabase/metabase/typescript-write
- cosmix `typescript`: https://agent-skills.md/skills/cosmix/claude-loom/typescript
- ilude `typescript-workflow`: https://agent-skills.md/skills/ilude/claude-code-config/typescript-workflow
- alexei-led `writing-typescript`: https://agent-skills.md/skills/alexei-led/claude-code-config/writing-typescript
