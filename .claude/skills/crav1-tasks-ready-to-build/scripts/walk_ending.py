#!/usr/bin/env python3
"""One shared ending for the ready check and the walks (kit 1.156.0).

The ready check (/crav1-tasks-ready-to-build), the tighten-and-plan ready
check, and /crav1-build-walk all end a run in the same shape, built here:

  1. Run next, first. One block per ready branch (1.164.0): the bold
     branch, one plain sentence from its plan step, `<n> open tasks:` one
     per line, then `Run the whole branch:` and `Run only T#, the first
     task:`, each command alone in its code span on the line under its
     label. One open task: `Run T#:` and one command.
  2. Held lines, then Branch runs status lines.
  3. Built (one line per task) and Left, for a branch run.
  4. Loop, verify-behind, orphan and other Waiting lines.
  5. The not-ready reason (only when it is not already the Run next
     line), at most the one-line /crav1-build-tasks alternative, notes,
     and Uncommitted.
  A walk ending has no Next line (1.157.0). A not-ready ready check
  starts its ending with Run next, naming the first real next step
  (1.163.0). An agent never adds a Next line of its own.

The skills print the text these functions return, as-is. The ready check's
`reply` (header, counts, Result, ending, Source, Build map) is ready_reply().

Usage:
  walk_ending.py --json <state file>   prints compose() of that state
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ALTERNATIVE = "/crav1-build-tasks builds one task without the walk."
COUNT_COLUMNS = (
    ("Ready", "ready"),
    ("Waiting", "waiting"),
    ("Waits in order", "waits_in_order"),
    ("Blocked", "blocked"),
    ("Needs verify", "needs_verify"),
    ("Done", "done"),
)


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


# ---------- Run next entries ----------

def run_entry(labels, branch_name, slug=None):
    """One ready branch's next-task entry (1.150.0).

    The command is alone on its line, inside a code span, and is a complete
    invocation for a new session: the command, each T#, and the slug when
    the caller passes one. The next line names the branch and each short
    task name.
    """
    ids = []
    names = []
    for label in labels:
        match = re.match(r"(T\d+)\s+(.*)", str(label).strip())
        if match:
            ids.append(match.group(1))
            names.append(f"{match.group(1)} {match.group(2).strip()}")
        else:
            token = str(label).strip()
            ids.append(token)
            names.append(token)
    ids_text = ", ".join(ids)
    command = f"/crav1-build-walk {slug} {ids_text}" if slug else f"/crav1-build-walk {ids_text}"
    detail = f"branch {branch_name}, {', '.join(names)}"
    return f"`{command}`\n{detail}"


def branch_entry(open_labels, branch_name, slug=None):
    """The whole-branch entry (1.155.0), offered with two or more open tasks."""
    names = [str(label).strip() for label in open_labels or [] if str(label).strip()]
    command = f"/crav1-build-walk {slug} {branch_name}" if slug else f"/crav1-build-walk {branch_name}"
    return f"`{command}`\nbranch {branch_name}, every open task: {', '.join(names)}"


def about_sentence(text, limit=140):
    """One plain sentence of what a branch does, from its plan step (1.164.0)."""
    one = re.sub(r"[*_`]+", "", str(text or ""))
    one = re.sub(r"\s+", " ", one).strip()
    if not one:
        return ""
    one = re.split(r"(?<=[.!?])\s", one, maxsplit=1)[0]
    if len(one) > limit:
        one = one[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"
    if one[-1] not in ".!?…":
        one += "."
    return one[:1].upper() + one[1:]


def _task_id(label):
    match = re.match(r"(T\d+)\b", str(label).strip())
    return match.group(1) if match else str(label).strip()


def branch_block(branch_name, open_labels, first=None, slug=None, about=None):
    """One ready branch in Run next (1.164.0).

    The bold branch, one plain sentence from its plan step (left out when
    there is none), the open tasks one per line, then each command alone in
    its code span under a label line: the whole branch first, then only the
    first task. A branch with one open task gets `Run T#:` and one command.
    """
    names = [str(label).strip() for label in open_labels or [] if str(label).strip()]
    first = str(first).strip() if first else (names[0] if names else "")
    if not names and first:
        names = [first]
    if not names:
        return ""
    lines = [f"**{branch_name}**"]
    sentence = about_sentence(about) if about else ""
    if sentence:
        lines.append(sentence)
    count = len(names)
    lines.append(f"{count} open task{'' if count == 1 else 's'}:")
    lines.extend(f"- {name}" for name in names)
    lines.append("")
    first_id = _task_id(first)
    task_cmd = f"/crav1-build-walk {slug} {first_id}" if slug else f"/crav1-build-walk {first_id}"
    if count == 1:
        lines.append(f"Run {first_id}:")
        lines.append(f"`{task_cmd}`")
    else:
        branch_cmd = f"/crav1-build-walk {slug} {branch_name}" if slug else f"/crav1-build-walk {branch_name}"
        lines.append("Run the whole branch:")
        lines.append(f"`{branch_cmd}`")
        lines.append(f"Run only {first_id}, the first task:")
        lines.append(f"`{task_cmd}`")
    return "\n".join(lines)


def run_entries(labels, branch_name, slug=None, open_labels=None, about=None):
    """One Run next block per ready branch (1.164.0): see branch_block."""
    labels = [label for label in labels or [] if str(label).strip()]
    if not labels:
        return []
    opens = list(open_labels) if open_labels is not None else list(labels)
    return [branch_block(branch_name, opens, first=labels[0], slug=slug, about=about)]


def run_block(entries) -> str:
    """`Run next:` and each entry, a blank line between entries."""
    runs = [str(entry) for entry in entries or [] if str(entry).strip()]
    if not runs:
        return ""
    return "Run next:\n\n" + "\n\n".join(runs)


# ---------- The ending ----------

def _prefixed(text, word):
    text = str(text).strip()
    if not text:
        return ""
    return text if text.startswith(word + ":") else f"{word}: {text}"


def compose(
    run=None,
    held=None,
    branch_runs=None,
    built=None,
    built_header=None,
    left=None,
    waiting=None,
    because=None,
    alternatives=None,
    notes=None,
    uncommitted=None,
) -> str:
    """The one ending, in the shared order. Empty parts are left out."""
    parts: list[str] = []
    block = run_block(run)
    if block:
        parts.append(block)
    if held:
        parts.append("Held:\n" + "\n".join(str(line) for line in held))
    if branch_runs:
        parts.append("Branch runs:\n" + "\n".join(str(line) for line in branch_runs))
    if built:
        parts.append((built_header or "Built:") + "\n" + "\n".join(str(line) for line in built))
    if left:
        parts.append("Left:\n" + "\n".join(str(line) for line in left))
    if waiting:
        if isinstance(waiting, str):
            waiting = [_prefixed(waiting, "Waiting")]
        lines = [str(line) for line in waiting if str(line).strip()]
        if lines:
            parts.append("\n".join(lines))
    if because:
        parts.append(str(because))
    if alternatives:
        lines = [str(line) for line in alternatives if str(line).strip()]
        if lines:
            parts.append("\n".join(lines))
    for note in notes or []:
        if note:
            parts.append(str(note))
    if uncommitted:
        parts.append(_prefixed(uncommitted, "Uncommitted"))
    return "\n\n".join(parts)


# ---------- The ready-check reply ----------

def counts_table(counts: dict) -> str:
    slug = counts.get("slug") or ""
    head = "| Slice | " + " | ".join(name for name, _ in COUNT_COLUMNS) + " |"
    rule = "| --- |" + " --- |" * len(COUNT_COLUMNS)
    row = f"| {slug} | " + " | ".join(str(counts.get(key, 0)) for _, key in COUNT_COLUMNS) + " |"
    return "\n".join((head, rule, row))


def ready_reply(
    slug: str,
    result: str,
    counts: dict | None,
    ending: str,
    sources: list[str] | None = None,
    build_map: str | None = None,
    work_item: bool = False,
    next_line: str | None = None,
    stop: bool = False,
) -> str:
    """The whole brief ready-check reply. Print it verbatim (1.156.0)."""
    if stop:
        return ending or ""
    parts = [f"Tasks ready to build — {slug}"]
    if counts:
        parts.append(counts_table(counts))
    parts.append(f"Result: {result}")
    if ending:
        parts.append(ending)
    if next_line:
        parts.append(next_line)
    tail = []
    if work_item:
        tail.append("Task states in Azure Boards are not read here; /crav1-ado-sync brings them back.")
    if sources:
        tail.append(f"Source: docs/specs/{slug}/" + ", ".join(sources))
    if build_map:
        tail.append(f"Build map: {build_map}")
        # The zoomable page, label on its own line, command alone (1.164.0).
        # export-map stays inside build-map.md.
        tail.append("Zoom the map in your browser:")
        tail.append(f"`/crav1-tasks-ready-to-build {slug} open-map`")
    if tail:
        parts.append("\n".join(tail))
    return "\n\n".join(parts)


def not_ready_next(slug: str, counts: dict | None, question_first: bool) -> str | None:
    """The one Next line a not-ready ready check prints (references next-*)."""
    counts = counts or {}
    left = sum(int(counts.get(key, 0) or 0) for key in ("ready", "waiting", "waits_in_order", "blocked"))
    if left == 0 and not counts.get("needs_verify"):
        return "Next: nothing needed now."
    if left == 0:
        return (
            f"Next: /crav1-verify-build-against-spec {slug}, "
            "because the built tasks are not verified yet."
        )
    if question_first and not counts.get("ready"):
        return (
            f"Next: /crav1-resolve-open-questions {slug}, "
            "because that question blocks the first task."
        )
    return None


def main(argv=None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="Compose the shared walk ending")
    parser.add_argument("--json", required=True, help="state file with compose() keys")
    args = parser.parse_args(argv)
    state = json.loads(Path(args.json).read_text(encoding="utf-8"))
    keys = compose.__code__.co_varnames[: compose.__code__.co_argcount]
    print(compose(**{key: state[key] for key in keys if key in state}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
