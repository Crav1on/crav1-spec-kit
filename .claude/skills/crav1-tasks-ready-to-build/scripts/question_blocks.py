#!/usr/bin/env python3
"""Which kept-open questions block which tasks (kit 1.125.0).

Reads `## Open questions` in spec.md and `## Risks` in plan.md. A question with
an Answered line is not kept open. `Blocks: T2, T4` blocks those tasks.
`Blocks: none` blocks no task, with an optional reason in parentheses.
No Blocks line blocks the whole slice. Any Blocks line wins over a Risk that
says "do not implement until resolved".

Usage: question_blocks.py <spec.md> [plan.md]
Prints JSON. Standard library only. Writes nothing.
"""
import json
import re
import sys

TASKS = re.compile(r"^T\d+(, T\d+)*$")
NONE = re.compile(r"^none(?: \(([^)]+)\))?$")
PHRASE = "do not implement until resolved"


def _section(text, heading):
    lines = text.splitlines()
    start = None
    want = heading.strip().lower()
    for i, line in enumerate(lines):
        if line.strip().lower() == want:
            start = i + 1
            break
    if start is None:
        return []
    out = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def _norm(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def kept_open(text):
    """Kept-open questions, in document order.

    mark is tasks, none, missing, or unparsed. blocks_slice is true only when
    there is no readable Blocks line that limits or clears the block.
    """
    questions = []
    current = None
    for line in _section(text, "## Open questions"):
        if line.startswith("- ") and not line.startswith("  "):
            body = line[2:].strip()
            current = {"text": body, "marks": []} if body else None
            if current:
                questions.append(current)
            continue
        if current is not None and line.startswith("  - "):
            current["marks"].append(line[4:].strip())
    out = []
    for q in questions:
        if any(m.startswith("Answered:") for m in q["marks"]):
            continue
        blocks = [m[len("Blocks:"):].strip() for m in q["marks"] if m.startswith("Blocks:")]
        line = blocks[-1] if blocks else None
        reason = None
        if line is None:
            mark, tasks = "missing", []
        else:
            none = NONE.fullmatch(line)
            if none:
                mark, tasks, reason = "none", [], none.group(1)
            elif TASKS.fullmatch(line):
                mark, tasks = "tasks", [part.strip() for part in line.split(",")]
            else:
                mark, tasks = "unparsed", []
        out.append({
            "text": q["text"],
            "mark": mark,
            "tasks": tasks,
            "reason": reason,
            "blocks_slice": mark in ("missing", "unparsed"),
            "recorded": mark in ("tasks", "none"),
        })
    return out


def risks(plan_text, questions):
    """Risk lines that say do not implement until resolved.

    blocks_slice is false when the line is about a question that has any
    Blocks line. The Blocks line wins.
    """
    rows = []
    for line in _section(plan_text, "## Risks"):
        if PHRASE not in line.lower():
            continue
        low = _norm(line)
        matched = None
        for q in questions:
            if _norm(q["text"]) and _norm(q["text"]) in low:
                matched = q
                break
        if matched and matched["mark"] != "missing":
            blocks = False
            because = "the question has a Blocks line"
        else:
            blocks = True
            because = "no Blocks line"
        rows.append({
            "text": line.strip(),
            "blocks_slice": blocks,
            "question": matched["text"] if matched else None,
            "because": because,
        })
    return rows


def analyse(spec_text, plan_text=""):
    questions = kept_open(spec_text)
    return {"questions": questions, "risks": risks(plan_text, questions)}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    spec = open(argv[0], encoding="utf-8").read()
    plan = open(argv[1], encoding="utf-8").read() if len(argv) > 1 else ""
    print(json.dumps(analyse(spec, plan), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
