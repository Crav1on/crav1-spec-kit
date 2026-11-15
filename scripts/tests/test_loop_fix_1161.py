"""1.161.0: the ready check offers a fix for a branch loop and applies it on a yes."""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BUILD_MAP = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"
PLAN_CHECK = SK / "crav1-plan-from-spec/scripts/plan_check.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load(BUILD_MAP, "build_map_1161")

SPEC = """# Orders

## Open questions

None.
"""

PLAN = """# Plan

Reviewed: 2026-11-14, P# open: 0

## Approach

1. feat/orders-cicd: build the new app pipeline. (T9, T10, T11, T12)
2. feat/orders-dev-switch: delete the old app on the agreed day, repoint pipeline 7 to the new app, delete pipeline 24, check the app key on TEST. (T13, T16)
"""

# The generic example: T14 and T15 sit on feat/orders-cicd but wait for T13
# on feat/orders-dev-switch, which waits for T12 on feat/orders-cicd.
TASKS = """# Tasks

- [ ] T9: Pipeline build stage (map: feat/orders-cicd) (after: )
- [ ] T10: Host setup script for the pipelines (map: feat/orders-cicd)
- [ ] T11: Pipeline deploy stage (map: feat/orders-cicd)
- [ ] T12: Pipeline release gate (map: feat/orders-cicd)
- [ ] T13: Delete the old app on the agreed day (map: feat/orders-dev-switch) (after: T12)
- [ ] T14: Repoint pipeline 7 to the new app (map: orders-api feat/orders-cicd) (after: T13)
- [ ] T15: Delete pipeline 24 (map: feat/orders-cicd)
- [ ] T16: Check the app key on TEST (map: feat/orders-dev-switch)
"""

# Only dropping a wait helps: T1 and T2 wait for each other directly.
DROP_ONLY = """# Tasks

- [ ] T1: Record the decision (map: feat/orders-a) (after: T2)
- [ ] T2: Send the note (map: feat/orders-b) (after: T1)
- [ ] T3: Store the record (map: feat/orders-a) (after: )
- [ ] T4: Mail the note (map: feat/orders-b) (after: )
"""

# Three branches in one loop. Moving T3 to feat/orders-b would leave a new
# loop between feat/orders-b and feat/orders-c, and dropping T3's wait on T2
# keeps the ring, so neither is offered.
NEW_LOOP = """# Tasks

- [ ] T1: First part (map: feat/orders-a) (after: )
- [ ] T2: Second part (map: feat/orders-b) (after: T1)
- [ ] T3: Third part (map: feat/orders-a) (after: T2, T4)
- [ ] T4: Fourth part (map: feat/orders-c) (after: )
- [ ] T5: Fifth part (map: feat/orders-c) (after: T2)
"""


def built(tasks, plan=PLAN):
    return bm.build("orders", SPEC, plan, tasks)


def write_slice(base, tasks, plan=PLAN):
    folder = pathlib.Path(base) / "docs" / "specs" / "orders"
    folder.mkdir(parents=True)
    (folder / "spec.md").write_text(SPEC, encoding="utf-8")
    (folder / "plan.md").write_text(plan, encoding="utf-8")
    (folder / "tasks.md").write_text(tasks, encoding="utf-8")
    return folder


def run(*args, cwd=None):
    env = dict(os.environ, PYTHONUTF8="1", CRAV1_NO_REMOTE_CHECK="1")
    return subprocess.run([sys.executable, "-X", "utf8", *map(str, args)], capture_output=True, text=True, cwd=cwd, env=env)


class MoveFix(unittest.TestCase):
    def test_recommended_fix_moves_t14_and_t15_with_the_plain_parts(self):
        result = built(TASKS)
        self.assertEqual(len(result["loops"]), 1)
        fix = result["loops"][0]["fixes"][0]
        self.assertEqual((fix["kind"], fix["tasks"], fix["target"]), ("move", [14, 15], "feat/orders-dev-switch"))
        self.assertEqual(fix["word"], "fix-loop")
        line = result["loop_lines"][1]
        card = result["loops"][0]["card"]
        option = card["options"][0]
        for text in (line, option["text"]):
            # the problem
            self.assertIn("T14 and T15 are on feat/orders-cicd, but they wait for T13 on feat/orders-dev-switch, "
                          "which itself waits for feat/orders-cicd to merge, so the two branches wait for each other.", text)
            # the move
            self.assertIn("Build T14 and T15 on feat/orders-dev-switch instead, right after T13.", text)
            # what stays
            self.assertIn("The tasks stay the same; only the branch and pull request they go into change.", text)
            # the order after
            self.assertIn("Then feat/orders-cicd holds T9-T12 and merges first, and "
                          "feat/orders-dev-switch runs T13, T14, T15, T16.", text)
        self.assertTrue(line.startswith("Recommended fix (say `fix-loop`): "))
        self.assertIn("already describes this work", line)
        self.assertTrue(option["label"].endswith("(Recommended)"))
        self.assertEqual(card["question"], "Two branches wait for each other, so neither can start. How should I fix it?")
        self.assertEqual(card["options"][-1]["word"], "stop")
        self.assertNotIn("Fix one of these lines", "\n".join(result["loop_lines"]))
        self.assertNotIn("Fix one of these lines", result["markdown"])

    def test_alternatives_are_numbered_and_drop_warns_about_order(self):
        fixes = built(TASKS)["loops"][0]["fixes"]
        self.assertEqual([fix["word"] for fix in fixes], ["fix-loop", "fix-loop 2", "fix-loop 3"][: len(fixes)])
        drops = [fix for fix in fixes if fix["kind"] == "drop"]
        self.assertTrue(drops)
        self.assertIn("this changes the build order", drops[0]["detail"])

    def test_every_offered_fix_leaves_no_loop(self):
        for tasks in (TASKS, DROP_ONLY, NEW_LOOP):
            for fix in built(tasks)["loops"][0]["fixes"]:
                after = built(bm.apply_fix_text(tasks, fix))
                self.assertEqual(after["loops"], [], (tasks.splitlines()[2], fix["label"]))


