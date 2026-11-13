"""1.132.0: ready-partial, held dependents, and done rows on the build map."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
MAP_SRC = ROOT / "scripts/build-map.py"
WHEN = "2026-11-11T12:00:00+00:00"

PLAN = """# Plan: the slice

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Record the decision. (T1)
2. Store the card. (T2)
3. Send the receipt. (T3)

## Risks
"""

SPEC_HELD = """# Spec

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to the partner. Question 1.
  - Blocks: T3

## Match

- Repo: orders-api https://github.com/contoso/orders-api
- Branch: orders-api feat/orders-retry (PR 12)
"""

SPEC_ANSWERED = """# Spec

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to the partner. Question 1.
  - Answered: 2026-11-11, the partner, mail: "Use the card currency." Source: docs/sources/2026-11-11-currency/
  - Blocks: T3

## Match

- Repo: orders-api https://github.com/contoso/orders-api
- Branch: orders-api feat/orders-retry (PR 12)
"""

MIXED = """# Tasks

- [ ] T1: Record the decision (after: )
- [ ] T2: Store the card (after: )
- [ ] T3: Choose the currency (after: )
- [ ] T4: Email the receipt (after: T3)
- [ ] T5: Archive the receipt (after: T4)
"""

CHAIN = """# Tasks

- [ ] T1: Record the decision
- [ ] T2: Store the card
- [ ] T3: Email the receipt
"""

ALL_HELD_SPEC = """# Spec

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to the partner. Question 1.
  - Blocks: T1
"""


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


def write_slice(root: Path, tasks: str, spec: str, plan: str = PLAN) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")


def record_resolve(root: Path) -> None:
    must([
        "record", "--root", str(root), "--slice", "docs/specs/cancel-booking",
        "--step", "resolve-open-questions", "--result", "done",
        "--when", WHEN, "--yes",
    ])


class ReadyPartial(unittest.TestCase):
    def test_mixed_ready_and_held_is_ready_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, MIXED, SPEC_HELD)
            record_resolve(root)
            payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["can_start"], ["T1", "T2"])
        self.assertEqual(payload["held"], ["T3", "T4", "T5"])
        self.assertIn("Ready now", payload["line"])
        self.assertIn("T1 Record the decision", payload["line"])
        self.assertIn("T2 Store the card", payload["line"])
        self.assertIn("Held", payload["line"])
        self.assertIn("T3 Choose the currency", payload["line"])
        self.assertIn("held, waits on T3", payload["line"])
        self.assertNotIn("Held from", payload["line"])
        self.assertIn("`/crav1-build-walk", payload["next"])
        self.assertIn("T1 Record the decision", payload["next"])
        self.assertIn("T2 Store the card", payload["next"])
        self.assertNotIn("Next: /crav1-build-walk T1 Record the decision", payload["next"])
        self.assertIn("/crav1-build-tasks builds one task without the walk.", payload["next"])
        self.assertNotIn("/crav1-build-tasks T1", payload["next"])
        self.assertNotIn("/crav1-build-tasks T2", payload["next"])
        self.assertNotIn("T1, T2", payload["next"])
        self.assertNotIn("not-ready", payload["result"])
        by_task = {row["task"]: row for row in payload["waiting"]}
        self.assertIn("Which currency", by_task["T3"]["reason"])
        self.assertEqual(by_task["T3"]["who"], "the partner")
        self.assertIn("held, waits on T3", by_task["T4"]["reason"])
        self.assertEqual(by_task["T4"]["who"], "the partner")
        self.assertIn("held, waits on T4", by_task["T5"]["reason"])

    def test_all_held_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, CHAIN, ALL_HELD_SPEC)
            record_resolve(root)
            payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "not-ready")
        self.assertNotIn("/crav1-build-walk", payload["next"] or "")
        self.assertEqual(payload["can_start"], [])
        self.assertEqual(payload["held"], ["T1", "T2", "T3"])
        self.assertIn("held, waits on T1", payload["waiting"][1]["reason"])
        self.assertIn("held, waits on T2", payload["waiting"][2]["reason"])

    def test_all_ready_stays_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, CHAIN, "# Spec\n\n## Open questions\n")
            payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["can_start"], ["T1"])
        self.assertIn("/crav1-build-walk", payload["next"])
        self.assertIn("T1 Record the decision", payload["next"])
        self.assertEqual(payload["held"], [])
        self.assertIsNone(payload["line"])

    def test_rerun_after_the_answer_moves_held_tasks_to_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, MIXED, SPEC_HELD)
            record_resolve(root)
            first = must(["readiness", "--root", str(root)])
            self.assertEqual(first["result"], "ready-partial")
            (root / "spec.md").write_text(SPEC_ANSWERED, encoding="utf-8")
            record_resolve(root)
            second = must(["readiness", "--root", str(root)])
        self.assertEqual(second["result"], "ready")
        self.assertTrue(second["ready"])
        self.assertEqual(second["held"], [])
        self.assertIn("T3", second["can_start"])
        self.assertNotIn("T4", second["can_start"])

    def test_ready_partial_record_is_covered_and_not_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, MIXED, SPEC_HELD)
            must([
                "record", "--root", str(root), "--slice", "docs/specs/cancel-booking",
                "--step", "tighten-spec", "--result", "done", "--when", WHEN, "--yes",
            ])
            recorded = must([
                "record", "--root", str(root), "--slice", "docs/specs/cancel-booking",
                "--step", "tasks-ready-to-build", "--result", "ready-partial", "--yes",
            ])
            text = (root / "walk-progress.md").read_text(encoding="utf-8")
            resumed = must(["resume", "--root", str(root), "--no-playbook"])
        self.assertEqual(recorded["result"], "ready-partial")
        self.assertIn("Result: ready-partial", text)
        self.assertNotIn("Result: not-ready", text)
        self.assertIn("Done: ", text)
        self.assertNotIn("--when", text)
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "keep")
        self.assertEqual(by_id["tasks-ready-to-build"]["result"], "ready-partial")
        self.assertEqual(by_id["tighten-spec"]["status"], "keep")

    def test_build_tasks_refuses_held_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, MIXED, SPEC_HELD)
            record_resolve(root)
            payload = must(["readiness", "--root", str(root)])
        gates = {row["task"]: row for row in payload["gates"]}
        self.assertTrue(gates["T1"]["allow"])
        self.assertFalse(gates["T1"]["refused"])
        self.assertTrue(gates["T2"]["allow"])
        self.assertFalse(gates["T3"]["allow"])
        self.assertTrue(gates["T3"]["refused"])
        self.assertIn("Which currency", gates["T3"]["reason"])
        self.assertTrue(gates["T4"]["refused"])
        self.assertIn("held, waits on T3", gates["T4"]["reason"])
        self.assertTrue(gates["T5"]["refused"])
        skill = (ROOT / ".cursor/skills/crav1/crav1-build-tasks/SKILL.md").read_text(encoding="utf-8")
        several = (ROOT / ".cursor/skills/crav1/crav1-build-tasks/branches/several-tasks/BRANCH.md").read_text(encoding="utf-8")
        features = (ROOT / ".cursor/skills/crav1/crav1-build-features/SKILL.md").read_text(encoding="utf-8")
        for text in (skill, several, features):
            self.assertIn("ready-partial", text)
            self.assertIn("refused", text)
            self.assertIn("do not ask to build it anyway", text.lower())


class BuildMapKeepsDone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location("build_map_wrapper", MAP_SRC)
        wrapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper)
        cls.bm = wrapper.load()

    def test_done_rows_stay_struck_with_the_pr_and_a_done_wave_folds(self):
        spec = """# Cancel a booking

