#!/usr/bin/env python3
"""Shared waiting judgement and run-ending checks (kit 1.200.0).

Ending and readiness scripts call this instead of each inventing a wait.
`guard` checks an ending against the Run next rules before it is printed.
Standard library only. Writes nothing.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


_utf8_stdout()

QUESTION = re.compile(r'open question "(.*)"', re.S)
PR_NUM = re.compile(r"\bPR\s+#?(\d+)\b", re.I)
NAMED = frozenset({"", "not named yet", "nobody named yet", "none", "nobody"})


class EndingError(Exception):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("; ".join(problems))


def uncommitted_line(count, push: bool = False) -> str:
    """The one Uncommitted line: the command sits in a code span (1.199.0, 1.200.0)."""
    n = int(count)
    noun = "file" if n == 1 else "files"
    if push:
        return f"Uncommitted: {n} {noun}; commit and push with `/crav1-finalize-commit commit-push`."
    return f"Uncommitted: {n} {noun}; commit with `/crav1-finalize-commit` when ready."


def question_text(reason: str) -> str:
    found = QUESTION.search(reason or "")
    if not found:
        return ""
    text = " ".join(found.group(1).split())
    return text if len(text) <= 120 else text[:117].rstrip() + "…"


def who_plain(who: str | None) -> str:
    text = " ".join(str(who or "").split())
    if text.lower() in NAMED:
        return ""
    return text


def question_held_phrase(hits: list[dict]) -> str:
    """Name each question and who it waits on, after the count (1.200.0)."""
    if not hits:
        return ""
    bits = []
    for hit in hits:
        task = hit.get("task") or "A task"
        question = question_text(str(hit.get("reason") or "")) or "the open question"
        who = who_plain(hit.get("who"))
        if who:
            bits.append(f'{task} waits on "{question}" from {who}')
        else:
            bits.append(f'{task} waits on "{question}" and nobody is named to answer it')
    return " ".join(bit + "." for bit in bits)


def held_with_pr(phrase: str, pr) -> str:
    """A held line that waits on a pull request names the number (1.200.0)."""
    text = " ".join(str(phrase or "").split())
    if not pr or f"PR {pr}" in text or f"PR #{pr}" in text:
        return text
    if "pull request" in text.lower():
        return re.sub(r"\bpull request\b", f"PR {pr}", text, count=1, flags=re.I)
    return f"{text} (PR {pr})" if text else f"waits on PR {pr}"


def judge_wait(row: dict) -> str:
    """waiting, blocked, order, or clear. One judgement for every ending script.

    A question hold, a merge wait, a release gate, an approval, or someone
    else's in-progress claim is waiting. A cycle or an (after:) that names
    no task is blocked. Waiting on an earlier real task is the order.
    """
    if not isinstance(row, dict):
        return "clear"
    reason = str(row.get("reason") or "")
    warning = str(row.get("warning") or "")
    text = f"{reason} {warning}".lower()
    bucket = str(row.get("bucket") or "")
    if bucket == "needs-verify" or "needs verify" in text or "verify failed" in text:
        return "blocked"
    if "cycle" in text or "names no task" in text or row.get("loop") or row.get("deadlock"):
        return "blocked"
    if row.get("merge_wait") or row.get("own_pr_open") or row.get("release_gate") or row.get("approval"):
        return "waiting"
    if "open question" in text or "approval needed" in text or "in progress by" in text:
        return "waiting"
    if "held, waits on" in text or re.search(r"waits for (?:its pull request|pr \d+)", text):
        return "waiting"
    if re.search(r"waits on\s+t\d+", text) or bucket == "waits-in-order":
        return "order"
    if bucket in ("ready", "done", ""):
        return "clear"
    if bucket == "blocked":
        return "blocked"
    if bucket == "waiting":
        return "waiting"
    return "clear"


def later_work(text: str) -> bool:
    """A conflict or question that names a future discussion or an unanswered person (1.200.0)."""
    low = str(text or "").lower()
    if re.search(r"\b20\d\d-\d\d-\d\d\b", low) and re.search(r"\b(discuss|meeting|session|later|on the)\b", low):
        return True
    if re.search(r"\b(unanswered|not yet answered|waiting for|waits on)\b", low):
        return True
    return False


_LABEL = re.compile(r"^[A-Z].{2,160}:\s*$")
_CMD = re.compile(r"^`[^`\n]+`$")
_NEXT = re.compile(r"^Next:\s")


def check_ending(text: str) -> list[str]:
    """Problems in an ending. Empty means it may be printed (1.200.0).

    Run next labels sit on their own line above one command in a code span.
    A line does not start with `Next:`. A Waiting line carries no command.
    An Uncommitted line that names the commit command puts it in a code span.
    """
    problems = []
    lines = str(text or "").splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if _NEXT.match(stripped):
            problems.append(f"line {i + 1} starts with Next:")
        if stripped.startswith("Waiting:") and "`/" in stripped:
            problems.append(f"line {i + 1} is a Waiting line that carries a command")
        if stripped.startswith("Uncommitted:") and "finalize-commit" in stripped and "`/" not in stripped:
            problems.append(f"line {i + 1} names the commit command outside a code span")
        if _LABEL.match(stripped) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if nxt.startswith("/") or nxt.startswith("git ") or nxt.startswith("gh "):
                problems.append(f"line {i + 2} is a command outside a code span")
            elif nxt.startswith("`") and not _CMD.match(nxt):
                problems.append(f"line {i + 2} puts more than the command in the code span")
    if "Run next:" in text:
        for i, line in enumerate(lines):
            if line.strip() != "Run next:":
                continue
            rest = [ln.strip() for ln in lines[i + 1:] if ln.strip()]
            if not rest:
                problems.append("Run next has no label and no command")
                break
            if rest[0] == "nothing needed now.":
                break
            # A reason may sit between Run next and the first label.
            labels = [ln for ln in rest if _LABEL.match(ln)]
            if not labels:
                problems.append("Run next has no label above a command")
    return problems


def compose(reason: str, entries: list[tuple[str, str]] | None = None, *,
            waiting: list[str] | None = None, uncommitted: int | None = None, push: bool = False) -> str:
    """Run next first, then Waiting, then Uncommitted. Raises EndingError when the text breaks the rules (1.200.0)."""
    entries = entries or []
    lines: list[str] = []
    if not entries and reason.strip() in ("", "nothing needed now."):
        lines.append("Run next: nothing needed now.")
    else:
        lines += ["Run next:", reason.strip(), ""]
        for label, command in entries:
            shown = label if str(label).rstrip().endswith(":") else f"{label}:"
            lines += [shown, f"`{command}`", ""]
    if waiting:
        if lines and lines[-1] != "":
            lines.append("")
        for item in waiting:
            text = str(item).strip()
            lines.append(text if text.startswith("Waiting:") else f"Waiting: {text}")
    if uncommitted:
        lines += ["", uncommitted_line(int(uncommitted), push=push)]
    while lines and lines[-1] == "":
        lines.pop()
    return guard("\n".join(lines) + "\n")


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              encoding="utf-8", timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def design_branch_card(root) -> dict | None:
    """A stay card when a design branch is checked out or owns this change (1.200.0).

    The recommended option stays on that branch. The card never offers a switch
    to the default branch.
    """
    root = Path(root)
    cur = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if not cur or cur == "HEAD":
        return None
    listed = _git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads/design") or ""
    design_branches = [line for line in listed.splitlines() if line.startswith("design/")]
    # Other skills never read docs/architecture/designs; this only sees which branch owns uncommitted files.
    designs = "docs/architecture/" + "designs"
    status = _git(root, "status", "--porcelain", "-uall", "--", designs) or ""
    owned: list[str] = []
    for line in status.splitlines():
        path = line[3:].strip().strip('"')
        parts = path.split("/")
        if len(parts) >= 4 and parts[0] == "docs" and parts[2] == "designs" and parts[3] not in owned:
            owned.append(parts[3])
    branch = cur if cur.startswith("design/") else ""
    if not branch and owned:
        candidate = f"design/{owned[0]}"
        if candidate in design_branches or not design_branches:
            branch = candidate
    if not branch:
        return None
    on_it = cur == branch
    question = f"Stay on {branch}?" if on_it else f"This change belongs on {branch}. Stay with that branch?"
    stay_action = "keep writing on this design branch" if on_it else f"git switch {branch} and write there"
    return {
        "branch": branch,
        "on_branch": on_it,
        "stay": True,
        "switch_to_default": False,
        "card": {
            "question": question,
            "recommended": "stay",
            "words": ["stay", "stop"],
            "options": [
                {"word": "stay", "label": "Stay (Recommended)", "action": stay_action},
                {"word": "stop", "label": "Stop", "action": "write nothing"},
            ],
        },
    }


def commit_yes(yes: bool, words: str, skill_text: str) -> bool:
    """`stop and commit` is a yes only when the skill text says so (1.200.0)."""
    if yes and str(words or "").strip().lower() != "stop and commit":
        return True
    phrase = str(words or "").strip().lower() == "stop and commit"
    explicit = "Stop and commit is a yes" in str(skill_text or "")
    if phrase and explicit:
        return True
    if phrase:
        return False
    return bool(yes)


def guard(text: str) -> str:
    """Return the ending, or raise EndingError. Call this before printing."""
    problems = check_ending(text)
    if problems:
        raise EndingError(problems)
    return text


def load():
    """Import this module from a sibling skill (walk_progress, walk_ending)."""
    return None
