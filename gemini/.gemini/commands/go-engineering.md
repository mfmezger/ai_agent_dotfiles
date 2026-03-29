---
description: Comprehensive Go engineering guidance for coding agents. Use when writing, reviewing, refactoring, or debugging Go code; designing packages and exported APIs; improving error handling, interfaces, concurrency, contexts, cancellation, tests, benchmarks, and module layout; or reviewing Go pull requests for idioms and maintainability. Trigger on Go, golang, go.mod, interfaces, goroutines, channels, context.Context, errors.Is, errors.As, testing, and benchmarks.
---


# Go Engineering

Produce Go that is small in surface area, explicit in behavior, and easy to read under review. Prefer straightforward package boundaries, concrete types first, small interfaces where they help callers, explicit error handling, and concurrency that can be reasoned about.

## Workflow

1. Identify the package boundary.
   Library: optimize for small exports, concrete behavior, and compatibility.
   Application: optimize for operability, wiring clarity, and cancellation-aware execution.
2. Model the package API before adding helpers.
   Keep exported identifiers minimal and make zero values useful when practical.
3. Choose concrete types first.
   Introduce interfaces where consumers benefit, not as a reflex.
4. Design error flow early.
   Wrap with context, support `errors.Is` and `errors.As`, and keep sentinel errors narrow.
5. Add concurrency only where it simplifies latency or throughput.
   Cancellation, shutdown, ownership, and goroutine lifetime must be explicit.
6. Verify before finalizing.
   Run `gofmt`, `go test ./...`, and `go vet ./...` when appropriate. Add `go test -race ./...` for concurrency-sensitive code. Keep examples and benchmarks honest.

## Load References By Need

| Need | Reference |
|---|---|
| Package layout, modules, exported API shape, CLI/app structure | `references/workflow.md` |
| Errors, wrapping, sentinels, concrete types vs interfaces | `references/api-and-errors.md` |
| Concurrency, channels, contexts, goroutines, shutdown | `references/concurrency.md` |
| Testing, table tests, fuzzing, benchmarks, temp dirs | `references/testing-and-quality.md` |
| Performance, allocations, slices, maps, common footguns | `references/performance-and-footguns.md` |

## Default Standards

- Keep packages focused and exports intentional.
- Start with concrete types; accept interfaces when they improve the consuming code.
- Pass `context.Context` explicitly for request-scoped or cancelable work.
- Return errors, wrap them with context, and avoid panic for ordinary failures.
- Prefer simple loops and data flow over abstraction-heavy “framework” patterns.
- Keep goroutine ownership clear. Every goroutine should have a reason to exit.
- Make the zero value useful when practical and not misleading.

## Code Review Checklist

- Is the package API smaller than the implementation internals?
- Are interfaces consumer-driven rather than speculative?
- Do wrapped errors retain useful identity and context?
- Can every goroutine stop, and is cancellation propagated?
- Are channels owned clearly, with close responsibility obvious?
- Are tests covering error cases and boundary behavior, not only happy paths?
- Is complexity coming from the problem, or from avoidable abstractions?

## Sources and Influences

This skill synthesizes ideas from the following public Go skill work rather than copying any one source directly:

- maragudk `go`: https://agent-skills.md/skills/maragudk/skills/go
- ilude `go-workflow`: https://agent-skills.md/skills/ilude/claude-code-config/go-workflow
- julianobarbosa `writing-go`: https://agent-skills.md/skills/julianobarbosa/claude-code-skills/writing-go
- 0xbigboss `go-best-practices`: https://agent-skills.md/skills/0xbigboss/claude-code/go-best-practices
- GitHub agent skills guidance: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills
