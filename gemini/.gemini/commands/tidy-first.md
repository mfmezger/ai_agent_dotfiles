---
description: Follow Kent Beck's "Tidy First" approach by strictly separating structural changes (renames, extractions, reorganizations that must not change behavior) from behavioral changes (features, bug fixes, logic changes). Use when refactoring, restructuring code, renaming variables/functions, extracting methods, separating concerns, preparing code for new features, or whenever you need structural and behavioral changes to land in separate commits.
---


# Tidy First

Follow Kent Beck's "Tidy First" approach by strictly separating structural
changes from behavioral changes in all development work.

## Source

This skill is adapted from the community skill **`snrsw-dotfiles-tidy-first`**
on the LobeHub Skills Marketplace.

- Original skill page: <https://lobehub.com/skills/snrsw-dotfiles-tidy-first?activeTab=skill>
- Raw SKILL.md: <https://lobehub.com/skills/snrsw-dotfiles-tidy-first/skill.md>
- Upstream author: [@snrsw](https://github.com/snrsw) — repo: [snrsw/dotfiles](https://github.com/snrsw/dotfiles)
- Upstream version referenced: 1.0.1

The instructional content below is the original skill's guidance, lightly
reformatted for this dotfiles repo. Marketplace install/registration steps
from the upstream page are intentionally omitted — this skill ships directly
via `shared/skills/` and is synced to each tool by `scripts/sync-skills.sh`.

## Core Principle

Separate all changes into two distinct types:

1. **Structural changes** — rearranging code without changing behavior:
   - Renaming variables, functions, classes
   - Extracting methods or functions
   - Moving code to different files or modules
   - Reorganizing code structure
   - Improving code organization

2. **Behavioral changes** — adding or modifying actual functionality:
   - Adding new features
   - Fixing bugs
   - Changing business logic
   - Modifying functionality

## Golden Rules

### Never mix change types

- Never mix structural and behavioral changes in the same commit.
- Each commit is either purely structural OR purely behavioral.
- This makes code review easier and debugging simpler.

### Structural changes first

- When both kinds of change are needed, always do the structural changes first.
- Tidy the code before adding new behavior.
- Prepare the structure to receive new functionality.

### Validate structural changes

- Validate that structural changes do not alter behavior.
- Run all tests before making the structural change.
- Run all tests after making the structural change.
- Tests must pass with the same results before and after. If behavior changed,
  it was not a pure structural change.

## Workflow

### When making structural changes

1. Ensure all tests are currently passing.
2. Make one structural change at a time.
3. Run tests to verify behavior is unchanged.
4. Commit the structural change with a clear message.
5. Repeat for the next structural change if needed.

### When making behavioral changes

1. Complete all structural changes first.
2. Commit all structural changes separately.
3. Now make the behavioral change.
4. Follow the TDD cycle (Red → Green → Refactor).
5. Commit behavioral changes separately.

## Commit Discipline

Follow the existing [`commit`](../commit/SKILL.md) skill for the actual subject
format. On top of that, signal change type clearly:

- Structural changes: `refactor` (or a `tidy` prefix in the summary)
- Behavioral changes: `feat` (new functionality) or `fix` (bug fix)

Only commit when:

1. All tests are passing.
2. All compiler/linter warnings have been resolved.
3. The change represents a single logical unit of work.

Prefer small, frequent commits over large, infrequent ones. Each structural
change gets its own commit; each behavioral change gets its own commit.

## Code Quality Standards

Apply these principles during structural changes:

- **Eliminate duplication ruthlessly** — find repeated patterns, extract
  common functionality, follow DRY.
- **Express intent clearly through naming and structure** — descriptive names,
  self-documenting code, structure that reveals intent.
- **Make dependencies explicit** — clearly show what depends on what, avoid
  hidden dependencies, use dependency injection where appropriate.
- **Keep methods small and focused on a single responsibility** — each
  function does one thing well; extract large methods into smaller ones.
- **Minimize state and side effects** — prefer pure functions, make side
  effects explicit and controlled, reduce mutable state.

## Refactoring Patterns

Use established refactoring patterns by name:

- **Extract Method** — pull code into a new method.
- **Rename** — change names to better express intent.
- **Move Method** — relocate a method to a more appropriate class/module.
- **Extract Class** — split a large class into smaller ones.
- **Inline Method** — replace a method call with the method body.
- **Replace Temp with Query** — replace a temporary variable with a method call.
- **Introduce Parameter Object** — group related parameters into an object.

## Examples

### Structural change (Extract Method, Go)

```go
// Before
func CalculateTotal(price float64, taxRate float64) float64 {
    tax := price * taxRate
    return price + tax
}

// After — Extract Method (no behavior change)
func CalculateTotal(price float64, taxRate float64) float64 {
    tax := CalculateTax(price, taxRate)
    return price + tax
}

func CalculateTax(price float64, taxRate float64) float64 {
    return price * taxRate
}
```

### Behavioral change (Go)

```go
// Before
func CalculateTotal(price float64, taxRate float64) float64 {
    tax := price * taxRate
    return price + tax
}

// After — new tax logic (behavior changed)
func CalculateTotal(price float64, taxRate float64) float64 {
    tax := price * taxRate * 1.1 // New tax logic
    return price + tax
}
```

## Benefits

- **Easier code review** — reviewers can quickly verify structural changes
  don't alter behavior.
- **Safer refactoring** — tests guarantee no behavior changed.
- **Better git history** — clear separation makes debugging and `git bisect`
  easier.
- **Easier rollback** — you can revert behavioral changes without losing
  structural improvements.
- **Lower risk** — small, focused changes reduce the chance of introducing
  bugs.
