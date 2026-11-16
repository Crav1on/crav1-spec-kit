"""1.167.0: what the user can fix now leads Run next as a Catch up first block.

verify.md behind tasks.md, a verify.md row for a T# that is not in tasks.md,
and a specs repo ahead of origin are no longer Waiting lines. They are one
`**Catch up first**` block at the top of Run next, before the branch blocks,
in the branch-block layout: a bold heading, one or two plain sentences, then
each command alone in its code span under its label line, and a `---` rule
before the first branch block. /crav1-verify-build-against-spec both checks
the behind tasks and drops an orphan row, so those share one command. No
block when nothing is behind. Generic fixtures only.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".cursor/skills/crav1"
SCRIPTS = SKILLS / "crav1-tasks-ready-to-build/scripts"
WALK = SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BUILD_WALK = SKILLS / "crav1-build-walk/scripts"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


we = _load("walk_ending_1167", SCRIPTS / "walk_ending.py")
wp = _load("walk_progress_1167", WALK)

BRANCH = we.branch_block(
    "feat/orders-cicd",
    ["T9 Orders CI/CD: infra Bicep", "T10 Orders CI/CD: cd pipeline (waits on T9)"],
    slug="orders-api",
    about="The orders CI/CD branch, cut from develop after billing-ops.",
)

TASKS = """# Tasks

- [x] T4 Orders: receipt export
- [x] T7 Orders: retry the receipt upload
- [ ] T9 Orders CI/CD: infra Bicep
"""

VERIFY = """# Verify

## TL;DR

