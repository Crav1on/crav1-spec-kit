"""1.186.0: an open task on someone else's pull request branch starts as new
work, even when the branch's other tasks wait for the merge. A take-in task
(`(take-in: develop)`, or text that says it takes in develop on a branch
another person owns) may merge the base into that branch. The ready check
and the walk ask the same task_state.walk_start."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
SNAP = ROOT / "scripts/tests/snapshots/other-owner-take-in"
BW = SK / "crav1-build-walk/scripts/build_walk.py"
USER = "Person C"
BRANCH = "feat/orders-fixes"


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SK / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ts = load("crav1-tasks-ready-to-build/scripts/task_state.py", "ts_1186")
inv = load("crav1-tasks-ready-to-build/scripts/task_invariants.py", "inv_1186")


def copy(tmp: str) -> Path:
    root = Path(tmp) / "orders-api"
    shutil.copytree(SNAP / "spec", root)
    return root


def run_bw(*args):
    proc = subprocess.run([sys.executable, str(BW), *args], capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, json.loads(proc.stdout or "{}")


def record(root: Path, step: str, result: str):
    code, out = run_bw("progress", "record", "--root", str(root), "--branch", BRANCH,
                       "--step", step, "--result", result, "--yes")
    assert code == 0, out


class TakeIn(unittest.TestCase):
    def test_mark_always_counts(self):
        self.assertEqual(ts.take_in_base("Merge the fixes (take-in: develop)"), "develop")
        self.assertEqual(ts.take_in_base("Merge the fixes (take-in: `main`)", "self"), "main")

    def test_text_counts_only_on_another_persons_branch(self):
        line = "PR 7 takes in develop, conflicts resolved"
        self.assertEqual(ts.take_in_base(line, "other"), "develop")
        self.assertIsNone(ts.take_in_base(line, "self"))
        self.assertEqual(ts.take_in_base("PR 7: take in develop after PR 6", "other"), "develop")

    def test_other_text_is_not_take_in(self):
        self.assertIsNone(ts.take_in_base("Add a test of the guard", "other"))
        self.assertIsNone(ts.take_in_base("takes in developer feedback", "other"))


class WalkStart(unittest.TestCase):
    def test_open_task_on_a_waiting_branch_is_startable(self):
        found = ts.walk_start(SNAP / "spec", "T4", USER)
        self.assertTrue(found["startable"])
        self.assertEqual(found["phase"], "build")
        self.assertEqual(found["take_in"], "develop")
        self.assertTrue(found["claim_needed"])
        self.assertTrue(found["header_needed"])

    def test_pushed_tasks_wait_for_the_merge(self):
        for task in ("T2", "T3"):
            found = ts.walk_start(SNAP / "spec", task, USER)
            self.assertFalse(found["startable"])
            self.assertEqual(found["phase"], "wait-merge")

    def test_claimed_by_someone_else_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            with (root / "claims.md").open("a", encoding="utf-8") as fh:
                fh.write(f"In progress: {BRANCH}, T4, Person B, since 2026-11-17T09:00:00+01:00\n")
            found = ts.walk_start(root, "T4", USER)
            self.assertEqual(found["phase"], "claimed")
            self.assertIn("Person B", found["reason"])
            self.assertTrue(ts.walk_start(root, "T4", "Person B")["startable"])

    def test_a_task_with_an_open_dependency_is_held(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            text = (root / "tasks.md").read_text(encoding="utf-8").replace("- [x] T1", "- [ ] T1")
            (root / "tasks.md").write_text(text, encoding="utf-8")
            found = ts.walk_start(root, "T4", USER)
            self.assertEqual(found["phase"], "held")
            self.assertEqual(found["waits_on"], ["T1"])

    def test_unknown_task(self):
        self.assertEqual(ts.walk_start(SNAP / "spec", "T99", USER)["phase"], "unknown")

    def test_no_mark_on_own_branch_is_a_normal_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            path = root / "build-progress/feat--orders-fixes.md"
            path.write_text(path.read_text(encoding="utf-8").replace("Owner: other", "Owner: self"), encoding="utf-8")
            found = ts.walk_start(root, "T4", USER)
            self.assertTrue(found["startable"])
            self.assertIsNone(found["take_in"])


class WalkNext(unittest.TestCase):
    def test_next_task_starts_t4_with_take_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run_bw("next", "--root", str(copy(tmp)), "--task", "T4", "--user", USER)
            self.assertEqual(code, 0, out)
            self.assertEqual(out["phase"], "build")
            self.assertTrue(out["allowed"]["take_in_base"])
            self.assertFalse(out["allowed"]["merge_pr"])
            self.assertFalse(out["allowed"]["merge_base"])
            self.assertEqual(out["start"]["take_in"], "develop")
            self.assertIn("progress start-task", out["start"]["command"])
            self.assertEqual(out["card"]["options"][0]["word"], "take-in")
            self.assertIn("git merge --no-ff origin/develop", out["card"]["options"][0]["text"])
            self.assertIn("Person A merges PR 7", out["card"]["options"][0]["text"])
            self.assertTrue(out["lead"].startswith("T4 starts as new work: take develop into feat/orders-fixes"))
            self.assertTrue(out["ending"].startswith("Run next:"))
            self.assertIn("`/crav1-build-walk orders-api T4`", out["ending"])

    def test_branch_with_an_open_task_is_not_wait_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run_bw("next", "--root", str(copy(tmp)), "--branch", BRANCH, "--user", USER)
            self.assertEqual(code, 0, out)
            self.assertEqual(out["phase"], "build")
            self.assertEqual(out["start"]["task"], "T4")

    def test_a_task_that_cannot_start_gets_a_card_and_run_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            with (root / "claims.md").open("a", encoding="utf-8") as fh:
                fh.write(f"In progress: {BRANCH}, T4, Person B, since 2026-11-17T09:00:00+01:00\n")
            code, out = run_bw("next", "--root", str(root), "--task", "T4", "--user", USER)
            self.assertEqual(code, 0, out)
            self.assertEqual(out["phase"], "cannot-start")
            self.assertTrue(out["ending"].startswith("Run next:\n\nCheck what can start now:\n`/crav1-tasks-ready-to-build orders-api`"))
            self.assertIn("Waiting: Person B to finish T4.", out["ending"])
            self.assertEqual([o["word"] for o in out["card"]["options"]], ["check-ready", "stop"])
            self.assertNotIn("Next:", out["ending"])

    def test_full_take_in_run_ends_naming_who_merges(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            code, out = run_bw("progress", "start-task", "--root", str(root), "--branch", BRANCH,
                               "--task", "T4", "--user", USER, "--yes")
            self.assertEqual(code, 0, out)
            claims = (root / "claims.md").read_text(encoding="utf-8")
            self.assertIn(f"In progress: {BRANCH}, T4, {USER}, since", claims)
            text = (root / "build-progress/feat--orders-fixes.md").read_text(encoding="utf-8")
            self.assertIn("Tasks: T2 A test of the 404 for an unknown order, T3 A test of the order id guard, T4 ", text)
            self.assertIn("- Step: start T4\n", text)
            self.assertIn("Result: started (take-in: develop)", text)
            code, out = run_bw("next", "--root", str(root), "--branch", BRANCH, "--user", USER)
            self.assertEqual((out["phase"], out["lead"]), ("build", "T4 is next to build on feat/orders-fixes."))
            record(root, "build T4", "done (take-in: develop at c3d4e5f, 2 conflicts resolved)")
            record(root, "verify", "done (T4: Implemented, verified, tick pending at c3d4e5f)")
            record(root, "commit", "done (T4: c3d4e5f)")
            code, out = run_bw("next", "--root", str(root), "--branch", BRANCH, "--user", USER)
            self.assertEqual(out["phase"], "comment")
            record(root, "comment", "done (T4: commented on PR 7)")
            code, out = run_bw("next", "--root", str(root), "--branch", BRANCH, "--user", USER)
            self.assertEqual(out["phase"], "wait-merge")
            self.assertEqual(out["lead"], "T2, T3 and T4 are pushed to PR 7 and wait for its merge.")
            self.assertEqual(out["ending"], "Waiting: Person A to merge pull request 7, then T2, T3 and T4 on feat/orders-fixes are ticked.")
            self.assertEqual(ts.walk_start(root, "T4", USER)["phase"], "wait-merge")

    def test_start_task_twice_writes_one_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            for _ in range(2):
                code, out = run_bw("progress", "start-task", "--root", str(root), "--branch", BRANCH,
                                   "--task", "T4", "--user", USER, "--yes")
                self.assertEqual(code, 0, out)
            text = (root / "build-progress/feat--orders-fixes.md").read_text(encoding="utf-8")
            self.assertEqual(text.count("- Step: start T4"), 1)
            claims = (root / "claims.md").read_text(encoding="utf-8")
            self.assertEqual(claims.count(", T4, "), 1)

    def test_start_task_refuses_a_pushed_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run_bw("progress", "start-task", "--root", str(copy(tmp)), "--branch", BRANCH,
                               "--task", "T3", "--user", USER, "--yes")
            self.assertEqual(code, 2)
            self.assertEqual(out["code"], "wait-merge")


class ReadyCheckAgrees(unittest.TestCase):
    def test_snapshot_offers_t4_and_invariant_holds(self):
        reply = (SNAP / "expected/reply.txt").read_text(encoding="utf-8")
        self.assertIn("`/crav1-build-walk other-owner-take-in T4`", reply)
        self.assertNotIn("other-owner-take-in T2`", reply)

    def test_i8_flags_an_offer_the_walk_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            out = {"rows": [], "counts": {}, "reply": "Run next:\n`/crav1-build-walk orders-api T3`\n"}
            broken = inv.check(root, out, USER)
            self.assertTrue(any(line.startswith("I8 the reply offers T3") for line in broken), broken)
            out["reply"] = "Run next:\n`/crav1-build-walk orders-api T4`\n"
            self.assertFalse([line for line in inv.check(root, out, USER) if line.startswith("I8")])


if __name__ == "__main__":
    unittest.main()
