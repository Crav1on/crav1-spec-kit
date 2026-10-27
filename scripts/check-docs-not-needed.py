#!/usr/bin/env python3
"""Flag a `Docs-not-needed:` line when the pull request changes docs/ (1.96.0).

A pull request that regenerates docs or touches anything under docs/ updated
the docs, so its body must not say `Docs-not-needed:`. The release stamp alone
(the `Kit version:` line in docs/reference/workflow.md, bumped in every release
commit) does not count as a docs change.

Prints a GitHub warning; does not fail the run.

Usage: check-docs-not-needed.py <base-ref> [<head-ref>]
Reads the pull request body from $GITHUB_EVENT_PATH.
"""
import json
import os
import re
import subprocess
import sys

LINE = re.compile(r"^\s*Docs-not-needed:", re.IGNORECASE | re.MULTILINE)
STAMP_FILE = "docs/reference/workflow.md"
STAMP = re.compile(r"^[+-]Kit version: ")


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def body():
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return (json.load(f).get("pull_request") or {}).get("body") or ""


def stamp_only(rng):
    diff = git("diff", "-U0", rng, "--", STAMP_FILE).splitlines()
    changed = [d for d in diff if d[:1] in "+-" and not d.startswith(("+++", "---"))]
    return all(STAMP.match(d) for d in changed)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    rng = f"{base}...{head}"
    docs = [p for p in git("diff", "--name-only", rng).split() if p.startswith("docs/")]
    if docs == [STAMP_FILE] and stamp_only(rng):
        docs = []
    if not LINE.search(body()):
        print("No Docs-not-needed line in the pull request body.")
        return
    if not docs:
        print("Docs-not-needed line, and nothing under docs/ changed beyond the release stamp.")
        return
    shown = ", ".join(docs[:5]) + (f" and {len(docs) - 5} more" if len(docs) > 5 else "")
    print(f"::warning title=Docs-not-needed with docs changes::This pull request changes {len(docs)} "
          f"file(s) under docs/ ({shown}), so its body must not say Docs-not-needed. "
          "Remove the line and say which docs changed.")


if __name__ == "__main__":
    main()
