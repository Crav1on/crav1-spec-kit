"""1.165.0: Run next fixes found on a real plan, on generic fixtures.

1. The branch sentence is a clean plan sentence, else the step heading, else
   left out. Plan notes (colon lists) never show. (1.166.0 changed this: see
   test_branch_description_1166.py.)
2. A long line is cut at a clause end or a word, never on a dangling word.
3. A heading-like question (`Client certificate.`) gives way to the question.
4. Tasks are listed in walk order; a task that cannot start says why, and
   the task command names the first one that can.
5. No person's name leads the branch sentence.
6. A `---` rule stands between two branch blocks.
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
WALK = SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-11T12:00:00+00:00"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


we = _load("walk_ending_1165", SKILLS / "crav1-tasks-ready-to-build/scripts/walk_ending.py")

NOTES = (
    "The orders CI/CD branch, cut from develop after billing-ops: merge main into develop "
    "on a work branch: infra-orders/, cd-orders.yml, ci.yml lints and tests the orders function."
)
PERSON = (
    "Person A builds PR 73: GetReceipts answers 404 for a cursor that matches no stored receipt, "
    "PR 73: the OpenAPI document lists every route and error."
)
LONG_Q = (
    "For the 2.0 rollout, where does TLS end, at the app host or at the gateway that gives the "
    "partner a fixed address, a known certificate chain and a renewal window that the partner can plan for?"
)

PLAN = f"""# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Record the decision. (T5)
2. {NOTES} (T9, T10)
3. **Receipt API fixes** — {PERSON} (T8, T43)
4. **Partner TLS** — trust the certificate header only from the chosen front end. (T25, T26)

## Risks
"""

SPEC = f"""# Spec

## Open questions

- {LONG_Q}
  - Asked: 2026-10-10, mail to the platform team. Question 1.
  - Blocks: T25
- Client certificate. Which certificate does the partner send when the gateway ends TLS?
  - Asked: 2026-10-10, mail to the partner. Question 2.
  - Blocks: T26
"""

TASKS = """# Tasks

