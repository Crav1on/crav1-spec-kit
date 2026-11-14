#!/usr/bin/env python3
"""Whole-branch run for /crav1-build-walk <slug> <branch> (kit 1.155.0).

`/crav1-build-walk <slug> T5` still builds one task. `/crav1-build-walk <slug>
<branch>` builds every open task on that branch in task order and stops only
for a real stop: an open question on the next task, a stakeholder yes that is
not recorded, a manual or secret step, tests or lint that stay red after a
fair try, a wanted change outside the task's scope, someone else claiming or
changing one of the run's tasks, and always before the pull request merge.

Position is kept in the branch's build-progress file, in a `## Run` section:
the tasks built with their commits and the next task. Rerunning the same
command continues from the next open task, reuses its own claim, and repeats
no work. One claim line in claims.md names every open task on the branch, in
the 1.151.0 format, so older ready checks read it too.

Usage (JSON on stdout):
  branch_run.py parse --root <docs/specs or spec-folder> --args "<slug> <branch-or-T#>"
  branch_run.py plan --root <spec-folder> --branch <name> [--user <name>]
  branch_run.py start --root <spec-folder> --branch <name> --user <name> --yes [--hint-every N]
  branch_run.py guard --root <spec-folder> --branch <name> --user <name> [--repo <git dir>]
  branch_run.py after --json <file>
  branch_run.py record --root <spec-folder> --branch <name> --task <T#> --commit <sha>
      --tests <green|red|none> [--repo <git dir> --push]
  branch_run.py ending --json <file>
  branch_run.py status --root <spec-folder> --branch <name> --state "<state>"

Each start and record also writes one status line for the branch in
walk-progress.md, for example `running, T9 done, next T10`, `stopped before
merge`, or `merged`, with a link to this log. That file stays the one place
every skill reads.

`start` without --yes writes nothing. `record --push` pushes the work
branch with no card: the start yes covers every push in the run. It never
merges, never rebases, and never force-pushes. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
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

DEFAULT_HINT_EVERY = 3
DEFAULT_FAIR_TRY = 3
RUN_HEADING = "## Run"
TASK_ARG = re.compile(r"^T?\d+,?$", re.I)
MANUAL_MARK = re.compile(r"\((?:[^)]*\b(?:manual|secret)\b[^)]*|host setup|Runs live)\)", re.I)
TASK_LINE = re.compile(r"^\s*- \[( |x|X)\] T(\d+)\b[:.]?\s*(.*)$")
PROGRESS_NOTE = re.compile(r"\s*\((?:PR\s+\d+[^)]*|done|live yes:[^)]*)\)", re.I)
BUILT_LINE = re.compile(r"^- Built: (T\d+), commit ([0-9a-f]{7,40}), tests (green|red|none)$")
STOPS = ("question", "approval", "manual", "tests", "scope", "claimed", "changed", "sync", "merge")


def _emit(payload: dict, status: int = 0) -> int:
    json.dump(payload, sys.stdout, indent=2, default=list)
    sys.stdout.write("\n")
    return status


def _load(folder: str, filename: str):
    import importlib.util

    path = Path(__file__).resolve().parents[2] / folder / "scripts" / filename
    spec = importlib.util.spec_from_file_location(filename[:-3] + "_br", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def map_mod():
    return _load("crav1-tasks-ready-to-build", "build_map.py")


def claims_mod():
    return _load("crav1-build-walk", "claims.py")


def approval_mod():
    return _load("crav1-record-approval", "approval_needed.py")


def walk_mod():
    return _load("crav1-tighten-and-plan-ready-to-build", "walk_progress.py")


def set_status(root: Path, branch: str, state: str, when: str | None = None) -> str | None:
    """One status line per branch in walk-progress.md (1.155.0). Returns the line."""
    try:
        out = walk_mod().set_branch_run(Path(root), branch, state, when)
    except SystemExit:
        return None
    return out.get("line")


def run_state(next_task: str | None, done: str | None = None) -> str:
    if not next_task:
        return "stopped before merge"
    if done:
        return f"running, {done} done, next {next_task}"
    return f"running, next {next_task}"


def questions_mod():
    return _load("crav1-tasks-ready-to-build", "question_blocks.py")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def tid(value) -> str:
    match = re.match(r"^T?(\d+)$", str(value).strip().rstrip(","), re.I)
    if not match:
        raise ValueError(f"not a task id: {value}")
    return f"T{int(match.group(1))}"


def file_slug(branch: str) -> str:
    return branch.replace("/", "--")


def progress_path(root: Path, branch: str) -> Path:
    return Path(root) / "build-progress" / f"{file_slug(branch)}.md"


# ---------- invocation ----------

def parse_args(tokens: list[str], specs_root: Path | None = None) -> dict:
    """task, branch, or (reserved) chain. A chain run is not in this release."""
    tokens = [tok for tok in (tokens or []) if tok.strip()]
    slug = None
    slugs = set()
    if specs_root is not None and Path(specs_root).is_dir():
        base = Path(specs_root)
        if (base / "tasks.md").is_file():
            slugs.add(base.name)
        else:
            slugs = {p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith("_")}
    if tokens and tokens[0] in slugs:
        slug = tokens.pop(0)
    if tokens and tokens[0].lower() == "chain":
        return {"ok": False, "code": "chain", "slug": slug,
                "line": "A chain run is not in this release. Name a branch or a T#."}
    if not tokens:
        return {"ok": True, "mode": "pick", "slug": slug}
    if all(TASK_ARG.match(tok) for tok in tokens):
        return {"ok": True, "mode": "task", "slug": slug, "tasks": [tid(tok) for tok in tokens]}
    if len(tokens) == 1 and not TASK_ARG.match(tokens[0]):
        if slug is None and tokens[0] in slugs:
            return {"ok": True, "mode": "pick", "slug": tokens[0]}
        return {"ok": True, "mode": "branch", "slug": slug, "branch": tokens[0]}
    return {"ok": False, "code": "args", "slug": slug,
            "line": "Name one branch, or one or more T#s, not both."}


# ---------- the branch's tasks ----------

def _task_lines(tasks_text: str) -> dict:
    found = {}
    for line in (tasks_text or "").splitlines():
        match = TASK_LINE.match(line)
        if match:
            found[f"T{int(match.group(2))}"] = line
    return found


def task_stamp(line: str) -> str:
    """Hash of a task line, ignoring the checkbox and progress notes."""
    match = TASK_LINE.match(line or "")
    body = match.group(3) if match else (line or "")
    body = PROGRESS_NOTE.sub("", body)
    body = re.sub(r"\s+", " ", body).strip()
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def stop_for(task_id: str, line: str, questions: list, holds: dict) -> dict | None:
    """The stop that holds this task before it is built, or None."""
    for question in questions:
        if task_id in (question.get("tasks") or []) or question.get("blocks_slice"):
            return {"kind": "question", "task": task_id,
                    "line": f"{task_id} has an open question: {question.get('text')}"}
    item = holds.get(task_id)
    if item:
        who = item.get("who") or "not named yet"
        return {"kind": "approval", "task": task_id,
                "line": f"{task_id} needs a yes from {who} that is not recorded"}
    if MANUAL_MARK.search(line or ""):
        return {"kind": "manual", "task": task_id,
                "line": f"{task_id} has a manual, secret, or live step that needs you"}
    return None


def branch_plan(root: Path, branch: str, user: str | None = None) -> dict:
    """Open tasks on the branch in task order, each with the stop that holds it."""
    root = Path(root)
    tasks_text = _read(root / "tasks.md")
    if not tasks_text:
        return {"ok": False, "code": "tasks", "line": f"No tasks.md in {root}."}
    spec_text = _read(root / "spec.md")
    plan_path = root / "plan.md"
    plan_text = _read(plan_path) if plan_path.is_file() else None
    bm = map_mod()
    built = bm.build(root.name, spec_text, plan_text, tasks_text)
    match = [b for b in built["branches"] if b["name"] == branch]
    if not match:
        names = [b["name"] for b in built["branches"]]
        return {"ok": False, "code": "branch",
                "line": f"No task in tasks.md is on {branch}.", "branches": names}
    found = match[0]
    analysed = bm.task_order.analyse(bm.parse_tasks(tasks_text))
    order = {n: i for i, n in enumerate(analysed["order"])}
    lines = _task_lines(tasks_text)
    ids = [f"T{t['id']}" for t in bm.parse_tasks(tasks_text)]
    questions = questions_mod().kept_open(spec_text, task_ids=ids)
    holds = approval_mod().holds(spec_text, ids) if spec_text else {}
    claims = claims_mod().parse_claims(_read(root / "claims.md"))["claims"]
    rows = []
    for task in sorted(found["tasks"], key=lambda t: (order.get(t["id"], 10**6), t["id"])):
        task_id = f"T{task['id']}"
        line = lines.get(task_id, "")
        row = {
            "id": task_id,
            "label": task.get("label") or task_id,
            "done": bool(task.get("done")),
            "deps": [f"T{d}" for d in task.get("deps") or []],
            "stamp": task_stamp(line),
            "stop": None,
        }
        if not row["done"]:
            row["stop"] = stop_for(task_id, line, questions, holds)
            claim = claims_mod().claim_for(claims, task_id)
            if claim and user and not same_person(claim["user"], user):
                row["stop"] = {"kind": "claimed", "task": task_id,
                               "line": f"{task_id} is {claim['phrase']}"}
        rows.append(row)
    open_rows = [row for row in rows if not row["done"]]
    return {
        "ok": True,
        "branch": branch,
        "status": found.get("status"),
        "tasks": rows,
        "open": [row["id"] for row in open_rows],
        "done": [row["id"] for row in rows if row["done"]],
        "first_stop": next((row["stop"] for row in open_rows if row["stop"]), None),
    }


def same_person(left, right) -> bool:
    return (left or "").strip().casefold() == (right or "").strip().casefold()


# ---------- progress (the ## Run section) ----------

def parse_run(text: str) -> dict | None:
    """The ## Run section of a build-progress file, or None."""
    lines = (text or "").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == RUN_HEADING)
    except StopIteration:
        return None
    run = {"yes": None, "next": None, "hint_every": DEFAULT_HINT_EVERY,
           "built": [], "stamps": {}, "session": 0}
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if stripped.startswith("Run yes:"):
            run["yes"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Next task:"):
            value = stripped.split(":", 1)[1].strip()
            run["next"] = None if value == "none" else value
        elif stripped.startswith("Fresh session hint:"):
            match = re.search(r"(\d+)", stripped)
            if match:
                run["hint_every"] = int(match.group(1))
        elif stripped.startswith("Task stamps:"):
            for part in stripped.split(":", 1)[1].split(","):
                bits = part.split()
                if len(bits) == 2:
                    run["stamps"][bits[0]] = bits[1]
        else:
            match = BUILT_LINE.match(stripped)
            if match:
                run["built"].append({"task": match.group(1), "commit": match.group(2),
                                     "tests": match.group(3)})
    return run


def render_run(run: dict) -> str:
    lines = [RUN_HEADING, "", "Run: whole branch", f"Run yes: {run['yes']}"]
    if run.get("hint_every", DEFAULT_HINT_EVERY) != DEFAULT_HINT_EVERY:
        lines.append(f"Fresh session hint: every {run['hint_every']} tasks")
    stamps = ", ".join(f"{task} {stamp}" for task, stamp in run.get("stamps", {}).items())
    if stamps:
        lines.append(f"Task stamps: {stamps}")
    lines.append(f"Next task: {run.get('next') or 'none'}")
    for row in run.get("built", []):
        lines.append(f"- Built: {row['task']}, commit {row['commit']}, tests {row['tests']}")
    return "\n".join(lines) + "\n"


def write_run(path: Path, run: dict, branch: str) -> None:
    text = _read(path)
    if not text:
        text = f"# Build progress\n\nWalk: build-walk\nBranch: {branch}\nOwner: self\n"
    lines = text.splitlines()
    out, skipping = [], False
    for line in lines:
        if line.strip() == RUN_HEADING:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            out.append(line)
    body = "\n".join(out).rstrip() + "\n\n" + render_run(run)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def load_run(root: Path, branch: str) -> dict | None:
    return parse_run(_read(progress_path(root, branch)))


# ---------- start and resume ----------

def start(root: Path, branch: str, user: str, yes: bool, hint_every: int | None = None,
          now: str | None = None) -> dict:
    """Claim the branch and write the run section. Resume reuses both."""
    root = Path(root)
    plan = branch_plan(root, branch, user)
    if not plan["ok"]:
        return plan
    existing = load_run(root, branch)
    claims = claims_mod().parse_claims(_read(root / "claims.md"))["claims"]
    mine = [c for c in claims if c["branch"] == branch and same_person(c["user"], user)]
    others = [row["stop"] for row in plan["tasks"] if row["stop"] and row["stop"]["kind"] == "claimed"]
    if others:
        return {"ok": False, "code": "claimed", "stop": others[0], "line": others[0]["line"]}
    built = {row["task"] for row in (existing or {}).get("built", [])}
    remaining = [t for t in plan["open"] if t not in built]
    next_task = remaining[0] if remaining else None
    held = set(claims_mod().claimed_ids(mine))
    resume = existing is not None and existing.get("yes") is not None
    claim_action = "reuse" if remaining and set(remaining) <= held else ("none" if not remaining else "add")
    payload = {
        "ok": True,
        "branch": branch,
        "resume": resume,
        "next_task": next_task,
        "remaining": remaining,
        "built": sorted(built, key=lambda t: int(t[1:])),
        "claim": claim_action,
        "first_stop": plan["first_stop"],
        "card": None if resume else {"words": ["yes", "stop"], "recommended": "yes",
                                      "action": f"claim {', '.join(remaining)} on {branch}, then build, commit, and push each task without another card"},
    }
    if not yes:
        payload["wrote"] = False
        return payload
    if claim_action == "add":
        added = claims_mod().add_claim(root, branch, remaining, user)
        if not added.get("ok"):
            return {**added, "stop": {"kind": "claimed", "line": added.get("line")}}
        payload["claim_line"] = f"In progress: {branch}, {', '.join(remaining)}, {user}, since {added['added']['since']}"
        payload["commit_message"] = added["commit_message"]
    run = existing or {"built": [], "stamps": {}, "hint_every": DEFAULT_HINT_EVERY}
    run["yes"] = run.get("yes") or f"{user}, {now or now_iso()}"
    if hint_every:
        run["hint_every"] = int(hint_every)
    run["stamps"] = {row["id"]: row["stamp"] for row in plan["tasks"] if row["id"] in remaining} or run.get("stamps", {})
    run["next"] = next_task
    write_run(progress_path(root, branch), run, branch)
    last = run["built"][-1]["task"] if run.get("built") else None
    payload["status_line"] = set_status(root, branch, run_state(next_task, last))
    payload["wrote"] = True
    payload["progress"] = str(progress_path(root, branch))
    return payload


# ---------- before each task ----------

def _upstream_author(repo: Path | None, path: Path) -> str | None:
    if repo is None:
        return None
    proc = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%an", "@{upstream}", "--", str(path)],
                          capture_output=True, text=True, check=False)
    name = (proc.stdout or "").strip()
    return name or None


