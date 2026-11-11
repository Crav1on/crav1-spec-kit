"""1.127.0: playbook before later steps, waiting who, row buckets,
ready or not-ready, and acknowledging a shared Done stamp.
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
BLOCKS = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/question_blocks.py"
WALK_SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"
WHEN = "2026-11-10T12:00:00+00:00"
WHEN_LATER = "2026-11-10T12:05:00+00:00"

PLAN = """# Plan: the slice

Reviewed: 2026-11-10, P# open: 0

## Risks
"""

CHAIN = """# Tasks

- [ ] T1: first step for the slice
- [ ] T2: second step for the slice
- [ ] T3: third step for the slice
"""

SPEC = """# Spec

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


def write_slice(root: Path, tasks: str = CHAIN, spec: str = SPEC, plan: str = PLAN) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")


class Buckets(unittest.TestCase):
    def test_order_waits_are_not_blocked_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root)
            payload = must(["readiness", "--root", str(root)])
        buckets = {row["task"]: row["bucket"] for row in payload["rows"]}
        self.assertEqual(buckets["T1"], "ready")
        self.assertEqual(buckets["T2"], "waits-in-order")
        self.assertEqual(buckets["T3"], "waits-in-order")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["blockers"], [])


class WaitingWho(unittest.TestCase):
    MIXED = """# Spec

## Open questions

- Waiting for the partner to confirm the currency?
  - Asked: 2026-10-10, mail to a colleague. Question 1.
  - Blocks: T1
- Which export format?
  - Blocks: T2
- Who signs the vendor file?
  - Pending: drafted 2026-10-10 for a colleague, mail. Not marked as sent yet.
  - Blocks: T3
"""

    UNNAMED = """# Spec

## Open questions

- Which export format?
  - Blocks: T1
"""

    def _ready(self, spec: str) -> dict:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        write_slice(root, spec=spec)
        must([
            "record", "--root", str(root), "--slice", "docs/specs/the-slice",
            "--step", "resolve-open-questions", "--result", "done",
            "--when", WHEN, "--yes",
        ])
        return must(["readiness", "--root", str(root)])

    def test_waiting_for_wins_over_the_asked_line(self):
        payload = self._ready(self.MIXED)
        by_task = {row["task"]: row for row in payload["waiting"]}
        self.assertEqual(by_task["T1"]["who"], "the partner")
        self.assertTrue(by_task["T1"]["asked"])
        self.assertNotEqual(by_task["T1"]["who"], "a colleague")
        self.assertEqual(by_task["T2"]["who"], "not named yet")
        self.assertEqual(by_task["T2"]["bucket"], "waiting")
        self.assertEqual(by_task["T3"]["who"], "a colleague")
        self.assertFalse(by_task["T3"]["asked"])
        self.assertEqual(
            payload["waiting_line"],
            "Waiting: 3 tasks wait on open questions (the partner, a colleague; 1 not named yet).",
        )
        rows = {row["task"]: row["bucket"] for row in payload["rows"]}
        self.assertEqual(rows["T1"], "waiting")
        self.assertEqual(rows["T2"], "waiting")
        self.assertEqual(rows["T3"], "waiting")

    def test_unnamed_question_stays_on_the_waiting_line(self):
        payload = self._ready(self.UNNAMED)
        self.assertEqual(payload["waiting"][0]["who"], "not named yet")
        self.assertEqual(
            payload["waiting_line"],
            "Waiting: 3 tasks wait on open questions (3 not named yet).",
        )
        self.assertEqual(len(payload["waiting"]), 3)
        self.assertEqual(payload["result"], "not-ready")

    def test_question_blocks_parser_prefers_waiting_for(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("question_blocks", BLOCKS)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        got = mod.analyse(self.MIXED, PLAN)
        by_text = {q["text"]: q["who"] for q in got["questions"]}
        self.assertEqual(
            by_text["Waiting for the partner to confirm the currency?"],
            "the partner",
        )
        self.assertIsNone(by_text["Which export format?"])
        self.assertEqual(by_text["Who signs the vendor file?"], "a colleague")


class ReadyResult(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_slice(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_ready_and_not_ready_are_recorded(self):
        ready = must([
            "record", "--root", str(self.root), "--slice", "docs/specs/the-slice",
            "--step", "tasks-ready-to-build", "--result", "ready",
            "--when", WHEN, "--yes",
        ])
        self.assertEqual(ready["result"], "ready")
        resumed = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "keep")
        self.assertEqual(by_id["tasks-ready-to-build"]["result"], "ready")
        must([
            "record", "--root", str(self.root), "--step", "tasks-ready-to-build",
            "--result", "not-ready", "--when", WHEN_LATER, "--yes",
        ])
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Result: not-ready", text)
        again = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in again["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "keep")
        self.assertEqual(by_id["tasks-ready-to-build"]["result"], "not-ready")

    def test_done_is_refused_for_a_new_ready_record_and_old_done_still_reads(self):
        code, payload = run([
            "record", "--root", str(self.root), "--step", "tasks-ready-to-build",
            "--result", "done", "--yes",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "result")
        self.assertFalse((self.root / "walk-progress.md").exists())
        must([
            "record", "--root", str(self.root), "--slice", "docs/specs/the-slice",
            "--step", "tasks-ready-to-build", "--result", "not-ready",
            "--when", WHEN, "--yes",
        ])
        path = self.root / "walk-progress.md"
        path.write_text(path.read_text(encoding="utf-8").replace("Result: not-ready", "Result: done"), encoding="utf-8")
        resumed = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "keep")
        self.assertEqual(by_id["tasks-ready-to-build"]["result"], "done")

    def test_other_steps_still_record_done(self):
        code, payload = run([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "ready", "--yes",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "result")


class AckStamps(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_slice(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _share(self, step: str, when: str) -> None:
        must([
            "record", "--root", str(self.root), "--slice", "docs/specs/the-slice",
            "--step", step, "--result", "done", "--when", when, "--yes",
        ])

    def test_ack_clears_that_stamp_and_a_new_one_warns(self):
        self._share("tighten-spec", WHEN)
        self._share("resolve-open-questions", WHEN)
        warned = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIn("ack-stamps", warned["done_stamp_warning"])
        self.assertIn("walk_progress.py ack-stamps --root <spec-folder> --yes", warned["done_stamp_warning"])
        self.assertIn(WHEN, warned["done_stamp_warning"])
        code, preview = run(["ack-stamps", "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(preview["code"], "needs-yes")
        self.assertEqual(
            preview["lines"],
            [f"Acknowledged stamp: {WHEN} (tighten-spec, resolve-open-questions)"],
        )
        self.assertNotIn("Acknowledged stamp:", (self.root / "walk-progress.md").read_text(encoding="utf-8"))
        wrote = must(["ack-stamps", "--root", str(self.root), "--yes"])
        self.assertEqual(wrote["lines"], preview["lines"])
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn(preview["lines"][0], text)
        quiet = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIsNone(quiet["done_stamp_warning"])
        checked = must(["readiness", "--root", str(self.root)])
        self.assertIsNone(checked["done_stamp_warning"])
        self._share("plan-from-spec", WHEN_LATER)
        self._share("review-and-tighten-plan", WHEN_LATER)
        again = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIn(WHEN_LATER, again["done_stamp_warning"])
        self.assertNotIn(WHEN, again["done_stamp_warning"])

    def test_a_larger_group_on_the_same_stamp_warns_again(self):
        self._share("tighten-spec", WHEN)
        self._share("resolve-open-questions", WHEN)
        must(["ack-stamps", "--root", str(self.root), "--yes"])
        self._share("plan-from-spec", WHEN)
        warned = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIn("plan-from-spec", warned["done_stamp_warning"])
        self.assertIn(WHEN, warned["done_stamp_warning"])


class WalkDocs(unittest.TestCase):
    def test_playbook_question_comes_before_later_steps(self):
        skill = (WALK_SKILL / "SKILL.md").read_text(encoding="utf-8")
        common = (WALK_SKILL / "references/common.md").read_text(encoding="utf-8")
        playbook = (WALK_SKILL / "references/playbook.md").read_text(encoding="utf-8")
        steps = (WALK_SKILL / "references/steps.md").read_text(encoding="utf-8")
        progress = (WALK_SKILL / "references/progress.md").read_text(encoding="utf-8")
        readiness = (WALK_SKILL / "references/readiness.md").read_text(encoding="utf-8")
        for text in (skill, common, playbook, steps):
            self.assertIn("before any later step", text)
        self.assertIn("read-only check", skill)
        self.assertIn("readiness", skill)
        self.assertIn("Resume may report status", skill)
        self.assertIn("No step runs until", playbook)
        self.assertIn("Result: ready", progress)
        self.assertIn("Result: not-ready", progress)
        self.assertIn("older `Result: done`", progress)
        self.assertIn("ack-stamps", progress)
        self.assertIn("Acknowledged stamp:", progress)
        self.assertIn("waits-in-order", readiness)
        self.assertIn("Waiting for", readiness)
        self.assertIn("not named yet", readiness)
        self.assertIn("Result: ready", readiness)
        self.assertIn("Result: not-ready", readiness)

    def test_script_docs_name_the_interpreter_order(self):
        page = (ROOT / "docs/reference/running-scripts.md").read_text(encoding="utf-8")
        rule = (ROOT / ".cursor/rules/crav1.mdc").read_text(encoding="utf-8")
        self.assertIn("python3", page)
        self.assertIn("python", page)
        self.assertIn("py -3", page)
        self.assertIn("Python was not found", page)
        self.assertIn("running-scripts.md", rule)
        skill_root = ROOT / ".cursor/skills/crav1"
        missing = []
        for path in skill_root.rglob("*.md"):
            if "crav1-docs" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            tells = "python3 " in text or "py -3" in text or "Run `scripts/" in text or "run `scripts/" in text
            if tells and "running-scripts.md" not in text:
                missing.append(str(path.relative_to(ROOT)))
        self.assertEqual(missing, [])
