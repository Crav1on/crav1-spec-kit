#!/usr/bin/env python3
"""Snapshot check for the ready check and the build map (1.180.0).

Each folder under scripts/tests/snapshots/<name>/ holds an anonymised spec
folder in `spec/` and the expected outputs in `expected/`: `reply.txt` (the
ready check's finished reply), `build-map.md`, and the `build-progress/`
files after the run. The check copies `spec/` to a temporary `<name>/`
folder, runs `walk_progress.py readiness --text --write-map` (no fetch, no
host lookup), runs the invariant checker, and compares.

Usage:
  scripts/snapshot-check.py            compare, exit 1 on a difference
  scripts/snapshot-check.py --update   rewrite expected/ from this run
  scripts/snapshot-check.py --only <name>

Since 1.188.0 a folder with `design-spec/` and `steps.json` is a design
snapshot: the check copies `design-spec/` and runs each step of
`design_run.py` from /crav1-design-architecture in order (`args`, optional
`input`, expected `code`). `expected/steps.txt` holds every step's output and
`expected/files/` the topic folders and the architecture spec afterwards.
Dates are written as YYYY-MM-DD.
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "scripts" / "tests" / "snapshots"
SK = ROOT / ".cursor" / "skills" / "crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build" / "scripts" / "walk_progress.py"
USER = "Person C"
DESIGN_RUN = SK / "crav1-design-architecture" / "scripts" / "design_run.py"


def _invariants():
    path = SK / "crav1-tasks-ready-to-build" / "scripts" / "task_invariants.py"
    spec = importlib.util.spec_from_file_location("task_invariants_snap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_one(folder: Path) -> tuple[dict, list[str]]:
    """{relative name: text} for one snapshot, and the broken invariants."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / folder.name
        shutil.copytree(folder / "spec", work)
        env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
        proc = subprocess.run(
            [sys.executable, str(WALK), "readiness", "--root", str(work), "--text", "--write-map",
             "--skip-sync", "--user", USER],
            capture_output=True, text=True, encoding="utf-8", env=env, timeout=120,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"{folder.name}: {proc.stderr or proc.stdout}")
        got = {"reply.txt": proc.stdout}
        if (work / "build-map.md").is_file():
            got["build-map.md"] = (work / "build-map.md").read_text(encoding="utf-8")
        for path in sorted((work / "build-progress").glob("*.md")) if (work / "build-progress").is_dir() else []:
            got[f"build-progress/{path.name}"] = path.read_text(encoding="utf-8")
        inv = _invariants()
        broken = inv.check(work, inv.readiness(work, USER), USER)
    return got, broken


def _dated(text: str) -> str:
    import re
    return re.sub(r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD", text)


def run_design(folder: Path) -> tuple[dict, list[str]]:
    """A design snapshot: run the steps, return {relative name: text} and problems."""
    import json
    steps = json.loads((folder / "steps.json").read_text(encoding="utf-8"))
    problems, log = [], []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / folder.name
        shutil.copytree(folder / "design-spec", work)
        for i, step in enumerate(steps, 1):
            argv = [sys.executable, str(DESIGN_RUN), "--root", str(work)] + list(step["args"])
            if step.get("input") is not None:
                inp = Path(tmp) / f"step{i}.json"
                inp.write_text(json.dumps(step["input"]), encoding="utf-8")
                argv += ["--input", str(inp)]
            proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", timeout=60,
                                  env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            want = step.get("code", 0)
            if proc.returncode != want:
                problems.append(f"step {i} ({' '.join(step['args'][:1])}) exited {proc.returncode}, expected {want}")
            out = (proc.stdout + proc.stderr).replace(str(work), "<root>").replace(tmp, "<tmp>")
            log.append(f"## Step {i}: design_run.py {' '.join(step['args'])}\n\nExit: {proc.returncode}\n\n{out.rstrip()}\n")
        got = {"steps.txt": _dated("\n".join(log))}
        for path in sorted((work / "docs" / "architecture").rglob("*")):
            if path.is_file():
                got["files/" + str(path.relative_to(work)).replace(os.sep, "/")] = _dated(path.read_text(encoding="utf-8"))
    return got, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare the ready check with its snapshots")
    parser.add_argument("--update", action="store_true", help="Rewrite expected/ from this run.")
    parser.add_argument("--only", default=None, help="One snapshot folder name.")
    args = parser.parse_args(argv)
    failed = False
    for folder in sorted(p for p in SNAPSHOTS.iterdir() if (p / "spec").is_dir() or (p / "steps.json").is_file()):
        if args.only and folder.name != args.only:
            continue
        got, broken = run_design(folder) if (folder / "steps.json").is_file() else run_one(folder)
        for line in broken:
            print(f"{folder.name}: {line}")
            failed = True
        expected = folder / "expected"
        if args.update:
            shutil.rmtree(expected, ignore_errors=True)
            for name, text in got.items():
                path = expected / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
            print(f"{folder.name}: updated")
            continue
        have = {str(p.relative_to(expected)).replace(os.sep, "/"): p.read_text(encoding="utf-8")
                for p in sorted(expected.rglob("*")) if p.is_file()} if expected.is_dir() else {}
        for name in sorted(set(have) | set(got)):
            if have.get(name) != got.get(name):
                failed = True
                print(f"{folder.name}: {name} differs")
                sys.stdout.writelines(difflib.unified_diff(
                    (have.get(name) or "").splitlines(True), (got.get(name) or "").splitlines(True),
                    f"expected/{name}", f"got/{name}"))
        if not failed:
            print(f"{folder.name}: matches")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
