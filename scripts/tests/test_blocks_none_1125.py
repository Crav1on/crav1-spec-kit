"""1.125.0: Blocks: none blocks no task, and the walk asks the choices it was skipping."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCKS = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/question_blocks.py"
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WALK_SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_walk(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        ["python3", str(WALK), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.returncode, json.loads(proc.stdout)


SPEC = """# Spec

## Open questions

- Which currency for refunds?
  - Blocks: T2, T4
- What format does the later phase use?
  - Blocks: none (later phase)
- Who signs the export?
- Is the cut-off local time?
  - Answered: 2026-10-14, Dana, email: "Yes." Source: docs/sources/2026-10-14-dana-retry-answer/
- Which queue holds retries?
  - Blocks: none
"""

PLAN = """# Plan

## Risks

- Which currency for refunds? Do not implement until resolved.
- What format does the later phase use? Do not implement until resolved.
- Who signs the export? Do not implement until resolved.
- The vendor note is stale. See docs/research/vendor-network.md.
"""


class QuestionBlocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load(BLOCKS, "question_blocks")

    def test_none_blocks_no_task_and_a_line_wins_over_the_risk(self):
        got = self.mod.analyse(SPEC, PLAN)
        by_text = {q["text"]: q for q in got["questions"]}
        self.assertEqual(set(by_text), {
            "Which currency for refunds?",
            "What format does the later phase use?",
            "Who signs the export?",
            "Which queue holds retries?",
        })
        self.assertEqual(by_text["Which currency for refunds?"]["mark"], "tasks")
        self.assertEqual(by_text["Which currency for refunds?"]["tasks"], ["T2", "T4"])
        self.assertFalse(by_text["Which currency for refunds?"]["blocks_slice"])
        later = by_text["What format does the later phase use?"]
        self.assertEqual(later["mark"], "none")
        self.assertEqual(later["reason"], "later phase")
        self.assertFalse(later["blocks_slice"])
        self.assertEqual(by_text["Which queue holds retries?"]["mark"], "none")
        self.assertIsNone(by_text["Which queue holds retries?"]["reason"])
        missing = by_text["Who signs the export?"]
        self.assertEqual(missing["mark"], "missing")
        self.assertTrue(missing["blocks_slice"])
        self.assertNotIn("Is the cut-off local time?", by_text)

        by_q = {r["question"]: r for r in got["risks"]}
        self.assertEqual(len(got["risks"]), 3)
        self.assertFalse(by_q["Which currency for refunds?"]["blocks_slice"])
        self.assertFalse(by_q["What format does the later phase use?"]["blocks_slice"])
        self.assertTrue(by_q["Who signs the export?"]["blocks_slice"])
        self.assertEqual(by_q["Who signs the export?"]["because"], "no Blocks line")

    def test_a_risk_with_no_matching_question_still_blocks_the_slice(self):
        plan = "## Risks\n\n- Something else. Do not implement until resolved.\n"
        got = self.mod.analyse("## Open questions\n\n- Who signs the export?\n", plan)
        self.assertTrue(got["questions"][0]["blocks_slice"])
        self.assertTrue(got["risks"][0]["blocks_slice"])
        self.assertIsNone(got["risks"][0]["question"])
        self.assertEqual(got["risks"][0]["because"], "no matching question")

    def test_cli_prints_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "spec.md"
            plan = root / "plan.md"
            spec.write_text(SPEC, encoding="utf-8")
            plan.write_text(PLAN, encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(BLOCKS), str(spec), str(plan)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(len(payload["questions"]), 4)


class WalkScripts(unittest.TestCase):
    def test_unlinked_lists_only_questions_with_no_blocks_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec.md").write_text(SPEC, encoding="utf-8")
            code, payload = run_walk(["unlinked", "--root", str(root)])
        self.assertEqual(code, 0)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["questions"], [{"text": "Who signs the export?"}])

    def test_blocks_none_is_not_a_ready_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.json"
            path.write_text(json.dumps({"rows": [
                {"bucket": "blocked", "task": "T2", "reason": 'open question "Later format?" Blocks: none'},
                {"bucket": "blocked", "task": "T9", "reason": 'plan Risk "Later format? do not implement until resolved" Blocks: none'},
                {"bucket": "blocked", "task": "T4", "reason": "plan Risk blocks the slice"},
                {"bucket": "needs-verify", "task": "T3", "reason": "no verify.md row"},
            ]}), encoding="utf-8")
            code, payload = run_walk(["readiness", "--full", "--json", str(path)])
        self.assertEqual(code, 0)
        self.assertFalse(payload["ready"])
        tasks = [row["task"] for row in payload["blockers"] + payload["outside_walk"]]
        self.assertNotIn("T2", tasks)
        self.assertNotIn("T9", tasks)
        self.assertIn("T4", tasks)
        self.assertIn("T3", tasks)

    def test_already_applied_still_asks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec.md").write_text("spec\n", encoding="utf-8")
            playbook = root / "orders-retry.md"
            playbook.write_text("playbook\n", encoding="utf-8")
            code, recorded = run_walk([
                "record", "--root", str(root), "--step", "playbook",
                "--result", "applied", "--playbook", str(playbook), "--yes",
                "--when", "2026-11-10T12:00:00+01:00",
            ])
            self.assertEqual(code, 0, recorded)
            code, status = run_walk([
                "playbook-status", "--root", str(root), "--playbook", str(playbook),
            ])
        self.assertEqual(code, 0)
        self.assertEqual(status["status"], "already-applied")
        self.assertEqual(status["offer"], "skip-or-reapply")
        self.assertIn("Ask once", status["note"])
        self.assertIn("even when the file has not changed", status["note"])
        self.assertIn("Do not move on without that question", status["note"])

    def test_record_without_yes_names_the_shown_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec.md").write_text("spec\n", encoding="utf-8")
            code, payload = run_walk([
                "record", "--root", str(root), "--step", "tighten-spec",
                "--result", "done",
            ])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "needs-yes")
        self.assertIn("shown and confirmed", payload["message"])


class WalkWording(unittest.TestCase):
    def test_record_confirm_shows_the_line(self):
        progress = (WALK_SKILL / "references/progress.md").read_text(encoding="utf-8")
        common = (WALK_SKILL / "references/common.md").read_text(encoding="utf-8")
        steps = (WALK_SKILL / "references/steps.md").read_text(encoding="utf-8")
        self.assertIn("Show the progress line and get a yes before `record --yes`", progress)
        self.assertIn("do not cover that line", progress)
        self.assertIn("An extra's yes is that case", progress)
        self.assertIn("shown the line", common)
        self.assertIn("The answers inside the step do not cover that line", steps)

    def test_already_applied_playbook_is_still_a_question(self):
        playbook = (WALK_SKILL / "references/playbook.md").read_text(encoding="utf-8")
        self.assertIn("even when the file has not changed", playbook)
        self.assertIn("Do not move on without it", playbook)
        self.assertIn("`skip` (Recommended)", playbook)

    def test_extras_are_offered_once_after_open_questions(self):
        steps = (WALK_SKILL / "references/steps.md").read_text(encoding="utf-8")
        self.assertIn("## After step 4, one batch of extras", steps)
        self.assertIn("when the kept-open questions are known", steps)
        self.assertIn("do not go on to the plan without that offer", steps)
        self.assertIn("Offer `/crav1-show-or-ask-open-questions` when any kept-open question is for someone else.", steps)
        self.assertIn("Auto-record stays this way", steps)
        self.assertLess(
            steps.index("## After step 4, one batch of extras"),
            steps.index("## 5. Plan"),
        )

    def test_unlinked_pass_is_before_the_plan_review(self):
        steps = (WALK_SKILL / "references/steps.md").read_text(encoding="utf-8")
        self.assertIn("## After the plan, questions with no Blocks line", steps)
        self.assertIn("unlinked --root", steps)
        self.assertIn("`one batch` (Recommended)", steps)
        self.assertIn("`one by one`", steps)
        self.assertIn("Before step 5 is recorded", steps)
        self.assertIn("**The whole slice** (`- Blocks: whole slice`)", steps)
        self.assertIn("kept open; blocks the whole slice until resolved.", steps)
        self.assertIn("A `Blocks:` line wins over that Risk wording", steps)
        self.assertNotIn("(no line)", steps)
        self.assertNotIn("leaves no line", steps)
        self.assertLess(
            steps.index("## After the plan, questions with no Blocks line"),
            steps.index("## 6. Review the plan, then tighten it"),
        )
        skill = (WALK_SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Blocks: none", skill)

    def test_plan_and_ready_rules_name_the_mark(self):
        write = (
            ROOT / ".cursor/skills/crav1/crav1-plan-from-spec/references/write.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Blocks: none", write)
        self.assertIn("one short batch", write.lower())
        self.assertIn('Do not write "do not implement until resolved"', write)
        self.assertIn("kept open; does not block the current tasks.", write)
        ready = (
            ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("`Blocks: none`", ready)
        self.assertIn("Any `Blocks:` line wins", ready)
        self.assertIn("question_blocks.py", ready)
        resolve = (
            ROOT / ".cursor/skills/crav1/crav1-resolve-open-questions/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("**None** writes `- Blocks: none`", resolve)
        self.assertIn("**The whole slice** writes `- Blocks: whole slice`", resolve)
        shared = (
            ROOT / ".cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Any `Blocks:` line wins", shared)
        layout = (ROOT / "docs/concepts/data-layout.md").read_text(encoding="utf-8")
        self.assertIn("`Blocks: none` blocks no task", layout)


if __name__ == "__main__":
    unittest.main()
