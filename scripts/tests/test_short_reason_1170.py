"""1.170.0: a short failed-verify reason, and plain words for a hold with nobody named.

The ready check's Catch up first line `T6 failed verify: <reason>.` pasted the
whole Verify cell of verify.md, a long paragraph of test names. It now keeps
the cell's opening sentence and the sentence naming the cause, about 200
characters, cut only at a sentence end. A held question or approval with
nobody named said `Waiting for not named yet.`; it now says so plainly.
Generic fixtures.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from test_verify_current_1169 import SPEC_NOT_ASKED, _readiness, _verify

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".cursor/skills/crav1"
SCRIPTS = SKILLS / "crav1-tasks-ready-to-build/scripts"
WALK = SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


we = _load("walk_ending_1170", SCRIPTS / "walk_ending.py")
bm = _load("build_map_1170", SCRIPTS / "build_map.py")
wp = _load("walk_progress_1170", WALK)

LONG_CELL = (
    "fail at PR 7's tip abc1234: pipeline 6 run 251 (Run tests, log 19), 110 failed, 173 passed. "
    "Four of the tests T6's verify rests on fail. "
    "TestReceipts::test_unknown_cursor gets 404 but asserts 200, TestReceipts::test_no_param gets "
    "the full list but asserts an empty page, and two more assert the old status codes. "
    "The 404 for a cursor that matches no stored receipt and the status codes still hold in the code "
    "at the tip (read from app.py and orders/store.py at abc1234), and the no-parameter call still "
    "passes the same text 1970-01-01 00:00:00+00:00 to get_orders_from as at def5678. "
    "9f8e7d6 made the asserts stale. Earlier pass: pytest tests, 283 passed at def5678 (2026-11-12)."
)
SHORT = "four of the tests T6's verify rests on fail at PR 7's tip abc1234. 9f8e7d6 made the asserts stale."


class FailedReason(unittest.TestCase):
    def test_long_cell_keeps_the_opening_and_the_cause(self):
        self.assertEqual(we.failed_reason(LONG_CELL), SHORT)
        self.assertLessEqual(len(we.failed_reason(LONG_CELL)), 200)

    def test_no_test_names_or_run_detail(self):
        reason = we.failed_reason(LONG_CELL)
        for gone in ("TestReceipts", "pipeline 6", "110 failed", "Earlier pass", "1970-01-01"):
            self.assertNotIn(gone, reason)

    def test_short_cell_is_unchanged(self):
        self.assertEqual(we.failed_reason("A3 fails"), "A3 fails.")
        self.assertEqual(we.failed_reason(""), "")

    def test_because_sentence_is_the_cause(self):
        cell = ("Two receipt tests fail. The totals test asserts 10.00 and gets 10.01. "
                "They fail because the total is rounded twice. Earlier pass: 40 passed.")
        self.assertEqual(
            we.failed_reason(cell),
            "two receipt tests fail. They fail because the total is rounded twice.",
        )

    def test_long_cause_is_dropped_not_cut_mid_phrase(self):
        cell = "Two receipt tests fail. " + "The totals " + "and the refunds " * 20 + "broke because of the rounding."
        self.assertEqual(we.failed_reason(cell), "two receipt tests fail.")

    def test_one_long_sentence_is_cut_at_a_clause_end(self):
        cell = ("The export writes the wrong date for every receipt, the totals skip refunds that were "
                "made after midnight, the header misses the store name on the second page, and the footer "
                "has the old address for every receipt printed after the change in October last year.")
        reason = we.failed_reason(cell)
        self.assertLessEqual(len(reason), 200)
        self.assertTrue(reason.endswith("on the second page."), reason)

    def test_catch_up_line(self):
        block = we.catch_up_block("orders-api", failed=[{"task": "T6", "reason": LONG_CELL}])
        self.assertEqual(
            block,
            f"**Catch up first**\nT6 failed verify: {SHORT}\n\nFix T6:\n`/crav1-fix-build-gaps orders-api T6`",
        )

    def test_verify_reply_change_line_is_short_too(self):
        before = {"T6": ("unverified", "not run")}
        after = {"T6": ("failed", LONG_CELL)}
        self.assertEqual(we.verify_changes(before, after), [f"T6 failed: {SHORT.rstrip('.')}"])

    def test_ready_check_end_to_end(self):
        verify = _verify().replace("| A3 fails |", f"| {LONG_CELL} |")
        out = _readiness(verify=verify)
        self.assertIn(f"T6 failed verify: {SHORT}\n\nFix T6:", out["ending"])
        self.assertNotIn("TestReceipts", out["ending"])

    def test_gap_keeps_the_whole_cell(self):
        from test_verify_current_1169 import TASKS
        verify = _verify().replace("| A3 fails |", f"| {LONG_CELL} |")
        gap = wp.verify_gap_from(TASKS, "", verify, "orders-api")
        self.assertEqual(gap["failed"], [{"task": "T6", "reason": LONG_CELL}])


class NobodyNamed(unittest.TestCase):
    def test_held_question_with_nobody_named(self):
        row = {"reason": 'open question "Which locale is on the receipt?" (recorded)', "who": "not named yet"}
        self.assertEqual(bm.held_phrase(row), 'open question "Which locale is on the receipt?" Nobody is named to answer it yet.')
        row["who"] = ""
        self.assertEqual(bm.held_phrase(row), 'open question "Which locale is on the receipt?" Nobody is named to answer it yet.')

    def test_held_question_with_someone_named(self):
        row = {"reason": 'open question "Which locale is on the receipt?" (recorded)', "who": "the partner"}
        self.assertEqual(bm.held_phrase(row), 'open question "Which locale is on the receipt?" Waiting for the partner.')

    def test_approval_with_nobody_named(self):
        row = {"reason": 'approval needed "Turn off the old pipelines."', "who": None}
        self.assertEqual(bm.held_phrase(row), 'approval "Turn off the old pipelines." Nobody is named to give it yet.')

    def test_waiting_line(self):
        hits = [{"task": "T1", "who": wp.NOT_NAMED}, {"task": "T2", "who": "the partner"}]
        self.assertEqual(wp._wait_phrase(hits, "open questions"),
                         "Waiting: 2 tasks wait on open questions (the partner; nobody named for 1).")

    def test_ready_check_never_says_not_named(self):
        text = _readiness(spec=SPEC_NOT_ASKED)["ending"]
        self.assertIn('at the gateway?" Nobody is named to answer it yet.', text)
        self.assertNotIn("not named yet", text)
        self.assertNotIn("Waiting for not", text)


if __name__ == "__main__":
    unittest.main()