def guard(root: Path, branch: str, user: str, repo: Path | None = None) -> dict:
    """After the fetch and merge: stop when someone else claimed or changed a run task."""
    root = Path(root)
    run = load_run(root, branch)
    if run is None:
        return {"ok": False, "code": "run", "line": f"No run is recorded for {branch}. Start it first."}
    claims = claims_mod().parse_claims(_read(root / "claims.md"))["claims"]
    built = {row["task"] for row in run["built"]}
    watched = [task for task in run["stamps"] if task not in built]
    for task in watched:
        claim = claims_mod().claim_for(claims, task)
        if claim and not same_person(claim["user"], user):
            return {"ok": True, "stop": True, "kind": "claimed", "task": task, "who": claim["user"],
                    "line": f"{task} is now {claim['phrase']}. Stopped before building it."}
    lines = _task_lines(_read(root / "tasks.md"))
    for task in watched:
        line = lines.get(task)
        if line is None:
            who = _upstream_author(repo, root / "tasks.md") or "someone"
            return {"ok": True, "stop": True, "kind": "changed", "task": task, "who": who,
                    "line": f"{task} was removed from tasks.md by {who}. Stopped before building it."}
        if task_stamp(line) != run["stamps"][task]:
            who = _upstream_author(repo, root / "tasks.md") or "someone"
            return {"ok": True, "stop": True, "kind": "changed", "task": task, "who": who,
                    "line": f"{task} was changed in tasks.md by {who}: {line.strip()}. Stopped before building it."}
    return {"ok": True, "stop": False, "line": "No one else claimed or changed this run's tasks."}


