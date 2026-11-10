#!/usr/bin/env python3
"""Progress file for /crav1-tighten-and-plan-ready-to-build (kit 1.123.0).

The spec, plan, and tasks stay the source of truth. This script only tracks
where the guided walk is, which version of each file a step covered, and which
ready-check rows belong to which step. It does not edit those files, does not
apply a playbook, and does not start a build.

A later step inside the walk leaves earlier steps done. An optional extra
the walk itself runs is recorded with `- Extra:` when it finishes, and that
record does the same. `cover` is optional: it counts a write made outside
this walk as part of the walk, and does not name an extra. A change that
nobody recorded or covered reopens only the steps that change affects.

Usage (JSON on stdout):
  walk_progress.py version --root <spec-folder>
  walk_progress.py record --root <spec-folder> --slice docs/specs/<slug> --step <id>
      --result <result> --yes [--when <full timestamp>] [--playbook <file>]
  walk_progress.py cover --root <spec-folder> --yes
  walk_progress.py clear --root <spec-folder> --step <id> --yes
  walk_progress.py resume --root <spec-folder>
  walk_progress.py playbook-status --root <spec-folder> --playbook <file>
  walk_progress.py readiness --json <file> [--root <spec-folder>]

record, cover, and clear without --yes write nothing and exit 2.
The script stamps Done itself. --when, when passed, must be a full timestamp.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime

sys.dont_write_bytecode = True  # before any sibling import; no __pycache__ in the project (1.121.1)

from pathlib import Path

WALK = "tighten-and-plan-ready-to-build"
PROGRESS_NAME = "walk-progress.md"
RESULTS = ("done", "nothing-to-do", "skipped", "applied", "reapplied")
APPLIED = {"applied", "reapplied"}

# Locked step order. Playbook is intake only. Step 6 is one step that runs
# review-plan and then tighten-plan. The ready check also records verify.md,
# because that file decides Needs verify.
ORDER = (
    "playbook",
    "review-architecture",
    "tighten-spec",
    "resolve-open-questions",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)
COVERS = {
    "playbook": ("playbook",),
    "review-architecture": ("spec",),
    "tighten-spec": ("spec",),
    "resolve-open-questions": ("spec",),
    "plan-from-spec": ("spec", "plan", "tasks"),
    "review-and-tighten-plan": ("spec", "plan", "tasks"),
    "tasks-ready-to-build": ("spec", "plan", "tasks", "verify"),
}
FILE_OF = {
    "spec": "spec.md",
    "plan": "plan.md",
    "tasks": "tasks.md",
    "verify": "verify.md",
}
LABEL = {
    "spec": "Spec version",
    "plan": "Plan version",
    "tasks": "Tasks version",
    "verify": "Verify version",
}
IMPACT = {
    "spec": "The spec changed since this step, so the step no longer covers the current spec.",
    "plan": "The plan changed since this step, so the step no longer covers the current plan.",
    "tasks": "The tasks changed since this step, so the step no longer covers the current tasks.",
    "verify": "verify.md changed since the ready check, so the check no longer covers it.",
    "playbook": "The playbook file changed since this step. The playbook is intake only.",
}

# Which file change reopens a step (1.123.0). Narrower than COVERS.
# review-architecture is handled in affects_of: once a later step covers the
# spec, a spec change does not send the walk back to the architecture review.
# plan-from-spec writes the plan from the spec, so a hand edit of the plan
# reopens the plan review, not the step that wrote the plan.
AFFECTS = {
    "playbook": ("playbook",),
    "review-architecture": ("spec",),
    "tighten-spec": ("spec",),
    "resolve-open-questions": ("spec",),
    "plan-from-spec": ("spec",),
    "review-and-tighten-plan": ("spec", "plan", "tasks"),
    "tasks-ready-to-build": ("spec", "plan", "tasks", "verify"),
}
STEP_COMMAND = {
    "playbook": "/crav1-tighten-and-plan-ready-to-build",
    "review-architecture": "/crav1-review-architecture",
    "tighten-spec": "/crav1-tighten-spec",
    "resolve-open-questions": "/crav1-resolve-open-questions",
    "plan-from-spec": "/crav1-plan-from-spec",
    "review-and-tighten-plan": "/crav1-review-plan",
    "tasks-ready-to-build": "/crav1-tasks-ready-to-build",
}
DONE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")

# Optional extras the walk can offer. They are not locked steps. Recording
# one when the walk finishes it counts that write as inside the walk.
EXTRAS = (
    "review-security",
    "research",
    "model-data",
    "show-or-ask-open-questions",
    "suggest-tests-for-code",
)
for _extra in EXTRAS:
    COVERS[_extra] = ("spec", "plan", "tasks")
    AFFECTS[_extra] = ()

# Ready-check rows. The command is the skill that owns the fix. can_jump_back
# is false when that skill is outside this walk.
JUMP = {
    "plan-from-spec": "/crav1-plan-from-spec",
    "resolve-open-questions": "/crav1-resolve-open-questions",
    "review-plan": "/crav1-review-plan",
    "tighten-plan": "/crav1-tighten-plan",
}


def version_of(path: Path) -> str:
    if not path.is_file():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def versions(root: Path, playbook: Path | None = None) -> dict:
    out = {key: version_of(root / name) for key, name in FILE_OF.items()}
    if playbook is not None:
        out["playbook"] = version_of(playbook)
    return out


def fail(code: str, message: str, status: int = 1) -> None:
    json.dump({"ok": False, "code": code, "message": message}, sys.stdout)
    sys.stdout.write("\n")
    raise SystemExit(status)


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


def progress_path(root: Path) -> Path:
    return root / PROGRESS_NAME


def parse_progress(text: str) -> dict:
    """Parse the progress file. A line the format does not allow is an error."""
    steps: dict[str, dict] = {}
    current: dict | None = None
    slice_line = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == f"Walk: {WALK}":
            continue
        if line.startswith("Slice: "):
            slice_line = line[len("Slice: "):]
            continue
        if line.startswith("- Step: "):
            step = line[len("- Step: "):]
            if step not in ORDER:
                fail("progress-file", f"unknown step {step}")
            current = {"step": step}
            steps[step] = current
            continue
        if line.startswith("- Extra: "):
            step = line[len("- Extra: "):]
            if step not in EXTRAS:
                fail("progress-file", f"unknown extra {step}")
            current = {"step": step, "extra": True}
            steps[step] = current
            continue
        if current is None:
            fail("progress-file", f"line outside a step: {line}")
        key, _, value = line.partition(": ")
        if not value:
            fail("progress-file", f"line has no value: {line}")
        if key == "Done":
            current["when"] = value
        elif key == "Result":
            if value not in RESULTS:
                fail("progress-file", f"unknown result {value}")
            current["result"] = value
        elif key == "Playbook":
            path, sep, hashed = value.rpartition("@")
            if not sep or not path:
                fail("progress-file", f"playbook line is not path@hash: {line}")
            current["playbook"] = path
            current["playbook_version"] = hashed
        elif key in LABEL.values():
            token = next(name for name, label in LABEL.items() if label == key)
            current[token] = value
        else:
            fail("progress-file", f"unknown line: {line}")
    for step, body in steps.items():
        for need in ("when", "result"):
            if need not in body:
                fail("progress-file", f"step {step} has no {need}")
        for token in COVERS[step]:
            if token == "playbook":
                if "playbook" not in body or "playbook_version" not in body:
                    fail("progress-file", f"step {step} has no playbook line")
            elif token not in body:
                fail("progress-file", f"step {step} has no {LABEL[token]}")
    return {"slice": slice_line, "steps": steps}


def load(root: Path) -> dict:
    path = progress_path(root)
    if not path.is_file():
        return {"slice": None, "steps": {}}
    return parse_progress(path.read_text(encoding="utf-8"))


def render(slice_label: str, steps: dict) -> str:
    lines = ["# Walk progress", "", f"Walk: {WALK}", f"Slice: {slice_label}", ""]
    for step in ORDER:
        body = steps.get(step)
        if not body:
            continue
        lines.append(f"- Step: {step}")
        lines.append(f"  Done: {body['when']}")
        lines.append(f"  Result: {body['result']}")
        if step == "playbook":
            lines.append(f"  Playbook: {body['playbook']}@{body['playbook_version']}")
        else:
            for token in COVERS[step]:
                lines.append(f"  {LABEL[token]}: {body[token]}")
        lines.append("")
    for step in EXTRAS:
        body = steps.get(step)
        if not body:
            continue
        lines.append(f"- Extra: {step}")
        lines.append(f"  Done: {body['when']}")
        lines.append(f"  Result: {body['result']}")
        for token in COVERS[step]:
            lines.append(f"  {LABEL[token]}: {body[token]}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def playbook_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-resolve-open-questions" / "scripts" / "playbook_store.py"
    spec = importlib.util.spec_from_file_location("playbook_store", path)
    if spec is None or spec.loader is None:
        fail("playbook", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def current_tokens(root: Path, step: str, playbook: Path | None) -> dict:
    got = versions(root)
    out = {}
    for token in COVERS[step]:
        if token == "playbook":
            if playbook is None:
                fail("playbook", "the playbook step needs --playbook")
            recorded, hashed = playbook_mod().recorded_playbook(root, playbook)
            out["playbook"] = recorded
            out["playbook_version"] = version_of(hashed)
        else:
            out[token] = got[token]
    return out


def done_stamp(when: str | None) -> str:
    """The script writes Done. A passed --when must already be a full timestamp."""
    if when is None or when == "":
        return datetime.now().astimezone().isoformat(timespec="seconds")
    if not DONE_RE.fullmatch(when):
        fail(
            "when",
            "Done is a full timestamp YYYY-MM-DDTHH:MM:SS+HH:MM, "
            "for example 2026-11-09T10:19:09+01:00. Omit --when and the script stamps it.",
        )
    return when


def record(args: argparse.Namespace) -> None:
    if args.step not in COVERS:
        fail("step", f"unknown step {args.step}")
    if args.result not in RESULTS:
        fail("result", f"result must be one of {', '.join(RESULTS)}")
    if not args.yes:
        fail("needs-yes", "record writes the progress file only with --yes", status=2)
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    body = {"when": done_stamp(args.when), "result": args.result}
    body.update(current_tokens(root, args.step, Path(args.playbook) if args.playbook else None))
    # A write inside the walk updates versions already recorded. Done and
    # Result stay. An extra the walk just finished updates every locked
    # step, because the extra is not itself a place in the locked order.
    if args.step in EXTRAS:
        restamp_recorded(root, data["steps"], set(COVERS[args.step]))
    else:
        restamp_earlier(root, data["steps"], args.step)
    data["steps"][args.step] = body
    label = args.slice or data["slice"] or f"docs/specs/{root.name}/"
    if not str(label).endswith("/"):
        label = f"{label}/"
    text = render(label, data["steps"])
    progress_path(root).write_text(text, encoding="utf-8")
    emit({"ok": True, "wrote": PROGRESS_NAME, "step": args.step, "result": args.result, "when": body["when"]})


def hash_drift(root: Path, step: str, body: dict) -> list[str]:
    """Covered files whose bytes differ from the version this step recorded."""
    changed = []
    if step == "playbook":
        path = Path(body["playbook"])
        if not path.is_file():
            # The recorded path may be repo-relative. Also try it under the root's parents.
            alt = find_playbook(root, body["playbook"])
            path = alt if alt is not None else path
        now = version_of(path)
        if now != body["playbook_version"]:
            changed.append("playbook")
        return changed
    now = versions(root)
    for token in COVERS[step]:
        if now[token] != body[token]:
            changed.append(token)
    return changed


def affects_of(step: str, steps: dict) -> tuple[str, ...]:
    """Files that reopen this step. Later spec steps supersede the architecture review."""
    if step == "review-architecture":
        own = ORDER.index(step)
        for later in ORDER[own + 1:]:
            if later in steps and "spec" in AFFECTS[later]:
                return ()
    return AFFECTS[step]


def affected_drift(root: Path, step: str, body: dict, steps: dict) -> list[str]:
    """Drift that reopens the step. A file it merely recorded does not."""
    affects = set(affects_of(step, steps))
    return [token for token in hash_drift(root, step, body) if token in affects]


def _restamp_body(body: dict, name: str, now: dict, tokens: set[str]) -> None:
    for token in COVERS[name]:
        if token == "playbook" or token not in tokens:
            continue
        body[token] = now[token]


def restamp_earlier(root: Path, steps: dict, step: str) -> None:
    """Bring earlier locked steps' covered versions up to the current files.

    Done and Result stay. Tokens this step does not cover stay, and the
    playbook line stays. The playbook is intake only. Recorded extras keep
    the version they saw.
    """
    now = versions(root)
    covered = set(COVERS[step])
    for earlier in ORDER[:ORDER.index(step)]:
        body = steps.get(earlier)
        if not body:
            continue
        _restamp_body(body, earlier, now, covered)


def restamp_recorded(root: Path, steps: dict, tokens: set[str]) -> None:
    """An extra finished inside the walk. Update locked steps already recorded.

    Done and Result stay. Extras keep the version they saw.
    """
    now = versions(root)
    for name in ORDER:
        body = steps.get(name)
        if not body:
            continue
        _restamp_body(body, name, now, tokens)


def refresh_versions(root: Path, step: str, body: dict) -> None:
    """Set one step's recorded versions to the files on disk. Done stays."""
    if step == "playbook":
        path = Path(body["playbook"])
        if not path.is_file():
            alt = find_playbook(root, body["playbook"])
            path = alt if alt is not None else path
        body["playbook_version"] = version_of(path)
        return
    now = versions(root)
    for token in COVERS[step]:
        body[token] = now[token]


