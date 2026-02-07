# Claude Code User-Level Guidelines

This file provides global context and guidelines that apply across all projects.

## Coding Guidelines

I follow the [Karpathy Guidelines](skills/karpathy-guidelines/SKILL.md) for all coding tasks, which help reduce common LLM coding mistakes:

### Core Principles

1. **Think Before Coding** - Surface assumptions, ask questions, present tradeoffs
2. **Simplicity First** - Minimum viable code, no overengineering or speculation
3. **Surgical Changes** - Only modify what's directly requested, match existing style
4. **Goal-Driven Execution** - Define verifiable success criteria, plan before implementing

**Note**: For trivial tasks, these guidelines can be relaxed using judgment. For complex or ambiguous tasks, they help ensure quality and clarity.

---

## My Preferences

<!-- Add your personal coding preferences here -->

### Language & Framework Preferences
- Python: Modern Python 3.10+, type hints preferred
- Testing: pytest, comprehensive coverage
- Documentation: Clear docstrings for public APIs

### Style
- Follow existing project conventions
- Clear variable names over clever brevity
- Comments explain "why", not "what"

### Workflow
- Test-driven when fixing bugs
- Incremental commits for multi-step changes
- Ask before major architectural changes

---

## Useful References

- Invoke `/karpathy-guidelines` skill to explicitly apply stricter coding discipline
- Project-specific guidelines should be in each project's `.claude/CLAUDE.md`