# ---------- after each task ----------

def after(state: dict) -> dict:
    """Keep going or stop, after one task was built and tested.

    state: task, next (T# or null), next_stop (stop dict or null), tests
    ("green", "red", "none"), attempts (fix tries so far), fair_try
    (default 3), out_of_scope (text or empty), done_in_session (count),
    hint_every (default 3), command (the resume command).
    """
    task = tid(state["task"])
    tests = state.get("tests") or "none"
    attempts = int(state.get("attempts") or 0)
    fair = int(state.get("fair_try") or DEFAULT_FAIR_TRY)
    if state.get("out_of_scope"):
        return {"stop": True, "kind": "scope", "task": task,
                "line": f"{task} wants a change outside its scope: {state['out_of_scope']}"}
    if tests == "red":
        if attempts < fair:
            return {"stop": False, "action": "fix", "task": task,
                    "line": f"{task} tests are red, fix try {attempts + 1} of {fair}"}
        return {"stop": True, "kind": "tests", "task": task,
                "line": f"{task} tests or lint are still red after {attempts} tries"}
    nxt = state.get("next")
    word = "tests green" if tests == "green" else "no tests to run"
    if not nxt:
        return {"stop": True, "kind": "merge", "task": task,
                "line": f"{task} done, {word}. Every task on the branch is built. Stopping before the merge."}
    nxt = tid(nxt)
    if state.get("next_stop"):
        stop = dict(state["next_stop"])
        stop.setdefault("kind", "question")
        return {"stop": True, "kind": stop["kind"], "task": nxt,
                "line": f"{task} done, {word}. Stopped before {nxt}: {stop.get('line') or stop['kind']}"}
    line = f"{task} done, {word}, starting {nxt}"
    count = int(state.get("done_in_session") or 0)
    every = int(state.get("hint_every") or DEFAULT_HINT_EVERY)
    hint = None
    if every > 0 and count > 0 and count % every == 0:
        command = state.get("command") or "/crav1-build-walk"
        hint = f"{count} tasks in this session; a fresh session with `{command}` keeps the context small"
        line = f"{line} ({hint})"
    return {"stop": False, "action": "continue", "task": task, "next": nxt, "line": line, "hint": hint}


