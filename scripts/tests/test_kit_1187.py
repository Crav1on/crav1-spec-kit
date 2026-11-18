"""1.187.0: a task's name stops where its verify items start.

The walk lead, the ending under Run next, the ready check and the build map
showed the whole task line, `; integration — ...; system — ...` included.
One helper, task_order.task_name, cuts at the first verify item, drops
unbalanced parentheses and tidies stray spaces."""

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
SNAP = ROOT / "scripts/tests/snapshots/orders-api-verify-names"
BW = SK / "crav1-build-walk/scripts/build_walk.py"
USER = "Person C"


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SK / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


to = load("crav1-tasks-ready-to-build/scripts/task_order.py", "to_1187")
bm = load("crav1-tasks-ready-to-build/scripts/build_map.py", "bm_1187")

SEMI = (
    "PR 12 takes in develop after PR 10 merges, with the conflicts in `app.py` and "
    "`tests/test_store.py` resolved; integration — an incoming request with only tag and "
    "content writes the audit row; contract — after the conflicts are resolved, each request "
    "field matches `app.py` ( handler reads only tag and content ); system — pipeline 6 is "
    "green on PR 12; system — PR 12 is merged into develop , with `api-doc.yaml` in it)"
)
PAREN = (
    "A test of the order id guard (verify: unit — an empty id is rejected; system — "
    "pipeline 6 is green on PR 20 ( guard on ) (regression)) (spec: AC2)"
)
SHORT = (
    "PR 12 takes in develop after PR 10 merges, with the conflicts in app.py and "
    "tests/test_store.py resolved"
)


class TaskName(unittest.TestCase):
    def test_semicolon_verify_items_are_cut(self):
        self.assertEqual(to.task_name(SEMI), SHORT)

    def test_verify_block_with_nested_parens_is_cut(self):
        self.assertEqual(to.task_name(PAREN), "A test of the order id guard")

    def test_plain_task_is_unchanged(self):
        line = "Add the orders endpoint (after: T2) (branch: feat/orders-api)"
        self.assertEqual(to.task_name(line), "Add the orders endpoint")
        self.assertEqual(to.task_name("Add the orders table"), "Add the orders table")

    def test_stray_spaces_and_unbalanced_parens_are_tidied(self):
        self.assertEqual(to.task_name("Fix the handler ( keeps tag ) for develop , today"),
                         "Fix the handler (keeps tag) for develop, today")
        self.assertEqual(to.task_name("Fix the handler) for develop"), "Fix the handler for develop")
        self.assertEqual(to.task_name("Fix the (handler for develop"), "Fix the handler for develop")

    def test_other_kinds_and_dashes(self):
        for tail in ("; unit — x", "; contract – x", "; system - x", "; regression — x", " (e2e: x)"):
            self.assertEqual(to.task_name("Add the guard" + tail), "Add the guard", tail)

    def test_words_like_unit_in_the_name_stay(self):
        self.assertEqual(to.task_name("Add a unit price to the orders table"),
                         "Add a unit price to the orders table")

    def test_parse_title_uses_the_name(self):
        tasks = to.parse(f"- [ ] T8 {SEMI}\n- [ ] T9 {PAREN}\n")
        self.assertEqual(tasks[0]["title"], SHORT)
        self.assertEqual(tasks[1]["title"], "A test of the order id guard")

    def test_build_map_short_name_stops_at_verify(self):
        self.assertEqual(bm.short_name(SEMI, trim=False), SHORT)
        self.assertNotIn("integration", bm.short_name(SEMI))


class WalkEnding(unittest.TestCase):
    def test_golden_ending_shows_the_short_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "orders-api"
            shutil.copytree(SNAP / "spec", root)
            proc = subprocess.run([sys.executable, str(BW), "next", "--root", str(root), "--task", "T4",
                                   "--user", USER], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = json.loads(proc.stdout)
        golden = (SNAP / "walk-ending.txt").read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(out["ending"], golden)
        self.assertIn("resolved on feat/orders-fixes:", out["ending"])
        for leak in ("integration —", "contract —", "system —", "api-doc.yaml"):
            self.assertNotIn(leak, out["ending"])
            self.assertNotIn(leak, out["lead"])

    def test_ready_check_snapshot_shows_the_short_name(self):
        reply = (SNAP / "expected/reply.txt").read_text(encoding="utf-8")
        self.assertIn("- T4 PR 7 takes in develop after PR 6 merges, with the conflicts in app.py and "
                      "tests/test_store.py resolved\n", reply)
        self.assertNotIn("integration —", reply)
        self.assertNotIn("regression", reply)


if __name__ == "__main__":
    unittest.main()
