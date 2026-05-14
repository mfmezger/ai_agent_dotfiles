#!/usr/bin/env python3
"""Fetch GitHub PR feedback into one structured JSON document.

This is a thin wrapper around the GitHub CLI. It intentionally has no external
Python dependencies so agents can run it anywhere `gh` is authenticated.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PR_FIELDS = ",".join(
    [
        "number",
        "title",
        "url",
        "author",
        "state",
        "isDraft",
        "baseRefName",
        "headRefName",
        "reviewDecision",
        "comments",
        "reviews",
        "latestReviews",
        "files",
        "statusCheckRollup",
    ]
)

THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          path
          line
          originalLine
          comments(first: 50) {
            nodes {
              author { login }
              body
              createdAt
              url
              diffHunk
            }
          }
        }
      }
    }
  }
}
"""


def run_json(cmd: list[str]) -> Any:
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    stdout = result.stdout.strip()
    if not stdout:
        return None
    return json.loads(stdout)


def run_text(cmd: list[str]) -> str:
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def parse_pr_url(url: str) -> tuple[str, str, int] | None:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        return None
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def current_repo() -> tuple[str, str]:
    name_with_owner = run_text(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    owner, repo = name_with_owner.split("/", 1)
    return owner, repo


def repo_from_args(repo: str | None) -> tuple[str, str] | None:
    if not repo:
        return None
    if "/" not in repo:
        raise ValueError("--repo must be in OWNER/REPO form")
    owner, name = repo.split("/", 1)
    return owner, name


def infer_identity(pr_ref: str | None, repo: str | None, pr_view: dict[str, Any]) -> tuple[str, str, int]:
    if pr_ref:
        parsed = parse_pr_url(pr_ref)
        if parsed:
            return parsed

    parsed = parse_pr_url(pr_view["url"])
    if parsed:
        return parsed

    repo_parts = repo_from_args(repo)
    if repo_parts:
        owner, name = repo_parts
    else:
        owner, name = current_repo()
    return owner, name, int(pr_view["number"])


def fetch_pr_view(pr_ref: str | None, repo: str | None) -> dict[str, Any]:
    cmd = ["gh", "pr", "view"]
    if pr_ref:
        cmd.append(pr_ref)
    cmd.extend(["--json", PR_FIELDS])
    if repo:
        cmd.extend(["--repo", repo])
    return run_json(cmd)


def fetch_inline_comments(owner: str, repo: str, number: int) -> list[dict[str, Any]]:
    return run_json(["gh", "api", f"repos/{owner}/{repo}/pulls/{number}/comments", "--paginate"])


def fetch_review_threads(owner: str, repo: str, number: int) -> list[dict[str, Any]]:
    data = run_json(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={repo}",
            "-F",
            f"number={number}",
            "-f",
            f"query={THREADS_QUERY}",
        ]
    )
    return data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]


def fetch_checks(pr_ref: str | None, repo: str | None) -> list[dict[str, Any]]:
    cmd = [
        "gh",
        "pr",
        "checks",
    ]
    if pr_ref:
        cmd.append(pr_ref)
    cmd.extend(["--json", "name,state,bucket,description,link,workflow,startedAt,completedAt"])
    if repo:
        cmd.extend(["--repo", repo])

    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        # `gh pr checks` exits non-zero when no checks are reported. Treat that
        # as an empty check list; preserve other failures as informational rows.
        if "no checks reported" in message.lower():
            return []
        return [{"error": message}]
    return json.loads(result.stdout or "[]")


def build_summary(payload: dict[str, Any]) -> str:
    pr = payload["pr"]
    checks = payload["checks"]
    comments = payload["inline_comments"]
    threads = payload["review_threads"]
    unresolved_threads = [thread for thread in threads if not thread.get("isResolved")]
    return "\n".join(
        [
            f"# PR #{pr['number']}: {pr['title']}",
            f"URL: {pr['url']}",
            f"State: {pr['state']} | Review decision: {pr.get('reviewDecision') or 'none'}",
            f"Reviews: {len(pr.get('reviews') or [])}",
            f"Top-level comments: {len(pr.get('comments') or [])}",
            f"Inline comments: {len(comments)}",
            f"Review threads: {len(threads)} ({len(unresolved_threads)} unresolved)",
            f"Checks: {len(checks)}",
            f"Changed files: {len(pr.get('files') or [])}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr", nargs="?", help="PR number, URL, or branch. Omit to use the current branch PR.")
    parser.add_argument("--repo", help="Repository in OWNER/REPO form. Useful when PR is given as a number.")
    parser.add_argument("--out", type=Path, help="Write JSON payload to this path instead of stdout.")
    parser.add_argument("--summary", action="store_true", help="Print a short human-readable summary after fetching.")
    args = parser.parse_args()

    try:
        pr_view = fetch_pr_view(args.pr, args.repo)
        owner, repo, number = infer_identity(args.pr, args.repo, pr_view)
        payload = {
            "repo": {"owner": owner, "name": repo, "nameWithOwner": f"{owner}/{repo}"},
            "pr": pr_view,
            "inline_comments": fetch_inline_comments(owner, repo, number),
            "review_threads": fetch_review_threads(owner, repo, number),
            "checks": fetch_checks(args.pr, args.repo),
        }
    except Exception as exc:  # noqa: BLE001 - command-line tool should show concise failures
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
        print(args.out)
    else:
        print(output)

    if args.summary:
        print("\n" + build_summary(payload), file=sys.stderr if args.out else sys.stdout)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