def record(root: Path, branch: str, task: str, commit: str, tests: str,
           repo: Path | None = None, push: bool = False) -> dict:
    """Write one built task to the run section, commit it, and push with no card."""
    root = Path(root)
    run = load_run(root, branch)
    if run is None or not run.get("yes"):
        return {"ok": False, "code": "run", "line": "No run yes is recorded. Nothing is pushed without the start yes."}
    task = tid(task)
    if not re.fullmatch(r"[0-9a-f]{7,40}", commit or ""):
        return {"ok": False, "code": "commit", "line": f"not a commit sha: {commit}"}
    if tests not in ("green", "red", "none"):
        return {"ok": False, "code": "tests", "line": "tests is green, red, or none"}
    run["built"] = [row for row in run["built"] if row["task"] != task]
    run["built"].append({"task": task, "commit": commit[:12], "tests": tests})
    built = {row["task"] for row in run["built"]}
    plan = branch_plan(root, branch)
    order = plan.get("tasks") or []
    remaining = [row["id"] for row in order if not row["done"] and row["id"] not in built]
    run["next"] = remaining[0] if remaining else None
    path = progress_path(root, branch)
    write_run(path, run, branch)
    status = set_status(root, branch, run_state(run["next"], task))
    out = {"ok": True, "task": task, "next_task": run["next"], "progress": str(path),
           "status_line": status, "committed": False, "pushed": False}
    if repo is None:
        return out
    rel = str(path.resolve().relative_to(Path(repo).resolve()))
    paths = [rel]
    for extra in (root / "claims.md", root / "walk-progress.md"):
        if extra.is_file():
            paths.append(str(extra.resolve().relative_to(Path(repo).resolve())))
    for item in paths:
        _git(repo, "add", "--", item)
    proc = _git(repo, "commit", "-m", f"Record {task} on {branch} in the build progress")
    out["committed"] = proc.returncode == 0
    if push:
        out.update(push_branch(Path(repo), branch))
    return out


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)


