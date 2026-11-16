"""1.166.0: every Run next branch block has a description, and a held
question that points to a note shows the quoted question.

1. The branch description, in order: (a) up to three clean sentences from
   the plan step, about 300 characters, cut only at a sentence end; (b) the
   plan note trimmed to its opening clause, with a person lead dropped;
   (c) the step heading; (d) one sentence from the open task names. Left
   out only when there is no plan step and no usable task name. A person's
   name never shows.
2. A held question that ends with `:` or only points to a note gives way
   to the blockquote under it, else the text in quotes after the colon,
   else the first sentence ending in `?`.
Generic fixtures only.
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
    spec.loader.exec_module(module)
    return module


we = _load("walk_ending_1166", SCRIPTS / "walk_ending.py")
qb = _load("question_blocks_1166", SCRIPTS / "question_blocks.py")
bm = _load("build_map_1166", SCRIPTS / "build_map.py")

NOTES = (
    "The orders CI/CD branch, cut from develop after billing-ops: merge main into develop "
    "on a work branch: infra-orders/, cd-orders.yml, ci.yml lints and tests the orders function."
)
PERSON = (
    "Person A builds PR 73: GetReceipts answers 404 for a cursor that matches no stored receipt, "
    "PR 73: the OpenAPI document lists every route and error."
)
THREE = (
    "PR 71 gets its README text, then is reviewed and merged. "
    "The README names the receipts table and the audit rows. "
    "Reviewers check the malformed payload section."
)
CICD_TASKS = [
    "T9 Orders CI/CD: infra Bicep for dev, test and prod",
    "T10 Orders CI/CD: cd pipeline with DEV, TEST and PROD stages",
    "T11 Orders CI/CD: ci lint and tests for the orders function",
    "T12 Orders CI/CD: deploy README for patching a bug",
]
POINTER = "Client certificate. The note docs/notes/tls-and-fixed-ip.md, in Open questions, question 5, says:"
ASKED = "Which certificate does the partner send, and does it change when the gateway ends TLS?"


class PlanSentences(unittest.TestCase):
    def test_up_to_three_clean_sentences(self):
        self.assertEqual(we.about_sentence(THREE), THREE)
        self.assertEqual(we.about_sentence(THREE + " A fourth sentence is not shown."), THREE)

    def test_stops_at_the_first_sentence_that_is_not_clean(self):
        text = "Record the decision. Then: mail it to the partner. Then file it."
        self.assertEqual(we.about_sentence(text), "Record the decision.")

    def test_never_cut_mid_sentence_at_the_limit(self):
        first = "Record the decision about the receipts in one short and plain sentence."
        second = "This second sentence is long " + "and keeps going " * 18 + "until it ends."
        out = we.about_sentence(f"{first} {second}")
        self.assertEqual(out, first)
        self.assertLessEqual(len(out), we.DESCRIPTION_LIMIT)
        self.assertEqual(we.DESCRIPTION_LIMIT, 300)

    def test_one_sentence_over_the_limit_falls_back(self):
        long_one = "Export " + "the receipt and " * 25 + "the refund."
        out = we.about_sentence(f"**Receipt export** — {long_one}")
        self.assertEqual(out, "Receipt export.")
        self.assertNotIn("…", out)


class OpeningClause(unittest.TestCase):
    def test_plan_notes_keep_the_opening_clause(self):
        # 1.171.0: how the branch was cut is a planning note, not a description.
        self.assertEqual(we.about_sentence(NOTES), "")

    def test_person_lead_is_dropped(self):
        out = we.about_sentence(PERSON)
        self.assertEqual(out, "GetReceipts answers 404 for a cursor that matches no stored receipt.")
        self.assertNotIn("Person A", out)
        self.assertNotIn("PR 73", out)

    def test_person_lead_without_a_colon_falls_to_the_tasks(self):
        out = we.about_sentence("Person A builds the receipt export", names=["T1 Export the receipt"])
        self.assertEqual(out, "Export the receipt.")

    def test_short_clause_falls_to_the_heading(self):
        self.assertEqual(we.about_sentence(f"Receipt API fixes: {NOTES}"), "Receipt API fixes.")

    def test_a_path_never_shows(self):
        out = we.about_sentence("Update infra-orders/main.bicep and cd-orders.yml: both stages", names=CICD_TASKS)
        self.assertNotIn("/", out.replace("CI/CD", ""))
        self.assertNotIn(".yml", out)


class TaskNames(unittest.TestCase):
    def test_shared_prefix_leads_once(self):
        self.assertEqual(
            we.about_sentence("", names=CICD_TASKS),
            "Orders CI/CD: infra Bicep, cd pipeline, ci lint and tests, and deploy README.",
        )

    def test_stays_under_the_limit_with_whole_items(self):
        names = [f"T{n} Orders CI/CD: stage number {n} of the long release train build" for n in range(1, 12)]
        out = we.tasks_sentence(names)
        self.assertLessEqual(len(out), we.TASK_SUMMARY_LIMIT)
        self.assertRegex(out, r"and \d+ more\.$")

    def test_two_names_without_prefix(self):
        self.assertEqual(
            we.tasks_sentence(["T1 Add the build pipeline", "T2 Add the test stage"]),
            "Add the build pipeline and add the test stage.",
        )

    def test_no_step_and_no_names_is_left_out(self):
        self.assertEqual(we.about_sentence("", names=[]), "")
        self.assertEqual(we.about_sentence(None, names=["T1 "]), "")


class EveryBlockHasADescription(unittest.TestCase):
    def test_block_without_plan_step(self):
        block = we.branch_block("feat/orders-cicd", CICD_TASKS[:2], slug="orders-api")
        lines = block.splitlines()
        self.assertEqual(lines[0], "**feat/orders-cicd**")
        self.assertEqual(lines[1], "Orders CI/CD: infra Bicep and cd pipeline.")
        self.assertEqual(lines[2], "2 open tasks:")


class HeldQuestion(unittest.TestCase):
    def test_blockquote_after_a_pointer(self):
        self.assertEqual(we.question_text(POINTER, quote=ASKED), ASKED)

    def test_quoted_text_after_the_colon(self):
        self.assertEqual(we.question_text(f'{POINTER} "{ASKED}" Asked twice.'), ASKED)

    def test_first_question_after_a_pointer(self):
        self.assertEqual(we.question_text(f"{POINTER} Some context here first. {ASKED}"), ASKED)

    def test_plain_question_unchanged(self):
        self.assertEqual(we.question_text("Which currency for refunds? It matters."), "Which currency for refunds?")

    def test_spec_blockquote_is_read_and_key_unchanged(self):
        spec = (
            "# Spec\n\n## Open questions\n\n"
            f"- {POINTER}\n  > {ASKED}\n  - Asked: 2026-10-10, mail to the partner.\n  - Blocks: T26\n"
        )
        plain = "# Spec\n\n## Open questions\n\n" + f"- {POINTER}\n  - Blocks: T26\n"
        with_quote = qb.kept_open(spec)[0]
        without = qb.kept_open(plain)[0]
        self.assertEqual(with_quote["quote"], ASKED)
        self.assertEqual(with_quote["text"], POINTER)
        self.assertEqual(with_quote["key"], without["key"])
        self.assertEqual(with_quote["tasks"], ["T26"])

    def test_held_phrase_keeps_inner_quotes(self):
        row = {"reason": f'open question "{POINTER} "{ASKED}"" (recorded)', "who": "the partner"}
        self.assertEqual(bm.held_phrase(row), f'open question "{ASKED}" Waiting for the partner.')

    def test_held_phrase_uses_the_row_quote(self):
        row = {"reason": f'open question "{POINTER}" (recorded)', "who": "the partner", "quote": ASKED}
        self.assertEqual(bm.held_phrase(row), f'open question "{ASKED}" Waiting for the partner.')


PLAN = f"""# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. {THREE} (T5)
2. {NOTES} (T9, T10)
3. {PERSON} (T8, T43)
4. **Partner TLS** — trust the certificate header only from the chosen front end. (T25, T26)

