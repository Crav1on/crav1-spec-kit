#!/usr/bin/env python3
"""Progress and next step for /crav1-build-walk (kit 1.142.0).

One progress file per work branch. The spec, plan, and tasks stay the source
of truth. This script records position, the normalized hashes a step covered,
the merge list, and the single Next line for the current state. It does not
push, open a pull request, merge, or run a live change. Those wait for a yes
in the walk. It never rebases.

A hash is of normalized text, the same rule as walk-progress.md: line endings
do not count, and a checkbox, a (PR n) or (done) note, and a (live yes) note
do not count. The line is `Content stamp: normalized`.

Usage (JSON on stdout):
  build_walk.py next --json <file>
  build_walk.py grouping --json <file>
  build_walk.py owner --user <name> [--pr-author <name>] [--commit-author <name>]...
  build_walk.py comment --branch <name> --pr <n> --summary <text>
  build_walk.py stack --json <file>
  build_walk.py offer --root <spec-folder> --task <T#> [--repo <git dir>]
  build_walk.py live --json <file>
  build_walk.py stamp --tasks <file>
  build_walk.py record --root <spec-folder> --branch <name> --step <id> --yes
  build_walk.py resolve-stamps --file <build-progress.md> [--yes]

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

sys.dont_write_bytecode = True

WALK = "build-walk"
DEFAULT_BASE = "develop"
STAMP_LABELS = (
    "Tasks version",
    "Spec version",
    "Plan version",
    "Verify version",
    "Content stamp",
)
RUNS_LIVE = re.compile(r"\(Runs live\)")
LIVE_YES = re.compile(r"\(live yes:\s*([^,]+),\s*(\d{4}-\d{2}-\d{2})\)")
HASH_LINE = re.compile(
    r"^(?:  )?(Tasks version|Spec version|Plan version|Verify version): ([0-9a-f]{12}|missing)$"
    r"|^(?:  )?Content stamp: normalized$"
)

# While one branch is in progress the walk prints one Next. These are the
# step-skill lines that must not be printed beside it.
SUPPRESSED = {
    "confirm-owner": ["/crav1-open-pr", "/crav1-merge-pr"],
    "approval": ["/crav1-build-tasks", "/crav1-open-pr"],
    "live-dry": ["/crav1-open-pr", "/crav1-merge-pr"],
    "live-yes": ["/crav1-open-pr", "/crav1-merge-pr"],
    "permission-refused": ["/crav1-open-pr", "/crav1-merge-pr"],
    "build": ["/crav1-open-pr"],
    "verify": ["/crav1-open-pr", "/crav1-fix-build-gaps"],
    "commit": ["/crav1-open-pr"],
    "open-pr": ["/crav1-review-pr"],
    "merge-base": ["/crav1-open-pr", "/crav1-review-pr"],
    "merge-pr": ["/crav1-finalize-commit", "/crav1-review-pr"],
    "tick": ["/crav1-open-pr"],
    "comment": ["/crav1-open-pr", "/crav1-merge-pr"],
    "wait-merge": ["/crav1-open-pr", "/crav1-merge-pr"],
    "next-task": ["/crav1-open-pr"],
    "grouping": [],
}


def _emit(payload: dict, status: int = 0) -> int:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return status


def _fail(code: str, message: str, status: int = 2) -> int:
    return _emit({"ok": False, "error": code, "message": message}, status)


def _load(folder: str, filename: str):
    import importlib.util

    path = Path(__file__).resolve().parents[2] / folder / "scripts" / filename
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def walk_mod():
    return _load("crav1-tighten-and-plan-ready-to-build", "walk_progress.py")


def map_mod():
    return _load("crav1-tasks-ready-to-build", "build_map.py")


def ending_mod():
    """The shared walk ending (1.156.0)."""
    return _load("crav1-tasks-ready-to-build", "walk_ending.py")


def approval_mod():
    return _load("crav1-record-approval", "approval_needed.py")


def permission_mod():
    return _load("crav1-build-tasks", "permission_block.py")


def same_person(left: str | None, right: str | None) -> bool:
    return (left or "").strip().casefold() == (right or "").strip().casefold()


def file_slug(branch: str) -> str:
    """feat/orders-note -> feat--orders-note. The file stores the real name."""
    safe = (branch or "").replace("/", "--")
    if not re.fullmatch(r"[A-Za-z0-9._+-]+", safe):
        raise ValueError(f"branch name cannot be a file: {branch}")
    return safe


def progress_path(root: Path, branch: str) -> Path:
    return root / "build-progress" / f"{file_slug(branch)}.md"


def tasks_hash(text: str) -> str:
    """Normalized hash. A live-yes note is progress, like a checkbox or (PR n)."""
    wp = walk_mod()
    norm = wp.normalize_text("tasks", text or "")
    norm = LIVE_YES.sub("", norm)
    norm = re.sub(r"[ \t]{2,}", " ", norm)
    return wp.version_text(norm)


def text_hash(kind: str, text: str) -> str:
    wp = walk_mod()
    if kind == "tasks":
        return tasks_hash(text)
    return wp.version_text(wp.normalize_text(kind, text or ""))


def progress_only(before: str, after: str) -> bool:
    return tasks_hash(before) == tasks_hash(after)


def detect_other_owner(current_user: str | None, pr_author: str | None = None, commit_authors: list | None = None) -> dict:
    """True when the pull request or a commit on the branch is someone else.

    The walk confirms before it switches. It does not guess when the current
    user is unnamed.
    """
    if not (current_user or "").strip():
        return {"other": False, "known": False, "why": "the current user is not named", "who": []}
    who = []
    reasons = []
    if (pr_author or "").strip() and not same_person(pr_author, current_user):
        who.append(pr_author.strip())
        reasons.append(f"pull request author is {pr_author.strip()}")
    for author in commit_authors or []:
        if (author or "").strip() and not same_person(author, current_user) and author.strip() not in who:
            who.append(author.strip())
            reasons.append(f"commit author is {author.strip()}")
    return {
        "other": bool(reasons),
        "known": True,
        "why": "; ".join(reasons),
        "who": who,
    }


def allowed_actions(owner: str | None, description_asked: bool = False) -> dict:
    """Other-owner mode never opens, never merges the base, and never merges the PR.

    A pull request description is edited only when this run asked for that.
    """
    other = owner == "other"
    return {
        "open_pr": not other,
        "merge_base": not other,
        "merge_pr": not other,
        "complete_pr": not other,
        "comment_per_push": other,
        "edit_description": bool(other and description_asked),
        "tick_waits_for_merge": other,
    }


def may_tick(owner: str | None, pr_merged: bool) -> bool:
    if owner == "other":
        return bool(pr_merged)
    return True


def push_comment(branch: str, pr: int | str, summary: str) -> dict:
    """One comment for one push. It does not edit the pull request description."""
    body = f"Pushed `{branch}`.\n\n{(summary or '').strip()}\n"
    return {
        "kind": "comment",
        "pr": pr,
        "branch": branch,
        "body": body,
        "edits_description": False,
    }


def refuse_unusable(name: str | None, fate: str | None) -> str | None:
    """A merged or deleted branch is not offered. Reuses the 1.140.0 fates."""
    if fate in ("merged", "deleted"):
        return None
    return name


def offer_for(slug: str, spec: str, plan: str, tasks: str, task_id, repo=None, work_item: str = "") -> dict | None:
    """The branch to offer. Never a merged or deleted name."""
    bm = map_mod()
    offer = bm.recommendation(slug, spec, plan, tasks, task_id, work_item, repo=repo)
    if not offer:
        return None
    offer = dict(offer)
    fate = bm.branch_fate(offer["name"], spec, tasks, repo, offer.get("base"))
    offer["fate"] = fate
    offer["refused"] = fate in ("merged", "deleted")
    if offer["refused"]:
        offer["refused_name"] = offer["name"]
        offer["name"] = None
    return offer


class InputError(Exception):
    def __init__(self, code: str, line: str) -> None:
        self.code = code
        self.line = line
        super().__init__(line)


def _task_number(value) -> int:
    """T27 and 27 are the same id. Anything else is not a task id."""
    text = str(value).strip()
    match = re.fullmatch(r"T?(\d+)", text, re.I)
    if not match:
        raise InputError("tasks", f"task id is not a T# or a number: {value}")
    return int(match.group(1))


def _task_token(value) -> str:
    return f"T{_task_number(value)}"


def _task_label(task: dict) -> str:
    title = (task.get("title") or "").strip()
    title = RUNS_LIVE.sub("", title)
    title = LIVE_YES.sub("", title)
    title = re.sub(r"\s{2,}", " ", title).strip(" .")
    return f"{_task_token(task.get('id'))} {title}".strip()


def normalize_task(item) -> dict:
    """A task is a T# string, a number, or an object with id and optional title."""
    if isinstance(item, str):
        match = re.fullmatch(r"(T?\d+)(?:\s+(.*))?", item.strip(), re.I)
        if not match:
            raise InputError("tasks", f"task is not a T# or an object: {item}")
        return {"id": _task_token(match.group(1)), "title": (match.group(2) or "").strip()}
    if isinstance(item, int) and not isinstance(item, bool):
        return {"id": _task_token(item), "title": ""}
    if isinstance(item, dict):
        if "id" not in item:
            raise InputError("tasks", "each task object needs an id")
        task = dict(item)
        task["id"] = _task_token(item["id"])
        task["title"] = str(task.get("title") or "").strip()
        return task
    raise InputError("tasks", "each task must be a T# string or an object with id and title")


