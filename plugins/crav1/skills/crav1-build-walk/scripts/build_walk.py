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


def _task_label(task: dict) -> str:
    title = (task.get("title") or "").strip()
    title = RUNS_LIVE.sub("", title)
    title = LIVE_YES.sub("", title)
    title = re.sub(r"\s{2,}", " ", title).strip(" .")
    return f"T{task['id']} {title}".strip()


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
    by_id = {int(task["id"]): task for task in tasks}
    cuts = {}
    rows = []
    for task in tasks:
        branch = task.get("branch")
        if not branch:
            continue
        deps = []
        for dep in task.get("deps") or []:
            other = by_id.get(int(dep))
            if other and other.get("branch"):
                deps.append(other["branch"])
        base = task.get("base") or default_base
        cut = cut_from_for(branch, deps, merged, base)
        cuts[branch] = cut
        rows.append({
            "id": int(task["id"]),
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


def grouping_lines(branches: list) -> list[str]:
    """One Next per ready branch, T number beside the task name. Parallel work."""
    lines = []
    for branch in branches:
        tasks = branch.get("tasks") or []
        label = _task_list(tasks) or branch.get("branch")
        lines.append(_one(
            f"/crav1-build-walk {label}",
            f"that work is on {branch.get('branch')}",
        ))
    return lines


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
    """Exactly one Next line, unless mode is grouping (one line per branch).

    The line replaces a step skill's own Next. `suppressed` names those commands.
    """
    if state.get("mode") == "grouping":
        lines = grouping_lines(state.get("branches") or [])
        return {
            "mode": "grouping",
            "next": lines,
            "count": len(lines),
            "suppressed": [],
            "allowed": allowed_actions(state.get("owner"), state.get("description_asked")),
        }
    phase = state.get("phase") or "build"
    owner = state.get("owner") or "self"
    if owner == "other" and phase in OTHER_FORBIDDEN:
        phase = "comment" if state.get("pushed") and not state.get("commented") else "wait-merge"
    command, because = _because(phase, state)
    line = _one(command, because)
    outcome = state.get("_permission") if phase == "permission-refused" else None
    result = {
        "mode": "walk",
        "phase": phase,
        "next": [line],
        "count": 1,
        "suppressed": list(SUPPRESSED.get(phase, [])),
        "allowed": allowed_actions(owner, state.get("description_asked")),
        "command": command,
    }
    if outcome:
        result["waiting"] = outcome["waiting"]
        result["offer"] = outcome["offer"]
        result["says_yes_missing"] = False
        result["lines"] = permission_mod().printable(outcome)
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


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cmd_next(args: argparse.Namespace) -> int:
    state = _read_json(args.json)
    if not state.get("phase") and state.get("mode") != "grouping":
        state = dict(state)
        state["phase"] = current_phase(state)
    result = next_for(state)
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
    state = _read_json(args.json)
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
    state = _read_json(args.json)
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
