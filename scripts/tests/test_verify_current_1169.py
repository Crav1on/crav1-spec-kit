"""1.169.0: a fresh verify is current, and Needs verify never hides ready branches.

Right after a verify that wrote T4 and T7 Verified and T6 Failed (all ticked),
an older TL;DR `Next:` line naming T4, T6 and T7 made the ready check say
verify.md was behind for all three, and the failed T6 (Needs verify) forced
not-ready, so Run next lost every branch block. Now a Verified or Failed row
is current, a failed task is `Fix T6:` with /crav1-fix-build-gaps in the
Catch up first block, ready branches keep their blocks after it, and
questions not asked yet stay a Run next entry after them. Generic fixtures.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".cursor/skills/crav1"
SCRIPTS = SKILLS / "crav1-tasks-ready-to-build/scripts"
WALK = SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-11T12:00:00+00:00"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


we = _load("walk_ending_1169", SCRIPTS / "walk_ending.py")
wp = _load("walk_progress_1169", WALK)

PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. **Readme** — READMEs describe the receipts table and audit rows. (T5)
2. **Orders CI/CD** — infra and a cd pipeline for the orders service. (T9, T10)
3. **Partner TLS** — trust the certificate header only from the chosen front end. (T25)

## Risks
"""
SPEC_ASKED = """# Spec

## Open questions

- For the 2.0 rollout, where does TLS end, at the app host or at the gateway?
  - Asked: 2026-10-10, mail to the platform team.
  - Blocks: T25
"""
SPEC_NOT_ASKED = SPEC_ASKED.replace("  - Asked: 2026-10-10, mail to the platform team.\n", "")
TASKS = """# Tasks

- [x] T4: Orders: receipt export (branch: feat/orders-receipts) (after: )
- [x] T6: Orders: audit rows (branch: feat/orders-receipts) (after: T4)
- [x] T7: Orders: retry the receipt upload (branch: feat/orders-receipts) (after: T4)
- [ ] T5: READMEs describe the receipts table and audit rows (branch: feat/orders-api-readme) (after: )
- [ ] T9: Orders CI/CD: infra Bicep for dev, test and prod (branch: feat/orders-cicd) (after: )
- [ ] T10: Orders CI/CD: cd pipeline with three stages (branch: feat/orders-cicd) (after: T9)
- [ ] T25: Trust the certificate header only from the front end (branch: feat/orders-mtls) (after: )
"""
NEXT = "Next: `/crav1-fix-build-gaps orders-api T6`, because the audit rows test fails. T4 and T7 are verified.\n\n"
VERIFY = """# Verify

## TL;DR

| | Count | Ids |
| --- | --- | --- |
| Implemented, verified | 2 | T4, T7 |
| Implemented, verify failed | 1 | T6 |

{next}## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T4 | Orders: receipt export | Implemented, verified | pass |
| T7 | Orders: retry the receipt upload | {t7} | pass |
| T6 | Orders: audit rows | Implemented, verify failed | A3 fails |
"""


def _verify(next_line=True, t7="Implemented, verified"):
    return VERIFY.format(next=NEXT if next_line else "", t7=t7)


def _readiness(spec=SPEC_ASKED, verify=None):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "orders-api"
        root.mkdir()
        for name, text in (("spec.md", spec), ("plan.md", PLAN), ("tasks.md", TASKS),
                           ("verify.md", verify if verify is not None else _verify())):
            (root / name).write_text(text, encoding="utf-8")
        subprocess.run(
            [sys.executable, str(WALK), "record", "--root", str(root), "--slice", "docs/specs/orders-api",
             "--step", "resolve-open-questions", "--result", "done", "--when", WHEN, "--yes"],
            capture_output=True, text=True, check=True,
        )
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(WALK), "readiness", "--root", str(root), "--full"],
            capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode != 0:
            raise AssertionError(proc.stderr + proc.stdout)
        return json.loads(proc.stdout)


