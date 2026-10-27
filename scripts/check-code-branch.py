#!/usr/bin/env python3
"""Kit 1.99.0: every skill file that writes or commits implementation code points to the
code-branch guard, and the create-feature-branch Build prompt never offers Stay on a base branch.

Run from the repo root: python scripts/check-code-branch.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ".cursor/skills/crav1/crav1-create-feature-branch/references/code-branch.md"
CODE_WRITERS = [
    ".cursor/skills/crav1/crav1-build-tasks/branches/implement/BRANCH.md",
    ".cursor/skills/crav1/crav1-build-tasks/branches/one-task/BRANCH.md",
    ".cursor/skills/crav1/crav1-build-tasks/branches/several-tasks/BRANCH.md",
    ".cursor/skills/crav1/crav1-build-tasks/branches/one-task/references/run.md",
    ".cursor/agents/crav1-build-task-agent.md",
    ".cursor/skills/crav1/crav1-build-features/SKILL.md",
    ".cursor/skills/crav1/crav1-fix-build-gaps/branches/verify-gaps/BRANCH.md",
    ".cursor/skills/crav1/crav1-finalize-commit/SKILL.md",
    ".cursor/skills/crav1/crav1-finalize-commit/references/base-branch.md",
    ".cursor/rules/crav1.mdc",
]
# The worker agent names the rule inline (it has no room for the pointer); it must still block on a base.
INLINE_OK = {".cursor/agents/crav1-build-task-agent.md": "on base branch"}


def main() -> int:
    errors: list[str] = []
    guard = ROOT / GUARD
    if not guard.is_file():
        errors.append(f"{GUARD} is missing")
    else:
        g = guard.read_text(encoding="utf-8")
        for need in ("release/*", "hotfix/", "Use an existing branch", "Other name", "Stop", "new branch", "STATUS: blocked"):
            if need not in g:
                errors.append(f"{GUARD} does not mention {need!r}")
    for rel in CODE_WRITERS:
        p = ROOT / rel
        if not p.is_file():
            errors.append(f"{rel} is missing")
            continue
        text = p.read_text(encoding="utf-8")
        if "code-branch.md" in text or "base-branch.md" in text:
            continue
        if rel in INLINE_OK and INLINE_OK[rel] in text:
            continue
        errors.append(f"{rel} writes or commits code but does not point to code-branch.md")
    cfb = (ROOT / ".cursor/skills/crav1/crav1-create-feature-branch/SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^\*\*Build\*\*.*?(?=^\*\*Task branch)", cfb, re.M | re.S)
    if not m:
        errors.append("create-feature-branch SKILL.md has no **Build** prompt section")
    else:
        for line in m.group(0).splitlines():
            if "base" in line.lower() and re.search(r"\*\*Stay\b", line) and "No Stay" not in line:
                errors.append(f"create-feature-branch Build prompt offers Stay on a base: {line.strip()[:120]}")
        if "No Stay on a base" not in m.group(0):
            errors.append("create-feature-branch Build prompt does not say No Stay on a base")
    for e in errors:
        print(f"ERROR: {e}")
    if not errors:
        print(f"code-branch guard: {len(CODE_WRITERS)} code-writing files point to it; no Stay on a base")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
