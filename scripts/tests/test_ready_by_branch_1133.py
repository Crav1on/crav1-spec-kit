"""1.133.0: ready check grouped by build-map branch, and T# on the map."""

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
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
MAP_SRC = ROOT / "scripts/build-map.py"
WHEN = "2026-11-11T12:00:00+00:00"

PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Record the decision. (T2, T5)
2. Export the receipt. (T6)
3. Choose the currency. (T3)
4. Archive the receipt. (T4)

## Risks
"""

SPEC = """# Spec

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to the partner. Question 1.
  - Blocks: T3

## Match

- Repo: orders-api https://github.com/contoso/orders-api
- Branch: orders-api feat/orders-api-record (PR 12)
"""

TASKS = """# Tasks

- [ ] T2: Record the decision (branch: feat/orders-api-record) (after: )
- [ ] T5: Store the card (branch: feat/orders-api-record) (after: )
- [ ] T6: Email the receipt (branch: feat/orders-api-export) (after: )
- [ ] T3: Choose the currency (branch: feat/orders-api-currency) (after: )
- [ ] T4: Archive the receipt (branch: feat/orders-api-archive) (after: T3)
"""

ONE = """# Tasks

- [ ] T1: Record the decision (branch: feat/orders-api-record) (after: )
- [ ] T2: Store the card (branch: feat/orders-api-record) (after: )
"""

ONE_PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Record the decision. (T1, T2)

## Risks
"""

ONE_SPEC = """# Spec

## Open questions
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


def write_slice(root: Path, tasks: str, spec: str, plan: str) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")


def record_resolve(root: Path) -> None:
    must([
        "record", "--root", str(root), "--slice", "docs/specs/orders-api",
        "--step", "resolve-open-questions", "--result", "done",
        "--when", WHEN, "--yes",
    ])


def load_map():
    spec = importlib.util.spec_from_file_location("build_map_wrapper", MAP_SRC)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    return wrapper.load()


class ReadyByBranch(unittest.TestCase):
    def test_ready_and_held_are_grouped_with_one_next_per_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, TASKS, SPEC, PLAN)
            record_resolve(root)
            payload = must(["readiness", "--root", str(root)])
            bm = load_map()
            text = (root / "tasks.md").read_text(encoding="utf-8")
            spec = (root / "spec.md").read_text(encoding="utf-8")
            plan = (root / "plan.md").read_text(encoding="utf-8")
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(payload["ready_lines"], [
            "- `feat/orders-api-record` (wave 1): T2 Record the decision; T5 Store the card",
            "- `feat/orders-api-export` (wave 1): T6 Email the receipt",
        ])
        self.assertEqual(payload["held_lines"], [
            '- `feat/orders-api-currency` (wave 1): T3 Choose the currency — open question "Which currency for refunds?" Waiting for the partner.',
            "- `feat/orders-api-archive` (wave 2): T4 Archive the receipt — held, waits on T3",
        ])
        self.assertEqual(payload["next_lines"], [
            "Next: /crav1-build-tasks T2 T5 (on `feat/orders-api-record`)",
            "Next: /crav1-build-tasks T6 (on `feat/orders-api-export`)",
        ])
        self.assertEqual(payload["next"], "\n".join(payload["next_lines"]))
        self.assertEqual(payload["line"], "Ready now\n" + "\n".join(payload["ready_lines"] + ["Held"] + payload["held_lines"]))
        for line in payload["ready_lines"] + payload["held_lines"]:
            self.assertRegex(line, r"T\d+ \S")
        for task, branch in (("T2", "feat/orders-api-record"), ("T6", "feat/orders-api-export"), ("T3", "feat/orders-api-currency"), ("T4", "feat/orders-api-archive")):
            self.assertEqual(bm.recommended_branch(root.name, spec, plan, text, task), branch)

    def test_walk_record_stays_ready_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, TASKS, SPEC, PLAN)
            record_resolve(root)
            recorded = must([
                "record", "--root", str(root), "--slice", "docs/specs/orders-api",
                "--step", "tasks-ready-to-build", "--result", "ready-partial", "--yes",
            ])
            text = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertEqual(recorded["result"], "ready-partial")
        self.assertIn("Result: ready-partial", text)
        self.assertNotIn("Result: not-ready", text)

    def test_single_branch_is_one_group_and_one_next_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, ONE, ONE_SPEC, ONE_PLAN)
            payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready")
        self.assertIsNone(payload["line"])
        self.assertEqual(payload["held_lines"], [])
        self.assertEqual(payload["ready_lines"], [
            "- `feat/orders-api-record` (wave 1): T1 Record the decision; T2 Store the card",
        ])
        self.assertEqual(payload["next_lines"], [
            "Next: /crav1-build-tasks T1 T2 (on `feat/orders-api-record`)",
        ])
        self.assertEqual(payload["next"].count("\n"), 0)

    def test_a_task_that_waits_in_order_is_not_on_the_next_line(self):
        tasks = """# Tasks

- [ ] T1: Record the decision (branch: feat/orders-api-record)
- [ ] T2: Store the card (branch: feat/orders-api-record)
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, tasks, ONE_SPEC, ONE_PLAN)
            payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready")
        self.assertEqual(payload["ready_lines"], [
            "- `feat/orders-api-record` (wave 1): T1 Record the decision",
        ])
        self.assertEqual(payload["next_lines"], [
            "Next: /crav1-build-tasks T1 (on `feat/orders-api-record`)",
        ])
        self.assertNotIn("T2", payload["next"])


class MapShowsTaskIds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bm = load_map()

    def test_tasks_field_and_done_rows_show_the_id_and_short_name(self):
        spec = """# Spec

## Open questions

## Match

- Repo: orders-api https://github.com/contoso/orders-api
- Branch: orders-api feat/orders-api-record (PR 12)
"""
        plan = """# Plan

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Nothing else starts before T1's `check` prints ok. (T1)
2. Require the pipeline. (T5)

## Risks
"""
        tasks = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-api-record) (after: )
- [ ] T5: Require the pipeline as build validation (after: )
"""
        verify = """# Verify

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T1 | Persist the decision | Implemented, verified | |
"""
        work = "Work item: 44 — task: T5 orders-api: require pipeline 6 as build validation (ADO: example/orders)\n"
        text = self.bm.build("orders-api", spec, plan, tasks, work, verify)["markdown"]
        self.assertIn("- Tasks: ~~T1 Persist the decision~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))", text)
        self.assertIn("- Tasks: T5 orders-api: require pipeline 6 as build validation", text)
        delivers = "\n".join(line for line in text.splitlines() if line.startswith("- Delivers:"))
        self.assertNotIn("T1", delivers)
        self.assertNotIn("T5", delivers)
        self.assertNotRegex(delivers, r"(^|\s)'s\b")
        self.assertEqual(
            self.bm.clean_prose("Nothing else starts before T1's `check` prints ok."),
            "Nothing else starts before `check` prints ok.",
        )


if __name__ == "__main__":
    unittest.main()
