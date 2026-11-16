"""1.174.0: the merge-pr hash wins over a later tick, Run next continues an
unfinished branch walk first, a built branch never waits on its own tasks,
full names in build-map.md, and the pull ending puts its label above."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bm = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "build_map_1174")
wp = load(SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py", "walk_progress_1174")
rs = load(SK / "crav1-build-walk/scripts/repo_sync.py", "repo_sync_1174")

# The live shape: merge-pr records the merge, a later tick step records the
# commit that ticked tasks.md and a verify commit.
TICK_AFTER_MERGE = """# Build progress

Walk: build-walk
Slice: docs/specs/orders/
Branch: feat/orders-host-setup
Owner: self
Tasks: T3 Require the CI build on develop; T27 Stop the prod orders-api
Cut from: develop
Merge list: none

- Step: build T3
  Done: 2026-11-13T14:40:00+01:00
  Result: done

- Step: open-pr
  Done: 2026-11-13T15:40:00+01:00
  Result: done (PR 80)

- Step: merge-pr
  Done: 2026-11-13T15:33:00+01:00
  Result: done (PR 80, 1a2b3c4, branch deleted)

- Step: tick T27
  Done: 2026-11-13T15:50:00+01:00
  Result: done (9f8e7d6, verify 5e4d3c2)

- Step: next-task
  Done: 2026-11-13T15:50:00+01:00
  Result: several ready branches (T4, T43), back to the grouping start
"""

TICK_ONLY = """# Build progress

Branch: feat/orders-readme
Owner: self
Tasks: T4 Orders README

- Step: tick T4
  Done: 2026-11-13T15:50:00+01:00
  Result: done (9f8e7d6, verify 5e4d3c2)
"""


def write(folder: Path, name: str, text: str) -> None:
    (folder / "build-progress").mkdir(parents=True, exist_ok=True)
    (folder / "build-progress" / name).write_text(text, encoding="utf-8")


class MergeHashWins(unittest.TestCase):
    def test_merge_pr_hash_wins_over_a_later_tick(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "feat--orders-host-setup.md", TICK_AFTER_MERGE)
            found = bm.progress_shas(root)
            self.assertEqual(found[3], "1a2b3c4")
            self.assertEqual(found[27], "1a2b3c4")
            self.assertEqual(found["feat/orders-host-setup"], "1a2b3c4")
            task = {"id": 27, "rest": "Stop the prod orders-api", "map": None, "branch": None}
            self.assertEqual(bm.done_evidence(task, "feat/orders-host-setup", {}, "", found), "1a2b3c4")

    def test_tick_hash_never_replaces_an_existing_mark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "feat--orders-readme.md", TICK_ONLY)
            found = bm.progress_shas(root)
            self.assertNotIn(4, found)
            task = {"id": 4, "rest": "Orders README", "map": None, "branch": None}
            existing = {4: "4c0ffee"}
            self.assertEqual(bm.done_evidence(task, "feat/orders-readme", {}, "", found, existing), "4c0ffee")
            # With nothing else, the tick commit is the fallback.
            self.assertEqual(bm.done_evidence(task, "feat/orders-readme", {}, "", found, {}), "9f8e7d6")


TASKS = """# Tasks

- [x] T1: Orders schema (branch: feat/orders-schema) (after: )
- [ ] T9: Orders CI/CD: infra Bicep on the consumption plan for dev, test and prod, with the storage account and the settings every stage needs (branch: feat/orders-cicd) (after: T1)
- [ ] T10: Orders CI/CD: deploy pipeline with DEV, TEST and PROD stages (branch: feat/orders-cicd) (after: T9)
- [ ] T11: Orders DEV: switch day for the new plan (branch: feat/orders-switch-day) (after: T10)
"""

PLAN = """# Plan: orders

## Approach

1. Schema. (T1)
2. CI/CD. (T9, T10)
3. Switch day. (T11)
"""

CLAIMS = """# Claims

In progress: feat/orders-cicd, T9, T10, person A, since 2026-11-16T09:00:00+01:00
"""

CICD = """# Build progress