def normalize_tasks(tasks) -> list:
    if tasks is None:
        return []
    if isinstance(tasks, str) or not isinstance(tasks, list):
        raise InputError("tasks", "tasks must be a list of T# strings or {id, title} objects")
    return [normalize_task(item) for item in tasks]


def normalize_branches(branches, code: str) -> list:
    if branches is None:
        return []
    if not isinstance(branches, list):
        raise InputError(code, f"{code} must be a list of branch objects")
    out = []
    for branch in branches:
        if not isinstance(branch, dict):
            raise InputError(code, f"each {code} entry must be an object")
        row = dict(branch)
        row["tasks"] = normalize_tasks(row.get("tasks"))
        if "open_tasks" in row:
            row["open_tasks"] = normalize_tasks(row.get("open_tasks"))
        out.append(row)
    return out


def cut_from_for(task_branch: str | None, dep_branches: list, merged: set, default_base: str = DEFAULT_BASE) -> str:
    """Cut from the unmerged branch this task needs, not from the default base."""
    needed = []
    for branch in dep_branches:
        if not branch or branch == task_branch or branch in merged:
            continue
        if branch not in needed:
            needed.append(branch)
    if not needed:
        return default_base
    return needed[-1]


def ordered_merges(cuts: dict, default_base: str = DEFAULT_BASE) -> list[dict]:
    """Child merges back into the branch it was cut from, before that parent moves on.

    `cuts` maps a branch to the branch it was cut from. The default base is
    the end of the list, not a child.
    """
    children: dict[str, list] = {}
    nodes = set()
    for branch, parent in cuts.items():
        if not branch:
            continue
        nodes.add(branch)
        parent = parent or default_base
        if parent != default_base:
            nodes.add(parent)
            children.setdefault(parent, [])
            if branch not in children[parent]:
                children[parent].append(branch)
    order = []
    seen = set()

    def walk(node: str) -> None:
        if node in seen or node == default_base:
            return
        seen.add(node)
        for child in sorted(children.get(node, [])):
            walk(child)
        order.append({"branch": node, "into": cuts.get(node, default_base)})

    roots = sorted(node for node in nodes if cuts.get(node, default_base) == default_base or cuts.get(node) not in nodes)
    for root in roots:
        walk(root)
    for node in sorted(nodes):
        walk(node)
    return order