def write_progress(root: Path, data: dict, slice_label: str | None = None) -> None:
    label = slice_label or data["slice"] or f"docs/specs/{root.name}/"
    if not str(label).endswith("/"):
        label = f"{label}/"
    progress_path(root).write_text(render(label, data["steps"]), encoding="utf-8")


def find_playbook(root: Path, recorded: str) -> Path | None:
    direct = Path(recorded)
    if direct.is_file():
        return direct
    for base in [root, *root.parents]:
        candidate = base / recorded
        if candidate.is_file():
            return candidate
        # A repo-relative docs/playbooks path is found from the repo, which is
        # the parent of docs/, not from inside the spec folder (1.120.0).
        if base.name == "docs":
            repo_candidate = base.parent / recorded
            if repo_candidate.is_file():
                return repo_candidate
            break
        if str(base) == "/":
            break
    return None


def resume(args: argparse.Namespace) -> None:
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    rows = []
    continue_from = None
    for step in ORDER:
        body = data["steps"].get(step)
        if body is None and step == "playbook" and args.no_playbook:
            row = {"id": step, "status": "skipped", "result": "skipped"}
            rows.append(row)
            continue
        if body is None:
            status = "not-started"
            row = {"id": step, "status": status}
        else:
            drift = affected_drift(root, step, body, data["steps"])
            if drift:
                status = "reopen"
                row = {
                    "id": step,
                    "status": status,
                    "result": body["result"],
                    "changed": drift,
                    "impact": " ".join(IMPACT[token] for token in drift),
                }
            else:
                status = "keep"
                row = {"id": step, "status": status, "result": body["result"]}
        if continue_from is None and status in ("not-started", "reopen"):
            continue_from = step
        rows.append(row)
    for step in EXTRAS:
        body = data["steps"].get(step)
        if not body:
            continue
        rows.append({
            "id": step,
            "status": "keep",
            "result": body["result"],
            "extra": True,
        })
    book = data["steps"].get("playbook")
    emit({
        "ok": True,
        "source_of_truth": "spec.md, plan.md, and tasks.md",
        "progress_file": PROGRESS_NAME,
        "steps": rows,
        "continue_from": continue_from,
        "playbook": book.get("playbook") if book else None,
    })


