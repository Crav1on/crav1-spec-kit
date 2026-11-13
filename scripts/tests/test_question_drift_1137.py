"""1.137.0: one new open question must not freeze an already-walked slice.

Yesterday the ready check was ready-partial. Today spec.md gains one question
that names T43 and has no Blocks line. T3 and T6 can still start. T43 and
the tasks that wait on it are held, inferred from the text. Older questions
stay waiting. Later walk steps stay covered. A question that names no task
holds the slice only when resolve-open-questions has never been recorded.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
TICK = ROOT / ".cursor/skills/crav1/crav1-build-tasks/scripts/tick_only.py"
RESOLVE = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/resolve_spec.py"
BLOCKS = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/question_blocks.py"
WHEN = "2026-11-11T09:00:00+00:00"

PLAN = """# Plan: orders export

Reviewed: 2026-11-11, P# open: 0

## Risks
"""

SPEC = """# Orders export

The receipt lists the order id.

Playbook: docs/playbooks/orders-export.md

Work item: 78 — orders export

## Match

- Branch: orders-api feat/orders-export (PR 78) merged

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to person A. Question 1.
  - Blocks: T7, T8
- Which lane prints the label?
  - Asked: 2026-10-10, mail to person A. Question 2.
  - Blocks: T9, T10
- Which file holds the manifest?
  - Blocks: T11, T12
- Which stamp goes on the carton?
  - Blocks: T13, T14
"""

NEW_QUESTION = """- Does T43 need a second column on the export?
"""

TASKS = """# Tasks

- [ ] T2: export the receipt (PR 78, merged) (branch: feat/orders-export) (after: ) (spec: A1)
- [ ] T3: record the order (branch: feat/orders-record) (after: ) (spec: A2)
- [ ] T6: send the mail (branch: feat/orders-mail) (after: ) (spec: A3)
- [ ] T7: choose the currency (after: ) (spec: A4)
- [ ] T8: round the currency (after: ) (spec: A5)
- [ ] T9: choose the lane (after: ) (spec: A6)
- [ ] T10: print the label (after: ) (spec: A7)
- [ ] T11: write the manifest (after: ) (spec: A8)
- [ ] T12: store the manifest (after: ) (spec: A9)
- [ ] T13: choose the stamp (after: ) (spec: A10)
- [ ] T14: apply the stamp (after: ) (spec: A11)
- [ ] T43: add the column (after: ) (spec: A12)
- [ ] T44: fill the column (after: T43) (spec: A13)
- [ ] T45: check the column (after: T44) (spec: A14)
"""

VERIFY = """# Verify

## TL;DR