## Open questions

- Which channel is used for the receipt?
  - Blocks: none

## Match

- Repo: orders-api https://github.com/contoso/orders-api
- Branch: orders-api feat/orders-retry (PR 12)
"""
        plan = """# Plan

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Record the decision. (T1)
2. Store the card. (T2)
3. Send the receipt. (T3)
"""
        tasks = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-retry) (after: )
- [x] T2: Store the card (branch: feat/orders-card) (after: )
- [ ] T3: Email the receipt (after: T1)
"""
        verify = """# Verify

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T1 | Persist the decision | Implemented, verified | abcdef1234567890 |
| T2 | Store the card | Implemented, verified | |
"""
        text = self.bm.build("cancel-booking", spec, plan, tasks, "", verify)["markdown"]
        self.assertIn(
            "~~T1 Persist the decision~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))",
            text,
        )
        self.assertIn("~~T2 Store the card~~ ✓ done (feat/orders-card)", text)
        self.assertIn("T3 Email the receipt", text)
        self.assertNotIn("Nothing left to build.", text)
        tasks_lines = [line for line in text.splitlines() if line.startswith("- Tasks:")]
        self.assertTrue(tasks_lines)
        other = "\n".join(line for line in text.splitlines() if not line.startswith("- Tasks:"))
        self.assertIsNone(re.search(r"\bT\d+\b", other))
        folded = re.search(r"<details>\n<summary>Wave 1 done \(2 tasks\)</summary>\n\n(.*?)\n</details>", text, re.S)
        self.assertIsNotNone(folded)
        body = folded.group(1)
        self.assertIn("## Wave 1:", body)
        self.assertIn("### feat/orders-retry", body)
        self.assertIn("### feat/orders-card", body)
        self.assertIn("~~Persist the decision~~", body)
        self.assertIn("~~Store the card~~", body)
        self.assertIn(", 2 done", body)
        outside = text.split("</details>", 1)[1]
        self.assertIn("### feat/cancel-booking-send-receipt", outside)
        self.assertNotIn("<details>", outside)
        self.assertIn("Email the receipt", outside)

    def test_done_evidence_uses_a_commit_when_no_pr_or_branch_is_recorded(self):
        task = {"id": 9, "rest": "Archive the note", "map": None, "branch": None}
        verify = "| T9 | Archive the note | Implemented, verified | abcdef1234567890 |"
        self.assertEqual(
            self.bm.done_evidence(task, "feat/cancel-booking-archive", {}, verify),
            "abcdef123456",
        )
        task["branch"] = "feat/orders-card"
        self.assertEqual(
            self.bm.done_evidence(task, "feat/cancel-booking-archive", {}, verify),
            "feat/orders-card",
        )


if __name__ == "__main__":
    unittest.main()
