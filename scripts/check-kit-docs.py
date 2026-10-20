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
    return errors


def version() -> list[str]:
    manifest = json.loads((ROOT / "plugins/crav1/.cursor-plugin/plugin.json").read_text(encoding="utf-8"))
    m = re.search(r"^## (\d+\.\d+\.\d+)\b", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    if not m:
        return ["CHANGELOG.md has no release heading (## X.Y.Z)"]
    if manifest.get("version") != m.group(1):
        return [f"plugin.json version {manifest.get('version')} differs from the newest CHANGELOG release {m.group(1)}"]
    return []


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
    errors = descriptions() + version()
    for e in errors:
        print(e)
    if errors:
        return 1
    print("Skill descriptions are within 1,024 characters; plugin.json matches the newest CHANGELOG release")
    return 0


if __name__ == "__main__":
    sys.exit(main())
