#!/usr/bin/env python3
"""Shared start-check helpers (1.196.0) for merged_since_sync.py and walk_progress.py code-drift.

    start_check.py state --code-repo <checkout> --branch <branch> --base <base> [--no-fetch]

One place decides two things the start checks used to get wrong:

- Which ref is the base: `origin/<base>` first (after one quiet fetch when
  the checkout has an origin remote), the local `<base>` only when there is
  no remote-tracking ref. A stale local develop never hides a merge.
- Whether a branch tip is already merged into the base: the tip is an
  ancestor of the base. Then the first merge commit on the ancestry path is
  the merge, and its subject gives the pull request number when it has one.

`state` prints both as JSON and writes nothing in the specs repo (the fetch
only updates remote-tracking refs in the code checkout).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

sys.dont_write_bytecode = True


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

PR_SUBJECT = re.compile(r"(?:Merge pull request #(\d+)|Merged PR (\d+):|\(#(\d+)\)\s*$)")
_FETCHED: set[str] = set()


def git(repo: str, *args: str, timeout: int = 20) -> str | None:
    try:
        done = subprocess.run(["git", "-C", repo, *args], capture_output=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.decode("utf-8", "replace").strip() if done.returncode == 0 else None


def ref_ok(repo: str, ref: str) -> bool:
    return git(repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}") is not None


def fetch(repo: str, skip: bool = False) -> str:
    """One quiet `git fetch origin` per checkout per run. Returns fetched, skipped, no-remote or failed."""
    if skip:
        return "skipped"
    if repo in _FETCHED:
        return "fetched"
    if not git(repo, "remote", "get-url", "origin"):
        return "no-remote"
    if git(repo, "fetch", "--quiet", "--prune", "origin", timeout=60) is None:
        return "failed"
    _FETCHED.add(repo)
    return "fetched"


def prefer_ref(repo: str, name: str) -> str:
    """origin/<name> first, then the local <name>; "" when neither exists."""
    if name.startswith("origin/"):
        return name if ref_ok(repo, name) else ""
    for cand in (f"origin/{name}", name):
        if ref_ok(repo, cand):
            return cand
    return ""


def is_ancestor(repo: str, older: str, newer: str) -> bool:
    try:
        done = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", older, newer],
                              capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def tip_merged(repo: str, tip: str, base_ref: str) -> dict | None:
    """When the branch tip is in the base: {merge, merge_short, pr, subject}; else None."""
    if not tip or not base_ref or not is_ancestor(repo, tip, base_ref):
        return None
    tip_sha = git(repo, "rev-parse", tip) or ""
    base_sha = git(repo, "rev-parse", base_ref) or ""
    if tip_sha and tip_sha == base_sha:
        return None
    merges = (git(repo, "rev-list", "--merges", "--ancestry-path", "--reverse", f"{tip}..{base_ref}") or "").split()
    merge = merges[0] if merges else tip_sha
    subject = git(repo, "log", "-1", "--format=%s", merge) or ""
    m = PR_SUBJECT.search(subject)
    pr = next((g for g in m.groups() if g), None) if m else None
    return {"merge": merge, "merge_short": merge[:7], "pr": pr, "subject": subject}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Shared start-check: base ref and merged tip.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("state")
    s.add_argument("--code-repo", required=True)
    s.add_argument("--branch", required=True)
    s.add_argument("--base", required=True)
    s.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args(argv)
    fetched = fetch(a.code_repo, a.no_fetch)
    base = prefer_ref(a.code_repo, a.base)
    tip = prefer_ref(a.code_repo, a.branch)
    merged = tip_merged(a.code_repo, tip, base) if base and tip else None
    json.dump({"ok": True, "fetch": fetched, "base": base, "tip": tip, "merged": merged}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
