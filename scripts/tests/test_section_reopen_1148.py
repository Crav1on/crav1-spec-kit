"""1.148.0: a spec edit reopens from the first owning step, not every later step.

Each ## section maps to the steps it invalidates. A requirement section
reopens tighten-spec and the plan steps, because the plan was written from
it. It does not reopen resolve-open-questions when the question ids are
unchanged. Match, In the code, a Synced at line, and an already-answered
question reopen nothing. A new, removed, or reworded open question still
reopens resolve. An unknown heading still reopens the plan.
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
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-13T10:00:00+00:00"

REQUIREMENT = (
    "tighten-spec",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)
# The locked map. A new slug in the script must be added here too.
EXPECT = {
    "preamble": REQUIREMENT,
    "problem": REQUIREMENT,
    "goals": REQUIREMENT,
    "non-goals": REQUIREMENT,
    "users-and-journeys": REQUIREMENT,
    "acceptance-criteria": REQUIREMENT,
    "constraints": REQUIREMENT,
    "requirements": REQUIREMENT,
    "scope": REQUIREMENT,
    "decisions": REQUIREMENT,
    "background": REQUIREMENT,
    "context": REQUIREMENT,
    "what-the-dump-says": REQUIREMENT,
    "trace": REQUIREMENT,
    "research-findings": REQUIREMENT,
    "open-questions": ("resolve-open-questions",),
    "match": (),
    "in-the-code": (),
}
HEADINGS = {
    "problem": "Problem",
    "goals": "Goals",
    "non-goals": "Non-goals",
    "users-and-journeys": "Users and journeys",
    "acceptance-criteria": "Acceptance criteria",
    "constraints": "Constraints",
    "requirements": "Requirements",
    "scope": "Scope",
    "decisions": "Decisions",
    "background": "Background",
    "context": "Context",
    "what-the-dump-says": "What the dump says",
    "trace": "Trace",
    "research-findings": "Research findings",
    "match": "Match",
    "in-the-code": "In the code",
}


def load_walk():
    spec = importlib.util.spec_from_file_location("walk_progress_1148", WALK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(WALK), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    return proc.returncode, payload


def must(args: list[str]) -> dict:
    code, payload = run(args)
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


def spec_text() -> str:
    parts = [
        "# Orders export",
        "",
        "The receipt lists the order id. MARK-preamble",
        "",
    ]
    for slug, heading in HEADINGS.items():
        parts.append(f"## {heading}")
        parts.append("")
        parts.append(f"- MARK-{slug}")
        parts.append("")
    parts.extend([
        "## Open questions",
        "",
        "- Which lane prints the label?",
        "  - Blocks: none",
        "",
        "## Approval needed",
        "",
        "- A lead signs the layout. MARK-approval",
        "",
    ])
    return "\n".join(parts)


def write_slice(root: Path, text: str | None = None) -> None:
    (root / "spec.md").write_text(text if text is not None else spec_text(), encoding="utf-8")
    (root / "plan.md").write_text("# Plan\n\n## Risks\n", encoding="utf-8")
    (root / "tasks.md").write_text(
        "# Tasks\n\n- [ ] T1 Record the lane (after: )\n",
        encoding="utf-8",
    )
    (root / "verify.md").write_text("# Verify\n", encoding="utf-8")


def record_walk(root: Path) -> None:
    for step, result in (
        ("review-architecture", "nothing-to-do"),
        ("tighten-spec", "done"),
        ("resolve-open-questions", "done"),
        ("plan-from-spec", "done"),
        ("review-and-tighten-plan", "done"),
        ("tasks-ready-to-build", "ready"),
    ):
        must([
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", step, "--result", result, "--when", WHEN, "--yes",
        ])


def statuses(root: Path) -> tuple[dict, dict]:
    payload = must(["resume", "--root", str(root), "--no-playbook"])
    return {row["id"]: row for row in payload["steps"]}, payload


class SectionMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_walk()

    def test_script_map_matches_the_locked_expectations(self):
        self.assertEqual(set(self.mod.SECTION_STEPS), set(EXPECT))
        for slug, owners in EXPECT.items():
            self.assertEqual(self.mod.SECTION_STEPS[slug], tuple(owners), slug)

    def test_each_section_reopens_only_its_owners(self):
        for slug, owners in EXPECT.items():
            with self.subTest(slug=slug):
                root = Path(tempfile.mkdtemp()) / "orders-export"
                root.mkdir()
                write_slice(root)
                record_walk(root)
                text = (root / "spec.md").read_text(encoding="utf-8")
                if slug == "open-questions":
                    edited = text.replace(
                        "- Which lane prints the label?\n",
                        "- Which lane prints the label?\n- Does the carton need a second stamp?\n",
                    )
                elif slug == "preamble":
                    edited = text.replace("MARK-preamble", "MARK-preamble edited")
                else:
                    edited = text.replace(f"MARK-{slug}", f"MARK-{slug} edited")
                (root / "spec.md").write_text(edited, encoding="utf-8")
                by_id, payload = statuses(root)
                reopened = [step for step, row in by_id.items() if row["status"] == "reopen"]
                self.assertEqual(reopened, list(owners), payload.get("reopen_line"))
                self.assertEqual(by_id["review-architecture"]["status"], "keep")
                if owners:
                    self.assertEqual(payload["continue_from"], owners[0])
                    self.assertIn("Reopen: " + ", ".join(owners), payload["reopen_line"])
                else:
                    self.assertEqual(payload["reopen_steps"], [])
                    self.assertIn("Reopen: none", payload["reopen_line"])
                    self.assertTrue(payload["restamp_only"])
                if slug != "open-questions":
                    self.assertEqual(by_id["resolve-open-questions"]["status"], "keep")
                    self.assertEqual(payload["changed_questions"], [])


class StableIdHook(unittest.TestCase):
    def test_a_question_key_that_is_not_the_word_hash_is_the_stable_id(self):
        mod = load_walk()

        class Fake:
            def question_key(self, text):
                return "q-export"

        mod.blocks_mod = lambda: Fake()
        ident, word, answered = mod._question_identity("Which lane prints the label?", [])
        self.assertEqual(ident, "q-export")
        self.assertNotEqual(word, "q-export")
        self.assertFalse(answered)

    def test_stable_question_id_wins_over_the_word_hash(self):
        mod = load_walk()

        class Fake:
            def stable_question_id(self, text, marks=None):
                return "q-stable"

            def question_key(self, text):
                return mod._word_hash(text)

        mod.blocks_mod = lambda: Fake()
        ident, word, _answered = mod._question_identity("Which lane prints the label?", [])
        self.assertEqual(ident, "q-stable")
        self.assertEqual(word, mod._word_hash("Which lane prints the label?"))


class MustStillReopen(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()) / "orders-export"
        self.root.mkdir()
        write_slice(self.root)
        record_walk(self.root)

    def test_constraint_line_reopens_the_plan_and_not_resolve(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(
            text.replace("MARK-constraints", "The lane name is at most 12 characters."),
            encoding="utf-8",
        )
        by_id, payload = statuses(self.root)
        for step in REQUIREMENT:
            self.assertEqual(by_id[step]["status"], "reopen", step)
        self.assertEqual(by_id["resolve-open-questions"]["status"], "keep")
        self.assertIn("Changed: Constraints.", payload["reopen_line"])
        self.assertNotIn("resolve-open-questions", payload["reopen_line"])

    def test_unknown_heading_reopens_the_plan(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(
            text + "\n## Shipping notes\n\n- Ships on Tuesday.\n",
            encoding="utf-8",
        )
        by_id, payload = statuses(self.root)
        for step in REQUIREMENT:
            self.assertEqual(by_id[step]["status"], "reopen", step)
        self.assertEqual(by_id["resolve-open-questions"]["status"], "keep")
        self.assertIn("Shipping notes", payload["reopen_line"])

    def test_reworded_question_reopens_only_resolve(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(
            text.replace("Which lane prints the label?", "Which dock prints the label?"),
            encoding="utf-8",
        )
        by_id, payload = statuses(self.root)
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        for step in REQUIREMENT:
            self.assertEqual(by_id[step]["status"], "keep", step)
        reasons = {row["reason"] for row in payload["changed_questions"]}
        self.assertIn("new", reasons)
        self.assertIn("removed", reasons)

    def test_deleted_question_reopens_only_resolve(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(
            text.replace("- Which lane prints the label?\n  - Blocks: none\n", ""),
            encoding="utf-8",
        )
        by_id, payload = statuses(self.root)
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        for step in REQUIREMENT:
            self.assertEqual(by_id[step]["status"], "keep", step)
        self.assertEqual(payload["changed_questions"][0]["reason"], "removed")

    def test_stable_id_reword_is_the_same_question(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        marked = text.replace(
            "- Which lane prints the label?\n  - Blocks: none\n",
            "- Which lane prints the label?\n  - Id: q-lane\n  - Blocks: none\n",
        )
        (self.root / "spec.md").write_text(marked, encoding="utf-8")
        must([
            "record", "--root", str(self.root), "--slice", "docs/specs/orders-export",
            "--step", "resolve-open-questions", "--result", "done",
            "--when", "2026-11-13T11:00:00+00:00", "--yes",
        ])
        (self.root / "spec.md").write_text(
            marked.replace("Which lane prints the label?", "Which dock prints the label?"),
            encoding="utf-8",
        )
        by_id, payload = statuses(self.root)
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        for step in REQUIREMENT:
            self.assertEqual(by_id[step]["status"], "keep", step)
        self.assertEqual(payload["changed_questions"], [{"id": "q-lane", "reason": "reworded"}])
        self.assertNotIn("new", {row["reason"] for row in payload["changed_questions"]})

    def test_architecture_reopens_when_it_is_the_only_spec_step(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        write_slice(root)
        must([
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", "review-architecture", "--result", "done", "--when", WHEN, "--yes",
        ])
        text = (root / "spec.md").read_text(encoding="utf-8")
        (root / "spec.md").write_text(text.replace("MARK-problem", "MARK-problem edited"), encoding="utf-8")
        by_id, payload = statuses(root)
        self.assertEqual(by_id["review-architecture"]["status"], "reopen")
        self.assertEqual(payload["continue_from"], "review-architecture")
        self.assertIn("Reopen: review-architecture", payload["reopen_line"])


class NoReopen(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()) / "orders-export"
        self.root.mkdir()
        write_slice(self.root)
        record_walk(self.root)

    def _keep(self, edited: str) -> dict:
        (self.root / "spec.md").write_text(edited, encoding="utf-8")
        by_id, payload = statuses(self.root)
        for row in by_id.values():
            if row.get("extra"):
                continue
            self.assertNotEqual(row["status"], "reopen", payload.get("reopen_line"))
        return payload

    def test_answered_line_on_the_same_words_does_not_reopen(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        payload = self._keep(
            text.replace(
                "- Which lane prints the label?\n  - Blocks: none\n",
                "- Which lane prints the label?\n  - Blocks: none\n"
                "  - Answered: 2026-11-13, a colleague, fact: \"Lane 4.\"\n",
            )
        )
        self.assertTrue(payload["restamp_only"])
        self.assertIn("Changed: Open questions. Reopen: none.", payload["reopen_line"])
        self.assertEqual(payload["changed_questions"], [])

    def test_new_answered_question_does_not_reopen(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        payload = self._keep(
            text.replace(
                "## Open questions\n\n",
                "## Open questions\n\n"
                "- Who signed the old layout?\n"
                "  - Answered: 2026-11-01, a colleague, fact: \"The lead.\"\n",
            )
        )
        self.assertTrue(payload["restamp_only"])
        self.assertEqual(payload["reopen_steps"], [])

    def test_blocks_line_does_not_reopen_or_offer_a_restamp(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        payload = self._keep(text.replace("Blocks: none", "Blocks: T1"))
        self.assertFalse(payload["restamp_only"])
        self.assertIn("Reopen: none", payload["reopen_line"])
        self.assertEqual(payload["changed_questions"], [])

    def test_synced_at_line_does_not_reopen(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        payload = self._keep(
            text.replace(
                "# Orders export\n",
                "# Orders export\n\nSynced at: orders-api feat/orders-export@155b5c4, 2026-11-13\n",
            )
        )
        self.assertTrue(payload["restamp_only"])
        self.assertIn("Changed: Synced at. Reopen: none.", payload["reopen_line"])

    def test_approval_needed_does_not_reopen(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        payload = self._keep(text.replace("MARK-approval", "MARK-approval edited"))
        self.assertIsNone(payload["reopen_line"])
        self.assertFalse(payload["restamp_only"])

    def test_restamp_refuses_a_constraint_and_accepts_match(self):
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(
            text.replace("MARK-constraints", "MARK-constraints edited"),
            encoding="utf-8",
        )
        code, payload = run(["restamp-covered", "--root", str(self.root), "--yes"])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "not-restamp")
        self.assertIn("Constraints", payload["message"])
        (self.root / "spec.md").write_text(text.replace("MARK-match", "MARK-match edited"), encoding="utf-8")
        code, payload = run(["restamp-covered", "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "needs-yes")
        self.assertIn("Reopen: none", payload["reopen_line"])
        stamped = must(["restamp-covered", "--root", str(self.root), "--yes"])
        self.assertIn("tighten-spec", stamped["restamped"])
        self.assertEqual(stamped["reopen_steps"], [])
        by_id, payload = statuses(self.root)
        for row in by_id.values():
            self.assertNotEqual(row["status"], "reopen")
        self.assertIsNone(payload["reopen_line"])

    def test_legacy_progress_without_section_stamps_still_reopens_broadly(self):
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        stripped = "\n".join(
            line for line in text.splitlines()
            if not line.strip().startswith("Section stamps:")
            and not line.strip().startswith("Question ids:")
        ) + "\n"
        (self.root / "walk-progress.md").write_text(stripped, encoding="utf-8")
        spec = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(
            spec.replace("MARK-constraints", "MARK-constraints edited"),
            encoding="utf-8",
        )
        by_id, payload = statuses(self.root)
        self.assertIsNone(payload["reopen_line"])
        self.assertEqual(by_id["tighten-spec"]["status"], "reopen")
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        self.assertEqual(by_id["plan-from-spec"]["status"], "reopen")
        self.assertEqual(by_id["review-and-tighten-plan"]["status"], "reopen")
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "reopen")


if __name__ == "__main__":
    unittest.main()