def push_branch(repo: Path, branch: str) -> dict:
    """Plain push of the work branch. Never --force. Sets upstream on the first push."""
    upstream = _git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if upstream.returncode == 0:
        proc = _git(repo, "push")
    else:
        proc = _git(repo, "push", "-u", "origin", branch)
    if proc.returncode != 0:
        return {"pushed": False, "stop": True, "kind": "sync",
                "line": "The push was rejected. Merge origin in (never rebase), then rerun the walk.",
                "detail": (proc.stderr or proc.stdout or "").strip()}
    return {"pushed": True}


# ---------- the ending ----------

def _label(task) -> str:
    if isinstance(task, dict):
        ident = tid(task.get("id"))
        title = (task.get("title") or "").strip()
        return f"{ident} {title}".strip()
    text = str(task).strip()
    match = re.match(r"^T?(\d+)\b\s*(.*)$", text, re.I)
    return f"T{int(match.group(1))} {match.group(2)}".strip() if match else text


def ending(state: dict) -> dict:
    """Run next, then what was built, then what is left. One string."""
    slug = state.get("slug")
    branch = state["branch"]
    prefix = f"/crav1-build-walk {slug}" if slug else "/crav1-build-walk"
    stop = state.get("stop") or {"kind": "merge"}
    kind = stop.get("kind") or "merge"
    pr = state.get("pr")
    runs = []
    if kind == "merge":
        if not pr or state.get("pr_failed"):
            runs.append(("`/crav1-open-pr`", f"open the pull request for {branch}"))
        else:
            runs.append((f"`{prefix} {branch}`",
                         f"merge PR {pr} into {state.get('base') or 'develop'}, after your yes"))
    else:
        runs.append((f"`{prefix} {branch}`", f"continue {branch} once this is settled: {stop.get('line') or kind}"))
    for other in state.get("ready_branches") or []:
        if not isinstance(other, dict):
            other = {"branch": str(other), "tasks": []}
        name = other.get("branch")
        if not name or name == branch:
            continue
        tasks = [_label(task) for task in other.get("tasks") or []]
        opens = [_label(task) for task in (other.get("open_tasks") or other.get("tasks") or [])]
        if tasks:
            first = tasks[0]
            runs.append((f"`{prefix} {first.split()[0]}`", f"branch {name}, {first}"))
        if len(opens) >= 2:
            runs.append((f"`{prefix} {name}`", f"branch {name}, every open task: {', '.join(opens)}"))
    parts = ["Run next:\n\n" + "\n\n".join(f"{cmd}\n{why}" for cmd, why in runs)]
    built = state.get("built") or []
    if built:
        header = f"Built on {branch}" + (f" (PR {pr} is open and up to date):" if pr and not state.get("pr_failed") else ":")
        rows = [f"- {row['task']}{(' ' + row['title']) if row.get('title') else ''}: commit {row['commit'][:7]}, tests {row['tests']}" for row in built]
        parts.append(header + "\n" + "\n".join(rows))
    left = []
    if kind != "merge" and stop.get("line"):
        left.append(f"- Stopped: {stop['line']}")
    for row in state.get("skipped") or []:
        left.append(f"- Skipped {row.get('task')}: {row.get('why')}")
    for text in state.get("questions") or []:
        left.append(f"- Open question: {text}")
    for text in state.get("verify_behind") or []:
        left.append(f"- verify.md is behind: {text}")
    if left:
        parts.append("Left:\n" + "\n".join(left))
    return {"ending": "\n\n".join(parts), "kind": kind, "merges": False}