def stack_from_tasks(tasks: list, merged: set | None = None, default_base: str = DEFAULT_BASE) -> dict:
    """`tasks` items have id, title, branch, deps (ids), and optional base.

    A dependency whose branch is not merged supplies the cut-from branch.
    """
    merged = set(merged or [])
    by_id = {_task_number(task["id"]): task for task in tasks}
    cuts = {}
    rows = []
    for task in tasks:
        branch = task.get("branch")
        if not branch:
            continue
        deps = []
        for dep in task.get("deps") or []:
            other = by_id.get(_task_number(dep))
            if other and other.get("branch"):
                deps.append(other["branch"])
        base = task.get("base") or default_base
        cut = cut_from_for(branch, deps, merged, base)
        cuts[branch] = cut
        rows.append({
            "id": _task_number(task["id"]),
            "title": task.get("title") or "",
            "branch": branch,
            "cut_from": cut,
            "label": _task_label(task),
        })
    return {
        "rows": rows,
        "cuts": cuts,
        "merge_list": ordered_merges(cuts, default_base),
    }


def stack_from_texts(slug: str, spec: str, plan: str, tasks_text: str, repo=None, default_base: str = DEFAULT_BASE) -> dict:
    """Cut-from uses the 1.140.0 offer, and skips a merged or deleted branch."""
    bm = map_mod()
    parsed = bm.parse_tasks(tasks_text)
    merged = set(bm.merged_branch_names(spec, tasks_text))
    tasks = []
    for task in parsed:
        if task.get("done"):
            continue
        offer = offer_for(slug, spec, plan, tasks_text, task["id"], repo=repo)
        if not offer or not offer.get("name"):
            continue
        fate = bm.branch_fate(offer["name"], spec, tasks_text, repo, offer.get("base"))
        if fate == "merged":
            merged.add(offer["name"])
            continue
        tasks.append({
            "id": task["id"],
            "title": task.get("title") or "",
            "branch": offer["name"],
            "base": offer.get("base") or default_base,
            "deps": list(task.get("deps") or []),
        })
    return stack_from_tasks(tasks, merged, default_base)