## Risks
"""
SPEC = f"""# Spec

## Open questions

- For the 2.0 rollout, where does TLS end, at the app host or at the gateway?
  - Asked: 2026-10-10, mail to the platform team.
  - Blocks: T25
- {POINTER}
  > {ASKED}
  - Asked: 2026-10-10, mail to the partner.
  - Blocks: T26
"""
TASKS = """# Tasks

- [ ] T5: PR 71: READMEs describe the receipts table and audit rows (branch: feat/orders-api-readme) (after: )
- [ ] T8: PR 73: take in develop, resolve conflicts, merge (branch: feat/orders-api-fixes) (after: T5)
- [ ] T9: Orders CI/CD: infra Bicep for dev, test and prod (branch: feat/orders-cicd) (after: )
- [ ] T10: Orders CI/CD: cd pipeline with three stages (branch: feat/orders-cicd) (after: T9)
- [ ] T25: Trust the certificate header only from the front end (branch: feat/orders-mtls) (after: )
- [ ] T26: Accept the old and the new partner certificate (branch: feat/orders-mtls) (after: )
- [ ] T43: Incoming JSON body with only tag and content (branch: feat/orders-api-fixes) (after: )
"""


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
            cls.text = json.loads(proc.stdout)["ending"]

    def test_every_branch_block_has_a_description(self):
        run_next = self.text.split("Held:")[0]
        for block in run_next.split("\n\n---\n\n"):
            lines = [line for line in block.splitlines() if line and line != "Run next:"]
            self.assertTrue(lines[0].startswith("**"), block)
            self.assertNotRegex(lines[1], r"^\d+ open tasks?:$", block)
            self.assertRegex(lines[2], r"^\d+ open tasks?:$", block)

    def test_descriptions(self):
        self.assertIn("**feat/orders-api-readme**\n" + THREE + "\n1 open task:", self.text)
        self.assertIn("**feat/orders-cicd**\nOrders CI/CD: infra Bicep and cd pipeline.\n", self.text)  # 1.171.0
        self.assertIn("**feat/orders-api-fixes**\nGetReceipts answers 404 for a cursor that matches no stored receipt.\n", self.text)
        self.assertNotIn("Person A", self.text)

    def test_held_question_is_the_quoted_one(self):
        self.assertIn(f'open question "{ASKED}"', self.text)
        self.assertNotIn("says:", self.text)


if __name__ == "__main__":
    unittest.main()