Next: /crav1-build-walk orders-api T9

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T4 | Orders: receipt export | Not implemented | — |
| T7 | Orders: retry the receipt upload | Not implemented | — |
| T44 | Orders: an old task | Implemented, verified | pass |
"""


def _commands(text):
    return [line for line in text.splitlines() if line.startswith("`")]


class CatchUpBlock(unittest.TestCase):
    def test_none_when_nothing_is_behind(self):
        self.assertEqual(we.catch_up_block("orders-api"), "")
        self.assertEqual(we.catch_up_block("orders-api", [], [], 0), "")
        ending = we.compose(run=[BRANCH], catch_up=we.catch_up_block("orders-api"))
        self.assertNotIn("Catch up first", ending)
        self.assertTrue(ending.startswith("Run next:\n\n**feat/orders-cicd**"))

    def test_verify_behind(self):
        block = we.catch_up_block("orders-api", behind=["T7", "T4"])
        self.assertEqual(
            block,
            "**Catch up first**\n"
            "verify.md is behind for T4 and T7.\n\n"
            "Check T4 and T7 against the spec:\n"
            "`/crav1-verify-build-against-spec orders-api`",
        )

    def test_orphan_row(self):
        block = we.catch_up_block("orders-api", orphans=["T44"])
        self.assertIn("verify.md has a row for T44, which is not in tasks.md.", block)
        self.assertIn("Remove the T44 row (it is in verify.md but not in tasks.md):\n"
                      "`/crav1-verify-build-against-spec orders-api`", block)
        plural = we.catch_up_block("orders-api", orphans=["T45", "T44"])
        self.assertIn("rows for T44 and T45, which are not in tasks.md.", plural)
        self.assertIn("Remove the T44 and T45 rows (they are in verify.md", plural)

    def test_behind_and_orphan_share_one_command(self):
        block = we.catch_up_block("orders-api", behind=["T4", "T7"], orphans=["T44"])
        self.assertIn(
            "verify.md is behind for T4 and T7, and it has a row for T44, which is not in tasks.md.",
            block,
        )
        self.assertEqual(_commands(block), ["`/crav1-verify-build-against-spec orders-api`"])
        self.assertIn("Check T4 and T7 against the spec and remove the T44 row:", block)

    def test_repo_ahead(self):
        block = we.catch_up_block("orders-api", ahead=2)
        # 1.175.0: the label says it once; no sentence repeats it.
        self.assertEqual(block.count("ahead of origin"), 1)
        self.assertIn("Push the specs repo, which is 2 commits ahead of origin:\n`git push`", block)
        one = we.catch_up_block(None, ahead=1)
        self.assertIn("Push the specs repo, which is 1 commit ahead of origin:", one)

    def test_each_command_alone_under_its_label(self):
        block = we.catch_up_block("orders-api", behind=["T4"], orphans=["T44"], ahead=2)
        lines = block.splitlines()
        self.assertEqual(lines[0], "**Catch up first**")
        self.assertEqual(len(_commands(block)), 2)
        for index, line in enumerate(lines):
            if line.startswith("`"):
                self.assertRegex(line, r"^`[^`]+`$")
                self.assertTrue(lines[index - 1].endswith(":"), lines[index - 1])
        # One or two plain sentences, no person and no hand-edit advice.
        summary = lines[1]
        self.assertLessEqual(len(re.findall(r"[.!?](?:\s|$)", summary)), 2)
        self.assertNotIn("edit", block.lower())

    def test_leads_run_next_with_a_rule_before_the_first_branch(self):
        block = we.catch_up_block("orders-api", behind=["T4"])
        ending = we.compose(run=[BRANCH], catch_up=block, waiting=["Waiting: person A reviews PR 71."])
        self.assertTrue(ending.startswith("Run next:\n\n**Catch up first**\n"))
        self.assertIn("`/crav1-verify-build-against-spec orders-api`\n\n---\n\n**feat/orders-cicd**", ending)
        self.assertLess(ending.index("**feat/orders-cicd**"), ending.index("Waiting: person A"))

    def test_compose_takes_a_dict_too(self):
        ending = we.compose(run=[BRANCH], catch_up={"slug": "orders-api", "ahead": 1})
        self.assertIn("**Catch up first**", ending)
        self.assertIn("`git push`", ending)

    def test_block_alone_when_no_branch_is_ready(self):
        ending = we.compose(run=None, catch_up={"slug": "orders-api", "behind": ["T4"]})
        self.assertTrue(ending.startswith("Run next:\n\n**Catch up first**"))
        self.assertNotIn("---", ending)


class ReadyCheckWiring(unittest.TestCase):
    def test_gap_and_sync_become_the_block(self):
        gap = wp.verify_gap_from(TASKS, "", VERIFY, "orders-api")
        self.assertEqual(gap["tasks"], ["T4", "T7"])
        self.assertEqual(gap["orphan_tasks"], ["T44"])
        self.assertNotIn("/crav1-tighten-plan", gap["orphan_waiting"])
        sync = {"state": "ahead", "ahead": 2}
        block = wp.catch_up_for("orders-api", gap, sync)
        self.assertIn("verify.md is behind for T4 and T7, and it has a row for T44", block)
        self.assertEqual(
            _commands(block),
            ["`/crav1-verify-build-against-spec orders-api`", "`git push`"],
        )

    def test_none_from_a_clean_gap(self):
        self.assertEqual(wp.catch_up_for("orders-api", {"behind": False, "tasks": [], "orphan_tasks": []}, {"state": "in-step"}), "")

    def test_compose_ending_puts_it_first_and_keeps_waiting_for_people(self):
        block = wp.catch_up_for("orders-api", {"behind": True, "tasks": ["T4"], "orphan_tasks": []}, {})
        ending = wp.compose_ending(
            "ready-partial", [BRANCH], ["- T25 held — Waiting for person A."],
            ["Waiting: person A answers the question."], ["/crav1-build-tasks builds one task without the walk."],
            None, None, catch_up=block,
        )
        self.assertTrue(ending.startswith("Run next:\n\n**Catch up first**"))
        self.assertLess(ending.index("**feat/orders-cicd**"), ending.index("Held:"))
        self.assertNotIn("verify.md is behind tasks.md", ending)
        self.assertIn("Waiting: person A answers the question.", ending)

    def test_not_ready_drops_the_duplicate_verify_and_push_entries(self):
        gap = {"behind": True, "tasks": ["T4"], "orphan_tasks": []}
        sync = {"state": "ahead", "ahead": 1}
        args = ("not-ready", "orders-api", [], [], None, gap, sync, None, {"needs_verify": 1}, None, False)
        self.assertEqual(len(wp.not_ready_run(*args)), 1)
        self.assertEqual(wp.not_ready_run(*args, catch_up=True), [])


class WalkWiring(unittest.TestCase):
    def test_build_walk_ending_leads_with_it(self):
        bw = _load("build_walk_1167", BUILD_WALK / "build_walk.py")
        out = bw.next_for({
            "mode": "grouping", "branches": [], "slug": "orders-api",
            "catch_up": {"slug": "orders-api", "ahead": 1},
        })
        self.assertTrue(out["ending"].startswith("Run next:\n\n**Catch up first**"))
        self.assertIn("`git push`", out["ending"])

    def test_branch_run_passes_it_on(self):
        source = (BUILD_WALK / "branch_run.py").read_text(encoding="utf-8")
        self.assertIn('catch_up=state.get("catch_up")', source)


if __name__ == "__main__":
    unittest.main()