def runs_live(line: str) -> bool:
    return bool(RUNS_LIVE.search(line or ""))


def record_live_yes(line: str, name: str, date: str) -> str:
    """Write the yes on the task line. The checkbox stays as it is."""
    mark = f"(live yes: {name}, {date})"
    if LIVE_YES.search(line or ""):
        return LIVE_YES.sub(mark, line)
    if "(after:" in line:
        return line.replace("(after:", f"{mark} (after:", 1)
    return line.rstrip() + " " + mark


def live_gate(line: str, approval_holding: bool = False, approval_asked: bool = False, dry_ran: bool = False, user_yes: bool = False, approved: bool = False, name: str | None = None, date: str | None = None, permission_refused: bool = False, live_command: str = "") -> dict:
    """Write the script, dry-run, then ask. An Approved line is not the live yes.

    Without the user's yes the script may be written and the task stays unticked.
    A held Approval needed item stops before the dry run.
    A recorded yes that the assistant's permission check refused does not run,
    and the lines do not say the yes is missing (1.143.0).
    """
    if not runs_live(line):
        return {"applies": False, "held": False, "run_live": False, "tick": False, "approved_counts_as_yes": False}
    base = {
        "applies": True,
        "approved_counts_as_yes": False,
        "approved_present": bool(approved),
        "tick": False,
        "run_live": False,
    }
    if approval_holding:
        command = "/crav1-record-approval" if approval_asked else "/crav1-show-or-ask-open-questions"
        why = "the quote can be recorded" if approval_asked else "the approval has not been asked"
        base.update({
            "phase": "approval",
            "held": True,
            "write_script": False,
            "run_check": False,
            "next_command": command,
            "why": why,
            "line": line,
        })
        return base
    if not dry_ran:
        base.update({
            "phase": "live-dry",
            "held": False,
            "write_script": True,
            "run_check": True,
            "line": line,
        })
        return base
    if not user_yes:
        base.update({
            "phase": "live-yes",
            "held": False,
            "write_script": True,
            "run_check": False,
            "record": False,
            "line": line,
            "says_yes_missing": True,
        })
        return base
    recorded = record_live_yes(line, name or "", date or "")
    if permission_refused:
        outcome = permission_mod().classify(True, True, live_command, "/crav1-build-walk")
        base.update({
            "phase": "permission-refused",
            "held": False,
            "write_script": True,
            "run_check": False,
            "run_live": False,
            "record": True,
            "line": recorded,
            "waiting": outcome["waiting"],
            "offer": outcome["offer"],
            "next_line": outcome["next"],
            "says_yes_missing": False,
            "still_unticked": "[ ]" in recorded or "[x]" not in recorded,
        })
        return base
    base.update({
        "phase": "run-live",
        "held": False,
        "write_script": True,
        "run_check": False,
        "run_live": True,
        "record": True,
        "line": recorded,
        "still_unticked": "[ ]" in recorded or "[x]" not in recorded,
    })
    return base


def _one(command: str, because: str) -> str:
    return f"Next: {command}, because {because}."


def _task_list(tasks: list) -> str:
    return ", ".join(_task_label(task) for task in tasks)


def _slug_for(state: dict) -> str | None:
    """Slug on a fresh-session command, or None when the repo has one slice."""
    slug = str(state.get("slug") or "").strip() or None
    root = state.get("root")
    if root:
        path = Path(str(root))
        if path.is_dir():
            needed = walk_mod().command_slug(path)
            if needed is None and walk_mod()._only_spec(path):
                return None
            slug = slug or (needed if needed else path.name)
    count = state.get("spec_count")
    if count is not None:
        try:
            count = int(count)
        except (TypeError, ValueError):
            count = None
    if count == 1:
        return None
    if count is not None and count > 1:
        return slug
    return slug


def _invocation(command: str, tasks: list, slug: str | None) -> str:
    """A command a new session can run. The T#s are on the command, not in because."""
    ids = ", ".join(_task_token(task["id"]) for task in tasks if task.get("id") is not None)
    if command == "/crav1-build-walk":
        if slug and ids:
            return f"/crav1-build-walk {slug} {ids}"
        if ids:
            return f"/crav1-build-walk {ids}"
        if slug:
            return f"/crav1-build-walk {slug}"
        return "/crav1-build-walk"
    if slug:
        return f"{command} {slug}"
    return command


def _entry(command: str, because: str, tasks: list, branch: str, slug: str | None) -> dict:
    labels = [_task_label(task) for task in tasks] or []
    invoked = _invocation(command, tasks, slug)
    if labels and branch:
        run = map_mod().run_entry(labels, branch, slug=slug if command == "/crav1-build-walk" else None)
        if command != "/crav1-build-walk":
            detail = run.split("\n", 1)[1]
            run = f"`{invoked}`\n{detail}"
    elif labels:
        run = f"`{invoked}`"
    else:
        run = f"`{invoked}`"
    return {"command": invoked, "run": run, "next": _one(invoked, because)}


