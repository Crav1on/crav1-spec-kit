#!/usr/bin/env python3
"""Fail when a pull request changes a skill's SKILL.md without touching docs/ for it.

A skill counts as documented in the pull request when at least one changed file
under docs/, outside docs/reference/, is the skill's walkthrough (its
`walkthrough` in docs/reference/skills.yaml), or has a changed line that names
the skill (for example `crav1-review-pr` or `/crav1-review-pr`), such as a
concept or data layout entry. The reference pages do not count, because they
are generated from skills.yaml.

Opt-out: the `docs-not-needed` label, or a line in the pull request body that
starts with `Docs-not-needed:` followed by the reason.

Usage: check-skill-docs-touched.py <base-ref> [<head-ref>]
Reads the pull request labels and body from $GITHUB_EVENT_PATH when it is set.
"""
import json
import os
import re
import subprocess
import sys

SKILL_PATHS = [
    re.compile(r"^\.cursor/skills/crav1/(?P<name>[^/]+)/SKILL\.md$"),
    re.compile(r"^plugins/crav1/skills/(?P<name>[^/]+)/SKILL\.md$"),
    re.compile(r"^\.claude/skills/(?P<name>[^/]+)/SKILL\.md$"),
]
OPT_OUT_LABEL = "docs-not-needed"
OPT_OUT_LINE = re.compile(r"^\s*Docs-not-needed:\s*\S", re.IGNORECASE | re.MULTILINE)


def opted_out():
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        pr = json.load(f).get("pull_request") or {}
    labels = {l.get("name") for l in pr.get("labels", [])}
    if OPT_OUT_LABEL in labels:
        print(f"Opt-out: the pull request has the `{OPT_OUT_LABEL}` label.")
        return True
    if OPT_OUT_LINE.search(pr.get("body") or ""):
        print("Opt-out: the pull request body has a `Docs-not-needed:` line.")
        return True
    return False


def load_walkthroughs():
    """Map skill name to walkthrough path from skills.yaml, without PyYAML."""
    out, name = {}, None
    try:
        with open("docs/reference/skills.yaml", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^- name:\s*(\S+)", line)
                if m:
                    name = m.group(1)
                    continue
                m = re.match(r"^\s+walkthrough:\s*(\S+)", line)
                if m and name and m.group(1) != "null":
                    out[name] = m.group(1)
    except FileNotFoundError:
        pass
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        check=True, capture_output=True, text=True,
    ).stdout.split()

    skills = set()
    for p in changed:
        for rx in SKILL_PATHS:
            m = rx.match(p)
            if m:
                skills.add(m.group("name"))
    if not skills:
        print("No SKILL.md changed.")
        return 0
    if opted_out():
        return 0

    docs = [p for p in changed if p.startswith("docs/") and not p.startswith("docs/reference/")]
    walkthroughs = load_walkthroughs()
    missing = []
    for name in sorted(skills):
        hits = []
        for p in docs:
            if walkthroughs.get(name) == p:
                hits.append(p)
                continue
            diff = subprocess.run(
                ["git", "diff", "-U0", f"{base}...{head}", "--", p],
                check=True, capture_output=True, text=True,
            ).stdout
            lines = [l for l in diff.splitlines()
                     if l[:1] in "+-" and not l.startswith(("+++", "---"))]
            if any(name in l for l in lines):
                hits.append(p)
        if hits:
            print(f"ok   {name}: docs touched ({', '.join(hits)})")
        else:
            missing.append(name)
            print(f"FAIL {name}: SKILL.md changed, but no docs change outside docs/reference/ covers it")
    if missing:
        print(
            "\nUpdate the skill's walkthrough (docs/from-*.md) and its concept or data layout"
            " entries in docs/concepts/, as CONTRIBUTING.md says. If the change really needs no"
            f" docs, add the `{OPT_OUT_LABEL}` label or a `Docs-not-needed: <reason>` line to the"
            " pull request body."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
