"""1.184.0: progress files from older kits record a second task's build as a
plain `- Step: build` with the task only in the result (`done (T47: ...)`).
It counts as built and waiting for the merge everywhere, the walk names every
task, and the next write adds it to the header."""

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
SNAP = ROOT / "scripts/tests/snapshots/orders-api-old-build-step"
BW = SK / "crav1-build-walk/scripts/build_walk.py"


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SK / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ts = load("crav1-tasks-ready-to-build/scripts/task_state.py", "ts_1184")
bm = load("crav1-tasks-ready-to-build/scripts/build_map.py", "bm_1184")
bw = load("crav1-build-walk/scripts/build_walk.py", "bw_1184")
OLD = (SNAP / "spec/build-progress/feat--orders-cicd.md").read_text(encoding="utf-8")


def copy(tmp: str) -> Path:
    root = Path(tmp) / "orders-api"
    shutil.copytree(SNAP / "spec", root)
    return root


def run_bw(*args):
    proc = subprocess.run([sys.executable, str(BW), *args], capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout or "{}")


class PlainBuildStep(unittest.TestCase):
    def test_result_prefix_names_the_task(self):
        found = ts.progress_tasks(OLD)
        self.assertEqual(found["listed"], ["T43"])
        self.assertEqual(found["built"], ["T47"])
        self.assertEqual(found["all"], ["T43", "T47"])

    def test_a_failed_plain_build_is_not_built(self):
        text = OLD.replace("Result: done (T47: orders-api af772f5", "Result: failed (T47: orders-api af772f5")
        self.assertEqual(ts.progress_tasks(text)["built"], [])

    def test_a_plain_build_without_a_task_prefix_names_nothing(self):
        text = OLD.replace("done (T47: orders-api af772f5", "done (orders-api af772f5")
        self.assertEqual(ts.progress_tasks(text)["all"], ["T43"])

    def test_build_map_counts_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            walk = bm.progress_state(copy(tmp))["feat/orders-cicd"]
            self.assertEqual(walk["built"], {47})
            self.assertEqual(walk["tasks"], {43, 47})
            self.assertTrue(walk["wait_merge"])


class WalkNamesEveryTask(unittest.TestCase):
    def test_read_progress_and_lead(self):
        self.assertEqual(bw.read_progress(OLD)["task_ids"], ["T43", "T47"])
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run_bw("next", "--root", str(copy(tmp)), "--branch", "feat/orders-cicd")
            self.assertEqual(code, 0, out)
            self.assertEqual(out["phase"], "wait-merge")
            self.assertTrue(out["lead"].startswith("T43 and T47 are pushed to PR 73 and wait for its merge"))
            self.assertIn("then T43 and T47 on feat/orders-cicd are ticked.", out["ending"])
            self.assertTrue(out["ending"].startswith("Run next:") or out["ending"].startswith("Waiting:"))

    def test_single_task_lead_is_unchanged(self):
        out = bw.lead_for("wait-merge", {"tasks": [{"id": 5, "title": "x"}], "pr": 71})
        self.assertEqual(out, "T5 is pushed to PR 71 and waits for its merge.")

    def test_next_write_adds_the_task_to_the_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy(tmp)
            code, out = run_bw("progress", "record", "--root", str(root), "--branch", "feat/orders-cicd",
                               "--step", "wait-merge", "--result", "waits for PR 73 to merge", "--yes")
            self.assertEqual(code, 0, out)
            text = (root / "build-progress/feat--orders-cicd.md").read_text(encoding="utf-8")
            self.assertIn("Tasks: T43 Add the build pipeline, T47 Add the deploy stage\n", text)
            self.assertIn("Result: done (T47: orders-api af772f5", text)


class ReadyCheck(unittest.TestCase):
    def test_snapshot_reply(self):
        reply = (SNAP / "expected/reply.txt").read_text(encoding="utf-8")
        self.assertIn("T47 Add the deploy stage — waits for PR 73 to merge", reply)
        self.assertIn("ticks T43 and T47, then T8 can start.", reply)
        self.assertIn("T8 Add smoke tests — held, waits on PR 73 to merge (T47, recorded)", reply)
        self.assertNotIn("is yours; the walk resumes it", reply)
        self.assertNotIn("/crav1-build-walk orders-api-old-build-step T47", reply)


if __name__ == "__main__":
    unittest.main()