def _compose_ending(entries: list, waiting, uncommitted) -> str:
    """Run next, Waiting, Uncommitted, then this walk's Next lines (shared order, 1.156.0)."""
    return ending_mod().compose(
        run=[entry["run"] for entry in entries if entry.get("run")],
        waiting=waiting or None,
        uncommitted=uncommitted or None,
        next_lines=[entry["next"] for entry in entries if entry.get("next")],
    )


def _other_ready(state: dict, current: str | None) -> list:
    """Other branches whose tasks can start, from readiness or from ready_branches."""
    branches = state.get("ready_branches")
    if branches is None and state.get("root"):
        path = Path(str(state["root"]))
        if path.is_dir():
            branches = walk_mod().ready_branches(path)
    out = []
    for branch in branches or []:
        if not isinstance(branch, dict):
            continue
        name = branch.get("branch")
        if not name or name == current:
            continue
        tasks = branch.get("tasks") or []
        if tasks:
            out.append(branch)
    return out


def branch_entries(branch: dict, slug: str | None = None) -> list[dict]:
    """Run next entries for one ready branch (1.155.0).

    The next task, `/crav1-build-walk <slug> T#`, then the whole branch,
    `/crav1-build-walk <slug> <branch>`, only when the branch has two or more
    open tasks. Each is its own entry with its own Next line.
    """
    tasks = branch.get("tasks") or []
    name = branch.get("branch") or ""
    opens = branch.get("open_tasks")
    if opens is None:
        opens = tasks
    entries = []
    if tasks:
        first = tasks[:1]
        label = _task_list(first) or name
        entries.append(_entry(
            "/crav1-build-walk",
            f"that work is on {name}" + (f" ({label})" if label and label != name else ""),
            first,
            name,
            slug,
        ))
    if name and len(opens) >= 2:
        command = f"/crav1-build-walk {slug} {name}" if slug else f"/crav1-build-walk {name}"
        run = map_mod().branch_entry([_task_label(task) for task in opens], name, slug=slug)
        entries.append({
            "command": command,
            "run": run,
            "next": _one(command, f"every open task on {name} builds in one run ({_task_list(opens)})"),
        })
    return entries


def grouping_lines(branches: list, slug: str | None = None) -> list[dict]:
    """Entries per ready branch. Parallel work, each a complete command."""
    entries = []
    for branch in branches:
        entries.extend(branch_entries(branch, slug))
    return entries


def _because(phase: str, state: dict) -> tuple[str, str]:
    """Return (command, because) for one in-walk phase. One command only."""
    branch = state.get("branch") or "this branch"
    tasks = _task_list(state.get("tasks") or [])
    pr = state.get("pr")
    owner = state.get("owner")
    if phase == "confirm-owner":
        who = state.get("who") or "someone else"
        return ("/crav1-build-walk", f"{who} owns {branch} and the walk has not switched")
    if phase == "approval":
        asked = bool(state.get("approval_asked"))
        command = "/crav1-record-approval" if asked else "/crav1-show-or-ask-open-questions"
        why = "that Approval needed item is unanswered" if not asked else "that Approval needed item can be recorded"
        return (command, f"{tasks or 'the task'} is held and {why}")
    if phase == "live-dry":
        return ("/crav1-build-walk", f"{tasks or 'the task'} runs live and the dry run has not been run")
    if phase == "live-yes":
        return ("/crav1-build-walk", f"{tasks or 'the task'} runs live and the live run needs your yes")
    if phase == "permission-refused":
        outcome = permission_mod().classify(
            True, True, state.get("command") or "", "/crav1-build-walk", tasks,
        )
        state["_permission"] = outcome
        why = outcome["next"].split(", because ", 1)[1].rstrip(".")
        return ("/crav1-build-walk", why)
    if phase == "build":
        return ("/crav1-build-walk", f"the next step on {branch} is to build {tasks or 'the tasks'}")
    if phase == "verify":
        return ("/crav1-build-walk", f"the next step on {branch} is to verify")
    if phase == "commit":
        return ("/crav1-build-walk", f"the next step on {branch} is to commit")
    if phase == "open-pr":
        return ("/crav1-build-walk", f"the next step on {branch} is to open the pull request")
    if phase == "merge-base":
        base = state.get("base") or DEFAULT_BASE
        return ("/crav1-build-walk", f"the next step is to merge {base} into {branch}")
    if phase == "merge-pr":
        named = f"pull request {pr}" if pr else "the pull request"
        return ("/crav1-build-walk", f"the next step is to merge {named}")
    if phase == "comment":
        named = f"pull request {pr}" if pr else "the pull request"
        return ("/crav1-build-walk", f"the push to {branch} needs one comment on {named}")
    if phase == "wait-merge":
        named = f"pull request {pr}" if pr else "the pull request"
        return ("/crav1-build-walk", f"ticks on {branch} wait until {named} is merged")
    if phase == "tick":
        return ("/crav1-build-walk", f"the next step on {branch} is to tick {tasks or 'the tasks'}")
    if phase == "next-task":
        nxt = state.get("next_branch")
        nxt_tasks = _task_list(state.get("next_tasks") or [])
        if nxt:
            return ("/crav1-build-walk", f"{nxt_tasks or 'the next task'} can start on {nxt}")
        return ("/crav1-build-walk", "no work branch remains")
    if owner == "other":
        return ("/crav1-build-walk", f"the walk is on {branch} in other-owner mode")
    return ("/crav1-build-walk", f"the walk is on {branch}")


