#!/usr/bin/env python3
"""Which kept-open questions block which tasks (kit 1.127.0).

Reads `## Open questions` in spec.md and `## Risks` in plan.md. A question with
an Answered line is not kept open. `Blocks: T2, T4` blocks those tasks.
`Blocks: none` blocks no task, with an optional reason in parentheses.
No Blocks line blocks the whole slice. Any Blocks line wins over a Risk that
says "do not implement until resolved".

A Risk matches a question on the question's first sentence, on an explicit
`(question: <first words>)` tag, or when the Risk names the same `Blocks T#`
tasks. A Risk that uses the phrase and matches no question blocks the slice;
`because` is "no matching question".

Usage: question_blocks.py <spec.md> [plan.md]
Prints JSON. Standard library only. Writes nothing.
"""
import json
import re
import sys

def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

TASKS = re.compile(r"^T\d+(, T\d+)*$")
NONE = re.compile(r"^none(?: \(([^)]+)\))?$")
PHRASE = "do not implement until resolved"
QUESTION_TAG = re.compile(r"\(question:\s*([^)]+)\)", re.I)
NAMED_BLOCKS = re.compile(r"\bblocks:?\s*((?:T\d+\s*(?:,\s*)?)+)", re.I)
ASKED_WHO = re.compile(r"\bto\s+([^.,;]+)")
PENDING_WHO = re.compile(r"\bfor\s+([^.,;]+)")
# The question's own "Waiting for <who>" wins over the person named on Asked or Pending.
WAITING_FOR = re.compile(
    r"\bwaiting for\s+(.+?)(?=\s+(?:to|on|before|until|about)\b|[,.;?!]|$)",
    re.I,
)


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


def _first_sentence(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)
    return parts[0].strip()


def _who_waiting(text):
    """Who from the question's own "Waiting for <who>" phrase, if it has one."""
    found = WAITING_FOR.search(text or "")
    if not found:
        return None
    who = found.group(1).strip()
    return who or None


def _who_asked(marks):
    """Who from the latest Asked or Pending line, and whether any Asked line exists."""
    who = None
    asked = False
    for mark in marks:
        if mark.startswith("Asked:"):
            asked = True
            found = ASKED_WHO.search(mark)
            if found:
                who = found.group(1).strip()
        elif mark.startswith("Pending:"):
            found = PENDING_WHO.search(mark)
            if found:
                who = found.group(1).strip()
    return who, asked


def _named_blocks(line):
    found = []
    for match in NAMED_BLOCKS.finditer(line):
        for task in re.findall(r"T\d+", match.group(1)):
            if task not in found:
                found.append(task)
    return found


def _match_question(line, questions):
    """Link a Risk to one question. The whole question line is not required."""
    tag_match = QUESTION_TAG.search(line)
    if tag_match:
        tag = _norm(tag_match.group(1))
        hits = []
        for q in questions:
            sentence = _norm(_first_sentence(q["text"]))
            full = _norm(q["text"])
            if tag and (sentence.startswith(tag) or full.startswith(tag)):
                hits.append(q)
        if hits:
            hits.sort(key=lambda q: len(_norm(_first_sentence(q["text"]))))
            return hits[0]
    low = _norm(line)
    for q in questions:
        sentence = _norm(_first_sentence(q["text"]))
        if sentence and sentence in low:
            return q
    named = _named_blocks(line)
    if not named:
        return None
    wanted = set(named)
    exact = [q for q in questions if q["mark"] == "tasks" and set(q["tasks"]) == wanted]
    if len(exact) == 1:
        return exact[0]
    holding = [q for q in questions if q["mark"] == "tasks" and wanted <= set(q["tasks"])]
    if len(holding) == 1:
        return holding[0]
    return None


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
        mark_who, asked = _who_asked(q["marks"])
        who = _who_waiting(q["text"]) or mark_who
        out.append({
            "text": q["text"],
            "mark": mark,
            "tasks": tasks,
            "reason": reason,
            "who": who,
            "asked": asked,
            "blocks_slice": mark in ("missing", "unparsed"),
            "recorded": mark in ("tasks", "none"),
        })
    return out


def risks(plan_text, questions):
    """Risk lines that say do not implement until resolved.

    blocks_slice is false when the line matches a question that has any
    Blocks line. The Blocks line wins. A line that matches no question
    still blocks the slice.
    """
    rows = []
    for line in _section(plan_text, "## Risks"):
        if PHRASE not in line.lower():
            continue
        matched = _match_question(line, questions)
        if matched is None:
            blocks = True
            because = "no matching question"
        elif matched["mark"] != "missing":
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


def _emit(text):
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except UnicodeEncodeError:
        sys.stdout.write(text.encode("ascii", "replace").decode("ascii"))
        sys.stdout.flush()


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        _emit(__doc__ or "")
        return 0
    spec = open(argv[0], encoding="utf-8").read()
    plan = open(argv[1], encoding="utf-8").read() if len(argv) > 1 else ""
    _emit(json.dumps(analyse(spec, plan), ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
