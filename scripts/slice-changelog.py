#!/usr/bin/env python3
"""Slice the repo-root changelog for install bundles.

The kit repo root CHANGELOG.md stays the full history. Each install's
crav1-docs/CHANGELOG.md (Cursor drop-in, Cursor plugin, Claude Code) keeps
the newest 15 release sections and one line that points at the full file
on GitHub.

  scripts/slice-changelog.py                 print the slice
  scripts/slice-changelog.py --write PATH    write the slice
  scripts/slice-changelog.py --check PATH    exit 1 when PATH is not the slice

The interpreter is python3 on this host (docs/reference/running-scripts.md).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CHANGELOG.md"
KEEP = 15
HEADING = re.compile(r"^## (\d+\.\d+\.\d+)\b", re.M)
FULL_URL = "https://github.com/Crav1on/crav1-spec-kit/blob/main/CHANGELOG.md"
FOOTER = (
    f"The newest {KEEP} releases are above. The full changelog is {FULL_URL}."
)


def slice_text(text: str, keep: int = KEEP) -> str:
    """Preamble plus the newest `keep` release sections, then the pointer line."""
    text = text.replace("\r\n", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    matches = list(HEADING.finditer(text))
    if not matches:
        raise SystemExit("CHANGELOG.md has no release heading (## X.Y.Z)")
    end = matches[keep].start() if len(matches) > keep else len(text)
    body = text[:end].rstrip() + "\n\n" + FOOTER + "\n"
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--keep", type=int, default=KEEP)
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--write", type=Path, metavar="PATH")
    group.add_argument("--check", type=Path, metavar="PATH")
    args = ap.parse_args()
    sliced = slice_text(args.source.read_text(encoding="utf-8"), args.keep)
    if args.check:
        got = args.check.read_text(encoding="utf-8") if args.check.is_file() else ""
        if got != sliced:
            print(
                f"{args.check} is not the newest {args.keep} releases of {args.source}",
                file=sys.stderr,
            )
            return 1
        print(f"{args.check} matches the newest {args.keep} releases")
        return 0
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(sliced, encoding="utf-8")
        print(f"Wrote {args.write}")
        return 0
    sys.stdout.write(sliced)
    return 0


if __name__ == "__main__":
    sys.exit(main())