# ---------- CLI ----------

def _json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Whole-branch build walk")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parse")
    p.add_argument("--root", default="docs/specs")
    p.add_argument("--args", default="")
    p = sub.add_parser("plan")
    p.add_argument("--root", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--user", default=None)
    p = sub.add_parser("start")
    p.add_argument("--root", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--yes", action="store_true")
    p.add_argument("--hint-every", type=int, default=None)
    p = sub.add_parser("guard")
    p.add_argument("--root", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--repo", default=None)
    p = sub.add_parser("after")
    p.add_argument("--json", required=True)
    p = sub.add_parser("record")
    p.add_argument("--root", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--tests", required=True)
    p.add_argument("--repo", default=None)
    p.add_argument("--push", action="store_true")
    p = sub.add_parser("ending")
    p.add_argument("--json", required=True)
    p = sub.add_parser("status")
    p.add_argument("--root", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--state", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "parse":
            return _emit(parse_args(args.args.split(), Path(args.root)))
        if args.cmd == "plan":
            out = branch_plan(Path(args.root), args.branch, args.user)
            return _emit(out, 0 if out["ok"] else 2)
        if args.cmd == "start":
            out = start(Path(args.root), args.branch, args.user, args.yes, args.hint_every)
            return _emit(out, 0 if out["ok"] else 2)
        if args.cmd == "guard":
            out = guard(Path(args.root), args.branch, args.user, Path(args.repo) if args.repo else None)
            return _emit(out, 0 if out["ok"] else 2)
        if args.cmd == "after":
            return _emit({"ok": True, **after(_json(args.json))})
        if args.cmd == "record":
            out = record(Path(args.root), args.branch, args.task, args.commit, args.tests,
                         Path(args.repo) if args.repo else None, args.push)
            return _emit(out, 0 if out["ok"] else 2)
        if args.cmd == "status":
            line = set_status(Path(args.root), args.branch, args.state)
            return _emit({"ok": bool(line), "line": line or "walk-progress.md could not be updated"}, 0 if line else 2)
        if args.cmd == "ending":
            return _emit({"ok": True, **ending(_json(args.json))})
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        return _emit({"ok": False, "code": "input", "line": f"input is not usable: {exc}"}, 2)
    return 2


if __name__ == "__main__":
    sys.exit(main())
