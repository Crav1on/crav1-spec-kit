"""1.155.0: one status line per branch run in walk-progress.md, and Run next offers T# and branch."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
RUN = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/branch_run.py"
BUILD_WALK = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/build_walk.py"
MAP = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/build_map.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wp = load(WALK, "walk_progress_1155")
br = load(RUN, "branch_run_1155b")
bw = load(BUILD_WALK, "build_walk_1155")
bm = load(MAP, "build_map_1155")

SPEC = """# Spec

The receipt lists the order id.

## Open questions
"""

PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Build the pipeline. (T1, T2, T3, T4)

## Risks
"""

TASKS = """# Tasks

- [ ] T1: Add the build pipeline (branch: feat/orders-cicd) (after: )
- [ ] T2: Add the test stage (branch: feat/orders-cicd) (after: T1)
- [ ] T3: Publish the artifact (branch: feat/orders-cicd) (after: T2)
- [ ] T4: Note the export (branch: feat/orders-note) (after: )
"""


def write_slice(base: Path) -> Path:
    root = base / "docs" / "specs" / "orders-api"
    root.mkdir(parents=True, exist_ok=True)
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    return root


def walk(*args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(WALK), *args], capture_output=True, text=True, check=False)
    return proc.returncode, json.loads(proc.stdout or "{}")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check)


