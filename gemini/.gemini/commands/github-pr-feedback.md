---
description: Use this skill whenever the user asks to look at GitHub PR feedback, PR review comments, review bot output, Gemini/Claude review feedback, or pasted reviewer suggestions and wants a markdown table that separates what should be fixed from what does not need to be fixed. This skill should trigger for PR feedback triage, deciding whether review comments are actionable, and producing a concise markdown report with yes/no emoji decisions and reasoning.
---


# GitHub PR Feedback Triage

Review GitHub pull request feedback and turn it into a clean markdown report with
**two tables**:

1. **What does not need to be fixed**
2. **What should be fixed**

Use this skill for both live GitHub PRs and pasted review feedback.

## Output Contract

Always produce markdown with this structure:

### 1) Table for items that do **not** need to be fixed

Use these exact columns:

| Problem | Description | Should be fixed? | Reasoning |
| ------- | ----------- | ---------------- | --------- |

For rows in this table, prefer `❌ No` in the **Should be fixed?** column.

### 2) Table for items that **should** be fixed

Use the same columns:

| Problem | Description | Should be fixed? | Reasoning |
| ------- | ----------- | ---------------- | --------- |

For rows in this table, prefer `✅ Yes` in the **Should be fixed?** column.

## Workflow

### 1. Gather the feedback source

Decide which input mode applies:

- **Live GitHub PR**: collect comments from the PR directly.
- **Pasted feedback**: analyze the pasted review text.
- **Mixed input**: combine both, but deduplicate overlapping items.

If the user refers to "the PR" and you have GitHub CLI access, inspect the PR
instead of asking them to paste everything.

### 2. For live GitHub PRs, collect complete feedback

Use the helper script. By default it now outputs the final two-table markdown triage report automatically:

```bash
python ~/.claude/skills/github-pr-feedback/scripts/fetch_feedback.py [PR] [--repo owner/repo]
```

Useful options:

```bash
# Current branch PR in current repo
python ~/.claude/skills/github-pr-feedback/scripts/fetch_feedback.py

# Specific PR number in current repo
python ~/.claude/skills/github-pr-feedback/scripts/fetch_feedback.py 123

# Specific PR in a repo
python ~/.claude/skills/github-pr-feedback/scripts/fetch_feedback.py 123 --repo owner/repo

# Raw JSON if you want structured inspection
python ~/.claude/skills/github-pr-feedback/scripts/fetch_feedback.py 123 --repo owner/repo --json

# Raw collected comments instead of auto-triaged tables
python ~/.claude/skills/github-pr-feedback/scripts/fetch_feedback.py 123 --repo owner/repo --snapshot
```

The helper script intentionally gathers:

- PR review summaries/bodies
- Inline review comments
- PR issue comments

This matters because `gh pr view --json comments` alone does **not** include
inline review comments.

Treat the script's default output as a strong first pass, not ground truth. If a
classification looks wrong, override it in your final response.

### 3. Triage each item

Classify every substantive feedback item into one of two buckets.

#### Usually **should be fixed**

Mark as `✅ Yes` when the feedback points to:

- correctness bugs
- broken behavior or regressions
- missing tests for meaningful risk
- security/privacy issues
- API/contract mismatches
- clear maintainability problems that will cause confusion or defects
- documentation mismatches that would mislead users
- concrete omissions in the PR scope

#### Usually **does not need to be fixed**

Mark as `❌ No` when the feedback is:

- praise, chatter, or non-actionable commentary
- a personal preference with no stated project standard
- already addressed by the current diff or follow-up comments
- based on a misunderstanding of the code or requirements
- outside the intended scope of the PR
- a duplicate of another stronger comment
- a bot summary that contains no actionable request by itself
- a speculative suggestion better treated as future work

### 4. Use judgment, not keyword matching

Do not blindly trust bot comments or reviewer confidence.

Check whether the comment is actually supported by:

- the diff
- surrounding code
- existing tests
- PR description/scope
- follow-up discussion on the thread

If a comment is partially right, split it into separate rows so the final table is
more precise.

### 5. Deduplicate aggressively

If multiple reviewers raise the same issue:

- keep one consolidated row
- mention the overlap in the description or reasoning if helpful
- do not spam the table with repeated rows

### 6. Be concise but specific

For each row:

- **Problem**: short label, 3-8 words when possible
- **Description**: one concise explanation of the concern
- **Should be fixed?**: `✅ Yes` or `❌ No`
- **Reasoning**: brief explanation of why the item is or is not worth fixing

## Recommended Review Heuristics

### Treat as stronger signals

- reproducible bug reports
- concrete line-level review comments
- comments tied to tests, types, API contracts, or documented behavior
- repeated concerns from multiple reviewers

### Treat as weaker signals

- vague stylistic suggestions
- drive-by opinions without evidence
- bot-generated summaries without a concrete requested change
- comments contradicted by the current code

## Handling Ambiguity

If something is borderline:

- choose the bucket you think is best
- explain the uncertainty in **Reasoning**
- prefer clarity over hedging

Do **not** create a third table unless the user explicitly asks for one.

## Suggested Response Template

```markdown
## Does not need to be fixed

| Problem | Description | Should be fixed? | Reasoning |
| ------- | ----------- | ---------------- | --------- |
| Example | Reviewer suggested renaming a local variable. | ❌ No | Pure preference, no project convention or readability issue demonstrated. |

## Should be fixed

| Problem | Description | Should be fixed? | Reasoning |
| ------- | ----------- | ---------------- | --------- |
| Missing test coverage | Reviewer noted an untested failure path in the new logic. | ✅ Yes | The change affects behavior and the missing test leaves a realistic regression risk. |
```

## Practical Notes

- If there is no live PR context, ask the user to paste the review feedback.
- If there are no items for one section, still include the section and write a
  single placeholder row.
- Keep the final report skimmable.
- Prefer actionable synthesis over exhaustive transcription.
