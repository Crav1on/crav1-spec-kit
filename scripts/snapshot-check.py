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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare the ready check with its snapshots")
    parser.add_argument("--update", action="store_true", help="Rewrite expected/ from this run.")
    parser.add_argument("--only", default=None, help="One snapshot folder name.")
    args = parser.parse_args(argv)
    failed = False
    for folder in sorted(p for p in SNAPSHOTS.iterdir() if (p / "spec").is_dir()):
        if args.only and folder.name != args.only:
            continue
        got, broken = run_one(folder)
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
