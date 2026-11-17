#!/usr/bin/env python3
"""One owner for a task's state (1.180.0).

The ready check (walk_progress.py readiness), build_map.py, verify's tick
offer and finalize-commit all read a task's state from here, so the same
facts give the same answer everywhere:

- done:          ticked in tasks.md, or its merge is recorded on the host.
- tick-pending:  recorded merged but still `[ ]` in tasks.md. That is not a
                 disagreement worth stopping a commit; Run next offers the tick.
- merge-wait:    built or verified on its branch, waits for its PR to merge.
- open:          anything else.

It also owns the owner-name clean-up used when names are written or read:
a leading word like `Admin` and a trailing `(...)` tag are dropped, and two
spellings of one person match.

Usage:
  task_state.py state --ticked yes-no --merged yes-no --verify "<status>" [--built yes-no]
  task_state.py clean-name "<name>"
"""
from __future__ import annotations

import argparse
import json
import re
import sys

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

DONE = "done"
TICK_PENDING = "tick-pending"
MERGE_WAIT = "merge-wait"
OPEN = "open"

PASSED = ("implemented, verified", "implemented, verified, tick pending", "implemented, verified on branch")

# Words a host puts before a display name. Only a leading word is dropped.
NAME_PREFIXES = ("admin", "administrator", "ext", "external", "guest", "contractor")
_TRAILING_TAG = re.compile(r"\s*[\(\[][^()\[\]]*[\)\]]\s*$")
_WAITING = re.compile(r"\bbuilt by\b.*\bwaits? for (?:pr|its pull request)\b|\bwaits? for pr \d+ to merge\b", re.I)


def clean_name(name: str | None) -> str:
    """`Admin Person A` -> `Person A`; `Person B (Tag)` -> `Person B`."""
    text = " ".join(str(name or "").split())
    previous = None
    while text and text != previous:
        previous = text
        text = _TRAILING_TAG.sub("", text).strip()
        parts = text.split(" ", 1)
        if len(parts) == 2 and parts[0].lower().rstrip(":") in NAME_PREFIXES:
            text = parts[1].strip()
    return text


def name_key(name: str | None) -> str:
    """The match key: cleaned, case-folded, single spaces."""
    return clean_name(name).casefold()


def same_person(left: str | None, right: str | None) -> bool:
    return bool(name_key(left)) and name_key(left) == name_key(right)


def unique_names(names) -> list[str]:
    """Clean names, one per person, first spelling kept."""
    seen = set()
    out = []
    for name in names or ():
        cleaned = clean_name(name)
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            out.append(cleaned)
    return out


def verify_passed(status: str | None) -> bool:
    return str(status or "").strip().lower() in PASSED


def is_waiting_reason(text: str | None) -> bool:
    """`built by <name>, waits for PR <n> to merge` is waiting, not a blocker."""
    return bool(_WAITING.search(str(text or "")))


def task_state(ticked: bool, merged: bool = False, verify: str | None = None, built: bool = False, merge_wait: bool = False) -> dict:
    """The one answer for a task's state, and what Run next should offer."""
    if ticked:
        return {"state": DONE, "counts_done": True, "offer_tick": False, "stop": False}
    if merged:
        # Recorded merged on the host but `[ ]`: done for the ready check,
        # tick offered in Run next, never a reason to stop a commit (M3).
        return {"state": TICK_PENDING, "counts_done": True, "offer_tick": True, "stop": False,
                "verify_first": not verify_passed(verify)}
    if built or merge_wait or str(verify or "").strip().lower() == "implemented, verified on branch":
        return {"state": MERGE_WAIT, "counts_done": False, "offer_tick": False, "stop": False}
    return {"state": OPEN, "counts_done": False, "offer_tick": False, "stop": False}


def deadlock_text(task: str, dep: str, pr, branch: str | None = None) -> str:
    """The one wording for a merge deadlock (M4), map and ready check alike."""
    where = f" is on {branch} and" if branch else ""
    return f"Merge deadlock: {task}{where} waits on {dep}, which ticks only when PR {pr} merges."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    state = sub.add_parser("state")
    state.add_argument("--ticked", choices=("yes", "no"), default="no")
    state.add_argument("--merged", choices=("yes", "no"), default="no")
    state.add_argument("--built", choices=("yes", "no"), default="no")
    state.add_argument("--verify", default="")
    name = sub.add_parser("clean-name")
    name.add_argument("name")
    args = parser.parse_args(argv)
    if args.cmd == "clean-name":
        print(json.dumps({"ok": True, "name": clean_name(args.name)}))
        return 0
    result = task_state(args.ticked == "yes", args.merged == "yes", args.verify, args.built == "yes")
    print(json.dumps({"ok": True, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
