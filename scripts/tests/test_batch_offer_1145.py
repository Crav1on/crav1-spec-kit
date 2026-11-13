"""1.145.0: a batch card is built from the findings table, and not without its rows."""

from __future__ import annotations

import importlib.util
import inspect
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-tighten-plan/scripts/batch_offer.py"

ROWS = [
    {
        "id": "P4",
        "issue": "tasks miss the 400 path",
        "options": "A add a test; B keep",
        "recommendation": "A add a test",
    },
    {
        "id": "P11",
        "issue": "the empty list is already covered",
        "options": "A add a test; keep",
        "recommendation": "keep",
    },
]

# Every batch or all-at-once card path. Each must name the table in this reply.
BATCH_PATHS = (
    ".cursor/skills/crav1/crav1-tighten-plan/SKILL.md",
    ".cursor/skills/crav1/crav1-tighten-spec/SKILL.md",
    ".cursor/skills/crav1/crav1-tighten-spec/references/pacing.md",
    ".cursor/skills/crav1/crav1-resolve-open-questions/SKILL.md",
    ".cursor/skills/crav1/crav1-resolve-open-questions/references/apply.md",
    ".cursor/skills/crav1/crav1-resolve-open-questions/references/conflicts.md",
    ".cursor/skills/crav1/crav1-add-to-spec/branches/dump/BRANCH.md",
    ".cursor/skills/crav1/crav1-add-to-spec/branches/code-change/BRANCH.md",
    ".cursor/skills/crav1/crav1-add-to-spec/branches/meeting/references/one-batch.md",
    ".cursor/skills/crav1/crav1-add-to-spec/references/sources-flagged.md",
    ".cursor/skills/crav1/crav1-add-to-spec/references/sources-mail.md",
    ".cursor/skills/crav1/crav1-suggest-tests-for-code/SKILL.md",
    ".cursor/skills/crav1/crav1-existing-to-specs/branches/repos-and-bundle/BRANCH.md",
    ".cursor/skills/crav1/crav1-what-do-we-know-about-this/references/walk.md",
    ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/references/steps.md",
    "docs/reference/question-cards.md",
)


def load_offer():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("batch_offer_1145", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


offer = load_offer()


class BatchOffer(unittest.TestCase):
    def test_card_text_takes_the_table_not_the_items(self):
        params = list(inspect.signature(offer.card_text).parameters)
        self.assertEqual(params, ["title", "table"])
        self.assertFalse(hasattr(offer, "card_text_from_items"))

    def test_card_text_cannot_be_built_without_rows(self):
        header = "| Id | Issue | Options | Recommendation |\n| --- | --- | --- | --- |\n"
        for table in ("", header, "no table here"):
            with self.assertRaises(offer.BatchOfferError) as caught:
                offer.card_text("Tighten-plan batch", table)
            self.assertIn("needs the findings table rows", str(caught.exception))
            self.assertNotIn("Yes applies", str(caught.exception))
        with self.assertRaises(offer.BatchOfferError):
            offer.offer("Tighten-plan batch", [])
        with self.assertRaises(offer.BatchOfferError):
            offer.render_table([])

    def test_a_row_missing_a_column_does_not_build_a_card(self):
        broken = [dict(ROWS[0])]
        del broken[0]["recommendation"]
        with self.assertRaises(offer.BatchOfferError):
            offer.offer("Tighten-plan batch", broken)

    def test_offer_prints_the_table_then_a_self_contained_card(self):
        text = offer.offer("Tighten-plan batch", ROWS)
        table, card = text.split("\n\n", 1)
        self.assertLess(text.index("| P4 |"), text.index("Card:"))
        self.assertIn("| Id | Issue | Options | Recommendation |", table)
        self.assertIn("| P4 | tasks miss the 400 path | A add a test; B keep | A add a test |", table)
        self.assertIn("| P11 | the empty list is already covered | A add a test; keep | keep |", table)
        self.assertIn(
            "Card: Tighten-plan batch. Yes applies every recommendation: "
            "P4 tasks miss the 400 path: A add a test; "
            "P11 the empty list is already covered: keep.",
            card,
        )
        self.assertNotIn("table above", text.lower())
        self.assertNotIn("the table recommends", text.lower())

    def test_card_text_reads_only_the_table_that_was_passed(self):
        table = offer.render_table(ROWS[:1])
        card = offer.card_text("Tighten-plan batch", table)
        self.assertIn("P4 tasks miss the 400 path: A add a test", card)
        self.assertNotIn("P11", card)

    def test_cli_without_items_prints_no_card(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--title", "Tighten-plan batch"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("Card:", proc.stdout)
        self.assertNotIn("| P4 |", proc.stdout)

    def test_cli_with_rows_prints_table_and_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            path.write_text(json.dumps(ROWS), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--title", "Tighten-plan batch", "--items", str(path)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(proc.stdout.startswith("| Id | Issue | Options | Recommendation |"))
        self.assertIn("P4 tasks miss the 400 path: A add a test", proc.stdout)
        self.assertLess(proc.stdout.index("| P4 |"), proc.stdout.index("Card:"))

    def test_cli_empty_list_exits_without_a_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            path.write_text("[]", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--title", "Tighten-plan batch", "--items", str(path)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Card:", proc.stdout)
        self.assertIn("needs the findings table rows", proc.stderr)

    def test_batch_paths_print_the_table_before_the_card(self):
        for rel in BATCH_PATHS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("findings table", text, rel)
            self.assertIn("this reply", text, rel)
            self.assertIn("table above", text, rel)
            self.assertIn("Never ask the card without the table", text, rel)

    def test_walk_endings_print_held_lines_and_do_not_point_above(self):
        """1.150.0: an ending prints held lines. It does not point at earlier output."""
        files = (
            ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/SKILL.md",
            ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/references/readiness.md",
            ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/references/progress.md",
        )
        pointer = re.compile(
            r"listed above|as listed|earlier output|already named|"
            r"the (?:table|list|lines|tasks|held).{0,40}\babove\b",
            re.I,
        )
        ban = re.compile(r"\b(never|do not|don't|does not)\b", re.I)
        for rel in files:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for line in text.splitlines():
                if pointer.search(line):
                    self.assertRegex(line, ban, f"{rel}: {line}")
        ready = (ROOT / files[1]).read_text(encoding="utf-8")
        self.assertIn("Print the script's `ending`", ready)
        self.assertIn("held line", ready)
        self.assertIn("Run next:", ready)
        self.assertIn("Do not say `above`, `listed above`, or earlier output.", ready)
        self.assertNotIn("already named", ready)

    def test_the_shared_rule_names_the_command_and_the_example(self):
        page = (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("P4 tasks miss the 400 path: A add a test", page)
        self.assertIn(
            '<interpreter> -X utf8 <skill crav1-tighten-plan>/scripts/batch_offer.py --title "Tighten-plan batch" --items <file>',
            page,
        )
        self.assertIn("immediately before the card", page)
        skill = (ROOT / ".cursor/skills/crav1/crav1-tighten-plan/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("P4 tasks miss the 400 path: A add a test", skill)


if __name__ == "__main__":
    unittest.main()
