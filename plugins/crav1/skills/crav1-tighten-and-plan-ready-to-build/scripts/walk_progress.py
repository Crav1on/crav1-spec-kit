#!/usr/bin/env python3
"""Progress file for /crav1-tighten-and-plan-ready-to-build (kit 1.135.0).

The spec, plan, and tasks stay the source of truth. This script only tracks
where the guided walk is, which version of each file a step covered, and which
ready-check rows belong to which step. It does not edit those files, does not
apply a playbook, and does not start a build. It never writes verify.md.
build-map.md stays with /crav1-tasks-ready-to-build.

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
  walk_progress.py spec-finding --root <spec-folder> --id P2 --text "<finding>"
      [--tag spec|plan] [--choice tighten-spec|open-point] [--yes]

readiness --root builds the rows from task_order.py and question_blocks.py
and adds the Reviewed warnings. It also compares tasks.md with verify.md.
Do not hand-build that JSON. spec-finding offers one jump back for a spec
finding, or records an open point when that finding already jumped. A plan
tag writes nothing.

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
RESULTS = ("done", "nothing-to-do", "skipped", "applied", "reapplied", "ready", "ready-partial", "not-ready")
# The ready check records ready, ready-partial, or not-ready. An older Result: done still reads.
READY_RESULTS = ("ready", "ready-partial", "not-ready", "nothing-to-do")
READY_ONLY = ("ready", "ready-partial", "not-ready")
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

# One jump back from a spec-tagged plan finding (1.135.0). The path is the
# sibling file the walk opens. A second sighting of the same finding is an
# open point. This script does not edit spec.md and does not write verify.md.
TIGHTEN_SPEC_PATH = "../crav1-tighten-spec/SKILL.md"
CONTINUE_JUMP = "plan-from-spec, review-and-tighten-plan, tasks-ready-to-build"
CONTINUE_POINT = "review-and-tighten-plan, tasks-ready-to-build"
JUMP_CHOICE = "run /crav1-tighten-spec on just that finding now (Recommended)"
POINT_CHOICE = "keep it as an open point and continue"
FINDING_ID = re.compile(r"^P[1-9][0-9]*$")
JUMP_RESULTS = {"jumped", "open-point"}


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


def _take_jump_line(current: dict, line: str) -> None:
    key, _, value = line.partition(": ")
    if not value:
        fail("progress-file", f"line has no value: {line}")
    if key == "Done":
        current["when"] = value
    elif key == "Finding":
        current["finding"] = value
    elif key == "Result":
        if value not in JUMP_RESULTS:
            fail("progress-file", f"unknown jump result {value}")
        current["result"] = value
    elif key == "Open":
        current["open"] = value
    elif key == "Continue":
        current["continue"] = value
    elif key == "Key":
        current["key"] = value
    else:
        fail("progress-file", f"unknown line: {line}")


def parse_progress(text: str) -> dict:
    """Parse the progress file. A line the format does not allow is an error."""
    steps: dict[str, dict] = {}
    acks: list[dict] = []
    jumps: list[dict] = []
    current: dict | None = None
    kind: str | None = None
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
        if line.startswith("- Jump-back: ") or line.startswith("- Open point: "):
            label, _, fid = line.partition(": ")
            if not FINDING_ID.fullmatch(fid):
                fail("progress-file", f"jump id is not a P#: {line}")
            current = {
                "kind": "jump-back" if label == "- Jump-back" else "open-point",
                "id": fid,
            }
            jumps.append(current)
            kind = "jump"
            continue
        if line.startswith("- Step: "):
            step = line[len("- Step: "):]
            if step not in ORDER:
                fail("progress-file", f"unknown step {step}")
            current = {"step": step}
            steps[step] = current
            kind = "step"
            continue
        if line.startswith("- Extra: "):
            step = line[len("- Extra: "):]
            if step not in EXTRAS:
                fail("progress-file", f"unknown extra {step}")
            current = {"step": step, "extra": True}
            steps[step] = current
            kind = "step"
            continue
        if current is None:
            fail("progress-file", f"line outside a step: {line}")
        if kind == "jump":
            _take_jump_line(current, line)
            continue
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
    for jump in jumps:
        for need in ("when", "finding", "result", "continue", "key"):
            if need not in jump:
                fail("progress-file", f"{jump['kind']} {jump['id']} has no {need}")
        if jump["kind"] == "jump-back":
            if jump["result"] != "jumped":
                fail("progress-file", f"jump-back {jump['id']} result is not jumped")
            if jump.get("open") != TIGHTEN_SPEC_PATH:
                fail("progress-file", f"jump-back {jump['id']} does not name {TIGHTEN_SPEC_PATH}")
        elif jump["result"] != "open-point":
            fail("progress-file", f"open point {jump['id']} result is not open-point")
    return {"slice": slice_line, "steps": steps, "acks": acks, "jumps": jumps}


def load(root: Path) -> dict:
    path = progress_path(root)
    if not path.is_file():
        return {"slice": None, "steps": {}, "acks": [], "jumps": []}
    data = parse_progress(path.read_text(encoding="utf-8"))
    data.setdefault("acks", [])
    data.setdefault("jumps", [])
    return data


def _render_jumps(lines: list[str], jumps: list | None) -> None:
    for jump in jumps or []:
        title = "Jump-back" if jump["kind"] == "jump-back" else "Open point"
        lines.append(f"- {title}: {jump['id']}")
        lines.append(f"  Done: {jump['when']}")
        lines.append(f"  Finding: {jump['finding']}")
        lines.append(f"  Result: {jump['result']}")
        if jump.get("open"):
            lines.append(f"  Open: {jump['open']}")
        lines.append(f"  Continue: {jump['continue']}")
        lines.append(f"  Key: {jump['key']}")
        lines.append("")


def render(slice_label: str, steps: dict, acks: list | None = None, jumps: list | None = None) -> str:
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
    _render_jumps(lines, jumps)
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
            "tasks-ready-to-build records Result: ready, Result: ready-partial, "
            "or Result: not-ready, from the readiness output. "
            "An older Result: done still reads.",
        )
    if step != "tasks-ready-to-build" and args.result in READY_ONLY:
        fail("result", "ready, ready-partial, and not-ready are only for tasks-ready-to-build")
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
    text = render(label, data["steps"], data.get("acks"), data.get("jumps"))
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
    progress_path(root).write_text(
        render(label, data["steps"], data.get("acks"), data.get("jumps")),
        encoding="utf-8",
    )


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
        "spec_findings": [
            {
                "id": jump["id"],
                "key": jump["key"],
                "result": jump["result"],
                "continue": [part for part in jump["continue"].split(", ") if part],
            }
            for jump in data.get("jumps") or []
        ],
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
    # A task that depends on a held task is held too, even with no question
    # of its own (1.132.0). That is waiting, not a jump back.
    if "held, waits on" in text:
        return _waiting(row)
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
        "reason": row.get("reason"),
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


def map_mod():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "crav1-tasks-ready-to-build" / "scripts" / "build_map.py"
    spec = importlib.util.spec_from_file_location("build_map_rows", path)
    if spec is None or spec.loader is None:
        fail("map", f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def branch_report(root: Path, rows: list[dict]) -> dict | None:
    """Ready and held tasks grouped by the build-map row (1.133.0).

    The branch is the one `build_map.py --recommend` prints. Missing files
    leave the report empty so the caller keeps the older line.
    """
    if root is None or not root.is_dir():
        return None
    tasks_path = root / "tasks.md"
    if not tasks_path.is_file():
        return None
    plan_path = root / "plan.md"
    spec_path = root / "spec.md"
    verify_path = root / "verify.md"
    work_path = root / "work-item.md"
    tasks = tasks_path.read_text(encoding="utf-8")
    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else None
    work = work_path.read_text(encoding="utf-8") if work_path.is_file() else ""
    verify = verify_path.read_text(encoding="utf-8") if verify_path.is_file() else ""
    built = map_mod().build(root.name, spec, plan, tasks, work, verify)
    return map_mod().report_by_branch(built, rows)


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


def _pr_merged(text: str) -> bool:
    """A pull request recorded on this line is merged. Local text only."""
    return bool(re.search(r"\(PR\s+\d+", text or "", re.I) and re.search(r"\bmerged\b", text or "", re.I))


def _merged_branches(spec_text: str) -> set[str]:
    names: set[str] = set()
    mod = map_mod()
    for line in (spec_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if not stripped.lower().startswith("branch:"):
            continue
        if not _pr_merged(stripped):
            continue
        body = stripped.split(":", 1)[1]
        cleaned = re.sub(r"\([^)]*\)", " ", body)
        cleaned = re.sub(r"\bmerged\b", " ", cleaned, flags=re.I)
        token = mod.branch_token(cleaned)
        if token:
            names.add(token)
    return names


def _task_merged(rest: str, branches: set[str]) -> bool:
    if _pr_merged(rest):
        return True
    mod = map_mod()
    for mark in re.finditer(r"\((?:branch|map):\s*([^)]+)\)", rest or "", re.I):
        token = mod.branch_token(mark.group(1))
        if token and token in branches:
            return True
    return False


def _task_rests(text: str) -> dict[int, str]:
    rests = {}
    for line in (text or "").splitlines():
        match = order_mod().TASK.match(line)
        if match:
            rests[int(match.group(2))] = match.group(3)
    return rests


def _overview_status(text: str | None, tid: str) -> str | None:
    """Status cell on the verify tasks table, or None when that row is absent."""
    if not text:
        return None
    in_tasks = False
    for line in text.splitlines():
        if line.startswith("## Tasks"):
            in_tasks = True
            continue
        if in_tasks and line.startswith("## "):
            break
        if not in_tasks or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == tid and len(cells) >= 3 and cells[2] not in ("Status", "---"):
            return cells[2]
    return None


def _not_implemented(status: str | None) -> bool:
    return bool(status) and "not implemented" in status.lower()


def _tldr_not_implemented(text: str | None, tid: str) -> bool:
    if not text:
        return False
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0].lower() != "not implemented":
            continue
        blob = " ".join(cells[1:])
        if re.search(rf"\b{re.escape(tid)}\b", blob):
            return True
    return False


def _listed_not_implemented(text: str | None, tid: str) -> bool:
    status = _overview_status(text, tid)
    if status is not None:
        return _not_implemented(status)
    return _tldr_not_implemented(text, tid)


def _built_ids(tasks_text: str, spec_text: str) -> dict[str, dict]:
    """Tasks that are ticked, or whose pull request is recorded merged."""
    branches = _merged_branches(spec_text)
    rests = _task_rests(tasks_text)
    built = {}
    for task in order_mod().parse(tasks_text):
        tid = f"T{task['id']}"
        rest = rests.get(task["id"], "")
        merged = _task_merged(rest, branches)
        if task["done"] or merged:
            built[tid] = {"done": task["done"], "merged": merged, "id": task["id"]}
    return built


def _stale_next(verify_text: str, built: set[str]) -> str | None:
    hits = []
    for line in (verify_text or "").splitlines():
        stripped = line.strip()
        if not stripped.lower().startswith("next:"):
            continue
        named = re.findall(r"\bT\d+\b", stripped)
        if any(tid in built for tid in named):
            hits.append(stripped)
    return " ".join(hits) if hits else None


def verify_gap_from(tasks_text: str, spec_text: str, verify_text: str, slug: str) -> dict:
    """verify.md is behind when a built task is still not implemented, or Next names one.

    Built means ticked in tasks.md, or the task's pull request is recorded merged
    on the task line or on its Match Branch line. This does not write verify.md.
    """
    empty = {"behind": False, "tasks": [], "waiting": None, "stale_next": None}
    if not verify_text.strip() or not tasks_text.strip():
        return empty
    built = _built_ids(tasks_text, spec_text)
    stale: list[str] = []
    for tid in built:
        if _listed_not_implemented(verify_text, tid):
            stale.append(tid)
    stale_next = _stale_next(verify_text, set(built))
    if stale_next:
        for tid in re.findall(r"\bT\d+\b", stale_next):
            if tid in built and tid not in stale:
                stale.append(tid)
    if not stale:
        return empty
    ordered = sorted(stale, key=lambda tid: int(tid[1:]))
    ids = ", ".join(ordered)
    waiting = (
        f"Waiting: /crav1-verify-build-against-spec {slug} - "
        f"verify.md is behind tasks.md ({ids})"
    )
    return {"behind": True, "tasks": ordered, "waiting": waiting, "stale_next": stale_next}


def verify_gap(root: Path) -> dict:
    empty = {"behind": False, "tasks": [], "waiting": None, "stale_next": None}
    if root is None or not root.is_dir():
        return empty
    verify_path = root / "verify.md"
    tasks_path = root / "tasks.md"
    if not verify_path.is_file() or not tasks_path.is_file():
        return empty
    spec_path = root / "spec.md"
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    return verify_gap_from(
        tasks_path.read_text(encoding="utf-8"),
        spec_text,
        verify_path.read_text(encoding="utf-8"),
        _slug(root),
    )


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
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    rests = _task_rests(tasks_path.read_text(encoding="utf-8"))
    merged_branches = _merged_branches(spec_text)
    for task in tasks:
        task["ticked"] = task["done"]
        task["merged"] = _task_merged(rests.get(task["id"], ""), merged_branches)
        # A merged pull request is built, so later tasks do not wait on it.
        if task["merged"]:
            task["done"] = True
    analysed = order.analyse(tasks)
    by_reason = {row["id"]: row for row in analysed["rows"]}
    blocks = blocks_mod().analyse(spec_text, plan_text)
    verify_text = verify_path.read_text(encoding="utf-8") if verify_path.is_file() else None
    warning = reviewed_warning(plan_text) if plan_path.is_file() else None
    rows = []
    for task in tasks:
        tid = f"T{task['id']}"
        merged = task["merged"]
        if task["ticked"] or merged:
            # A built task that verify.md still calls not implemented is stale,
            # not Needs verify. The waiting line names the catch-up (1.135.0).
            if _listed_not_implemented(verify_text, tid):
                row = {"bucket": "done", "task": tid, "stale_verify": True}
                _attach_deps(row, task)
                rows.append(row)
                continue
            if task["ticked"]:
                bucket, reason = _verify_for(verify_text, tid)
                row = {"bucket": bucket, "task": tid}
                if reason:
                    row["reason"] = reason
                _attach_deps(row, task)
                rows.append(row)
                continue
            status = (_overview_status(verify_text, tid) or "").lower()
            if "unverified" in status or "claimed" in status or "failed" in status:
                bucket, reason = _verify_for(verify_text, tid)
                row = {"bucket": bucket, "task": tid}
                if reason:
                    row["reason"] = reason
            else:
                row = {"bucket": "done", "task": tid}
            _attach_deps(row, task)
            rows.append(row)
            continue
        if not plan_path.is_file():
            row = {"bucket": "blocked", "task": tid, "reason": "no plan.md (recorded)"}
            _attach_deps(row, task)
            rows.append(row)
            continue
        question = _question_row(blocks, tid)
        if question:
            _attach_deps(question, task)
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
            row = {"bucket": bucket, "task": tid, "reason": reason}
            _attach_deps(row, task)
            rows.append(row)
            continue
        row = {"bucket": "ready", "task": tid}
        if warning:
            row["warning"] = warning
        _attach_deps(row, task)
        rows.append(row)
    return rows


def _attach_deps(row: dict, task: dict) -> None:
    row["deps"] = [f"T{dep}" for dep in task["deps"]]
    row["dep_recorded"] = bool(task["recorded"])


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


def propagate_held(rows: list[dict], hits: list[dict]) -> None:
    """A task that depends on a held task is held too (1.132.0).

    The dependency is the one tasks.md already records (`(after: …)`, or the
    task just before it). A cycle, or an after: that names no task, stays a
    blocker. A question that is still a jump back is not propagated: only a
    row already classified as waiting seeds the hold.
    """
    held: dict[str, dict] = {}
    for hit in hits:
        if hit.get("kind") != "waiting" or not hit.get("task"):
            continue
        held[hit["task"]] = hit
    changed = True
    while changed:
        changed = False
        for row in rows:
            task = row.get("task")
            if not task or task in held:
                continue
            if row.get("bucket") in ("needs-verify", "done"):
                continue
            reason = (row.get("reason") or "").lower()
            if "cycle" in reason or "names no task" in reason:
                continue
            if "no plan" in reason or "no tasks" in reason or "plan risk" in reason:
                continue
            deps = [dep for dep in row.get("deps") or [] if dep in held]
            if not deps:
                continue
            tag = "recorded" if row.get("dep_recorded") else "inferred"
            if len(deps) == 1:
                text = f"held, waits on {deps[0]} ({tag})"
            else:
                text = "held, waits on " + ", ".join(deps) + f" ({tag})"
            row["bucket"] = "waiting"
            row["reason"] = text
            row["held"] = True
            source = held[deps[0]]
            if source.get("who"):
                row["who"] = source["who"]
            if "asked" in source:
                row["asked"] = source.get("asked")
            hit = _waiting(row)
            hits.append(hit)
            held[task] = hit
            changed = True


def slice_result(rows: list[dict], hits: list[dict]) -> tuple[str, list, list]:
    """ready, ready-partial, or not-ready.

    ready-partial is some tasks that can start now and some that are held,
    with no other walk blocker. not-ready is when nothing can start, and also
    when a walk blocker other than a kept-open question is still open (a
    cycle, a missing task, no plan, needs verify, an assumption, a reopened
    step, or a question that is still a jump back).
    """
    hard = [hit for hit in hits if hit.get("kind") != "waiting"]
    can_start = [row.get("task") for row in rows if row.get("bucket") == "ready" and row.get("task")]
    held = [row.get("task") for row in rows if row.get("bucket") == "waiting" and row.get("task")]
    if hard:
        return "not-ready", can_start, held
    if can_start and held:
        return "ready-partial", can_start, held
    if held and not can_start:
        return "not-ready", can_start, held
    return "ready", can_start, held


def line_for(result: str, can_start: list, held: list) -> str | None:
    if result != "ready-partial":
        return None
    ready = ", ".join(task for task in can_start if task) or "none"
    first = next((task for task in held if task), "the held tasks")
    return f"Ready: {ready}. Held from {first}."


def gates_for(rows: list[dict]) -> list[dict]:
    """Per-task build gate. A held task is refused. A ready task may start."""
    gates = []
    for row in rows:
        task = row.get("task")
        if not task or row.get("bucket") == "done":
            continue
        if row.get("bucket") == "waiting" or row.get("held"):
            gates.append({
                "task": task,
                "allow": False,
                "refused": True,
                "reason": row.get("reason") or "held",
            })
        elif row.get("bucket") == "ready":
            gates.append({"task": task, "allow": True, "refused": False})
        else:
            gates.append({
                "task": task,
                "allow": False,
                "refused": False,
                "reason": row.get("reason") or row.get("bucket"),
            })
    return gates


def next_for(result: str, can_start: list, waiting_next: str | None) -> str | None:
    if result == "ready":
        return "/crav1-build-tasks, because the slice is ready to build."
    if result == "ready-partial":
        ids = ", ".join(task for task in can_start if task)
        return f"/crav1-build-tasks {ids}, because those tasks can start now."
    return waiting_next


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
    propagate_held(rows, hits)
    reopened = reopened_hits(root) if root is not None else []
    hits.extend(reopened)
    blockers = [h for h in hits if h["kind"] == "blocker" and not h["outside_walk"]]
    outside = [h for h in hits if h["outside_walk"]]
    assumptions = [h for h in hits if h["kind"] == "assumption"]
    waiting = [h for h in hits if h["kind"] == "waiting"]
    unmapped = [h for h in hits if h["command"] is None and h["kind"] != "waiting"]
    jump = [h for h in hits if h["can_jump_back"]]
    result, can_start, held = slice_result(rows, hits)
    ready = result == "ready"
    slug = _slug(root) if root is not None else ""
    waiting_line, waiting_next = _waiting_lines(waiting, slug)
    report = branch_report(root, rows) if root is not None else None
    ready_lines = (report or {}).get("ready_lines") or []
    held_lines = (report or {}).get("held_lines") or []
    next_lines = (report or {}).get("next_lines") or []
    if result in ("ready", "ready-partial") and next_lines:
        nxt = "\n".join(next_lines)
    else:
        nxt = next_for(result, can_start, waiting_next)
        next_lines = []
    if result == "ready-partial" and report and report.get("line"):
        line = report["line"]
    else:
        line = line_for(result, can_start, held)
    gap = verify_gap(root) if root is not None else {
        "behind": False, "tasks": [], "waiting": None, "stale_next": None,
    }
    out = {
        "ok": True,
        "ready": ready,
        "result": result,
        "can_start": can_start,
        "held": held,
        "line": line,
        "ready_lines": ready_lines,
        "held_lines": held_lines,
        "next_lines": next_lines,
        "gates": gates_for(rows),
        "next": nxt,
        "start_build": False,
        "blockers": blockers,
        "outside_walk": outside,
        "assumptions": assumptions,
        "unmapped": unmapped,
        "waiting": waiting,
        "waiting_line": waiting_line,
        "waiting_next": waiting_next,
        "recommend_jump": bool(jump) and result == "not-ready",
        "jump_back": jump,
        "reopened": reopened,
        "verify_behind": gap["behind"],
        "verify_stale": gap["tasks"],
        "verify_waiting": gap["waiting"],
        "stale_next": gap["stale_next"],
        "trust_stale_next": False,
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


def _finding_key(text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def _short_finding(text: str) -> str:
    one = re.sub(r"\s+", " ", text.strip())
    if len(one) > 160:
        return one[:157].rstrip() + "..."
    return one


def _continue_list(text: str) -> list[str]:
    return [part for part in text.split(", ") if part]


def _append_finding(root: Path, data: dict, kind: str, fid: str, text: str, key: str, result: str, continue_line: str, open_path: str | None = None) -> None:
    jump = {
        "kind": kind,
        "id": fid,
        "when": done_stamp(None),
        "finding": _short_finding(text),
        "result": result,
        "continue": continue_line,
        "key": key,
    }
    if open_path:
        jump["open"] = open_path
    data.setdefault("jumps", []).append(jump)
    if not data.get("slice"):
        data["slice"] = f"docs/specs/{root.name}/"
    write_progress(root, data)


def spec_finding(args: argparse.Namespace) -> None:
    """One jump-back card for a spec finding. A plan finding is left as it is.

    The same finding (the same words) is offered once. After that jump, a
    return is an open point and the walk continues. This writes walk-progress.md
    only with --yes. It does not write verify.md, spec.md, plan.md, or tasks.md.
    """
    tag = args.tag or "spec"
    if tag == "plan":
        emit({
            "ok": True,
            "offer": None,
            "spec": False,
            "behave_as_today": True,
            "pause": False,
            "wrote": None,
            "message": "A plan finding stays in /crav1-tighten-plan. This walk does not jump back for it.",
        })
        return
    if tag != "spec":
        fail("tag", "tag must be spec or plan")
    if not args.text or not str(args.text).strip():
        fail("finding", "a spec finding needs --text")
    if not FINDING_ID.fullmatch(args.id or ""):
        fail("finding", "id must be a P# such as P2")
    root = Path(args.root)
    if not root.is_dir():
        fail("root", f"not a folder: {root}")
    data = load(root)
    key = _finding_key(args.text)
    jumps = data.get("jumps") or []
    jumped = any(item.get("key") == key and item["kind"] == "jump-back" for item in jumps)
    pointed = any(item.get("key") == key and item["kind"] == "open-point" for item in jumps)
    if jumped or pointed:
        payload = {
            "ok": True,
            "offer": None,
            "spec": True,
            "finding": args.id,
            "already_jumped": jumped,
            "open_point": True,
            "pause": False,
            "continue": _continue_list(CONTINUE_POINT),
            "refused_second_jump": args.choice == "tighten-spec",
        }
        if pointed:
            payload["already_recorded"] = True
            payload["wrote"] = None
            emit(payload)
            return
        if not args.yes:
            payload["needs_record"] = True
            payload["wrote"] = None
            emit(payload)
            return
        _append_finding(root, data, "open-point", args.id, args.text, key, "open-point", CONTINUE_POINT)
        payload["recorded"] = "open-point"
        payload["wrote"] = PROGRESS_NAME
        emit(payload)
        return
    if not args.choice:
        emit({
            "ok": True,
            "offer": "jump-back",
            "spec": True,
            "finding": args.id,
            "question": (
                f"{args.id} is a spec finding. Jump back to /crav1-tighten-spec "
                "for this finding only, or keep it as an open point and continue?"
            ),
            "options": [
                {"id": "tighten-spec", "label": JUMP_CHOICE, "recommended": True},
                {"id": "open-point", "label": POINT_CHOICE, "recommended": False},
            ],
            "path": TIGHTEN_SPEC_PATH,
            "already_jumped": False,
            "pause": False,
            "wrote": None,
        })
        return
    if args.choice not in ("tighten-spec", "open-point"):
        fail("choice", "choice must be tighten-spec or open-point")
    if not args.yes:
        fail(
            "needs-yes",
            "spec-finding writes the progress file only with --yes, after the card was answered",
            status=2,
        )
    if args.choice == "tighten-spec":
        _append_finding(
            root, data, "jump-back", args.id, args.text, key, "jumped",
            CONTINUE_JUMP, TIGHTEN_SPEC_PATH,
        )
        emit({
            "ok": True,
            "offer": None,
            "spec": True,
            "finding": args.id,
            "recorded": "jump-back",
            "choice": "tighten-spec",
            "path": TIGHTEN_SPEC_PATH,
            "scoped_to": args.id,
            "pause": False,
            "continue": _continue_list(CONTINUE_JUMP),
            "wrote": PROGRESS_NAME,
        })
        return
    _append_finding(root, data, "open-point", args.id, args.text, key, "open-point", CONTINUE_POINT)
    emit({
        "ok": True,
        "offer": None,
        "spec": True,
        "finding": args.id,
        "recorded": "open-point",
        "choice": "open-point",
        "pause": False,
        "continue": _continue_list(CONTINUE_POINT),
        "wrote": PROGRESS_NAME,
    })


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

    f = sub.add_parser("spec-finding")
    f.add_argument("--root", required=True)
    f.add_argument("--id", required=True)
    f.add_argument("--text", required=True)
    f.add_argument("--tag", default="spec", help="spec offers a jump back. plan behaves as today.")
    f.add_argument("--choice", help="tighten-spec or open-point")
    f.add_argument("--yes", action="store_true")
    f.set_defaults(func=spec_finding)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