def resolve_playbook(root: Path, given: str) -> Path:
    path = Path(given)
    if path.is_file():
        return path
    found = find_playbook(root, given)
    return found if found is not None else path


def same_playbook_path(root: Path, recorded: str, given: str, resolved: Path) -> bool:
    if recorded == given:
        return True
    if resolved.is_file():
        try:
            recorded_rel, _hashed = playbook_mod().recorded_playbook(root, resolved)
        except SystemExit:
            raise
        except Exception:
            recorded_rel = ""
        if recorded_rel == recorded:
            return True
        found = find_playbook(root, recorded)
        try:
            if found is not None and found.resolve() == resolved.resolve():
                return True
        except OSError:
            return False
    try:
        return Path(recorded).resolve() == Path(given).resolve()
    except OSError:
        return False


def playbook_status(args: argparse.Namespace) -> None:
    root = Path(args.root)
    playbook = resolve_playbook(root, args.playbook)
    data = load(root) if root.is_dir() else {"steps": {}}
    body = data["steps"].get("playbook")
    now = version_of(playbook)
    if body is None:
        emit({
            "ok": True,
            "status": "not-recorded",
            "already_applied": False,
            "offer": "show-changes",
            "note": "No progress line for this playbook. Use the apply compare. Do not treat it as already applied.",
        })
        return
    same_path = same_playbook_path(root, body["playbook"], args.playbook, playbook)
    same_hash = body.get("playbook_version") == now and now != "missing"
    if same_path and same_hash and body["result"] in APPLIED:
        emit({
            "ok": True,
            "status": "already-applied",
            "already_applied": True,
            "offer": "skip-or-reapply",
            "result": body["result"],
        })
        return
    if same_path and same_hash and body["result"] == "skipped":
        emit({
            "ok": True,
            "status": "already-skipped",
            "already_applied": False,
            "offer": "skip-or-apply",
            "result": body["result"],
        })
        return
    emit({
        "ok": True,
        "status": "changed" if same_path else "different-file",
        "already_applied": False,
        "offer": "show-changes",
        "result": body.get("result"),
    })


