"""1.168.0: the verify reply gets the shared ending.

/crav1-verify-build-against-spec prints a brief reply built by
walk_ending.py --verify: the header, a Result line with counts, one line
per changed task, Run next (a Catch up first block, then the step with its
reason once, the label on its own line and the command alone in its code
span), Waiting, and Report. No Next line. Generic fixtures only.
"""

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
SKILLS = ROOT / ".cursor/skills/crav1"
VERIFY = SKILLS / "crav1-verify-build-against-spec"
SCRIPT = SKILLS / "crav1-tasks-ready-to-build/scripts/walk_ending.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


we = _load("walk_ending_1168", SCRIPT)


def verify_md(rows, counts):
    tldr = "\n".join(
        f"| {label} | {counts.get(key, 0)} | |" for key, label, _w in we.VERIFY_STATUSES
    )
    table = "\n".join(f"| {tid} | {title} | {status} | {check} |" for tid, title, status, check in rows)
    return (
        "# Verify\n\nDate: 2026-11-15\n\n## TL;DR\n\n| | Count | Ids |\n| --- | --- | --- |\n"
        f"{tldr}\n\nNext: `/crav1-fix-build-gaps`, because a verify id is not proved yet.\n\n"
        "## Tasks — overview (dependency order)\n\n| T# | Title | Status | Verify |\n| --- | --- | --- | --- |\n"
        f"{table}\n\n## Acceptance — details\n\n| Id | Acceptance | Evidence | Result | Task |\n"
        "| --- | --- | --- | --- | --- |\n| A1 | x | y | pass | T4 |\n"
    )


BEFORE = verify_md(
    [
        ("T4", "Merge main", "Claimed done, unverified", "not run"),
        ("T6", "Orders paging", "Implemented, verified", "paging tests pass"),
        ("T9", "Orders CI/CD infra", "Not implemented", ""),
        ("T44", "Old row", "Not implemented", ""),
    ],
    {"verified": 1, "not_implemented": 2, "unverified": 1},
)
AFTER = verify_md(
    [
        ("T4", "Merge main", "Implemented, verified", "pipeline 6 passed on develop"),
        ("T6", "Orders paging", "**Implemented, verify failed**", "4 paging tests fail at the PR's tip"),
        ("T9", "Orders CI/CD infra", "Not implemented", ""),
    ],
    {"verified": 1, "failed": 1, "not_implemented": 1, "no_task": 1},
)
TASKS = "# Tasks\n\n- [x] T4: Merge main\n- [x] T6: Orders paging\n- [ ] T9: Orders CI/CD infra\n"
STEP = {
    "reason": "T6's four tests fail on stale asserts at the PR's tip.",
    "label": "Fix T6:",
    "command": "/crav1-fix-build-gaps orders-api T6",
}


def _commands(text):
    return re.findall(r"^`[^`]+`$", text, re.M)


class Parsing(unittest.TestCase):
    def test_counts_and_result_line(self):
        counts = we.verify_counts(AFTER)
        self.assertEqual(counts["failed"], 1)
        self.assertEqual(
            we.result_line(counts),
            "Result: 1 verified, 1 failed, 1 not implemented, 1 acceptance with no task.",
        )
        self.assertEqual(we.result_line({}), "Result: no tasks checked.")

    def test_tick_pending_is_not_verified(self):
        self.assertEqual(we.status_key("Implemented, verified, tick pending"), "tick_pending")
        self.assertEqual(we.status_key("Claimed done, unverified (on feat/x, not checked out)"), "unverified")

    def test_changes_one_line_per_changed_task_and_dropped_row(self):
        lines = we.verify_changes(we.verify_tasks(BEFORE), we.verify_tasks(AFTER), ["T4", "T6", "T9"])
        self.assertEqual(
            lines,
            [
                "T4 verified: pipeline 6 passed on develop",
                "T6 failed: 4 paging tests fail at the PR's tip",
                "T44 row dropped: not in tasks.md",
            ],
        )

    def test_no_previous_verify_no_change_lines(self):
        self.assertEqual(we.verify_changes({}, we.verify_tasks(AFTER)), [])