Branch: feat/orders-cicd
Owner: self
Tasks: T9 Orders CI/CD infra; T10 Orders CI/CD pipeline

- Step: build T9
  Done: 2026-11-16T09:30:00+01:00
  Result: done

- Step: build T10
  Done: 2026-11-16T09:50:00+01:00
  Result: done

- Step: open-pr
  Done: 2026-11-16T10:00:00+01:00
  Result: done (PR 82)
"""


def make_slice(tmp: str, progress: str | None = CICD) -> Path:
    root = Path(tmp) / "orders"
    root.mkdir(parents=True)
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (root / "claims.md").write_text(CLAIMS, encoding="utf-8")
    if progress:
        write(root, "feat--orders-cicd.md", progress)
    return root


def ready_now(text: str, branch: str) -> str:
    block = text.split(f"### {branch}", 1)[1].split("\n### ", 1)[0]
    line = next(line for line in block.splitlines() if line.startswith("- Ready now:"))
    return line[len("- Ready now: "):]


class BuiltBranchStatus(unittest.TestCase):
    def test_built_branch_waits_for_its_pull_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp)
            text, code = bm.run_dir(root)
            self.assertEqual(code, 0, text)
            out = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertEqual(ready_now(out, "feat/orders-cicd"), "built, waits for PR 82 to merge")
            self.assertNotIn("waits on T9", out)
            # The branch after it still waits on the branch, not on its tasks.
            self.assertIn("waits on feat/orders-cicd", ready_now(out, "feat/orders-switch-day"))

    def test_claimed_branch_not_built_is_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, progress=None)
            bm.run_dir(root)
            out = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertEqual(ready_now(out, "feat/orders-cicd"), "in progress")
            self.assertNotIn("waits on T9", out)


class FullNamesInMap(unittest.TestCase):
    def test_tasks_and_delivers_lines_are_never_cut(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp)
            bm.run_dir(root)
            out = (root / "build-map.md").read_text(encoding="utf-8")
            full = "with the storage account and the settings every stage needs"
            for line in out.splitlines():
                if line.startswith("- Tasks:") or line.startswith("- Delivers:"):
                    self.assertNotIn("...", line)
            self.assertIn(full, out)


class ResumeWalkFirst(unittest.TestCase):
    def test_unfinished_walk_is_offered_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp)
            (Path(tmp) / "other").mkdir()
            wp.set_branch_run(root, "feat/orders-cicd", "stopped before merge", "2026-11-16T10:00:00+01:00")
            entries = wp.resume_walk_entries(root, "orders")
            self.assertEqual(entries, ["Continue the build walk on feat/orders-cicd:\n`/crav1-build-walk orders feat/orders-cicd`"])

    def test_merge_wait_and_merged_runs_are_not_offered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, progress=CICD + "\n- Step: wait-merge\n  Done: 2026-11-16T10:10:00+01:00\n  Result: waiting (PR 82)\n")
            wp.set_branch_run(root, "feat/orders-cicd", "stopped before merge", "2026-11-16T10:00:00+01:00")
            self.assertEqual(wp.resume_walk_entries(root, "orders"), [])
            wp.set_branch_run(root, "feat/orders-cicd", "merged", "2026-11-16T11:00:00+01:00")
            self.assertEqual(wp.resume_walk_entries(root, "orders"), [])


class PullEndingLayout(unittest.TestCase):
    def test_label_is_above_the_command(self):
        text = rs.pull_ending("Merge origin into your local branch, since they have diverged (never rebase):")
        lines = text.splitlines()
        self.assertEqual(lines[0], "Run next:")
        self.assertEqual(lines[-2], "Merge origin into your local branch, since they have diverged (never rebase):")
        self.assertEqual(lines[-1], "`git pull --no-rebase`")

    def test_behind_default_label(self):
        lines = rs.pull_ending().splitlines()
        self.assertTrue(lines[-2][0].isupper() and lines[-2].endswith(":"))
        self.assertEqual(lines[-1], "`git pull --no-rebase`")


if __name__ == "__main__":
    unittest.main()