def classify(row: dict) -> dict | None:
    bucket = str(row.get("bucket") or "")
    reason = str(row.get("reason") or "")
    warning = str(row.get("warning") or "")
    text = f"{reason} {warning}".lower()
    task = row.get("task")
    if bucket == "needs-verify" or "needs verify" in text or "no verify.md" in text:
        return {
            "task": task,
            "bucket": "needs-verify",
            "step": None,
            "command": "/crav1-verify-build-against-spec",
            "can_jump_back": False,
            "outside_walk": True,
            "kind": "blocker",
            "why": "Needs verify belongs to /crav1-verify-build-against-spec, which is outside this walk. Do not start it. Do not report ready.",
        }
    if "plan review unknown" in text:
        return _hit(task, "assumption", "review-plan", "The ready check assumed a plan review. Run /crav1-review-plan, then /crav1-tighten-plan.")
    if "p# open" in text or "open p#" in text:
        return _hit(task, "assumption", "tighten-plan", "The plan review still has open P# items. Run /crav1-tighten-plan.")
    if bucket in ("ready", "done") and not warning:
        return None
    if bucket == "ready" and warning:
        return _hit(task, "assumption", None, f"Unrecognized ready warning: {warning}")
    if "no plan" in text:
        return _hit(task, "blocker", "plan-from-spec", "There is no plan.md. Run /crav1-plan-from-spec.")
    if "open question" in text:
        return _hit(task, "blocker", "resolve-open-questions", "An open question blocks the work. Run /crav1-resolve-open-questions.")
    if "plan risk" in text:
        return _hit(task, "blocker", "tighten-plan", "A plan risk blocks the work. Run /crav1-review-plan, then /crav1-tighten-plan.")
    if "cycle" in text or "after names no task" in text or "waits on" in text:
        return _hit(task, "blocker", "tighten-plan", "A task dependency is blocked. Fix the (after:) marks with /crav1-tighten-plan.")
    return _hit(task, "blocker", None, f"Unrecognized blocker: {reason or bucket}")