# Phases that other-owner mode must never enter.
OTHER_FORBIDDEN = {"open-pr", "merge-base", "merge-pr"}


def next_for(state: dict) -> dict:
    """The walk ending. Run next is first. One full Next line per entry.

    While this branch is in progress, the first entry continues the walk.
    Each other branch whose tasks can start is its own entry. Grouping is
    one entry per ready branch. The step skill's own Next is not included.
    """
    slug = _slug_for(state)
    waiting = state.get("waiting")
    uncommitted = state.get("uncommitted")
    if state.get("mode") == "grouping":
        entries = grouping_lines(state.get("branches") or [], slug)
        lines = [entry["next"] for entry in entries]
        ending = _compose_ending(entries, waiting, uncommitted)
        return {
            "mode": "grouping",
            "next": lines,
            "ending": ending,
            "count": len(lines),
            "suppressed": [],
            "allowed": allowed_actions(state.get("owner"), state.get("description_asked")),
        }
    phase = state.get("phase") or "build"
    owner = state.get("owner") or "self"
    if owner == "other" and phase in OTHER_FORBIDDEN:
        phase = "comment" if state.get("pushed") and not state.get("commented") else "wait-merge"
    command, because = _because(phase, state)
    branch = state.get("branch") or ""
    tasks = state.get("tasks") or []
    entries = []
    if phase == "next-task":
        ready = list(state.get("ready_branches") or [])
        if not ready and state.get("root"):
            path = Path(str(state["root"]))
            if path.is_dir():
                ready = walk_mod().ready_branches(path)
        if ready:
            entries.extend(grouping_lines(ready, slug))
        else:
            use_tasks = state.get("next_tasks") or []
            use_branch = state.get("next_branch") or ""
            entries.append(_entry(command, because, use_tasks, use_branch, slug))
    else:
        entries.append(_entry(command, because, tasks, branch, slug))
        for other in _other_ready(state, branch):
            entries.extend(branch_entries(other, slug))
    lines = [entry["next"] for entry in entries]
    ending = _compose_ending(entries, waiting, uncommitted)
    outcome = state.get("_permission") if phase == "permission-refused" else None
    result = {
        "mode": "walk",
        "phase": phase,
        "next": lines,
        "ending": ending,
        "count": len(lines),
        "suppressed": list(SUPPRESSED.get(phase, [])),
        "allowed": allowed_actions(owner, state.get("description_asked")),
        "command": entries[0]["command"] if entries else command,
    }
    if outcome:
        result["waiting"] = outcome["waiting"]
        result["offer"] = outcome["offer"]
        result["says_yes_missing"] = False
        result["lines"] = permission_mod().printable(outcome)
        if not waiting:
            ending = _compose_ending(entries, outcome["waiting"], uncommitted)
            result["ending"] = ending
    return result


def current_phase(facts: dict) -> str:
    """The phase the walk is on, from what is already true."""
    if facts.get("detected_other") and facts.get("owner") not in ("self", "other"):
        return "confirm-owner"
    owner = facts.get("owner") or "self"
    if facts.get("approval_holding"):
        return "approval"
    if facts.get("runs_live") and not facts.get("dry_ran"):
        return "live-dry"
    if facts.get("runs_live") and facts.get("live_yes") and facts.get("permission_refused"):
        return "permission-refused"
    if facts.get("runs_live") and not facts.get("live_yes"):
        return "live-yes"
    if not facts.get("built"):
        return "build"
    if not facts.get("verified"):
        return "verify"
    if facts.get("dirty"):
        return "commit"
    if owner == "other":
        if facts.get("pushed") and not facts.get("commented"):
            return "comment"
        if not facts.get("pr_merged"):
            return "wait-merge"
        if not facts.get("ticked"):
            return "tick"
        return "next-task"
    if not facts.get("pr_open"):
        return "open-pr"
    if facts.get("behind"):
        return "merge-base"
    if not facts.get("pr_merged"):
        return "merge-pr"
    if not facts.get("ticked"):
        return "tick"
    return "next-task"