| | Count | Ids |
| --- | --- | --- |
| Implemented, verified, tick pending | 1 | T2 |

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | export the receipt | Implemented, verified, tick pending | unit |
| T3 | record the order | Not implemented | |
| T6 | send the mail | Not implemented | |
"""

HELD_BY_BLOCKS = [f"T{n}" for n in range(7, 15)]
LATER = (
    "tighten-spec",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)


def run(script: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def must_json(script: Path, args: list[str]) -> dict:
    code, out, err = run(script, args)
    try:
        payload = json.loads(out or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(err + out) from exc
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


def write_slice(root: Path, spec: str = SPEC) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    (root / "verify.md").write_text(VERIFY, encoding="utf-8")


def record_walk(root: Path) -> None:
    for step, result in (
        ("tighten-spec", "done"),
        ("resolve-open-questions", "done"),
        ("plan-from-spec", "done"),
        ("review-and-tighten-plan", "done"),
        ("tasks-ready-to-build", "ready-partial"),
    ):
        must_json(WALK, [
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", step, "--result", result, "--when", WHEN, "--yes",
        ])


def with_new_question(spec: str = SPEC) -> str:
    return spec.rstrip() + "\n" + NEW_QUESTION


class QuestionDrift(unittest.TestCase):
    def test_one_new_question_keeps_ready_partial(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        write_slice(root)
        record_walk(root)
        before = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(before["result"], "ready-partial")
        self.assertIn("T3", before["can_start"])
        self.assertIn("T6", before["can_start"])
        self.assertIn("T43", before["can_start"])
        for tid in HELD_BY_BLOCKS:
            self.assertIn(tid, before["held"])

        (root / "spec.md").write_text(with_new_question(), encoding="utf-8")
        payload = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(payload["can_start"], ["T3", "T6"])
        for tid in ("T43", "T44", "T45"):
            self.assertIn(tid, payload["held"])
        for tid in HELD_BY_BLOCKS:
            self.assertIn(tid, payload["held"])
        by_task = {row["task"]: row for row in payload["rows"]}
        self.assertIn("inferred from the text", by_task["T43"]["reason"])
        self.assertIn("T43", by_task["T44"]["reason"])
        self.assertIn("T44", by_task["T45"]["reason"])
        self.assertTrue(by_task["T7"]["kept"])
        waiting_tasks = {hit["task"] for hit in payload["waiting"]}
        self.assertIn("T7", waiting_tasks)
        self.assertIn("T43", waiting_tasks)
        self.assertNotIn("T3", waiting_tasks)
        reopened = [hit["step"] for hit in payload["reopened"]]
        self.assertEqual(reopened, ["resolve-open-questions"])
        for step in LATER:
            self.assertNotIn(step, reopened)
        self.assertIn("rerun or clear", payload["next"])
        self.assertIn("/crav1-resolve-open-questions orders-export", payload["next"])
        self.assertIn("Waiting:", payload["resolve_waiting"])
        self.assertIn("resolve-open-questions", payload["resolve_waiting"])
        joined = "\n".join(payload["held_lines"])
        self.assertIn("Inferred from the text.", joined)

        resumed = must_json(WALK, ["resume", "--root", str(root), "--no-playbook"])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        self.assertEqual(by_id["resolve-open-questions"]["changed"], ["questions"])
        for step in LATER:
            self.assertEqual(by_id[step]["status"], "keep", step)

    def test_adding_blocks_and_recording_resolve_leaves_later_steps_covered(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        write_slice(root)
        record_walk(root)
        spec = with_new_question().replace(
            "- Does T43 need a second column on the export?\n",
            "- Does T43 need a second column on the export?\n  - Blocks: T43\n",
        )
        (root / "spec.md").write_text(spec, encoding="utf-8")
        must_json(WALK, [
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", "resolve-open-questions", "--result", "done",
            "--when", "2026-11-12T09:00:00+00:00", "--yes",
        ])
        resumed = must_json(WALK, ["resume", "--root", str(root), "--no-playbook"])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["resolve-open-questions"]["status"], "keep")
        for step in LATER:
            self.assertEqual(by_id[step]["status"], "keep", step)
        payload = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(payload["reopened"], [])
        self.assertIn("T43", payload["held"])
        by_task = {row["task"]: row for row in payload["rows"]}
        self.assertIn("(recorded)", by_task["T43"]["reason"])
        self.assertIsNone(payload["resolve_waiting"])

    def test_a_question_with_no_task_holds_the_slice_only_before_resolve_is_recorded(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        spec = "# Orders export\n\n## Open questions\n\n- Who signs the export?\n"
        tasks = "# Tasks\n\n- [ ] T3: record the order (after: )\n- [ ] T6: send the mail (after: )\n"
        (root / "spec.md").write_text(spec, encoding="utf-8")
        (root / "plan.md").write_text(PLAN, encoding="utf-8")
        (root / "tasks.md").write_text(tasks, encoding="utf-8")
        held = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(held["result"], "not-ready")
        self.assertEqual(held["can_start"], [])
        blocked = {row["task"] for row in held["blockers"]}
        self.assertEqual(blocked, {"T3", "T6"})
        self.assertTrue(all(row["step"] == "resolve-open-questions" for row in held["blockers"]))

        must_json(WALK, [
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", "resolve-open-questions", "--result", "done",
            "--when", WHEN, "--yes",
        ])
        clear = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(clear["can_start"], ["T3", "T6"])
        self.assertEqual(clear["held"], [])
        self.assertEqual(clear["result"], "ready")

    def test_a_spec_edit_outside_open_questions_reopens_later_steps(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        write_slice(root)
        record_walk(root)
        text = (root / "spec.md").read_text(encoding="utf-8")
        (root / "spec.md").write_text(
            text.replace("The receipt lists the order id.", "The receipt lists the order id and the lane."),
            encoding="utf-8",
        )
        payload = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "not-ready")
        reopened = [hit["step"] for hit in payload["reopened"]]
        for step in LATER:
            if step == "tasks-ready-to-build":
                self.assertNotIn(step, reopened)
                self.assertNotIn(step, payload["next"])
                self.assertNotIn(step, payload["because"])
            else:
                self.assertIn(step, reopened)
                self.assertIn(step, payload["next"])
        self.assertIn("rerun or clear", payload["next"])
        ticked = must_json(TICK, ["--root", str(root), "T2", "--yes"])
        self.assertTrue(ticked["ticked"])
        self.assertFalse(ticked["worker"])
        self.assertEqual(ticked["result"], "not-ready")
        self.assertIn("- [x] T2:", (root / "tasks.md").read_text(encoding="utf-8"))


class ResolverTokens(unittest.TestCase):
    def test_cc_1_0_matches_one_playbook_and_an_ambiguous_query_stops(self):
        root = Path(tempfile.mkdtemp())
        one = root / "slice-a"
        one.mkdir()
        (one / "spec.md").write_text(
            "# Receipts\n\nPlaybook: docs/playbooks/cc-process-1-0.md\n",
            encoding="utf-8",
        )
        exact = must_json(RESOLVE, ["cc process 1.0", "--root", str(root), "--json"])
        self.assertEqual(exact["slug"], "slice-a")
        self.assertEqual(exact["how"], "playbook")
        partial = must_json(RESOLVE, ["cc 1.0", "--root", str(root), "--json"])
        self.assertEqual(partial["slug"], "slice-a")
        self.assertIn("playbook", partial["how"])

        other = root / "slice-b"
        other.mkdir()
        (other / "spec.md").write_text(
            "# Billing\n\nPlaybook: docs/playbooks/cc-billing-1-0.md\n",
            encoding="utf-8",
        )
        code, out, err = run(RESOLVE, ["cc 1.0", "--root", str(root)])
        self.assertEqual(code, 2, err + out)
        self.assertIn("Several spec folders match", out)
        self.assertIn("slice-a", out)
        self.assertIn("slice-b", out)
        self.assertIn("Stop.", out)

    def test_no_match_lists_nearest_slugs(self):
        root = Path(tempfile.mkdtemp())
        folder = root / "orders-export"
        folder.mkdir()
        (folder / "spec.md").write_text("# Orders export\n", encoding="utf-8")
        code, out, err = run(RESOLVE, ["zebra 9", "--root", str(root)])
        self.assertEqual(code, 2, err + out)
        self.assertIn("No spec folder matches 'zebra 9'.", out)
        self.assertIn("Nearest:", out)
        self.assertIn("- orders-export", out)
        payload = json.loads(run(RESOLVE, ["zebra 9", "--root", str(root), "--json"])[1])
        self.assertEqual(payload["nearest"], ["orders-export"])


class WholeSliceMark(unittest.TestCase):
    def test_explicit_whole_slice_holds_after_resolve_and_an_open_questions_edit(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        spec = """# Orders export