def _hit(task, kind: str, command_key: str | None, why: str) -> dict:
    if command_key is None:
        return {
            "task": task,
            "bucket": kind,
            "step": None,
            "command": None,
            "can_jump_back": False,
            "outside_walk": False,
            "kind": kind,
            "why": why + " The walk does not invent a step for this.",
        }
    step = "review-and-tighten-plan" if command_key in ("review-plan", "tighten-plan") else command_key
    return {
        "task": task,
        "bucket": kind,
        "step": step,
        "command": JUMP[command_key],
        "can_jump_back": True,
        "outside_walk": False,
        "kind": kind,
        "why": why,
    }


def cover(args: argparse.Namespace) -> None:
    """Count the current spec, plan, tasks, and verify as part of the walk.

    Optional. For a write made outside this walk. An extra the walk itself
    just ran is recorded with `- Extra:` instead. The playbook line stays.
    Cover does not add an extra line.
    """
    if not args.yes:
        fail("needs-yes", "cover writes the progress file only with --yes", status=2)
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    if not data["steps"]:
        fail("progress-file", "no walk progress to cover")
    now = versions(root)
    covered = []
    for step, body in data["steps"].items():
        if step == "playbook":
            continue
        for token in COVERS[step]:
            body[token] = now[token]
        covered.append(step)
    write_progress(root, data)
    emit({"ok": True, "wrote": PROGRESS_NAME, "covered": covered})