class Reply(unittest.TestCase):
    def reply(self, **kw):
        base = dict(slug="orders-api", counts=we.verify_counts(AFTER), changes=["T6 failed: x"], steps=[STEP])
        base.update(kw)
        return we.verify_reply(**base)

    def test_shape_and_order(self):
        out = self.reply(
            catch_up={"uncommitted": ["verify.md"], "plan_notes": ["The plan says T24 to T26 may belong to another slice"]},
            waiting=["T5 merges after a review."],
        )
        heads = [out.index(h) for h in ("Verify — orders-api", "Result:", "Changed since the last verify:",
                                        "Run next:", "**Catch up first**", "Fix T6:", "Waiting:", "Report:")]
        self.assertEqual(heads, sorted(heads))
        self.assertTrue(out.endswith("Report: docs/specs/orders-api/verify.md"))
        self.assertNotRegex(out, r"(?m)^Next:")
        self.assertNotIn("Uncommitted:", out)
        self.assertNotIn("| --- |", out)

    def test_step_reason_once_label_then_command_alone(self):
        out = self.reply()
        self.assertIn(
            "T6's four tests fail on stale asserts at the PR's tip.\n\nFix T6:\n`/crav1-fix-build-gaps orders-api T6`",
            out,
        )
        self.assertEqual(out.count("stale asserts"), 1)
        for line in _commands(out):
            self.assertEqual(line.count("`"), 2)

    def test_catch_up_commands(self):
        block = we.verify_catch_up_block(
            slug="orders-api",
            uncommitted=["verify.md"],
            plan_notes=["The plan says T24 to T26 may belong to another slice"],
        )
        self.assertTrue(block.startswith("**Catch up first**\n"))
        self.assertEqual(
            _commands(block),
            ["`/crav1-tighten-plan orders-api`", "`/crav1-finalize-commit`", "`git push`"],
        )
        self.assertIn("Settle the plan note in the plan:\n`/crav1-tighten-plan orders-api`", block)
        self.assertNotIn("spec.md", block)
        self.assertIn("Commit verify.md:\n`/crav1-finalize-commit`\nThen push the specs repo:\n`git push`", block)
        self.assertNotIn("by hand", block.lower())

    def test_unticked_is_not_a_state_key(self):
        state = {"root": "/nonexistent/orders-api", "unticked": ["A5"], "uncommitted": [], "ahead": 0}
        self.assertNotIn("unticked", we.verify_state(state)["catch_up"])
        with self.assertRaises(TypeError):
            we.verify_catch_up_block(unticked=["A5"])

    def test_catch_up_push_only_and_empty(self):
        self.assertIn("Push the specs repo (2 commits ahead):\n`git push`", we.verify_catch_up_block(ahead=2))
        self.assertEqual(we.verify_catch_up_block(), "")

    def test_catch_up_leads_with_rule_before_step(self):
        out = self.reply(catch_up={"uncommitted": ["verify.md"]})
        self.assertIn("Run next:\n\n**Catch up first**\n", out)
        self.assertIn("`git push`\n\n---\n\nT6's four tests", out)

    def test_nothing_needed_and_walk(self):
        done = self.reply(steps=[], changes=[])
        self.assertIn("Run next:\n\nNothing needed now.", done)
        walk = self.reply(walk=True, catch_up={"uncommitted": ["verify.md"]})
        self.assertNotIn("Run next:", walk)

    def test_branch_heading_steps(self):
        out = self.reply(steps=[
            {"heading": "feat/orders-cicd", "reason": "T9 is the first task that can start.", "label": "Run T9:",
             "command": "/crav1-build-walk orders-api T9"},
            {"heading": "feat/orders-fixes", "reason": "T43 is the first task that can start.", "label": "Run T43:",
             "command": "/crav1-build-walk orders-api T43"},
        ])
        self.assertIn("**feat/orders-cicd**\nT9 is the first task that can start.\n\nRun T9:\n`/crav1-build-walk orders-api T9`\n\n---\n\n**feat/orders-fixes**", out)


class Cli(unittest.TestCase):
    def test_verify_cli_reads_files_and_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            folder = repo / "docs/specs/orders-api"
            folder.mkdir(parents=True)
            (folder / "tasks.md").write_text(TASKS, encoding="utf-8")
            (folder / "verify.md").write_text(BEFORE, encoding="utf-8")
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            subprocess.run(git + ["commit", "-qm", "init"], cwd=repo, check=True)
            (folder / "verify.md").write_text(AFTER, encoding="utf-8")
            state = repo / "state.json"
            state.write_text(json.dumps({"root": str(folder), "steps": [STEP]}), encoding="utf-8")
            wrapper = VERIFY / "scripts/walk_ending.py"
            out = subprocess.run(
                [sys.executable, "-X", "utf8", str(wrapper), "--verify", str(state)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            ).stdout
            self.assertIn("Result: 1 verified, 1 failed, 1 not implemented, 1 acceptance with no task.", out)
            self.assertIn("- T44 row dropped: not in tasks.md", out)
            self.assertIn("verify.md is not committed.", out)
            self.assertIn("Commit verify.md:\n`/crav1-finalize-commit`", out)
            self.assertNotRegex(out, r"(?m)^Next:")
            full = json.loads(state.read_text())
            full["full"] = True
            state.write_text(json.dumps(full), encoding="utf-8")
            long = subprocess.run(
                [sys.executable, "-X", "utf8", str(wrapper), "--verify", str(state)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            ).stdout
            self.assertIn("## Tasks — overview (dependency order)", long)
            self.assertNotRegex(long, r"(?m)^Next:")


class SkillText(unittest.TestCase):
    def test_skill_routes_through_the_script_and_reads_less(self):
        text = (VERIFY / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("scripts/walk_ending.py --verify", text)
        self.assertIn("references/reply.md", text)
        self.assertIn("Do not open `build-map.md`, `claims.md`, `walk-progress.md` or a log", text)
        self.assertNotIn("One `Next` line", text)
        self.assertIn("`full`", text)
        self.assertLessEqual(len(text.split()), 1416)

    def test_case_files_have_no_next_line(self):
        for path in sorted((VERIFY / "references").glob("next-*.md")):
            body = path.read_text(encoding="utf-8")
            self.assertNotIn("Next:", body, path.name)
            self.assertIn("1.168.0", body, path.name)

    def test_reply_reference_has_no_acceptance_tick(self):
        body = (VERIFY / "references/reply.md").read_text(encoding="utf-8")
        self.assertNotIn("unticked", body)
        self.assertNotIn("/crav1-tighten-spec", body)
        for word in ("contoso", "person a"):
            self.assertNotIn(word, body.lower())

    def test_tighten_spec_is_unchanged(self):
        body = (SKILLS / "crav1-tighten-spec/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("1.168.0", body)

    def test_wrapper_matches_build_walk_wrapper(self):
        a = (VERIFY / "scripts/walk_ending.py").read_bytes()
        b = (SKILLS / "crav1-build-walk/scripts/walk_ending.py").read_bytes()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
