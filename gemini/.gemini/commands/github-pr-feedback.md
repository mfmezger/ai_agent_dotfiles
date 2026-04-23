---
description: Use this skill whenever the user asks to look at GitHub PR feedback, PR review comments, review bot output, Gemini/Claude review feedback, or pasted reviewer suggestions and wants a markdown table that separates what should be fixed from what does not need to be fixed. This skill should trigger for PR feedback triage, deciding whether review comments are actionable, and producing a concise markdown report with yes/no emoji decisions and reasoning.
---


# GitHub PR Feedback Triage

Turn GitHub pull request feedback into a concise, defensible markdown triage
report. The goal is to help the user decide which comments require code changes
and which can be safely declined, deferred, or answered without changing code.

## Review Lens

Always keep the `karpathy-guidelines` skill in mind when judging PR feedback.
Bias toward simple, surgical fixes with clear success criteria:

- Do not accept feedback that adds speculative abstractions, broad refactors, or
  configurability the PR does not need.
- Do not reject feedback that identifies a concrete bug, unclear assumption, or
  missing verification just because the fix is inconvenient.
- Prefer the smallest code or documentation change that resolves the reviewer
  concern.
- Surface uncertainty directly in the reasoning instead of pretending the answer
  is more certain than the evidence supports.

## Prerequisites

- Use `gh` when feedback must be fetched from GitHub.
- `gh` must be installed and authenticated for live PR access.
- If the user pasted the feedback directly, do not fetch from GitHub unless they
  ask you to verify the current PR state.

## Input Sources

Prefer the most direct available input:

1. Pasted feedback in the conversation.
2. A PR URL or PR number provided by the user.
3. The PR associated with the current branch.

If no PR or feedback is available, ask the user for either a PR URL/number or the
feedback text.

## Fetching GitHub Feedback

Start with the high-level PR data:

```bash
gh pr view <pr> --json number,title,url,author,reviewDecision,comments,reviews,latestReviews,files
```

If the user did not provide `<pr>`, infer it from the current branch:

```bash
gh pr view --json number,title,url,headRefName,baseRefName
```

Fetch inline review threads when line-level comments matter. Replace
`OWNER`, `REPO`, and `NUMBER` with the PR repository and number:

```bash
gh api graphql \
  -f owner='OWNER' \
  -f name='REPO' \
  -F number=NUMBER \
  -f query='
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          path
          line
          originalLine
          comments(first: 20) {
            nodes {
              author { login }
              body
              createdAt
              url
            }
          }
        }
      }
    }
  }
}'
```

Also inspect failed checks if review feedback references CI failures:

```bash
gh pr checks <pr>
```

If GitHub access fails, explain the blocker briefly and ask the user to paste
the PR feedback. Do not fabricate comments.

## Triage Rules

Classify each distinct problem, not each individual comment. Merge duplicate
comments that point at the same underlying issue.

Use `✅ Yes` in `Should Be Fixed` when the feedback identifies:

- A correctness bug, regression, broken build, failing test, or runtime error.
- A security, privacy, data-loss, race-condition, or reliability risk.
- Missing behavior required by the PR description, ticket, or existing contract.
- A maintainability issue likely to confuse future changes or hide defects.
- A small requested cleanup that is clearly valid and low-risk to apply.

Use `❌ No` in `Should Be Fixed` when the feedback is:

- Incorrect because it misreads the code or ignores existing behavior.
- Already handled elsewhere in the PR.
- Pure preference without a project convention or concrete benefit.
- Out of scope for this PR and safer as a follow-up.
- A speculative optimization without evidence or measurable impact.
- A comment that only needs a written reply, clarification, or documentation
  pointer rather than a code change.

When uncertain, prefer `✅ Yes` only if there is a concrete user-facing,
correctness, security, or maintainability reason. Otherwise mark `❌ No` and
explain what evidence would change the decision.

## Required Output

Always produce exactly two markdown tables in this order:

1. `## Does Not Need To Be Fixed`
2. `## Should Be Fixed`

Each table must use these exact columns:

```markdown
| Problem | Description | Should Be Fixed | Reasoning |
| --- | --- | --- | --- |
```

Use `❌ No` for every real feedback row in `Does Not Need To Be Fixed`.
Use `✅ Yes` for every real feedback row in `Should Be Fixed`.

If a section has no entries, include one row that says there were no items:

```markdown
| None | No PR feedback landed in this category. | ❌ No | No action needed. |
```

For an empty `Should Be Fixed` section, use:

```markdown
| None | No PR feedback landed in this category. | ❌ No | No fixes identified. |
```

Keep rows concise:

- `Problem`: short noun phrase, ideally with file/path if available.
- `Description`: summarize the reviewer concern in one sentence.
- `Should Be Fixed`: only `✅ Yes` or `❌ No`.
- `Reasoning`: explain the decision, including scope, risk, and evidence.
- Escape `|` characters inside table cells so the markdown table stays valid.

After the two tables, add a short `## Summary` section with:

- Count of `✅ Yes` items.
- Count of `❌ No` items.
- The highest-priority fix, if any.

Do not include a long raw dump of GitHub comments unless the user asks.

## Decision Quality Checklist

Before finalizing the report:

- Verify that every meaningful review comment is represented or merged into a
  row.
- Check resolved comments too, because they may still explain important context.
- Separate "needs a code change" from "needs a reply".
- Do not mark a comment as unnecessary just because it is inconvenient.
- Do not mark a comment as required just because a reviewer wrote it.
- Tie the reasoning to concrete code behavior, project conventions, or PR scope.

## Example Output

```markdown
## Does Not Need To Be Fixed

| Problem | Description | Should Be Fixed | Reasoning |
| --- | --- | --- | --- |
| Rename helper | Reviewer suggested renaming `buildPayload` to `makePayload`. | ❌ No | The current name matches nearby helpers and the suggestion is stylistic without improving clarity. |

## Should Be Fixed

| Problem | Description | Should Be Fixed | Reasoning |
| --- | --- | --- | --- |
| Missing null guard in webhook handler | Reviewer noted that `event.user` can be absent for system events. | ✅ Yes | This can cause a runtime exception on valid webhook payloads, so the handler should guard before reading user fields. |

## Summary

- `✅ Yes`: 1 item.
- `❌ No`: 1 item.
- Highest priority: add the webhook null guard because it prevents a runtime failure.
```