def render_merge_list(merges: list) -> list[str]:
    if not merges:
        return ["Merge list: none"]
    lines = ["Merge list:"]
    for row in merges:
        lines.append(f"Merge: {row['branch']} into {row['into']}")
    return lines


def render_progress(slice_label: str, branch: str, owner: str, tasks: list, cut_from: str, merges: list, steps: list) -> str:
    lines = [
        "# Build progress",
        "",
        f"Walk: {WALK}",
        f"Slice: {slice_label}",
        f"Branch: {branch}",
        f"Owner: {owner}",
        f"Tasks: {_task_list(tasks) if tasks else 'none'}",
        f"Cut from: {cut_from}",
    ]
    lines.extend(render_merge_list(merges))
    lines.append("")
    for step in steps:
        lines.append(f"- Step: {step['step']}")
        lines.append(f"  Done: {step['when']}")
        lines.append(f"  Result: {step['result']}")
        for label in ("Spec version", "Plan version", "Tasks version", "Verify version"):
            if label in step:
                lines.append(f"  {label}: {step[label]}")
        if step.get("content_stamp"):
            lines.append("  Content stamp: normalized")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _marker(line: str) -> str | None:
    stripped = (line or "").lstrip()
    for prefix in ("<<<<<<<", "=======", ">>>>>>>", "|||||||"):
        if stripped.startswith(prefix):
            return prefix
    return None


def classify_conflict(text: str) -> str:
    """`clean`, `stamps`, or `mixed`. A stamp hunk is only hash lines."""
    if "<<<<<<<" not in (text or ""):
        return "clean"
    lines = (text or "").splitlines()
    i = 0
    saw = False
    while i < len(lines):
        if _marker(lines[i]) == "<<<<<<<":
            saw = True
            i += 1
            while i < len(lines) and _marker(lines[i]) != ">>>>>>>":
                row = lines[i]
                i += 1
                if _marker(row) in ("=======", "|||||||"):
                    continue
                stripped = row.strip()
                if not stripped:
                    continue
                if HASH_LINE.match(stripped) or HASH_LINE.match(row):
                    continue
                return "mixed"
            if i < len(lines) and _marker(lines[i]) == ">>>>>>>":
                i += 1
            continue
        i += 1
    return "stamps" if saw else "clean"


def settle_stamps(text: str, hashes: dict | None = None) -> str | None:
    """Take the upstream side of stamp-only hunks. Mixed conflicts are not rewritten.

    `hashes` replaces a settled hash line when the caller already knows the
    merged file's normalized hash. `Content stamp: normalized` is written
    when a Tasks version line is rewritten.
    """
    if classify_conflict(text) == "mixed":
        return None
    if classify_conflict(text) == "clean":
        return text
    out = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if _marker(lines[i]) == "<<<<<<<":
            ours = []
            theirs = []
            side = ours
            i += 1
            while i < len(lines) and _marker(lines[i]) != ">>>>>>>":
                if _marker(lines[i]) == "=======":
                    side = theirs
                    i += 1
                    continue
                side.append(lines[i])
                i += 1
            if i < len(lines) and _marker(lines[i]) == ">>>>>>>":
                i += 1
            chosen = theirs if theirs else ours
            for row in chosen:
                match = re.match(r"^(  )?(Tasks version|Spec version|Plan version|Verify version): \S+$", row)
                if match and hashes and match.group(2) in hashes:
                    out.append(f"{match.group(1) or ''}{match.group(2)}: {hashes[match.group(2)]}")
                else:
                    out.append(row)
            continue
        out.append(lines[i])
        i += 1
    text_out = "\n".join(out)
    if hashes and hashes.get("Tasks version") and "Content stamp: normalized" not in text_out:
        text_out = text_out.rstrip() + "\n  Content stamp: normalized\n"
    if not text_out.endswith("\n"):
        text_out += "\n"
    return text_out


def _load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_json(path: str):
    try:
        return _load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError("json", f"cannot read next json: {exc}") from exc


def prepare_state(state: dict) -> dict:
    """Normalize the next --json object. tasks may be T# strings or objects."""
    if not isinstance(state, dict):
        raise InputError("json", "next --json must be an object")
    state = dict(state)
    if "tasks" in state:
        state["tasks"] = normalize_tasks(state.get("tasks"))
    if "next_tasks" in state:
        state["next_tasks"] = normalize_tasks(state.get("next_tasks"))
    if "branches" in state:
        state["branches"] = normalize_branches(state.get("branches"), "branches")
    if "ready_branches" in state:
        state["ready_branches"] = normalize_branches(state.get("ready_branches"), "ready_branches")
    return state