class StatusLineTests(unittest.TestCase):
    def setUp(self):
        self.root = write_slice(Path(tempfile.mkdtemp()))

    def test_one_line_per_branch_replaced_in_place(self):
        wp.set_branch_run(self.root, "feat/orders-cicd", "running, next T1", "2026-11-14T09:00:00+01:00")
        wp.set_branch_run(self.root, "feat/orders-note", "running, next T4", "2026-11-14T09:01:00+01:00")
        wp.set_branch_run(self.root, "feat/orders-cicd", "running, T1 done, next T2", "2026-11-14T09:10:00+01:00")
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.startswith("- Branch run: ")]
        self.assertEqual(lines, [
            "- Branch run: feat/orders-cicd: running, T1 done, next T2 (2026-11-14T09:10:00+01:00). Log: build-progress/feat--orders-cicd.md",
            "- Branch run: feat/orders-note: running, next T4 (2026-11-14T09:01:00+01:00). Log: build-progress/feat--orders-note.md",
        ])
        self.assertIn("## Branch runs", text)

    def test_steps_survive_a_status_write_and_a_step_record_keeps_status(self):
        code, _ = walk("record", "--root", str(self.root), "--slice", "docs/specs/orders-api",
                       "--step", "resolve-open-questions", "--result", "done", "--yes")
        self.assertEqual(code, 0)
        wp.set_branch_run(self.root, "feat/orders-cicd", "stopped before merge", "2026-11-14T09:00:00+01:00")
        data = wp.load(self.root)
        self.assertIn("resolve-open-questions", data["steps"])
        wp.write_progress(self.root, data)
        again = wp.load(self.root)
        self.assertEqual(again["branch_runs"]["feat/orders-cicd"]["state"], "stopped before merge")
        resumed = wp.resume_payload(self.root, True)
        self.assertEqual(len(resumed["branch_runs"]), 1)
        self.assertTrue(resumed["has_steps"])

    def test_cli_needs_yes(self):
        code, out = walk("branch-status", "--root", str(self.root), "--branch", "feat/orders-cicd", "--state", "merged")
        self.assertNotEqual(code, 0)
        self.assertFalse((self.root / "walk-progress.md").exists())
        code, out = walk("branch-status", "--root", str(self.root), "--branch", "feat/orders-cicd", "--state", "merged", "--yes")
        self.assertEqual(code, 0, out)
        self.assertIn("feat/orders-cicd: merged", out["line"])

    def test_branch_run_writes_status_after_start_and_each_task(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        self.assertIn("feat/orders-cicd: running, next T1",
                      (self.root / "walk-progress.md").read_text(encoding="utf-8"))
        out = br.record(self.root, "feat/orders-cicd", "T1", "a1b2c3d", "green")
        self.assertIn("running, T1 done, next T2", out["status_line"])
        br.record(self.root, "feat/orders-cicd", "T2", "b1b2c3d", "green")
        out = br.record(self.root, "feat/orders-cicd", "T3", "c1b2c3d", "green")
        self.assertIn("feat/orders-cicd: stopped before merge", out["status_line"])
        self.assertIn("Log: build-progress/feat--orders-cicd.md", out["status_line"])
        self.assertTrue((self.root / "build-progress" / "feat--orders-cicd.md").is_file())

    def test_ready_check_prints_open_runs_not_merged(self):
        wp.set_branch_run(self.root, "feat/orders-cicd", "running, T1 done, next T2", "2026-11-14T09:00:00+01:00")
        wp.set_branch_run(self.root, "feat/orders-note", "merged", "2026-11-14T09:00:00+01:00")
        code, out = walk("readiness", "--full", "--root", str(self.root), "--skip-sync")
        self.assertEqual(code, 0, out)
        self.assertIn("Branch runs:\n- feat/orders-cicd: running, T1 done, next T2 (log: build-progress/feat--orders-cicd.md)", out["ending"])
        self.assertNotIn("feat/orders-note: merged", out["ending"])

    def test_bad_line_is_refused(self):
        self.assertIsNone(wp.parse_branch_run("- Branch run: feat/x running"))


class ConflictTests(unittest.TestCase):
    """Two sessions update their own status lines; the merge settles them."""

    def test_status_only_conflict_is_settled_by_newest_time(self):
        base = Path(tempfile.mkdtemp())
        repo = base / "repo"
        repo.mkdir()
        git(repo, "init", "-b", "main")
        for key, value in (("user.email", "a@example.com"), ("user.name", "person A"), ("commit.gpgsign", "false")):
            git(repo, "config", key, value)
        root = write_slice(repo)
        walk("record", "--root", str(root), "--slice", "docs/specs/orders-api",
             "--step", "resolve-open-questions", "--result", "done", "--yes")
        wp.set_branch_run(root, "feat/orders-cicd", "running, next T1", "2026-11-14T09:00:00+01:00")
        git(repo, "add", "-A")
        git(repo, "commit", "-m", "start")
        git(repo, "checkout", "-b", "other")
        wp.set_branch_run(root, "feat/orders-cicd", "running, T1 done, next T2", "2026-11-14T10:00:00+01:00")
        git(repo, "commit", "-am", "other session")
        git(repo, "checkout", "main")
        wp.set_branch_run(root, "feat/orders-cicd", "running, T1 done, next T2", "2026-11-14T09:30:00+01:00")
        git(repo, "commit", "-am", "this session")
        merged = git(repo, "merge", "--no-edit", "other", check=False)
        self.assertNotEqual(merged.returncode, 0)
        self.assertIn("<<<<<<<", (root / "walk-progress.md").read_text(encoding="utf-8"))
        code, out = walk("resolve-stamps", "--root", str(root), "--yes")
        self.assertEqual(code, 0, out)
        text = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertNotIn("<<<<<<<", text)
        self.assertIn("(2026-11-14T10:00:00+01:00)", text)
        self.assertEqual(text.count("- Branch run: feat/orders-cicd"), 1)

    def test_merge_keeps_both_branches(self):
        ours = {"feat/a": {"branch": "feat/a", "state": "merged", "when": "2026-11-14T11:00:00+01:00", "log": "build-progress/feat--a.md"}}
        theirs = {"feat/a": {"branch": "feat/a", "state": "running, next T2", "when": "2026-11-14T10:00:00+01:00", "log": "build-progress/feat--a.md"},
                  "feat/b": {"branch": "feat/b", "state": "running, next T5", "when": "2026-11-14T10:00:00+01:00", "log": "build-progress/feat--b.md"}}
        merged = wp.merge_branch_runs(ours, theirs)
        self.assertEqual(merged["feat/a"]["state"], "merged")
        self.assertIn("feat/b", merged)


class RunNextChoiceTests(unittest.TestCase):
    def test_two_open_tasks_offer_task_and_branch(self):
        entries = bm.run_entries(["T1 Add the build pipeline"], "feat/orders-cicd", slug="orders-api",
                                 open_labels=["T1 Add the build pipeline", "T2 Add the test stage"])
        self.assertEqual(entries, [
            "`/crav1-build-walk orders-api T1`\nbranch feat/orders-cicd, T1 Add the build pipeline",
            "`/crav1-build-walk orders-api feat/orders-cicd`\nbranch feat/orders-cicd, every open task: T1 Add the build pipeline, T2 Add the test stage",
        ])

    def test_one_open_task_offers_only_the_task(self):
        entries = bm.run_entries(["T4 Note the export"], "feat/orders-note", slug="orders-api",
                                 open_labels=["T4 Note the export"])
        self.assertEqual(entries, ["`/crav1-build-walk orders-api T4`\nbranch feat/orders-note, T4 Note the export"])

    def test_ready_check_run_and_next_lines_agree(self):
        root = write_slice(Path(tempfile.mkdtemp()))
        walk("record", "--root", str(root), "--slice", "docs/specs/orders-api",
             "--step", "resolve-open-questions", "--result", "done", "--yes")
        report = wp.branch_report(root, wp.build_rows(root))
        run_cmds = [line for entry in report["run_lines"] for line in entry.splitlines() if line.startswith("`")]
        next_cmds = [line for entry in report["next_lines"] for line in entry.splitlines() if line.startswith("`")]
        self.assertEqual(run_cmds, next_cmds)
        self.assertIn("`/crav1-build-walk T1`", run_cmds)
        self.assertIn("`/crav1-build-walk feat/orders-cicd`", run_cmds)
        self.assertIn("`/crav1-build-walk T4`", run_cmds)
        self.assertNotIn("`/crav1-build-walk feat/orders-note`", run_cmds)
        branch = next(b for b in report["ready_branches"] if b["branch"] == "feat/orders-cicd")
        self.assertEqual([t["id"] for t in branch["open_tasks"]], ["T1", "T2", "T3"])

    def test_build_walk_ending_offers_both_for_other_branches(self):
        state = bw.prepare_state({
            "phase": "build", "branch": "feat/orders-note", "tasks": ["T4"], "slug": "orders-api", "spec_count": 2,
            "ready_branches": [{"branch": "feat/orders-cicd", "tasks": ["T1 Add the build pipeline"],
                                "open_tasks": ["T1 Add the build pipeline", "T2 Add the test stage"]}],
        })
        out = bw.next_for(state)
        lines = out["ending"].splitlines()
        self.assertIn("`/crav1-build-walk orders-api T1`", lines)
        self.assertIn("`/crav1-build-walk orders-api feat/orders-cicd`", lines)
        self.assertEqual(len(out["next"]), 3)
        for line in lines:
            if line.startswith("`"):
                self.assertRegex(line, r"^`[^`]+`$")
        index = lines.index("`/crav1-build-walk orders-api feat/orders-cicd`")
        self.assertTrue(lines[index + 1].startswith("branch feat/orders-cicd, every open task: T1"))

    def test_grouping_single_open_task_has_no_branch_entry(self):
        out = bw.next_for(bw.prepare_state({
            "mode": "grouping", "slug": "orders-api", "spec_count": 2,
            "branches": [{"branch": "feat/orders-note", "tasks": ["T4 Note the export"], "open_tasks": ["T4 Note the export"]}],
        }))
        self.assertEqual(out["count"], 1)
        self.assertNotIn("`/crav1-build-walk orders-api feat/orders-note`", out["ending"])

    def test_branch_run_ending_follows_the_rule(self):
        out = br.ending({"slug": "orders-api", "branch": "feat/orders-note", "pr": 4,
                         "ready_branches": [{"branch": "feat/orders-cicd",
                                             "tasks": [{"id": "T1", "title": "Add the build pipeline"}],
                                             "open_tasks": [{"id": "T1", "title": "Add the build pipeline"},
                                                            {"id": "T2", "title": "Add the test stage"}]}]})
        text = out["ending"]
        self.assertIn("`/crav1-build-walk orders-api T1`\nbranch feat/orders-cicd, T1 Add the build pipeline", text)
        self.assertIn("`/crav1-build-walk orders-api feat/orders-cicd`\nbranch feat/orders-cicd, every open task: T1 Add the build pipeline, T2 Add the test stage", text)


if __name__ == "__main__":
    unittest.main()
