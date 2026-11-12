#!/usr/bin/env python3
"""Tick one recorded-merged or already-verified task. No worker (1.137.0).

tick_only.py --root <spec-folder> T2 [--yes]

The row must still be `[ ]`. Recorded merged is `(PR n)` and the word merged
on the task line, or on the Match Branch line for its `(branch:)` or `(map:)`.
Already verified is a verify.md status that says verified and is not failed,
claimed, or unverified, including Implemented, verified, tick pending.

The slice result does not matter. A not-ready result still ticks this row.
That tick starts no worker and does not re-implement. It is not a way to
build a task the ready check refuses. Without --yes this writes nothing.

Prints JSON. worker is false. Standard library only.
"""
import json
import re
import subprocess
import sys

sys.dont_write_bytecode = True

from pathlib import Path

TASK = re.compile(r"^(\s*- \[)( |x|X)(\] T(\d+)\b.*)$")
WALK = (
    Path(__file__).resolve().parents[2]
    / "crav1-tighten-and-plan-ready-to-build"
    / "scripts"
    / "walk_progress.py"
)


def _utf8_stdout():
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        return


_utf8_stdout()


def emit(payload, code):
    _utf8_stdout()
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return code


def load_walk():
    import importlib.util

    spec = importlib.util.spec_from_file_location("walk_progress_tick", WALK)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {WALK}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def task_number(token):
    match = re.fullmatch(r"T?(\d+)", (token or "").strip(), re.I)
    if not match:
        return None
    return int(match.group(1))


def already_verified(status):
    if not status:
        return False
    low = status.lower()
    if any(word in low for word in ("not implemented", "failed", "unverified", "claimed")):
        return False
    return "verified" in low


def readiness(root):
    proc = subprocess.run(
        [sys.executable, str(WALK), "readiness", "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    if proc.returncode != 0 or not payload.get("ok"):
        return None
    return payload


def tick_text(text, number):
    lines = text.splitlines(keepends=True)
    changed = False
    out = []
    for line in lines:
        match = TASK.match(line.rstrip("\r\n"))
        if match and int(match.group(4)) == number and match.group(2) == " " and not changed:
            nl = "\n" if line.endswith("\n") else ""
            if line.endswith("\r\n"):
                nl = "\r\n"
            body = line[:-len(nl)] if nl else line
            line = body.replace("- [ ]", "- [x]", 1) + nl
            changed = True
        out.append(line)
    return "".join(out), changed


def main(argv):
    _utf8_stdout()
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__ or "")
        return 0
    yes = "--yes" in argv
    args = [arg for arg in argv if arg != "--yes"]
    root = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--root" and i + 1 < len(args):
            root = Path(args[i + 1])
            i += 2
            continue
        positional.append(args[i])
        i += 1
    number = task_number(positional[0]) if len(positional) == 1 else None
    if root is None or number is None:
        return emit({"ok": False, "code": "usage", "worker": False, "ticked": False}, 2)
    tasks_path = root / "tasks.md"
    if not tasks_path.is_file():
        return emit({"ok": False, "code": "no-tasks", "worker": False, "ticked": False}, 2)
    walk = load_walk()
    tasks_text = tasks_path.read_text(encoding="utf-8")
    spec_path = root / "spec.md"
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    rests = walk._task_rests(tasks_text)
    rest = rests.get(number, "")
    if number not in rests:
        return emit({
            "ok": False, "code": "no-task", "task": f"T{number}", "worker": False, "ticked": False,
        }, 2)
    parsed = {task["id"]: task for task in walk.order_mod().parse(tasks_text)}
    task = parsed.get(number)
    if task is None:
        return emit({
            "ok": False, "code": "no-task", "task": f"T{number}", "worker": False, "ticked": False,
        }, 2)
    if task["done"]:
        return emit({
            "ok": False, "code": "already-ticked", "task": f"T{number}", "worker": False, "ticked": False,
        }, 2)
    merged = walk._task_merged(rest, walk._merged_branches(spec_text))
    verify_path = root / "verify.md"
    verify_text = verify_path.read_text(encoding="utf-8") if verify_path.is_file() else ""
    status = walk._overview_status(verify_text, f"T{number}")
    verified = already_verified(status)
    if not merged and not verified:
        return emit({
            "ok": False,
            "code": "not-tick-only",
            "task": f"T{number}",
            "worker": False,
            "ticked": False,
        }, 2)
    report = readiness(root)
    if report is None:
        return emit({"ok": False, "code": "readiness", "worker": False, "ticked": False}, 2)
    result = report.get("result")
    if not yes:
        return emit({
            "ok": False,
            "code": "needs-yes",
            "task": f"T{number}",
            "result": result,
            "worker": False,
            "ticked": False,
        }, 2)
    updated, changed = tick_text(tasks_text, number)
    if not changed:
        return emit({
            "ok": False, "code": "not-open", "task": f"T{number}", "worker": False, "ticked": False,
        }, 2)
    tasks_path.write_text(updated, encoding="utf-8")
    return emit({
        "ok": True,
        "code": "ticked",
        "task": f"T{number}",
        "result": result,
        "worker": False,
        "ticked": True,
    }, 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
