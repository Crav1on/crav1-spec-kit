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

It also owns the box colour on the build map (box_state) and the
finalize-commit decision for a task recorded merged but not ticked
(commit_check), so the map, the ready check and finalize-commit agree.

Usage:
  task_state.py state --ticked yes-no --merged yes-no --verify "<status>" [--built yes-no]
  task_state.py clean-name "<name>"
  task_state.py commit-check --root <spec-folder>
  task_state.py walk-start --root <spec-folder> --task T8 [--user "<name>"]

walk_start (1.186.0) says whether `/crav1-build-walk <slug> <T#>` can start a
task now. The ready check offers a task only when it can, and the walk
starts from the same answer.
"""
from __future__ import annotations

import argparse
import json
import importlib.util
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

DONE = "done"
TICK_PENDING = "tick-pending"
MERGE_WAIT = "merge-wait"
OPEN = "open"

PASSED = ("implemented, verified", "implemented, verified, tick pending", "implemented, verified on branch")
# 1.182.0: `Implemented, verified on branch` and `Implemented, verified, tick
# pending` are one state. Only TICK_PENDING_STATUS is written; the old
# wording is still read, and rewritten once when its file is touched.
TICK_PENDING_STATUS = "Implemented, verified, tick pending"
OLD_TICK_PENDING_STATUS = "Implemented, verified on branch"
WAITING_STATUSES = ("implemented, verified on branch", "implemented, verified, tick pending")

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
    if built or merge_wait or str(verify or "").strip().lower() in WAITING_STATUSES:
        return {"state": MERGE_WAIT, "counts_done": False, "offer_tick": False, "stop": False}
    return {"state": OPEN, "counts_done": False, "offer_tick": False, "stop": False}


def is_waiting_status(status: str | None) -> bool:
    """Either wording of verified and waiting for the tick (1.182.0)."""
    return str(status or "").strip().lower() in WAITING_STATUSES


def new_status(status: str | None) -> str:
    """The one written wording: the old on-branch wording becomes tick pending (1.182.0)."""
    text = str(status or "").strip()
    return TICK_PENDING_STATUS if text.lower() == OLD_TICK_PENDING_STATUS.lower() else text


_OLD_STATUS_CELL = re.compile(r"^(\|\s*T\d+\s*\|[^|\n]*\|\s*)Implemented, verified on branch(\s*\|)", re.I | re.M)
_OLD_COUNT_ROW = re.compile(r"^\|\s*Implemented, verified on branch\s*\|\s*\d+\s*\|[^\n]*\n?", re.I | re.M)


def rewrite_old_status(text: str) -> str:
    """verify.md text with the old on-branch wording gone (1.182.0).

    Each task row's old status becomes the one wording, and the old TL;DR
    count row is dropped; the caller recounts.
    """
    out = _OLD_STATUS_CELL.sub(lambda m: m.group(1) + TICK_PENDING_STATUS + m.group(2), text or "")
    if re.search(r"^\|\s*Implemented, verified, tick pending\s*\|\s*\d+\s*\|", out, re.I | re.M):
        return _OLD_COUNT_ROW.sub("", out)
    # No tick pending count row yet: the old one becomes it.
    return re.sub(r"^(\|\s*)Implemented, verified on branch(\s*\|\s*\d+\s*\|)",
                  lambda m: m.group(1) + TICK_PENDING_STATUS + m.group(2), out, flags=re.I | re.M)


# A build-progress step that names tasks: `- Step: build T47` (1.182.0).
_BUILD_STEP = re.compile(r"^-\s*Step:\s*build\b(?P<rest>[^\n]*)$(?P<body>(?:\n[ \t]+.*)*)", re.M | re.I)
_RESULT_TASK = re.compile(r"^(?:done|merged)\b\s*\(\s*T(\d+)\s*:", re.I)
_BUILT_ROW = re.compile(r"^-\s*Built:\s*([^,\n]*)", re.M | re.I)


def progress_tasks(text: str | None) -> dict:
    """The tasks a build-progress file is about (1.182.0).

    {"listed": [T# on the header's Tasks: line], "built": [T# with a done
    `Step: build T#`, a done plain `Step: build` whose result starts
    `done (T#:` (older kits, 1.184.0), or a `- Built: T#` row], "all": listed, then any task a
    build step names}. A build step naming a task counts for that task
    whatever the header says, so older files that list only the first task
    still count the second one as built, waiting for the merge.
    """
    text = text or ""
    head = text.split("\n- Step:", 1)[0]
    line = re.search(r"^Tasks:\s*(.*)$", head, re.M)
    listed = [f"T{int(n)}" for n in re.findall(r"\bT(\d+)\b", line.group(1))] if line else []
    named: list[str] = []
    built: list[str] = []
    for match in _BUILD_STEP.finditer(text):
        ids = [f"T{int(n)}" for n in re.findall(r"\bT(\d+)\b", match.group("rest"), re.I)]
        result = re.search(r"^[ \t]+Result:\s*(.*)$", match.group("body") or "", re.M)
        done = bool(result and re.match(r"(done|merged)\b", result.group(1).strip(), re.I))
        if not ids and result:
            # 1.184.0: older kits wrote a plain `- Step: build` with the task
            # only in the result, `Result: done (T47: <repo> af772f5 on ...)`.
            lead = _RESULT_TASK.match(result.group(1).strip())
            if lead:
                ids = [f"T{int(lead.group(1))}"]
        for task in ids:
            if task not in named:
                named.append(task)
            if done and task not in built:
                built.append(task)
    for match in _BUILT_ROW.finditer(text):
        for n in re.findall(r"\bT(\d+)\b", match.group(1)):
            task = f"T{int(n)}"
            if task not in built:
                built.append(task)
    everything = list(listed)
    for task in named + built:
        if task not in everything:
            everything.append(task)
    return {"listed": listed, "built": built, "all": everything}


def deadlock_text(task: str, dep: str, pr, branch: str | None = None) -> str:
    """The one wording for a merge deadlock (M4), map and ready check alike."""
    where = f" is on {branch} and" if branch else ""
    return f"Merge deadlock: {task}{where} waits on {dep}, which ticks only when PR {pr} merges."


# The box colour a task state gives, worst first (1.180.0).
STATE_COLOUR = {DONE: "done", TICK_PENDING: "done", MERGE_WAIT: "waiting", OPEN: "todo"}
COLOUR_RANK = ("blocked", "waiting", "todo", "done")


def row_state(row: dict) -> str:
    """A ready-check row's state, by the same rules as task_state()."""
    bucket = row.get("bucket")
    if bucket in ("done", "needs-verify"):
        # Needs verify is ticked (or claimed done) without a verify row.
        return DONE
    waits = bool(row.get("merge_wait") or row.get("claim_built") or row.get("verified_on_branch"))
    return task_state(False, built=waits)["state"]