class StaleNext(unittest.TestCase):
    def test_verified_and_failed_rows_are_current(self):
        gap = wp.verify_gap_from(TASKS, "", _verify(), "orders-api")
        self.assertFalse(gap["behind"])
        self.assertEqual(gap["tasks"], [])
        self.assertIsNone(gap["stale_next"])
        self.assertEqual(gap["failed"], [{"task": "T6", "reason": "A3 fails"}])

    def test_an_unverified_row_is_still_behind(self):
        gap = wp.verify_gap_from(TASKS, "", _verify(t7="Claimed done, unverified"), "orders-api")
        self.assertTrue(gap["behind"])
        self.assertEqual(gap["tasks"], ["T7"])

    def test_a_ticked_task_with_no_row_is_behind(self):
        verify = _verify().replace("| T7 | Orders: retry the receipt upload | Implemented, verified | pass |\n", "")
        gap = wp.verify_gap_from(TASKS, "", verify, "orders-api")
        self.assertEqual(gap["tasks"], ["T7"])

    def test_not_implemented_still_behind_without_a_next_line(self):
        gap = wp.verify_gap_from(TASKS, "", _verify(next_line=False, t7="Not implemented"), "orders-api")
        self.assertEqual(gap["tasks"], ["T7"])

    def test_template_has_no_next_line(self):
        for path in (ROOT / "docs/specs/_template/verify.md",
                     SKILLS / "crav1-verify-build-against-spec/assets/verify.md",
                     ROOT / ".cursor/agent-assets/crav1-spec-reviewer-agent/verify.md"):
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(line.startswith("Next:") for line in text.splitlines()), path)


class FailedFix(unittest.TestCase):
    def test_catch_up_block_fix_line(self):
        block = we.catch_up_block("orders-api", failed=[{"task": "T6", "reason": "A3 fails"}])
        self.assertEqual(
            block,
            "**Catch up first**\nT6 failed verify: A3 fails.\n\nFix T6:\n`/crav1-fix-build-gaps orders-api T6`",
        )

    def test_behind_and_failed_share_one_block(self):
        block = we.catch_up_block("orders-api", ["T7"], failed=["T6"])
        self.assertIn("verify.md is behind for T7. T6 failed verify.", block)
        self.assertIn("Check T7 against the spec:\n`/crav1-verify-build-against-spec orders-api`\nFix T6:\n`/crav1-fix-build-gaps orders-api T6`", block)

    def test_nothing_failed_is_unchanged(self):
        self.assertEqual(we.catch_up_block("orders-api", failed=[]), "")


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = _readiness()
        cls.text = cls.out["ending"]

    def test_not_behind(self):
        self.assertFalse(self.out["verify_behind"])
        self.assertNotIn("verify.md is behind", self.text)
        self.assertNotIn("/crav1-verify-build-against-spec", self.text)

    def test_failed_task_goes_to_fix(self):
        self.assertTrue(self.text.startswith(
            "Run next:\n\n**Catch up first**\nT6 failed verify: A3 fails.\n\nFix T6:\n`/crav1-fix-build-gaps orders-api T6`\n\n---\n\n**feat/orders-api-readme**"
        ), self.text)

    def test_ready_branches_still_show(self):
        self.assertEqual(self.out["result"], "ready-partial")
        self.assertEqual(self.out["can_start"], ["T5", "T9"])
        self.assertIn("**feat/orders-cicd**", self.text)
        self.assertIn("Run the whole branch:\n`/crav1-build-walk orders-api feat/orders-cicd`", self.text)
        self.assertIn("Run only T9, the first task:\n`/crav1-build-walk orders-api T9`", self.text)
        self.assertIn("Run T5:\n`/crav1-build-walk orders-api T5`", self.text)
        self.assertIn("Held:", self.text)

    def test_questions_not_asked_stay_an_entry_after_the_branches(self):
        text = _readiness(spec=SPEC_NOT_ASKED)["ending"]
        run_next = text.split("Held:")[0]
        self.assertIn("**feat/orders-cicd**", run_next)
        self.assertIn("`/crav1-show-or-ask-open-questions orders-api`\nthe questions are not asked yet.", run_next)
        self.assertLess(run_next.index("**feat/orders-cicd**"), run_next.index("/crav1-show-or-ask-open-questions"))

    def test_only_needs_verify_left_is_not_ready(self):
        rows = [{"task": "T6", "bucket": "needs-verify", "reason": "verify failed"}]
        hits = [wp.classify(rows[0])]
        self.assertEqual(wp.slice_result(rows, hits)[0], "not-ready")
        self.assertIn("/crav1-fix-build-gaps", hits[0]["why"])

    def test_needs_verify_with_tasks_to_start_is_partial(self):
        rows = [
            {"task": "T6", "bucket": "needs-verify", "reason": "claimed done, unverified"},
            {"task": "T5", "bucket": "ready", "reason": ""},
        ]
        hits = [hit for hit in (wp.classify(row) for row in rows) if hit]
        self.assertEqual(wp.slice_result(rows, hits)[0], "ready-partial")


class VerifyFull(unittest.TestCase):
    def test_full_text_still_drops_an_old_next_line(self):
        text = we._full_text(_verify())
        self.assertIn("## TL;DR", text)
        self.assertIn("| T6 | Orders: audit rows | Implemented, verify failed | A3 fails |", text)
        self.assertNotIn("Next:", text)


if __name__ == "__main__":
    unittest.main()
