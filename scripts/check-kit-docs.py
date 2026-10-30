#!/usr/bin/env python3
"""Kit checks that are not about the generated pages.

  scripts/check-kit-docs.py   exit non-zero when
    - a skill description in .cursor/skills/crav1/, plugins/crav1/skills/, or
      .claude/skills/ is longer than 1,024 characters (Agent Skills limit), or
    - plugins/crav1/.cursor-plugin/plugin.json "version" differs from the
      newest release heading in CHANGELOG.md (## X.Y.Z ...).
  It also warns, without failing, when a SKILL.md in .cursor/skills/crav1/ is
  over 2,000 words (1.71.0): keep the common path there and move rare cases
  into references/ with a one-line pointer.

Needs PyYAML (pip install pyyaml).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is missing. Install it with: python3 -m pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
TREES = (".cursor/skills/crav1", "plugins/crav1/skills", ".claude/skills")
LIMIT = 1024
DESC_WORDS = 60  # 1.106.0: descriptions load up front for skill matching; trigger text only
WORDS = 2000


def descriptions() -> list[str]:
    errors: list[str] = []
    for tree in TREES:
        for path in sorted((ROOT / tree).glob("*/SKILL.md")):
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                errors.append(f"{path.relative_to(ROOT)}: no frontmatter")
                continue
            front = yaml.safe_load(text.split("---", 2)[1])
            desc = str(front.get("description", ""))
            if not desc:
                errors.append(f"{path.relative_to(ROOT)}: description is empty")
            elif len(desc) > LIMIT:
                errors.append(f"{path.relative_to(ROOT)}: description is {len(desc)} characters (limit {LIMIT})")
            elif len(desc.split()) > DESC_WORDS:
                errors.append(f"{path.relative_to(ROOT)}: description is {len(desc.split())} words (limit {DESC_WORDS})")
    return errors


def version() -> list[str]:
    manifest = json.loads((ROOT / "plugins/crav1/.cursor-plugin/plugin.json").read_text(encoding="utf-8"))
    m = re.search(r"^## (\d+\.\d+\.\d+)\b", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    if not m:
        return ["CHANGELOG.md has no release heading (## X.Y.Z)"]
    if manifest.get("version") != m.group(1):
        return [f"plugin.json version {manifest.get('version')} differs from the newest CHANGELOG release {m.group(1)}"]
    return []


def workflow_stamp() -> list[str]:
    """Every copy of workflow.md carries the plugin.json version (1.93.1)."""
    want = json.loads((ROOT / "plugins/crav1/.cursor-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    out = []
    for path in sorted(ROOT.glob("**/reference/workflow.md")):
        if ".git" in path.parts:
            continue
        m = re.search(r"^Kit version: (\S+)$", path.read_text(encoding="utf-8"), re.M)
        got = m.group(1) if m else None
        if got != want:
            out.append(f"{path.relative_to(ROOT)} Kit version {got} differs from plugin.json {want}; run scripts/gen-workflow.py and sync")
    return out


def word_warnings() -> list[str]:
    out: list[str] = []
    for path in sorted((ROOT / TREES[0]).glob("*/SKILL.md")):
        n = len(path.read_text(encoding="utf-8").split())
        if n > WORDS:
            rel = path.relative_to(ROOT)
            out.append(f"::warning file={rel}::{rel} is {n} words (over {WORDS:,}); move rare cases into references/")
    return out


def main() -> int:
    for w in word_warnings():
        print(w)
    errors = descriptions() + version() + workflow_stamp()
    for e in errors:
        print(e)
    if errors:
        return 1
    print("Skill descriptions are within 60 words and 1,024 characters; plugin.json matches the newest CHANGELOG release and every workflow.md stamp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