def box_state(branch: dict) -> str:
    """One of done, waiting, blocked, todo: a build-map box colour.

    Blocked only for a truly blocked branch: in a loop, the Blocked section,
    a merge deadlock, or a walk whose last result failed or was reopened.
    Waiting for a question hold, a hold on another branch, or a task built
    and waiting for its pull request. Done when every task's state is done.
    Else todo (ready, waits in order, in progress).
    """
    status = branch.get("status")
    if (branch.get("loop") or branch.get("deadlock") or status == "blocked"
            or branch.get("section") == "blocked" or branch.get("failed")):
        return "blocked"
    states = [task.get("state") for task in branch.get("tasks") or [] if task.get("state")]
    if status == "done" or (states and all(STATE_COLOUR[state] == "done" for state in states)):
        return "done"
    if status == "waiting on a question":
        return "waiting"
    if status == "held":
        return "todo" if (branch.get("held_text") or "") == "in progress" else "waiting"
    open_colours = {STATE_COLOUR[state] for state in states if STATE_COLOUR[state] != "done"}
    return "waiting" if open_colours == {"waiting"} else "todo"


def _build_map():
    path = Path(__file__).resolve().parent / "build_map.py"
    spec = importlib.util.spec_from_file_location("build_map_ts", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_VERIFY_ROW = re.compile(r"^\|\s*T(\d+)\s*\|[^|]*\|\s*([^|]+?)\s*\|", re.M)


def slice_states(root) -> dict:
    """{"T5": task_state(...)} for every task in a spec folder.

    Ticks from tasks.md, merges and builds from build-progress (the same
    progress_state the build map reads), verify status from verify.md.
    """
    root = Path(root)
    tasks = (root / "tasks.md").read_text(encoding="utf-8") if (root / "tasks.md").is_file() else ""
    verify = (root / "verify.md").read_text(encoding="utf-8") if (root / "verify.md").is_file() else ""
    statuses = {f"T{int(n)}": status for n, status in _VERIFY_ROW.findall(verify)}
    bm = _build_map()
    walks = bm.progress_state(root) if (root / "build-progress").is_dir() else {}
    # The same per-task decision the build map makes (apply_task_states).
    parsed = bm.parse_tasks(tasks)
    states = bm.apply_task_states(parsed, walks)
    out = {}
    for task, state in states.items():
        merged = state == TICK_PENDING
        out[task] = task_state(state == DONE, merged, statuses.get(task), state == MERGE_WAIT)
    return out


def commit_check(root) -> dict:
    """Finalize-commit's merged-but-not-ticked decision (M3).

    A task recorded merged on the host but `[ ]` in tasks.md is tick
    pending. It is never a reason to recommend `stop`: name it, recommend
    `commit`, and put the next step in Run next (verify when verify.md does
    not pass it yet, else the tick).
    """
    states = slice_states(root)
    pending = [task for task, state in states.items() if state["state"] == TICK_PENDING]
    slug = Path(root).name
    if not pending:
        return {"ok": True, "tick_pending": [], "recommend": None, "stop": False, "run_next": None, "line": None}
    verify_first = [task for task in pending if states[task].get("verify_first")]
    joined = ", ".join(pending)
    line = f"{joined} {'is' if len(pending) == 1 else 'are'} recorded merged but not ticked in tasks.md; that is tick pending, not a reason to stop."
    if verify_first:
        run_next = f"Verify {', '.join(verify_first)}, recorded merged on the host:\n`/crav1-verify-build-against-spec {slug}`"
    else:
        run_next = (f"Tick {joined} in tasks.md, recorded merged and verified:\n"
                    f"`verify_rows.py tick --file docs/specs/{slug}/verify.md --task {pending[0]} --merged yes --yes`")
    return {"ok": True, "tick_pending": pending, "recommend": "commit", "stop": False, "run_next": run_next, "line": line}


# A task that takes the base into its branch (1.186.0). The mark is
# `(take-in: develop)`. Without the mark, a task on another person's branch
# whose text says it takes in a base branch is a take-in task too, so
# nobody adds the mark by hand.
TAKE_IN_MARK = re.compile(r"\(take-in:\s*`?([A-Za-z0-9._/-]+?)`?\s*\)", re.I)
TAKE_IN_TEXT = re.compile(
    r"\btak(?:e|es|ing)\s+in\s+`?(develop|development|main|master|dev|trunk|release/[A-Za-z0-9._-]+)`?(?![A-Za-z0-9_/-])",
    re.I,
)
_CLAIM = re.compile(
    r"^\s*In progress:\s*(?P<branch>\S+),\s*(?P<tasks>T?\d+(?:\s*,\s*T?\d+)*),\s*(?P<user>.+?),\s*since\s+(?P<since>\S+)\s*$",
    re.I | re.M,
)
_PR_IN = re.compile(r"\b(?:PR|pull request)\s+#?(\d+)", re.I)


def take_in_base(text: str | None, owner: str | None = None) -> str | None:
    """`develop` for a take-in task, else None (1.186.0).

    The `(take-in: <base>)` mark always counts. Without it, a task whose text
    says `takes in develop` (or main, master, ...) counts only on a branch
    another person owns, where the walk would otherwise never merge the base.
    """
    text = str(text or "")
    mark = TAKE_IN_MARK.search(text)
    if mark:
        return mark.group(1)
    if owner == "other":
        found = TAKE_IN_TEXT.search(text)
        if found:
            return found.group(1)
    return None


def branch_file(branch: str) -> str:
    """feat/orders-note -> feat--orders-note (the build-progress file name)."""
    return (branch or "").replace("/", "--")


def _progress_header(root: Path, branch: str | None) -> dict:
    """Owner, PR, author and listed tasks from a branch's build-progress file."""
    if not branch:
        return {"exists": False, "owner": None, "pr": None, "author": None, "listed": []}
    path = Path(root) / "build-progress" / f"{branch_file(branch)}.md"
    if not path.is_file():
        return {"exists": False, "owner": None, "pr": None, "author": None, "listed": []}
    text = path.read_text(encoding="utf-8", errors="replace")
    head = text.split("\n- Step:", 1)[0]

    def field(label):
        match = re.search(rf"^{label}:\s*(.*)$", head, re.M)
        return match.group(1).strip() if match else None

    prs = _PR_IN.findall(text)
    return {
        "exists": True,
        "owner": (field("Owner") or "self").lower(),
        "pr": int(prs[-1]) if prs else None,
        "author": clean_name(field("PR author")) or None,
        "listed": progress_tasks(text)["listed"],
    }


def read_claims(root) -> list[dict]:
    """`In progress:` lines of claims.md as {branch, tasks, user, since}."""
    path = Path(root) / "claims.md"
    if not path.is_file():
        return []
    out = []
    for match in _CLAIM.finditer(path.read_text(encoding="utf-8", errors="replace")):
        tasks = [f"T{int(n)}" for n in re.findall(r"\d+", match.group("tasks"))]
        out.append({"branch": match.group("branch"), "tasks": tasks,
                    "user": clean_name(match.group("user")), "since": match.group("since")[:10]})
    return out


def walk_starts(root, user: str | None = None) -> dict:
    """{"T8": walk_start(...)} for every task in a spec folder, read once (1.186.0)."""
    root = Path(root)
    tasks_md = root / "tasks.md"
    text = tasks_md.read_text(encoding="utf-8") if tasks_md.is_file() else ""
    parsed = _build_map().parse_tasks(text)
    states = slice_states(root)
    claims = read_claims(root)
    return {f"T{int(task['id'])}": _walk_start(root, task, states, claims, user) for task in parsed}


def _open_after_pr(root, task: dict):
    """The first pull request this task waits on that the host has not merged (1.201.1)."""
    import os
    numbers = []
    for number in task.get("after_prs") or ():
        try:
            value = int(number)
        except (TypeError, ValueError):
            continue
        if value not in numbers:
            numbers.append(value)
    if not numbers:
        return None
    if os.environ.get("CRAV1_NO_HOST_LOOKUP"):
        return numbers[0]
    try:
        merged = _walk_progress()._host_merged
    except Exception:  # noqa: BLE001 - a host miss leaves the task held
        return numbers[0]
    for number in numbers:
        if not merged(root, number):
            return number
    return None


_WALK_PROGRESS = None


def _walk_progress():
    global _WALK_PROGRESS
    if _WALK_PROGRESS is None:
        path = Path(__file__).resolve().parents[1].parent / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
        spec = importlib.util.spec_from_file_location("task_state_walk_progress", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _WALK_PROGRESS = module
    return _WALK_PROGRESS


def walk_start(root, task: str, user: str | None = None) -> dict:
    """Can `/crav1-build-walk <slug> <task>` start this task now? (1.186.0)

    The one answer for the ready check and the walk. `phase` is:
    - `build`: startable. An open task with every dependency done, not
      claimed by someone else. A branch whose other tasks wait for their
      merge does not stop it: wait-merge is only for pushed tasks.
    - `wait-merge`: built and pushed, its tick waits for the merge.
    - `done`: ticked, or recorded merged.
    - `held`: a dependency is not done yet.
    - `claimed`: someone else's `In progress:` line holds it.
    - `unknown`: not in tasks.md.
    """
    token = f"T{int(re.sub(r'[^0-9]', '', str(task)) or 0)}"
    starts = walk_starts(root, user)
    if token not in starts:
        return {"ok": True, "task": token, "startable": False, "phase": "unknown",
                "reason": f"{token} is not in tasks.md.", "branch": None, "owner": None, "pr": None,
                "take_in": None, "claim_needed": False, "header_needed": False}
    return starts[token]


def _walk_start(root: Path, task: dict, states: dict, claims: list[dict], user: str | None) -> dict:
    token = f"T{int(task['id'])}"
    branch = task.get("branch") or task.get("map")
    header = _progress_header(root, branch)
    owner = header["owner"] or "self"
    out = {
        "ok": True,
        "task": token,
        "title": task.get("title") or "",
        "branch": branch,
        "owner": owner,
        "pr": header["pr"],
        "author": header["author"],
        "take_in": take_in_base(task.get("rest") or task.get("title"), owner),
        "claim_needed": False,
        "header_needed": False,
    }
    state = (states.get(token) or {}).get("state", OPEN)
    if state in (DONE, TICK_PENDING):
        return {**out, "startable": False, "phase": "done", "reason": f"{token} is done."}
    if state == MERGE_WAIT:
        named = f"PR {header['pr']}" if header["pr"] else "its pull request"
        return {**out, "startable": False, "phase": "wait-merge",
                "reason": f"{token} is pushed to {named} and waits for its merge."}
    claim = next((item for item in claims if token in item["tasks"]), None)
    if claim and not (user and same_person(claim["user"], user)):
        # Someone else's claim, or no user to compare with: held, as the
        # ready check holds it.
        return {**out, "startable": False, "phase": "claimed", "claimed_by": claim["user"],
                "reason": f"{token} is in progress by {claim['user']} since {claim['since']}."}
    open_deps = []
    for dep in task.get("deps") or []:
        dep_state = (states.get(f"T{int(dep)}") or {}).get("state", OPEN)
        if dep_state not in (DONE, TICK_PENDING):
            open_deps.append(f"T{int(dep)}")
    if open_deps:
        return {**out, "startable": False, "phase": "held", "waits_on": open_deps,
                "reason": f"{token} waits on {', '.join(open_deps)}."}
    # 1.201.1: `(after: PR N)` or `after PR N merges` holds the walk until the
    # host says that pull request merged. The same phrase as the ready check.
    held_pr = _open_after_pr(root, task)
    if held_pr:
        return {**out, "startable": False, "phase": "held", "pr": held_pr,
                "reason": f"waits for PR {held_pr} to merge."}
    return {**out, "startable": True, "phase": "build", "reason": f"{token} can start on {branch or 'its branch'}.",
            "claim_needed": claim is None,
            "header_needed": bool(header["exists"]) and token not in header["listed"]}


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
    check = sub.add_parser("commit-check")
    check.add_argument("--root", required=True)
    start = sub.add_parser("walk-start")
    start.add_argument("--root", required=True)
    start.add_argument("--task", required=True)
    start.add_argument("--user", default=None)
    args = parser.parse_args(argv)
    if args.cmd == "walk-start":
        print(json.dumps(walk_start(args.root, args.task, args.user), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "commit-check":
        print(json.dumps(commit_check(args.root), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "clean-name":
        print(json.dumps({"ok": True, "name": clean_name(args.name)}))
        return 0
    result = task_state(args.ticked == "yes", args.merged == "yes", args.verify, args.built == "yes")
    print(json.dumps({"ok": True, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