The receipt lists the order id.

## Match

- Branch: orders-api feat/orders-export (PR 78) merged

## Open questions

- Who signs the export?
  - Blocks: whole slice
"""
        tasks = """# Tasks

- [ ] T2: export the receipt (PR 78, merged) (after: )
- [ ] T3: record the order (after: )
- [ ] T6: send the mail (after: )
"""
        verify = """# Verify

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | export the receipt | Implemented, verified, tick pending | unit |
| T3 | record the order | Not implemented | |
| T6 | send the mail | Not implemented | |
"""
        (root / "spec.md").write_text(spec, encoding="utf-8")
        (root / "plan.md").write_text(PLAN, encoding="utf-8")
        (root / "tasks.md").write_text(tasks, encoding="utf-8")
        (root / "verify.md").write_text(verify, encoding="utf-8")
        for step, result in (
            ("tighten-spec", "done"),
            ("resolve-open-questions", "done"),
            ("plan-from-spec", "done"),
            ("review-and-tighten-plan", "done"),
            ("tasks-ready-to-build", "not-ready"),
        ):
            must_json(WALK, [
                "record", "--root", str(root), "--slice", "docs/specs/orders-export",
                "--step", step, "--result", result, "--when", WHEN, "--yes",
            ])
        held = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(held["can_start"], [])
        self.assertEqual(held["held"], ["T3", "T6"])
        self.assertEqual(held["result"], "not-ready")
        by_task = {row["task"]: row for row in held["rows"]}
        self.assertIn("blocks the whole slice (recorded)", by_task["T3"]["reason"])
        self.assertIn("Holds the whole slice.", "\n".join(held["held_lines"]))

        edited = spec.rstrip() + "\n- Which lane prints the label?\n  - Blocks: none\n"
        (root / "spec.md").write_text(edited, encoding="utf-8")
        after = must_json(WALK, ["readiness", "--root", str(root)])
        self.assertEqual(after["can_start"], [])
        self.assertEqual(after["held"], ["T3", "T6"])
        self.assertNotIn("T3", {row["task"] for row in after["blockers"]})
        resumed = must_json(WALK, ["resume", "--root", str(root), "--no-playbook"])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        for step in LATER:
            self.assertEqual(by_id[step]["status"], "keep", step)
        ticked = must_json(TICK, ["--root", str(root), "T2", "--yes"])
        self.assertTrue(ticked["ticked"])
        self.assertFalse(ticked["worker"])
        self.assertEqual(ticked["result"], "not-ready")
        self.assertIn("- [x] T2:", (root / "tasks.md").read_text(encoding="utf-8"))

    def test_parser_accepts_whole_slice_wording_and_the_skill_writes_the_mark(self):
        root = Path(tempfile.mkdtemp())
        spec = root / "spec.md"
        plan = root / "plan.md"
        spec.write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Who signs the export?\n  - Blocks: the whole slice\n"
            "- Which lane prints the label?\n  - Blocks: Whole Slice\n",
            encoding="utf-8",
        )
        plan.write_text("## Risks\n", encoding="utf-8")
        code, out, err = run(BLOCKS, [str(spec), str(plan)])
        self.assertEqual(code, 0, err + out)
        payload = json.loads(out)
        for row in payload["questions"]:
            self.assertEqual(row["mark"], "whole")
            self.assertTrue(row["blocks_slice"])
            self.assertTrue(row["recorded"])
        skill = (
            ROOT / ".cursor/skills/crav1/crav1-resolve-open-questions/SKILL.md"
        ).read_text(encoding="utf-8")
        reference = (
            ROOT / ".cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md"
        ).read_text(encoding="utf-8")
        self.assertIn("**The whole slice** writes `- Blocks: whole slice`", skill)
        self.assertIn("Blocks: whole slice", reference)
        self.assertNotIn("writes no `Blocks:` line", skill)


class InferredBlocks(unittest.TestCase):
    def test_text_ids_are_limited_to_tasks_that_exist(self):
        root = Path(tempfile.mkdtemp())
        spec = root / "spec.md"
        plan = root / "plan.md"
        tasks = root / "tasks.md"
        spec.write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Does T43 need a second column, or is T99 enough?\n"
            "- Who signs the export?\n",
            encoding="utf-8",
        )
        plan.write_text("## Risks\n", encoding="utf-8")
        tasks.write_text(
            "- [ ] T3: record the order\n- [ ] T43: add the column\n",
            encoding="utf-8",
        )
        code, out, err = run(BLOCKS, [str(spec), str(plan), str(tasks)])
        self.assertEqual(code, 0, err + out)
        payload = json.loads(out)
        by_text = {row["text"]: row for row in payload["questions"]}
        named = by_text["Does T43 need a second column, or is T99 enough?"]
        self.assertEqual(named["mark"], "inferred")
        self.assertEqual(named["tasks"], ["T43"])
        self.assertFalse(named["blocks_slice"])
        missing = by_text["Who signs the export?"]
        self.assertEqual(missing["mark"], "missing")
        self.assertTrue(missing["blocks_slice"])


if __name__ == "__main__":
    unittest.main()
