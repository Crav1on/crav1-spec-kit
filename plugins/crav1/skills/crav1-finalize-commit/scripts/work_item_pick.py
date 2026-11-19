#!/usr/bin/env python3
"""Pick the work-item mention for a commit (1.193.0): one line, or one question card when unclear.

Reads docs/specs/<slug>/work-item.md as branches/message-only/references/work-item-mention.md says and
counts Feature lines only. With several Feature lines and no label that matches a named slice, it
returns status `ask` with at most 4 options (the last is `No mention`) plus a typed Other. It never
reads git log or an earlier commit. commit-now asks this too; a headless run ends as `copy`.

  work_item_pick.py --file docs/specs/<slug>/work-item.md [--slice <name>]...
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

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

LINE_RE = re.compile(r"^\s*(?:work item:\s*)?(?P<id>AB#\d+|#\d+|\d+)(?:\s+(?:—|-)\s+(?P<label>.*?))?\s*$", re.I)
HOME_RE = re.compile(r"\s*\(ADO: [^)]*\)\s*$")
TASK_RE = re.compile(r"^task:\s*T\d+", re.I)
MAX_OPTIONS = 4


def feature_lines(text: str) -> list[dict]:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for raw in text.splitlines():
        line = HOME_RE.sub("", raw).strip()
        if not line:
            continue
        if not line.lower().startswith("work item:") and not line.startswith(("AB#", "#")):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        label = (m.group("label") or "").strip()
        if TASK_RE.match(label):
            continue
        out.append({"id": m.group("id"), "label": label})
    return out


def pick(text: str, slices: list[str]) -> dict:
    lines = feature_lines(text)
    if not lines:
        return {"status": "none", "lines": 0}
    if len(lines) == 1:
        return {"status": "one", "mention": lines[0]}
    wanted = {s.strip().lower() for s in slices if s.strip()}
    hits = [l for l in lines if l["label"] and l["label"].lower() in wanted]
    if len(hits) == 1:
        return {"status": "one", "mention": hits[0]}
    shown = lines[: MAX_OPTIONS - 1]
    options = [f"{l['id']} - {l['label'] or 'no label'}" for l in shown] + ["No mention"]
    return {
        "status": "ask",
        "question": "Which work item should this commit mention?",
        "options": options,
        "other": "Type another recorded id or label" if len(lines) > len(shown) else "Type an id or label",
        "lines": len(lines),
        "never": "Do not copy a mention from git log or an earlier commit.",
        "headless": "copy",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", required=True)
    ap.add_argument("--slice", action="append", default=[], help="a milestone or slice this turn shows; repeatable")
    a = ap.parse_args(argv)
    path = Path(a.file)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    out = pick(text, a.slice) if text else {"status": "none", "lines": 0, "missing": True}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