def _bad(code: str, line: str, status: int = 2) -> int:
    return _emit({"ok": False, "code": code, "line": line}, status)


def cmd_next(args: argparse.Namespace) -> int:
    try:
        raw = _read_json(args.json)
        state = prepare_state(raw)
        if not state.get("phase") and state.get("mode") != "grouping":
            state["phase"] = current_phase(state)
        result = next_for(state)
    except InputError as exc:
        return _bad(exc.code, exc.line)
    except (AttributeError, TypeError, ValueError, KeyError) as exc:
        return _bad("input", f"next input is not usable: {exc}")
    result["ok"] = True
    return _emit(result)


def cmd_owner(args: argparse.Namespace) -> int:
    found = detect_other_owner(args.user, args.pr_author, args.commit_author)
    found["ok"] = True
    found["allowed"] = allowed_actions("other" if found["other"] else "self", args.edit_description)
    return _emit(found)


def cmd_comment(args: argparse.Namespace) -> int:
    body = push_comment(args.branch, args.pr, args.summary)
    body["ok"] = True
    return _emit(body)


def cmd_live(args: argparse.Namespace) -> int:
    state = _load_json(args.json)
    result = live_gate(
        state.get("line") or "",
        approval_holding=bool(state.get("approval_holding")),
        approval_asked=bool(state.get("approval_asked")),
        dry_ran=bool(state.get("dry_ran")),
        user_yes=bool(state.get("user_yes")),
        approved=bool(state.get("approved")),
        name=state.get("name"),
        date=state.get("date"),
    )
    result["ok"] = True
    return _emit(result)


def cmd_stack(args: argparse.Namespace) -> int:
    state = _load_json(args.json)
    if "tasks" in state and "spec" not in state:
        result = stack_from_tasks(state.get("tasks") or [], set(state.get("merged") or []), state.get("base") or DEFAULT_BASE)
    else:
        result = stack_from_texts(
            state.get("slug") or "orders",
            state.get("spec") or "",
            state.get("plan") or "",
            state.get("tasks_text") or "",
            default_base=state.get("base") or DEFAULT_BASE,
        )
    result["ok"] = True
    return _emit(result)


def cmd_stamp(args: argparse.Namespace) -> int:
    text = Path(args.tasks).read_text(encoding="utf-8")
    return _emit({"ok": True, "tasks": tasks_hash(text), "content_stamp": "normalized"})


def cmd_resolve(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        return _fail("file", f"no file {path}")
    text = path.read_text(encoding="utf-8")
    kind = classify_conflict(text)
    if kind == "mixed":
        return _emit({
            "ok": False,
            "kind": "mixed",
            "line": "A build-progress conflict touches more than hash lines. Nothing was rewritten.",
        })
    settled = settle_stamps(text)
    wrote = False
    if args.yes and settled is not None and kind == "stamps":
        path.write_text(settled, encoding="utf-8")
        wrote = True
    return _emit({"ok": True, "kind": kind, "wrote": wrote, "line": "Settled stamp-only lines in the build progress file." if wrote else "Nothing to settle."})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build walk progress and next step")
    sub = parser.add_subparsers(dest="cmd", required=True)

    nxt = sub.add_parser("next")
    nxt.add_argument("--json", required=True)
    nxt.set_defaults(func=cmd_next)

    own = sub.add_parser("owner")
    own.add_argument("--user", default="")
    own.add_argument("--pr-author", default="")
    own.add_argument("--commit-author", action="append", default=[])
    own.add_argument("--edit-description", action="store_true")
    own.set_defaults(func=cmd_owner)

    comment = sub.add_parser("comment")
    comment.add_argument("--branch", required=True)
    comment.add_argument("--pr", required=True)
    comment.add_argument("--summary", required=True)
    comment.set_defaults(func=cmd_comment)

    live = sub.add_parser("live")
    live.add_argument("--json", required=True)
    live.set_defaults(func=cmd_live)

    stack = sub.add_parser("stack")
    stack.add_argument("--json", required=True)
    stack.set_defaults(func=cmd_stack)

    stamp = sub.add_parser("stamp")
    stamp.add_argument("--tasks", required=True)
    stamp.set_defaults(func=cmd_stamp)

    resolve = sub.add_parser("resolve-stamps")
    resolve.add_argument("--file", required=True)
    resolve.add_argument("--yes", action="store_true")
    resolve.set_defaults(func=cmd_resolve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