class DropOnly(unittest.TestCase):
    def test_tasks_that_wait_for_each_other_get_only_drop_fixes(self):
        fixes = built(DROP_ONLY)["loops"][0]["fixes"]
        self.assertTrue(fixes)
        self.assertEqual({fix["kind"] for fix in fixes}, {"drop"})
        self.assertIn("Let T", fixes[0]["label"])
        self.assertIn("No task moves branch", fixes[0]["detail"])


class NoNewLoop(unittest.TestCase):
    def test_a_fix_that_makes_a_new_loop_is_not_offered(self):
        fixes = built(NEW_LOOP)["loops"][0]["fixes"]
        offered = [(fix["kind"], tuple(fix["tasks"]), fix.get("dep") or fix["target"]) for fix in fixes]
        self.assertNotIn(("move", (3,), "feat/orders-b"), offered)
        self.assertNotIn(("drop", (3,), 2), offered)
        self.assertIn(("drop", (2,), 1), offered)


class Apply(unittest.TestCase):
    def test_without_yes_nothing_is_written_and_the_card_is_shown(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = write_slice(tmp, TASKS)
            proc = run(WALK, "fix-loop", "--root", folder, "--text")
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual((folder / "tasks.md").read_text(encoding="utf-8"), TASKS)
            self.assertIn("Card: Two branches wait for each other", proc.stdout)
            self.assertIn("1. Build T14 and T15 on feat/orders-dev-switch (Recommended) (`fix-loop`)", proc.stdout)
            self.assertIn("The tasks stay the same; only the branch and pull request they go into change.", proc.stdout)

    def test_yes_writes_map_marks_replaces_the_old_one_and_the_rerun_has_no_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = write_slice(tmp, TASKS)
            proc = run(WALK, "fix-loop", "--root", folder, "--yes", "--text")
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            text = (folder / "tasks.md").read_text(encoding="utf-8")
            t14 = next(line for line in text.splitlines() if "T14:" in line)
            t15 = next(line for line in text.splitlines() if "T15:" in line)
            self.assertEqual(t14.count("(map:"), 1)
            self.assertIn("(map: orders-api feat/orders-dev-switch)", t14)
            self.assertIn("(map: feat/orders-dev-switch)", t15)
            self.assertIn("(after: T13)", t14)
            self.assertIn("No loop left.", proc.stdout)
            self.assertIn("Uncommitted: docs/specs/orders/tasks.md", proc.stdout)
            self.assertNotIn("Loop:", (folder / "build-map.md").read_text(encoding="utf-8"))
            ready = run(WALK, "readiness", "--root", folder, "--skip-sync", "--text")
            self.assertEqual(ready.returncode, 0, ready.stderr)
            self.assertNotIn("Loop:", ready.stdout)
            self.assertEqual((folder / "spec.md").read_text(encoding="utf-8"), SPEC)

    def test_drop_pick_removes_one_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = write_slice(tmp, NEW_LOOP)
            drop = next(fix for fix in built(NEW_LOOP)["loops"][0]["fixes"] if fix["kind"] == "drop")
            proc = run(BUILD_MAP, folder, "--fix-loop", "--pick", str(drop["number"]), "--yes")
            self.assertEqual(proc.returncode, 0, proc.stdout)
            t2 = next(line for line in (folder / "tasks.md").read_text(encoding="utf-8").splitlines() if "T2:" in line)
            self.assertIn("(after: )", t2)

    def test_readiness_offers_the_fix_word(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = write_slice(tmp, TASKS + "- [ ] T20: Other work (map: feat/orders-other) (after: )\n")
            proc = run(WALK, "readiness", "--root", folder, "--skip-sync", "--full")
            payload = json.loads(proc.stdout)
            self.assertIn("Recommended fix (say `fix-loop`)", payload["ending"])
            self.assertIn("`/crav1-tasks-ready-to-build fix-loop`", payload["ending"])
            self.assertEqual(payload["loop_card"]["options"][0]["word"], "fix-loop")


class PlanTime(unittest.TestCase):
    def test_plan_check_order_lists_the_branch_loop_with_the_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = write_slice(tmp, TASKS)
            proc = run(PLAN_CHECK, "order", "--root", folder)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("- Branch loop: feat/orders-cicd and feat/orders-dev-switch wait for each other", proc.stdout)
            self.assertIn("Recommended fix 1 (fix-loop): T14 and T15 are on feat/orders-cicd", proc.stdout)
            self.assertIn("--pick 1 --yes", proc.stdout)


class Docs(unittest.TestCase):
    def test_no_skill_file_tells_the_user_to_hand_edit_a_loop(self):
        bad = []
        for path in list(SK.rglob("*.md")) + list((ROOT / "docs").rglob("*.md")):
            if path.name == "CHANGELOG.md":
                continue
            if "Fix one of these lines in tasks.md" in path.read_text(encoding="utf-8"):
                bad.append(str(path.relative_to(ROOT)))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