def clear(args: argparse.Namespace) -> None:
    """Refresh one reopened step after a one-line 'nothing new' confirmation.

    Done and Result stay. Other steps stay as they are.
    """
    if args.step not in COVERS:
        fail("step", f"unknown step {args.step}")
    if not args.yes:
        fail("needs-yes", "clear writes the progress file only with --yes", status=2)
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    body = data["steps"].get(args.step)
    if body is None:
        fail("step", f"{args.step} is not recorded")
    drift = affected_drift(root, args.step, body, data["steps"])
    if not drift:
        fail("not-reopened", f"{args.step} is not reopened")
    refresh_versions(root, args.step, body)
    write_progress(root, data)
    emit({
        "ok": True,
        "wrote": PROGRESS_NAME,
        "cleared": args.step,
        "confirmation": "nothing new",
        "changed": drift,
    })


def reopen_hit(step: str, drift: list[str]) -> dict:
    why = " ".join(IMPACT[token] for token in drift)
    why += " Jump back and rerun this step, or clear it with nothing new."
    return {
        "task": None,
        "bucket": "reopened",
        "step": step,
        "command": STEP_COMMAND[step],
        "can_jump_back": True,
        "outside_walk": False,
        "kind": "blocker",
        "clear": "nothing new",
        "changed": drift,
        "why": why,
    }


def reopened_hits(root: Path) -> list[dict]:
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    hits = []
    for step in ORDER:
        body = data["steps"].get(step)
        if not body:
            continue
        drift = affected_drift(root, step, body, data["steps"])
        if drift:
            hits.append(reopen_hit(step, drift))
    return hits


def readiness(args: argparse.Namespace) -> None:
    try:
        payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("readiness", f"cannot read rows: {exc}")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        fail("readiness", "rows must be a list")
    hits = []
    for row in rows:
        if not isinstance(row, dict):
            fail("readiness", "each row must be an object")
        hit = classify(row)
        if hit:
            hits.append(hit)
    reopened = reopened_hits(Path(args.root)) if args.root else []
    hits.extend(reopened)
    blockers = [h for h in hits if h["kind"] == "blocker" and not h["outside_walk"]]
    outside = [h for h in hits if h["outside_walk"]]
    assumptions = [h for h in hits if h["kind"] == "assumption"]
    unmapped = [h for h in hits if h["command"] is None]
    ready = not hits
    emit({
        "ok": True,
        "ready": ready,
        "start_build": False,
        "blockers": blockers,
        "outside_walk": outside,
        "assumptions": assumptions,
        "unmapped": unmapped,
        "jump_back": [h for h in hits if h["can_jump_back"]],
        "reopened": reopened,
    })


def cmd_version(args: argparse.Namespace) -> None:
    root = Path(args.root)
    emit({"ok": True, "versions": versions(root, Path(args.playbook) if args.playbook else None)})


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Guided walk progress file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("version")
    v.add_argument("--root", required=True)
    v.add_argument("--playbook")
    v.set_defaults(func=cmd_version)

    r = sub.add_parser("record")
    r.add_argument("--root", required=True)
    r.add_argument("--slice")
    r.add_argument("--step", required=True)
    r.add_argument("--result", required=True)
    r.add_argument("--when", help="Full timestamp. Omit to let the script stamp Done.")
    r.add_argument("--playbook")
    r.add_argument("--yes", action="store_true")
    r.set_defaults(func=record)

    c = sub.add_parser("cover")
    c.add_argument("--root", required=True)
    c.add_argument("--yes", action="store_true")
    c.set_defaults(func=cover)

    k = sub.add_parser("clear")
    k.add_argument("--root", required=True)
    k.add_argument("--step", required=True)
    k.add_argument("--yes", action="store_true")
    k.set_defaults(func=clear)

    s = sub.add_parser("resume")
    s.add_argument("--root", required=True)
    s.add_argument("--no-playbook", action="store_true")
    s.set_defaults(func=resume)

    p = sub.add_parser("playbook-status")
    p.add_argument("--root", required=True)
    p.add_argument("--playbook", required=True)
    p.set_defaults(func=playbook_status)

    d = sub.add_parser("readiness")
    d.add_argument("--json", required=True)
    d.add_argument("--root", help="Spec folder. Reopened walk steps block ready.")
    d.set_defaults(func=readiness)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
