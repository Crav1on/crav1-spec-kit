#!/usr/bin/env python3
"""Which kept-open questions block which tasks (kit 1.137.0).

Reads `## Open questions` in spec.md and `## Risks` in plan.md. A question with
an Answered line is not kept open. `Blocks: T2, T4` blocks those tasks.
`Blocks: none` blocks no task, with an optional reason in parentheses.
`Blocks: whole slice` (also `the whole slice`, any case) holds every
unfinished task and stays a recorded hold after resolve-open-questions is
recorded. No Blocks line: `T#` ids in the question text that exist in
tasks.md are the hold, marked inferred from the text. The whole slice is
held only when the text names no such task and the caller says
resolve-open-questions has never been recorded. Any Blocks line wins over a
Risk that says "do not implement until resolved".

A Risk matches a question on the question's first sentence, on an explicit
`(question: <first words>)` tag, or when the Risk names the same `Blocks T#`
tasks. A Risk that uses the phrase and matches no question blocks the slice;
`because` is "no matching question".

Usage: question_blocks.py <spec.md> [plan.md] [tasks.md]
Prints JSON. Standard library only. Writes nothing. The ready check passes
resolve_recorded when that step is already in walk-progress.md. This command
does not, so a question that names no task still holds the slice.
"""
import hashlib
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
TASK_ID = re.compile(r"\bT\d+\b")
TASK_LINE = re.compile(r"(?m)^- \[[ xX]\] (T\d+)\b")
NONE = re.compile(r"^none(?: \(([^)]+)\))?$")
WHOLE = re.compile(r"^(?:the\s+)?whole\s+slice$", re.I)
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


def question_key(text):
    """Stable id for one question's words. Used to remember it was already waiting."""
    return hashlib.sha256(_norm(text or "").encode("utf-8")).hexdigest()[:12]


def task_ids_from_tasks(text):
    """T# ids on task lines, in document order."""
    found = []
    for match in TASK_LINE.finditer(text or ""):
        tid = match.group(1)
        if tid not in found:
            found.append(tid)
    return found


def _text_tasks(text, known):
    """T# ids named in the question text that exist in tasks.md, in order.

    known is None when tasks.md was not passed. Then nothing is inferred.
    """
    if known is None:
        return []
    allowed = set(known)
    found = []
    for match in TASK_ID.finditer(text or ""):
        tid = match.group(0)
        if tid in allowed and tid not in found:
            found.append(tid)
    return found


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


def kept_open(text, task_ids=None, resolve_recorded=False):
    """Kept-open questions, in document order.

    mark is tasks, none, whole, inferred, missing, or unparsed. `Blocks:
    whole slice` is recorded and blocks_slice. A missing line blocks_slice
    only when the text names no task that exists in tasks.md and
    resolve-open-questions has never been recorded. A Blocks line still
    limits or clears the block.
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
        blocks = []
        for mark_line in q["marks"]:
            if mark_line.lower().startswith("blocks:"):
                blocks.append(mark_line.split(":", 1)[1].strip())
        line = blocks[-1] if blocks else None
        reason = None
        blocks_slice = False
        if line is None:
            named = _text_tasks(q["text"], task_ids)
            if named:
                mark, tasks = "inferred", named
            elif resolve_recorded:
                mark, tasks = "missing", []
            else:
                mark, tasks = "missing", []
                blocks_slice = True
        else:
            none = NONE.fullmatch(line)
            if none:
                mark, tasks, reason = "none", [], none.group(1)
            elif WHOLE.fullmatch(line):
                mark, tasks = "whole", []
                blocks_slice = True
            elif TASKS.fullmatch(line):
                mark, tasks = "tasks", [part.strip() for part in line.split(",")]
            else:
                mark, tasks = "unparsed", []
                blocks_slice = True
        mark_who, asked = _who_asked(q["marks"])
        who = _who_waiting(q["text"]) or mark_who
        out.append({
            "text": q["text"],
            "key": question_key(q["text"]),
            "mark": mark,
            "tasks": tasks,
            "reason": reason,
            "who": who,
            "asked": asked,
            "blocks_slice": blocks_slice,
            "inferred": mark == "inferred",
            "recorded": mark in ("tasks", "none", "whole"),
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
        elif matched["mark"] == "inferred":
            blocks = False
            because = "inferred from the text"
        elif matched["mark"] != "missing":
            blocks = False
            because = "the question has a Blocks line"
        elif not matched["blocks_slice"]:
            blocks = False
            because = "resolve-open-questions is already recorded"
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


def analyse(spec_text, plan_text="", task_ids=None, resolve_recorded=False):
    questions = kept_open(spec_text, task_ids=task_ids, resolve_recorded=resolve_recorded)
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
    task_ids = None
    if len(argv) > 2:
        task_ids = task_ids_from_tasks(open(argv[2], encoding="utf-8").read())
    _emit(json.dumps(analyse(spec, plan, task_ids=task_ids), ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
