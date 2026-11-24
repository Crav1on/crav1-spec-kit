#!/usr/bin/env python3
"""Invariant checker for the ready check's state (1.180.0).

Runs `walk_progress.py readiness --full` on a spec folder (no fetch, no
host lookup, no map write) and checks the rules that must hold
whatever the slice looks like:

  I1  The counts add up to the number of task rows.
  I2  A Blocked row is never invisible: its T# is in the reply.
  I3  A ticked task is never counted ready or waiting.
  I4  The merge list never puts a PR before one it waits on.
  I5  A merge deadlock is Blocked and the reply names /crav1-tighten-plan.
  I6  The reply has no `Next:` line, and a not-ready reply starts its ending
      with Run next.
  I7  No stored or printed owner name keeps a leading `Admin` or a
      trailing `(...)` tag.
  I8  Every task the reply offers as `/crav1-build-walk <slug> <T#>` starts
      in the walk: task_state.walk_start says startable (1.186.0).

Usage:
  task_invariants.py --root <spec-folder> [--json]
Exit 0 when every invariant holds, 1 when one breaks.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
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

HERE = Path(__file__).resolve().parent
WALK = HERE.parent.parent / "crav1-tighten-and-plan-ready-to-build" / "scripts" / "walk_progress.py"
BUCKET_COUNT = {"ready": "ready", "waiting": "waiting", "waits-in-order": "waits_in_order",
                "blocked": "blocked", "needs-verify": "needs_verify", "done": "done"}
_TICKED = re.compile(r"^\s*[-*]\s*\[[xX]\]\s*\**\s*(T\d+)\b", re.M)
_BAD_NAME = re.compile(r"^(?:PR author|Opened by):\s*(?:admin\b.*|.*\([^)]*\)\s*)$", re.M | re.I)


def readiness(root: Path, user: str | None = None) -> dict:
    env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
    cmd = [sys.executable, str(WALK), "readiness", "--root", str(root), "--full", "--skip-sync"]
    if user:
        cmd += ["--user", user]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return json.loads(proc.stdout)


def _walk_starts(root: Path, user: str | None) -> dict:
    import importlib.util
    path = HERE / "task_state.py"
    spec = importlib.util.spec_from_file_location("task_state_inv", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.walk_starts(root, user)


def check(root: Path, out: dict, user: str | None = None) -> list[str]:
    broken = []
    rows = [row for row in out.get("rows") or [] if row.get("task")]
    counts = out.get("counts") or {}
    total = sum(int(counts.get(key, 0) or 0) for key in BUCKET_COUNT.values())
    if total != len(rows):
        broken.append(f"I1 counts add up to {total}, but there are {len(rows)} task rows")
    reply = out.get("reply") or ""
    for row in rows:
        if row.get("bucket") == "blocked" and not re.search(rf"\b{row['task']}\b", reply):
            broken.append(f"I2 {row['task']} is Blocked but the reply does not name it")
    tasks_md = root / "tasks.md"
    ticked = set(_TICKED.findall(tasks_md.read_text(encoding="utf-8"))) if tasks_md.is_file() else set()
    for row in rows:
        if row["task"] in ticked and row.get("bucket") in ("ready", "waiting", "waits-in-order"):
            broken.append(f"I3 {row['task']} is ticked but counted {row.get('bucket')}")
    numbers = [int(n) for n in re.findall(r"(?m)^\d+\. PR (\d+) ", reply)]
    for match in re.finditer(r"(?m)^\d+\. PR (\d+) .*not ready to merge: (.*)$", reply):
        for other in re.findall(r"\(PR (\d+)\)", match.group(2)):
            pr, dep = int(match.group(1)), int(other)
            if dep in numbers and numbers.index(dep) > numbers.index(pr):
                broken.append(f"I4 PR {pr} is listed before PR {dep}, which it waits on")
    for row in rows:
        if row.get("deadlock"):
            if row.get("bucket") != "blocked":
                broken.append(f"I5 {row['task']} is in a merge deadlock but not Blocked")
            if "/crav1-tighten-plan" not in reply:
                broken.append(f"I5 {row['task']} is in a merge deadlock but the reply has no /crav1-tighten-plan")
    if re.search(r"(?m)^Next:", reply):
        broken.append("I6 the reply has a Next: line")
    if out.get("result") == "not-ready" and "Run next:" in reply:
        ending = reply.split("Result: not-ready", 1)[-1].strip()
        if not ending.startswith("Run next:") and not ending.startswith("**Catch up first**"):
            broken.append("I6 the not-ready ending does not start with Run next")
    progress = root / "build-progress"
    for path in sorted(progress.glob("*.md")) if progress.is_dir() else []:
        if _BAD_NAME.search(path.read_text(encoding="utf-8", errors="replace")):
            broken.append(f"I7 build-progress/{path.name} keeps an uncleaned owner name")
    if re.search(r"\bAdmin [A-Z]", reply):
        broken.append("I7 the reply prints an uncleaned owner name")
    offered = re.findall(rf"`/crav1-build-walk {re.escape(root.name)} (T\d+)`", reply)
    if offered:
        starts = _walk_starts(root, user)
        for task in offered:
            found = starts.get(task) or {}
            if not found.get("startable"):
                broken.append(f"I8 the reply offers {task}, but the walk would not start it: {found.get('reason', 'not in tasks.md')}")
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the ready check's invariants on a spec folder")
    parser.add_argument("--root", required=True)
    parser.add_argument("--user", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root)
    broken = check(root, readiness(root, args.user), args.user)
    if args.json:
        print(json.dumps({"ok": not broken, "broken": broken}, indent=2))
    else:
        print("Invariants hold." if not broken else "\n".join(broken))
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
