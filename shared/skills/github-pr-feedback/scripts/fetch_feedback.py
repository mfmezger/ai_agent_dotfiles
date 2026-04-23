#!/usr/bin/env python3
"""Fetch GitHub PR feedback and render a first-pass markdown triage report.

By default, this script gathers PR reviews, inline review comments, and issue
comments, then emits the two-table markdown report expected by the
`github-pr-feedback` skill.

Examples:
    python fetch_feedback.py
    python fetch_feedback.py 123
    python fetch_feedback.py 123 --repo owner/repo
    python fetch_feedback.py https://github.com/owner/repo/pull/123 --snapshot
    python fetch_feedback.py 123 --repo owner/repo --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse


ACTIONABLE_KEYWORDS = (
    "should",
    "must",
    "need",
    "needs",
    "missing",
    "remove",
    "removed",
    "redundant",
    "incorrect",
    "wrong",
    "bug",
    "broken",
    "regression",
    "inconsistent",
    "fix",
    "fails",
    "failure",
    "test",
    "coverage",
    "error",
    "security",
    "privacy",
    "docs",
    "documentation",
    "rename",
    "avoid",
    "consider",
)

CODE_CONTEXT_KEYWORDS = (
    "file",
    "line",
    "path",
    "diff",
    "function",
    "method",
    "class",
    "variable",
    "test",
    "fixture",
    "config",
    "env",
    "api",
    "response",
    "request",
    "behavior",
    "logic",
    "docs",
    "documentation",
)

ISSUE_COMMENT_CONTEXT_KEYWORDS = (
    "file",
    "line",
    "path",
    "diff",
    "function",
    "method",
    "class",
    "variable",
    "test",
    "fixture",
    "config",
    "env",
    "api",
    "response",
    "request",
    "docs",
    "documentation",
)

NON_ACTIONABLE_PATTERNS = (
    "lgtm",
    "looks good",
    "look good",
    "nice work",
    "great work",
    "great job",
    "thanks",
    "thank you",
    "approved",
    "ship it",
)

PREFERENCE_KEYWORDS = (
    "nit:",
    "nitpick",
    "personally",
    "i prefer",
    "could maybe",
    "optional",
)

OUT_OF_SCOPE_KEYWORDS = (
    "legal",
    "policy",
    "leadership",
    "eu peers",
    "how dare",
    "hacker news",
    "community input",
    "enshittification",
)


@dataclass
class FeedbackItem:
    kind: str
    author: str
    created_at: str
    url: str
    body: str
    state: str | None = None
    path: str | None = None
    line: int | None = None
    start_line: int | None = None
    side: str | None = None
    in_reply_to_id: int | None = None


@dataclass
class TriageRow:
    problem: str
    description: str
    should_fix: bool
    reasoning: str
    source: str


def run_gh(args: list[str], expect_json: bool = True) -> Any:
    try:
        result = subprocess.run(
            ["gh", *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise SystemExit("Error: 'gh' (GitHub CLI) is not installed or not in PATH. Please install it to use this skill.")
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "gh command failed"
        raise SystemExit(message)

    if not expect_json:
        return result.stdout.strip()

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse JSON from gh output: {exc}") from exc


def flatten_paginated(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list) and data and all(isinstance(page, list) for page in data):
        flattened: list[dict[str, Any]] = []
        for page in data:
            flattened.extend(page)
        return flattened
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def parse_repo_from_pr_url(pr_url: str) -> str:
    parsed = urlparse(pr_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 4 or parts[2] != "pull":
        raise SystemExit(f"Could not parse owner/repo from PR URL: {pr_url}")
    return f"{parts[0]}/{parts[1]}"


def resolve_pr(pr: str | None, repo: str | None) -> tuple[str, dict[str, Any]]:
    args = ["pr", "view"]
    if pr:
        args.append(pr)
    if repo:
        args.extend(["--repo", repo])
    args.extend(["--json", "number,title,url,reviewDecision"])

    pr_data = run_gh(args)
    resolved_repo = repo or parse_repo_from_pr_url(pr_data["url"])
    return resolved_repo, pr_data


def fetch_reviews(repo: str, number: int) -> list[FeedbackItem]:
    data = run_gh(
        [
            "api",
            f"repos/{repo}/pulls/{number}/reviews",
            "--paginate",
            "--slurp",
        ]
    )
    items: list[FeedbackItem] = []
    for review in flatten_paginated(data):
        body = (review.get("body") or "").strip()
        if not body:
            continue
        items.append(
            FeedbackItem(
                kind="review",
                author=review.get("user", {}).get("login", "unknown"),
                created_at=review.get("submitted_at") or review.get("submittedAt") or "",
                url=review.get("html_url") or review.get("_links", {}).get("html", {}).get("href", ""),
                body=body,
                state=review.get("state"),
            )
        )
    return items


def fetch_review_comments(repo: str, number: int) -> list[FeedbackItem]:
    data = run_gh(
        [
            "api",
            f"repos/{repo}/pulls/{number}/comments",
            "--paginate",
            "--slurp",
        ]
    )
    items: list[FeedbackItem] = []
    for comment in flatten_paginated(data):
        body = (comment.get("body") or "").strip()
        if not body:
            continue
        items.append(
            FeedbackItem(
                kind="review_comment",
                author=comment.get("user", {}).get("login", "unknown"),
                created_at=comment.get("created_at") or "",
                url=comment.get("html_url") or "",
                body=body,
                path=comment.get("path"),
                line=comment.get("line"),
                start_line=comment.get("start_line"),
                side=comment.get("side"),
                in_reply_to_id=comment.get("in_reply_to_id"),
            )
        )
    return items


def fetch_issue_comments(repo: str, number: int) -> list[FeedbackItem]:
    data = run_gh(
        [
            "api",
            f"repos/{repo}/issues/{number}/comments",
            "--paginate",
            "--slurp",
        ]
    )
    items: list[FeedbackItem] = []
    for comment in flatten_paginated(data):
        body = (comment.get("body") or "").strip()
        if not body:
            continue
        items.append(
            FeedbackItem(
                kind="issue_comment",
                author=comment.get("user", {}).get("login", "unknown"),
                created_at=comment.get("created_at") or "",
                url=comment.get("html_url") or "",
                body=body,
            )
        )
    return items


def normalize_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def first_sentence(text: str, max_len: int = 180) -> str:
    cleaned = normalize_text(text)
    if not cleaned:
        return "No description provided."
    parts = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)
    sentence = parts[0]
    if len(sentence) <= max_len:
        return sentence
    return sentence[: max_len - 1].rstrip() + "…"


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def looks_like_bot_summary(item: FeedbackItem, normalized_body: str) -> bool:
    if not item.author.endswith("[bot]"):
        return False
    return (
        "pull request overview" in normalized_body.lower()
        or "files reviewed:" in normalized_body.lower()
        or "comments generated:" in normalized_body.lower()
        or "show a summary per file" in normalized_body.lower()
    )


def infer_problem(item: FeedbackItem, normalized_body: str, should_fix: bool) -> str:
    lowered = normalized_body.lower()
    if "test" in lowered or "coverage" in lowered:
        return "Missing test coverage" if should_fix else "Test discussion only"
    if "doc" in lowered or "documentation" in lowered:
        return "Documentation mismatch" if should_fix else "Documentation preference"
    if "redundant" in lowered or "remove" in lowered:
        return "Redundant code/config" if should_fix else "Optional cleanup"
    if "rename" in lowered:
        return "Naming suggestion"
    if looks_like_bot_summary(item, normalized_body):
        return "Bot summary only"
    if contains_any(normalized_body, OUT_OF_SCOPE_KEYWORDS):
        return "Out-of-scope discussion"
    if item.kind == "review_comment" and item.path:
        return f"Review comment on {item.path.split('/')[-1]}"
    if item.kind == "review":
        return "Review summary"
    if item.kind == "issue_comment":
        return "General PR comment"
    return "Reviewer concern"


def build_source_label(item: FeedbackItem) -> str:
    bits = [item.kind, f"by {item.author}"]
    if item.path:
        location = item.path
        if item.line is not None:
            location += f":{item.line}"
        bits.append(location)
    return " / ".join(bits)


def classify_item(item: FeedbackItem) -> TriageRow:
    normalized_body = normalize_text(item.body)
    lowered = normalized_body.lower()

    actionable = contains_any(normalized_body, ACTIONABLE_KEYWORDS)
    code_context = item.kind == "review_comment" or bool(item.path) or contains_any(normalized_body, CODE_CONTEXT_KEYWORDS)
    if item.kind == "issue_comment":
        code_context = bool(item.path) or contains_any(normalized_body, ISSUE_COMMENT_CONTEXT_KEYWORDS)
    non_actionable = contains_any(normalized_body, NON_ACTIONABLE_PATTERNS)
    preference = contains_any(normalized_body, PREFERENCE_KEYWORDS)
    out_of_scope = contains_any(normalized_body, OUT_OF_SCOPE_KEYWORDS)
    bot_summary = looks_like_bot_summary(item, normalized_body)

    should_fix = False
    reasoning = ""

    if bot_summary:
        should_fix = False
        reasoning = "Bot overview text is informational; rely on concrete inline comments instead of the summary itself."
    elif out_of_scope and not code_context:
        should_fix = False
        reasoning = "Comment is discussion or opinion outside the concrete code-review scope of the PR."
    elif non_actionable and not actionable:
        should_fix = False
        reasoning = "Comment does not request a concrete code or documentation change."
    elif item.in_reply_to_id and not actionable:
        should_fix = False
        reasoning = "Reply in a review thread, but not a standalone actionable request."
    elif preference and item.kind != "review_comment":
        should_fix = False
        reasoning = "Looks like a preference rather than a demonstrated correctness or maintainability issue."
    elif item.kind == "review_comment":
        should_fix = True
        reasoning = "Line-level review comments are usually actionable and should be handled unless clearly superseded."
    elif item.kind == "issue_comment" and not code_context:
        should_fix = False
        reasoning = "General PR discussion without code-specific context is usually not something to fix in this PR."
    elif item.kind == "review" and item.state == "APPROVED" and not code_context:
        should_fix = False
        reasoning = "Approved review summary without a concrete requested change."
    elif actionable and code_context:
        should_fix = True
        reasoning = "Concrete review feedback tied to implementation details is worth addressing in the PR."
    else:
        should_fix = False
        reasoning = "No clear actionable change request was identified from this feedback item."

    problem = infer_problem(item, normalized_body, should_fix)
    description = f"{first_sentence(item.body)} ({build_source_label(item)})"

    return TriageRow(
        problem=problem,
        description=description,
        should_fix=should_fix,
        reasoning=reasoning,
        source=item.url,
    )


def dedupe_rows(rows: list[TriageRow]) -> list[TriageRow]:
    seen: set[tuple[str, str, bool]] = set()
    deduped: list[TriageRow] = []
    for row in rows:
        key = (
            row.problem.lower(),
            normalize_text(row.description).lower(),
            row.should_fix,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def render_rows(rows: list[TriageRow], should_fix: bool) -> list[str]:
    table_lines = [
        "| Problem | Description | Should be fixed? | Reasoning |",
        "| ------- | ----------- | ---------------- | --------- |",
    ]

    if not rows:
        placeholder = "✅ Yes" if should_fix else "❌ No"
        table_lines.append(
            f"| None | No items in this category. | {placeholder} | Placeholder row included so the section is never empty. |"
        )
        return table_lines

    for row in rows:
        decision = "✅ Yes" if row.should_fix else "❌ No"
        table_lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row.problem),
                    escape_cell(row.description),
                    decision,
                    escape_cell(row.reasoning),
                ]
            )
            + " |"
        )
    return table_lines


def render_triage(payload: dict[str, Any]) -> str:
    all_items = [
        FeedbackItem(**item) for item in payload["review_summaries"]
    ] + [
        FeedbackItem(**item) for item in payload["inline_review_comments"]
    ] + [
        FeedbackItem(**item) for item in payload["issue_comments"]
    ]

    triaged = dedupe_rows([classify_item(item) for item in all_items])
    not_fix = [row for row in triaged if not row.should_fix]
    should_fix = [row for row in triaged if row.should_fix]

    lines = [
        f"# PR Feedback Triage: #{payload['pr']['number']} {payload['pr']['title']}",
        "",
        f"Source PR: {payload['pr']['url']}",
        f"Repository: `{payload['repository']}`",
        f"Review decision: `{payload['pr'].get('reviewDecision') or 'UNKNOWN'}`",
        "",
        "> This is an automatic first-pass triage based on PR comments and review metadata.",
        "> Use judgment and the current diff before making final keep/fix decisions.",
        "",
        "## What does not need to be fixed",
        "",
        *render_rows(not_fix, should_fix=False),
        "",
        "## What should be fixed",
        "",
        *render_rows(should_fix, should_fix=True),
        "",
    ]
    return "\n".join(lines)


def render_snapshot(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# PR Feedback Snapshot",
        "",
        f"- Repository: `{payload['repository']}`",
        f"- PR: [#{payload['pr']['number']}: {payload['pr']['title']}]({payload['pr']['url']})",
        f"- Review decision: `{payload['pr'].get('reviewDecision') or 'UNKNOWN'}`",
        f"- Review summaries: {len(payload['review_summaries'])}",
        f"- Inline review comments: {len(payload['inline_review_comments'])}",
        f"- Issue comments: {len(payload['issue_comments'])}",
        "",
    ]

    sections = [
        ("Review summaries", payload["review_summaries"]),
        ("Inline review comments", payload["inline_review_comments"]),
        ("Issue comments", payload["issue_comments"]),
    ]

    for heading, items in sections:
        lines.append(f"## {heading}")
        lines.append("")
        if not items:
            lines.append("_None_")
            lines.append("")
            continue

        for index, item in enumerate(items, start=1):
            lines.append(f"### {index}. {item['kind']}")
            lines.append(f"- Author: `{item['author']}`")
            if item.get("state"):
                lines.append(f"- State: `{item['state']}`")
            if item.get("path"):
                location = item["path"]
                if item.get("line") is not None:
                    location += f":{item['line']}"
                lines.append(f"- Location: `{location}`")
            if item.get("created_at"):
                lines.append(f"- Created: `{item['created_at']}`")
            if item.get("url"):
                lines.append(f"- URL: {item['url']}")
            if item.get("in_reply_to_id"):
                lines.append(f"- Reply to: `{item['in_reply_to_id']}`")
            lines.append("- Body:")
            lines.append("")
            for body_line in item["body"].splitlines() or [""]:
                lines.append(f"  > {body_line}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch GitHub PR feedback")
    parser.add_argument("pr", nargs="?", help="PR number, URL, or branch (defaults to current branch PR)")
    parser.add_argument("--repo", help="Repository in owner/repo form")
    parser.add_argument("--json", action="store_true", help="Output normalized JSON")
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Output the raw collected feedback snapshot instead of the triage tables",
    )
    args = parser.parse_args()

    repo, pr_data = resolve_pr(args.pr, args.repo)
    number = int(pr_data["number"])

    review_summaries = [asdict(item) for item in fetch_reviews(repo, number)]
    inline_review_comments = [asdict(item) for item in fetch_review_comments(repo, number)]
    issue_comments = [asdict(item) for item in fetch_issue_comments(repo, number)]

    payload = {
        "repository": repo,
        "pr": pr_data,
        "review_summaries": review_summaries,
        "inline_review_comments": inline_review_comments,
        "issue_comments": issue_comments,
    }

    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    if args.snapshot:
        sys.stdout.write(render_snapshot(payload))
        return

    sys.stdout.write(render_triage(payload))


if __name__ == "__main__":
    main()
