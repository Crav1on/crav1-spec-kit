#!/usr/bin/env python3
"""Progress file for /crav1-tighten-and-plan-ready-to-build (kit 1.127.0).

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
  walk_progress.py readiness --root <spec-folder>
  walk_progress.py readiness --json <file> [--root <spec-folder>]
  walk_progress.py unlinked --root <spec-folder>
  walk_progress.py ack-stamps --root <spec-folder> --yes

readiness --root builds the rows from task_order.py and question_blocks.py
and adds the Reviewed warnings. Do not hand-build that JSON.

record, cover, and clear without --yes write nothing and exit 2.
record takes one step per call and stamps Done itself. --when, when passed,
must be a full timestamp. Do not pass --when from the walk.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime


def _utf8_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()

sys.dont_write_bytecode = True  # before any sibling import; no __pycache__ in the project (1.121.1)

from pathlib import Path

WALK = "tighten-and-plan-ready-to-build"
PROGRESS_NAME = "walk-progress.md"
RESULTS = ("done", "nothing-to-do", "skipped", "applied", "reapplied", "ready", "not-ready")
# The ready check records ready or not-ready. An older Result: done still reads.
READY_RESULTS = ("ready", "not-ready", "nothing-to-do")
NOT_NAMED = "not named yet"
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


ACK_LINE = re.compile(
    r"^Acknowledged stamp: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}) \(([^)]+)\)$"
)


def _parse_ack(line: str) -> dict:
    match = ACK_LINE.fullmatch(line)
    if not match:
        fail("progress-file", f"ack line is not a shared stamp: {line}")
    names = [part.strip() for part in match.group(2).split(",") if part.strip()]
    known = set(ORDER) | set(EXTRAS)
    if len(names) < 2 or any(name not in known for name in names):
        fail("progress-file", f"ack line needs the steps that share the stamp: {line}")
    return {"when": match.group(1), "steps": names}


def _ack_line(when: str, names: list[str]) -> str:
    return f"Acknowledged stamp: {when} ({', '.join(names)})"


def parse_progress(text: str) -> dict:
    """Parse the progress file. A line the format does not allow is an error."""
    steps: dict[str, dict] = {}
    acks: list[dict] = []
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
        if line.startswith("Acknowledged stamp: "):
            acks.append(_parse_ack(line))
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
    return {"slice": slice_line, "steps": steps, "acks": acks}


def load(root: Path) -> dict:
    path = progress_path(root)
    if not path.is_file():
        return {"slice": None, "steps": {}, "acks": []}
    data = parse_progress(path.read_text(encoding="utf-8"))
    data.setdefault("acks", [])
    return data


def render(slice_label: str, steps: dict, acks: list | None = None) -> str:
    lines = ["# Walk progress", "", f"Walk: {WALK}", f"Slice: {slice_label}", ""]
    for ack in acks or []:
        lines.append(_ack_line(ack["when"], ack["steps"]))
    if acks:
        lines.append("")
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


def _one_step(values) -> str:
    """One step id. A comma, 'and', or a repeated --step is refused."""
    if isinstance(values, str):
        values = [values]
    parts: list[str] = []
    for value in values or []:
        parts.extend(part for part in re.split(r"\s*,\s*|\s+\band\b\s+", value) if part)
    if len(parts) != 1:
        fail(
            "one-step",
            "record takes one step per call. Record the step that just finished, "
            "then record the next step in its own call.",
        )
    return parts[0]


def record(args: argparse.Namespace) -> None:
    step = _one_step(args.step)
    if step not in COVERS:
        fail("step", f"unknown step {step}")
    if args.result not in RESULTS:
        fail("result", f"result must be one of {', '.join(RESULTS)}")
    if step == "tasks-ready-to-build" and args.result not in READY_RESULTS:
        fail(
            "result",
            "tasks-ready-to-build records Result: ready or Result: not-ready, "
            "from the readiness output. An older Result: done still reads.",
        )
    if step != "tasks-ready-to-build" and args.result in ("ready", "not-ready"):
        fail("result", "ready and not-ready are only for tasks-ready-to-build")
    if not args.yes:
        fail(
            "needs-yes",
            "record writes the progress file only with --yes, after the line was shown and confirmed",
            status=2,
        )
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    previous = data["steps"].get(step)
    result = args.result
    kept_done = False
    # A reopened step with nothing new is clear, not a fresh nothing-to-do.
    # nothing-to-do does not replace an earlier done Result.
    if previous and result == "nothing-to-do":
        drift = affected_drift(root, step, previous, data["steps"])
        if drift:
            fail(
                "use-clear",
                f"{step} is reopened. Run clear --step {step} --yes when nothing new. "
                "Do not record nothing-to-do.",
            )
        if previous.get("result") == "done":
            result = "done"
            kept_done = True
    body = {"when": done_stamp(args.when), "result": result}
    body.update(current_tokens(root, step, Path(args.playbook) if args.playbook else None))
    # A write inside the walk updates versions already recorded. Done and
    # Result stay. An extra the walk just finished updates every locked
    # step, because the extra is not itself a place in the locked order.
    if step in EXTRAS:
        restamp_recorded(root, data["steps"], set(COVERS[step]))
    else:
        restamp_earlier(root, data["steps"], step)
    data["steps"][step] = body
    label = args.slice or data["slice"] or f"docs/specs/{root.name}/"
    if not str(label).endswith("/"):
        label = f"{label}/"
    text = render(label, data["steps"], data.get("acks"))
    progress_path(root).write_text(text, encoding="utf-8")
    payload = {"ok": True, "wrote": PROGRESS_NAME, "step": step, "result": result, "when": body["when"]}
    if kept_done:
        payload["kept_done"] = True
    emit(payload)


def _shared_groups(steps: dict) -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = {}
    for step in list(ORDER) + list(EXTRAS):
        body = steps.get(step)
        if not body or "when" not in body:
            continue
        grouped.setdefault(body["when"], []).append(step)
    return [(when, names) for when, names in grouped.items() if len(names) >= 2]


def _ack_covers(acks: list, when: str, names: list[str]) -> bool:
    wanted = set(names)
    for ack in acks:
        if ack.get("when") == when and wanted <= set(ack.get("steps") or []):
            return True
    return False


def done_stamp_warning(steps: dict, acks: list | None = None) -> str | None:
    """Set when two or more steps share a Done stamp that is not acknowledged."""
    pending = [
        (when, names)
        for when, names in _shared_groups(steps)
        if not _ack_covers(acks or [], when, names)
    ]
    if not pending:
        return None
    bits = [f"{', '.join(names)} share Done {when}" for when, names in pending]
    return (
        "Record each step when it finishes, one record per call. "
        + "; ".join(bits)
        + ". Acknowledge that shared stamp once with "
        "walk_progress.py ack-stamps --root <spec-folder> --yes."
    )


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
    progress_path(root).write_text(render(label, data["steps"], data.get("acks")), encoding="utf-8")


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
        "done_stamp_warning": done_stamp_warning(data["steps"], data.get("acks")),
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
            "note": (
                "Ask once: skip (Recommended) or reapply, even when the file has not changed. "
                "Do not move on without that question."
            ),
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


def blocks_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "question_blocks.py"
    spec = importlib.util.spec_from_file_location("question_blocks", path)
    if spec is None or spec.loader is None:
        fail("blocks", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unlinked(args: argparse.Namespace) -> None:
    """Kept-open questions that still have no Blocks line. Writes nothing."""
    root = Path(args.root)
    spec = root / "spec.md"
    if not spec.is_file():
        fail("spec", f"no spec.md in {root}")
    questions = blocks_mod().kept_open(spec.read_text(encoding="utf-8"))
    missing = [{"text": q["text"]} for q in questions if q["mark"] == "missing"]
    emit({"ok": True, "count": len(missing), "questions": missing})


def classify(row: dict, resolve_kept: bool = False) -> dict | None:
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
    # Blocks: none blocks no task, and that line wins over Risk wording (1.125.0).
    if "blocks: none" in text or "blocks no task" in text or "blocks no current" in text:
        return None
    if "plan review unknown" in text:
        return _hit(task, "assumption", "review-plan", "The ready check assumed a plan review. Run /crav1-review-plan, then /crav1-tighten-plan.")
    if "p# open" in text or "open p#" in text:
        return _hit(task, "assumption", "tighten-plan", "The plan review still has open P# items. Run /crav1-tighten-plan.")
    if bucket == "waits-in-order":
        return None
    if bucket in ("ready", "done") and not warning:
        return None
    if bucket == "ready" and warning:
        return _hit(task, "assumption", None, f"Unrecognized ready warning: {warning}")
    if "no tasks" in text:
        return _hit(task, "blocker", "plan-from-spec", "There is no tasks.md. Run /crav1-plan-from-spec.")
    if "no plan" in text:
        return _hit(task, "blocker", "plan-from-spec", "There is no plan.md. Run /crav1-plan-from-spec.")
    if "open question" in text:
        # Already settled as kept-open at this spec version: waiting, not a jump back.
        if resolve_kept:
            return _waiting(row)
        return _hit(task, "blocker", "resolve-open-questions", "An open question blocks the work. Run /crav1-resolve-open-questions.")
    if "plan risk" in text:
        return _hit(task, "blocker", "tighten-plan", "A plan risk blocks the work. Run /crav1-review-plan, then /crav1-tighten-plan.")
    # A cycle, or an after: that names no task, is a blocker. Waiting on a
    # real earlier task is the order, not a blocker (1.126.0).
    if "cycle" in text or "names no task" in text:
        return _hit(task, "blocker", "tighten-plan", "A task dependency is blocked. Fix the (after:) marks with /crav1-tighten-plan.")
    if re.search(r"waits on\s+t\d+", text):
        return None
    return _hit(task, "blocker", None, f"Unrecognized blocker: {reason or bucket}")


def _waiting(row: dict) -> dict:
    who = row.get("who")
    if isinstance(who, str):
        who = who.strip() or None
    else:
        who = None
    if not who:
        who = NOT_NAMED
    return {
        "task": row.get("task"),
        "bucket": "waiting",
        "step": "resolve-open-questions",
        "command": None,
        "can_jump_back": False,
        "outside_walk": False,
        "kind": "waiting",
        "who": who,
        "asked": bool(row.get("asked")),
        "why": (
            "Resolve-open-questions already covers this spec. "
            "The question waits on someone else. Do not jump back."
        ),
    }


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


def order_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "task_order.py"
    spec = importlib.util.spec_from_file_location("task_order_rows", path)
    if spec is None or spec.loader is None:
        fail("order", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REVIEWED_RE = re.compile(r"^Reviewed:\s*.*?P# open:\s*(\d+)", re.M)


def reviewed_warning(plan_text: str) -> str | None:
    if not plan_text.strip():
        return "plan review unknown (inferred), run /crav1-review-plan"
    match = REVIEWED_RE.search(plan_text)
    if not match:
        return "plan review unknown (inferred), run /crav1-review-plan"
    count = int(match.group(1))
    if count > 0:
        return f"plan review has {count} open P# (recorded), see /crav1-tighten-plan"
    return None


def _verify_for(text: str | None, tid: str) -> tuple[str, str | None]:
    if not text:
        return "needs-verify", "no verify.md row"
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] != tid or len(cells) < 3:
            continue
        status = cells[2].lower()
        if "unverified" in status or "claimed" in status:
            return "needs-verify", "claimed done, unverified"
        if "failed" in status:
            return "needs-verify", "verify failed"
        if "verified" in status:
            return "done", None
        return "needs-verify", "no verify.md row"
    for line in text.splitlines():
        if not re.search(rf"\b{re.escape(tid)}\b", line):
            continue
        low = line.lower()
        if "unverified" in low or "claimed done" in low:
            return "needs-verify", "claimed done, unverified"
        if "verify failed" in low:
            return "needs-verify", "verify failed"
        if "implemented, verified" in low:
            return "done", None
    return "needs-verify", "no verify.md row"


def _oq_row(tid: str, question: dict, whole: bool) -> dict:
    sentence = str(question.get("text") or "").strip()
    if whole:
        reason = f'open question "{sentence}" blocks the whole slice (inferred)'
    else:
        reason = f'open question "{sentence}" (recorded)'
    row = {
        "bucket": "blocked",
        "task": tid,
        "reason": reason,
        "asked": bool(question.get("asked")),
    }
    if question.get("who"):
        row["who"] = question["who"]
    return row


def _question_row(blocks: dict, tid: str) -> dict | None:
    slice_q = None
    for question in blocks.get("questions") or []:
        if question.get("mark") == "tasks" and tid in (question.get("tasks") or []):
            return _oq_row(tid, question, whole=False)
        if question.get("blocks_slice") and slice_q is None:
            slice_q = question
    if slice_q is not None:
        return _oq_row(tid, slice_q, whole=True)
    for risk in blocks.get("risks") or []:
        if not risk.get("blocks_slice"):
            continue
        short = str(risk.get("text") or "").strip()
        if short.startswith("- "):
            short = short[2:].strip()
        return {
            "bucket": "blocked",
            "task": tid,
            "reason": f'plan Risk "{short}" blocks the whole slice (inferred)',
        }
    return None


def build_rows(root: Path) -> list[dict]:
    """Ready-check rows from the spec folder. The walk does not hand-build these."""
    tasks_path = root / "tasks.md"
    plan_path = root / "plan.md"
    spec_path = root / "spec.md"
    verify_path = root / "verify.md"
    if not tasks_path.is_file():
        return [{"bucket": "blocked", "task": None, "reason": "no tasks.md"}]
    order = order_mod()
    tasks = order.parse(tasks_path.read_text(encoding="utf-8"))
    if not tasks:
        return [{"bucket": "blocked", "task": None, "reason": "no tasks.md"}]
    analysed = order.analyse(tasks)
    by_reason = {row["id"]: row for row in analysed["rows"]}
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    blocks = blocks_mod().analyse(spec_text, plan_text)
    verify_text = verify_path.read_text(encoding="utf-8") if verify_path.is_file() else None
    warning = reviewed_warning(plan_text) if plan_path.is_file() else None
    rows = []
    for task in tasks:
        tid = f"T{task['id']}"
        if task["done"]:
            bucket, reason = _verify_for(verify_text, tid)
            row = {"bucket": bucket, "task": tid}
            if reason:
                row["reason"] = reason
            rows.append(row)
            continue
        if not plan_path.is_file():
            rows.append({"bucket": "blocked", "task": tid, "reason": "no plan.md (recorded)"})
            continue
        question = _question_row(blocks, tid)
        if question:
            rows.append(question)
            continue
        dep = by_reason.get(task["id"])
        if dep and dep.get("reason"):
            reason = dep["reason"]
            # A wait on a real earlier task is the order. A cycle, or an
            # after: that names no task, stays blocked.
            if re.search(r"waits on\s+T\d+", reason) and "cycle" not in reason.lower() and "names no task" not in reason.lower():
                bucket = "waits-in-order"
            else:
                bucket = "blocked"
            rows.append({"bucket": bucket, "task": tid, "reason": reason})
            continue
        row = {"bucket": "ready", "task": tid}
        if warning:
            row["warning"] = warning
        rows.append(row)
    return rows


def resolve_is_keep(root: Path) -> bool:
    """True when resolve-open-questions is recorded against the current spec."""
    if not root.is_dir():
        return False
    data = load(root)
    body = data["steps"].get("resolve-open-questions")
    if not body:
        return False
    return not affected_drift(root, "resolve-open-questions", body, data["steps"])


def _slug(root: Path) -> str:
    data = load(root) if root.is_dir() else {"slice": None}
    parts = [part for part in str(data.get("slice") or "").strip("/").split("/") if part]
    if parts:
        return parts[-1]
    return root.name


def _waiting_lines(waiting: list[dict], slug: str) -> tuple[str | None, str | None]:
    if not waiting:
        return None, None
    tasks: list[str] = []
    whos: list[str] = []
    unnamed = 0
    for hit in waiting:
        task = hit.get("task")
        if task and task not in tasks:
            tasks.append(task)
        who = hit.get("who")
        if not who or who == NOT_NAMED:
            unnamed += 1
        elif who not in whos:
            whos.append(who)
    count = len(tasks) or len(waiting)
    if whos and unnamed:
        tail = f" ({', '.join(whos)}; {unnamed} not named yet)"
    elif whos:
        tail = f" ({', '.join(whos)})"
    elif unnamed:
        tail = f" ({unnamed} not named yet)"
    else:
        tail = ""
    line = f"Waiting: {count} tasks wait on open questions{tail}."
    if all(hit.get("asked") for hit in waiting):
        nxt = (
            f"/crav1-tighten-and-plan-ready-to-build {slug}, "
            "because the walk resumes when the answers arrive."
        )
    else:
        nxt = (
            f"/crav1-show-or-ask-open-questions {slug}, "
            "because the questions are not asked yet."
        )
    return line, nxt


def readiness(args: argparse.Namespace) -> None:
    root = Path(args.root) if args.root else None
    built = False
    if args.json:
        try:
            payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail("readiness", f"cannot read rows: {exc}")
        rows = payload.get("rows")
        if not isinstance(rows, list):
            fail("readiness", "rows must be a list")
    elif root is not None:
        if not root.is_dir():
            fail("root", f"not a folder: {root}")
        rows = build_rows(root)
        built = True
    else:
        fail("readiness", "pass --root <spec-folder>, or --json <rows file>")
    for row in rows:
        if not isinstance(row, dict):
            fail("readiness", "each row must be an object")
    resolve_kept = resolve_is_keep(root) if root is not None else False
    hits = []
    for row in rows:
        hit = classify(row, resolve_kept=resolve_kept)
        if hit:
            hits.append(hit)
            if hit["kind"] == "waiting":
                row["bucket"] = "waiting"
    reopened = reopened_hits(root) if root is not None else []
    hits.extend(reopened)
    blockers = [h for h in hits if h["kind"] == "blocker" and not h["outside_walk"]]
    outside = [h for h in hits if h["outside_walk"]]
    assumptions = [h for h in hits if h["kind"] == "assumption"]
    waiting = [h for h in hits if h["kind"] == "waiting"]
    unmapped = [h for h in hits if h["command"] is None and h["kind"] != "waiting"]
    jump = [h for h in hits if h["can_jump_back"]]
    ready = not hits
    slug = _slug(root) if root is not None else ""
    waiting_line, waiting_next = _waiting_lines(waiting, slug)
    out = {
        "ok": True,
        "ready": ready,
        "start_build": False,
        "blockers": blockers,
        "outside_walk": outside,
        "assumptions": assumptions,
        "unmapped": unmapped,
        "waiting": waiting,
        "waiting_line": waiting_line,
        "waiting_next": waiting_next,
        "recommend_jump": bool(jump),
        "jump_back": jump,
        "reopened": reopened,
    }
    if built:
        out["rows"] = rows
    if root is not None and root.is_dir():
        loaded = load(root)
        out["done_stamp_warning"] = done_stamp_warning(loaded["steps"], loaded.get("acks"))
    emit(out)


def ack_stamps(args: argparse.Namespace) -> None:
    """Record that a shared Done stamp was seen, so the warning stops for it.

    A later stamp that two steps still share warns again. Show the line and
    pass --yes only after that yes. Without --yes this writes nothing.
    """
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    if not data["steps"]:
        fail("progress-file", "no walk progress to acknowledge")
    pending = [
        (when, names)
        for when, names in _shared_groups(data["steps"])
        if not _ack_covers(data.get("acks") or [], when, names)
    ]
    if not pending:
        emit({"ok": True, "wrote": None, "lines": [], "message": "no shared stamp to acknowledge"})
        return
    lines = [_ack_line(when, names) for when, names in pending]
    if not args.yes:
        emit({
            "ok": False,
            "code": "needs-yes",
            "message": (
                "ack-stamps writes the progress file only with --yes, "
                "after the line was shown and confirmed"
            ),
            "lines": lines,
        })
        raise SystemExit(2)
    acks = list(data.get("acks") or [])
    for when, names in pending:
        acks.append({"when": when, "steps": list(names)})
    data["acks"] = acks
    write_progress(root, data)
    emit({"ok": True, "wrote": PROGRESS_NAME, "lines": lines})


def cmd_version(args: argparse.Namespace) -> None:
    root = Path(args.root)
    emit({"ok": True, "versions": versions(root, Path(args.playbook) if args.playbook else None)})


def main(argv: list[str] | None = None) -> None:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description="Guided walk progress file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("version")
    v.add_argument("--root", required=True)
    v.add_argument("--playbook")
    v.set_defaults(func=cmd_version)

    r = sub.add_parser("record")
    r.add_argument("--root", required=True)
    r.add_argument("--slice")
    r.add_argument("--step", action="append", required=True, help="One step id. More than one is refused.")
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
    d.add_argument("--json", help="Rows file. Omit with --root to build the rows from the spec folder.")
    d.add_argument("--root", help="Spec folder. Builds the rows when --json is omitted. Reopened steps block ready.")
    d.set_defaults(func=readiness)

    u = sub.add_parser("unlinked")
    u.add_argument("--root", required=True)
    u.set_defaults(func=unlinked)

    a = sub.add_parser("ack-stamps")
    a.add_argument("--root", required=True)
    a.add_argument("--yes", action="store_true")
    a.set_defaults(func=ack_stamps)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