- [ ] T5: Record the decision (branch: feat/orders-api-record) (after: )
- [ ] T8: Take in develop, resolve conflicts, merge (branch: feat/orders-api-fixes) (after: T5)
- [ ] T9: Orders CI/CD: infra for dev, test and prod (branch: feat/orders-cicd) (after: )
- [ ] T10: Orders CI/CD: pipeline with three stages (branch: feat/orders-cicd) (after: )
- [ ] T25: Trust the certificate header only from the front end (branch: feat/orders-mtls) (after: )
- [ ] T26: Accept the old and the new partner certificate (branch: feat/orders-mtls) (after: )
- [ ] T43: Incoming JSON body with only tag and content (branch: feat/orders-api-fixes) (after: )
"""

DANGLING = {"a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "from", "with", "and", "or", "that"}


def readiness_text() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "orders-api"
        root.mkdir()
        for name, text in (("spec.md", SPEC), ("plan.md", PLAN), ("tasks.md", TASKS)):
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
        return json.loads(proc.stdout)["ending"]


class BranchSentence(unittest.TestCase):
    def test_clean_sentence_is_kept(self):
        # Up to three clean sentences since 1.166.0.
        self.assertEqual(we.about_sentence("Record the decision. Then mail it."), "Record the decision. Then mail it.")

    def test_plan_notes_trim_to_opening_clause(self):
        # 1.166.0: plan notes give their opening clause, not nothing.
        # 1.171.0: how the branch was cut is a planning note, not a description.
        self.assertEqual(we.about_sentence(NOTES), "")

    def test_person_lead_falls_back_to_heading(self):
        # 1.166.0: the person lead is dropped and the clause after it kept.
        self.assertEqual(we.about_sentence(PERSON), "GetReceipts answers 404 for a cursor that matches no stored receipt.")
        self.assertEqual(we.about_sentence(f"**Receipt API fixes** — {PERSON}"), "GetReceipts answers 404 for a cursor that matches no stored receipt.")
        self.assertEqual(we.about_sentence(f"Receipt API fixes: {PERSON}"), "Receipt API fixes.")

    def test_no_full_stop_is_not_clean(self):
        self.assertEqual(we.about_sentence("export the receipt"), "")


class Shorten(unittest.TestCase):
    def test_cut_never_splits_a_word_or_dangles(self):
        for limit in range(40, 160, 7):
            out = we.shorten(LONG_Q, limit)
            self.assertLessEqual(len(out), limit)
            self.assertTrue(out.endswith("…"), out)
            body = out[:-1]
            self.assertTrue(LONG_Q.startswith(body), out)
            self.assertIn(LONG_Q[len(body)], " ,", out)
            self.assertNotIn(body.split()[-1].lower(), DANGLING, out)

    def test_clause_end_preferred(self):
        self.assertEqual(we.shorten("Alpha beta gamma delta, epsilon zeta eta theta iota kappa", 40), "Alpha beta gamma delta…")

    def test_short_line_unchanged(self):
        self.assertEqual(we.shorten("Which currency for refunds?"), "Which currency for refunds?")


class HeldQuestion(unittest.TestCase):
    def test_heading_fragment_gives_way_to_the_question(self):
        text = "Client certificate. We use one today. Which certificate does the partner send?"
        self.assertEqual(we.question_text(text), "Which certificate does the partner send?")

    def test_fragment_without_question_takes_next_sentence(self):
        self.assertEqual(we.question_text("Client certificate. The partner sends its own one."), "The partner sends its own one.")

    def test_real_first_sentence_stays(self):
        self.assertEqual(we.question_text("Which currency for refunds? It matters."), "Which currency for refunds?")


class WalkOrder(unittest.TestCase):
    def test_waiting_task_says_why_and_command_names_one_that_can_start(self):
        block = we.branch_block(
            "feat/orders-api-fixes", ["T8 Take in develop", "T43 Incoming JSON"],
            first="T43 Incoming JSON", slug="orders-api", waits={"T8": "waits on T5"},
        )
        self.assertIn("- T8 Take in develop (waits on T5)\n- T43 Incoming JSON", block)
        self.assertIn("Run only T43, the first task that can start:\n`/crav1-build-walk orders-api T43`", block)

    def test_first_listed_is_the_first_task(self):
        block = we.branch_block("feat/x", ["T1 a", "T2 b"], first="T1 a", waits={"T2": "waits on T1"})
        self.assertIn("Run only T1, the first task:", block)
        self.assertIn("- T2 b (waits on T1)", block)


class Separation(unittest.TestCase):
    def test_rule_between_blocks_only(self):
        text = we.run_block(["**feat/a**\n1 open task:\n- T1 a\n\nRun T1:\n`/crav1-build-walk T1`",
                             "**feat/b**\n1 open task:\n- T2 b\n\nRun T2:\n`/crav1-build-walk T2`"])
        self.assertIn("`/crav1-build-walk T1`\n\n---\n\n**feat/b**", text)
        self.assertFalse(text.rstrip().endswith("---"))
        self.assertEqual(text.count("\n---\n"), 1)


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ending = readiness_text()

    def test_all_six(self):
        text = self.ending
        # 1 and 5: no plan notes, no person in a branch sentence; since
        # 1.166.0 every branch keeps a description.
        self.assertNotIn("merge main into develop", text)
        self.assertNotIn("Person A", text)
        self.assertIn("**feat/orders-api-fixes**\n" + "GetReceipts answers 404 for a cursor that matches no stored receipt." + "\n2 open tasks:", text)
        self.assertIn("**feat/orders-cicd**\nOrders CI/CD: infra for dev, test and prod and pipeline with three stages.\n2 open tasks:", text)  # 1.171.0
        # 2: the long question is whole or cut at a word, never mid-word.
        line = next(row for row in text.splitlines() if "T25" in row and "open question" in row)
        quoted = line.split('"')[1]
        self.assertTrue(quoted == LONG_Q or (quoted.endswith("…") and LONG_Q.startswith(quoted[:-1])), quoted)
        # 3: the question, not its heading.
        self.assertNotIn('"Client certificate."', text)
        self.assertIn('"Which certificate does the partner send when the gateway ends TLS?"', text)
        # 4: walk order, the reason, and the first task that can start.
        self.assertIn("- T43 Incoming JSON body with only tag and content\n- T8 ", text)
        self.assertRegex(text, r"- T8 [^\n]*\(waits on T5\)")
        self.assertIn("Run only T43, the first task:", text)
        # 6: a rule between blocks.
        self.assertEqual(text.split("Held:")[0].count("\n\n---\n\n"), 2)


if __name__ == "__main__":
    unittest.main()
