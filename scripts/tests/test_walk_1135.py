"""1.135.0: one jump back from a spec finding, and a stale verify.md.

The walk offers the jump once, records Continue, and does not write verify.md.
The ready check flags verify.md when a ticked task is still not implemented,
when Next names a ticked task, or when a merged task is still Not implemented.
A merged unticked task whose only leftover is the tick is not behind.
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
SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"
WHEN = "2026-11-11T20:30:00+00:00"
FINDING = (
    "the plan requires a named person's yes to stop a prod function app, "
    "but the spec names no approver"
)
RECOMMENDED = "run /crav1-tighten-spec on just that finding now (Recommended)"
OTHER = "keep it as an open point and continue"
WAITING = (
    "Waiting: /crav1-verify-build-against-spec orders-api - "
    "verify.md is behind tasks.md (T2, T45)"
)

SPEC = """# Spec

## Match

- Branch: orders-api feat/orders-export (PR 45) merged

## Open questions
"""

PLAN = """# Plan: the slice

Reviewed: 2026-11-11, P# open: 0

## Risks
"""

TASKS = """# Tasks

- [x] T2: export the receipt (verify: unit — receipt test) (spec: A1)
- [ ] T45: stop the function app (branch: feat/orders-export) (verify: unit — stop test) (spec: A2)
- [ ] T1: record the order (verify: unit — record test) (spec: A3)
"""

VERIFY = """# Verify

## TL;DR

| | Count | Ids |
| --- | --- | --- |
| Not implemented | 2 | T2, T45 |

Next: /crav1-build-tasks T2 T45, because they are not built.

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | export the receipt | Not implemented | |
| T45 | stop the function app | Not implemented | |
| T1 | record the order | Not implemented | |
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


def slice_dir() -> Path:
    root = Path(tempfile.mkdtemp()) / "orders-api"
    root.mkdir()
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    (root / "verify.md").write_text(VERIFY, encoding="utf-8")
    return root


class JumpBack(unittest.TestCase):
    def test_offer_is_one_card_and_the_skill_names_it(self):
        root = slice_dir()
        before = (root / "verify.md").read_bytes()
        payload = must(["spec-finding", "--root", str(root), "--id", "P2", "--text", FINDING])
        self.assertEqual(payload["offer"], "jump-back")
        self.assertFalse(payload["pause"])
        self.assertIsNone(payload["wrote"])
        self.assertEqual(payload["path"], "../crav1-tighten-spec/SKILL.md")
        labels = [item["label"] for item in payload["options"]]
        self.assertEqual(labels, [RECOMMENDED, OTHER])
        self.assertTrue(payload["options"][0]["recommended"])
        self.assertFalse((root / "walk-progress.md").exists())
        self.assertEqual((root / "verify.md").read_bytes(), before)
        steps = (SKILL / "references" / "steps.md").read_text(encoding="utf-8")
        self.assertIn(RECOMMENDED, steps)
        self.assertIn(OTHER, steps)
        self.assertIn("Open `../crav1-tighten-spec/SKILL.md`", steps)
        self.assertIn("A plan-tagged finding stays", steps)
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never writes `verify.md`", skill.lower())

    def test_one_jump_then_open_point_and_continue(self):
        root = slice_dir()
        before = (root / "verify.md").read_bytes()
        jumped = must([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", FINDING,
            "--choice", "tighten-spec", "--yes",
        ])
        self.assertEqual(jumped["recorded"], "jump-back")
        self.assertEqual(
            jumped["continue"],
            ["plan-from-spec", "review-and-tighten-plan", "tasks-ready-to-build"],
        )
        self.assertEqual(jumped["path"], "../crav1-tighten-spec/SKILL.md")
        self.assertFalse(jumped["pause"])
        progress = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("- Jump-back: P2", progress)
        self.assertIn("Result: jumped", progress)
        self.assertIn("Open: ../crav1-tighten-spec/SKILL.md", progress)
        self.assertIn(
            "Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build",
            progress,
        )
        code, again = run(["spec-finding", "--root", str(root), "--id", "P2", "--text", FINDING])
        self.assertEqual(code, 0)
        self.assertIsNone(again["offer"])
        self.assertTrue(again["already_jumped"])
        self.assertTrue(again["open_point"])
        self.assertTrue(again["needs_record"])
        self.assertIsNone(again["wrote"])
        refused = must([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", FINDING,
            "--choice", "tighten-spec", "--yes",
        ])
        self.assertTrue(refused["refused_second_jump"])
        self.assertEqual(refused["recorded"], "open-point")
        self.assertEqual(
            refused["continue"],
            ["review-and-tighten-plan", "tasks-ready-to-build"],
        )
        progress = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("- Open point: P2", progress)
        self.assertIn("Result: open-point", progress)
        self.assertIn("Continue: review-and-tighten-plan, tasks-ready-to-build", progress)
        must([
            "record", "--root", str(root), "--step", "review-architecture",
            "--result", "done", "--yes", "--when", WHEN,
        ])
        kept = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("- Jump-back: P2", kept)
        self.assertIn("Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build", kept)
        self.assertEqual((root / "verify.md").read_bytes(), before)

    def test_plan_finding_is_not_a_jump(self):
        root = slice_dir()
        payload = must([
            "spec-finding", "--root", str(root), "--id", "P1",
            "--text", "the task has no verify kind", "--tag", "plan",
        ])
        self.assertTrue(payload["behave_as_today"])
        self.assertIsNone(payload["offer"])
        self.assertIsNone(payload["wrote"])
        self.assertFalse((root / "walk-progress.md").exists())


class StaleVerify(unittest.TestCase):
    def test_ticked_task_merged_pr_and_stale_next(self):
        root = slice_dir()
        before = (root / "verify.md").read_bytes()
        payload = must(["readiness", "--root", str(root)])
        self.assertTrue(payload["verify_behind"])
        self.assertEqual(payload["verify_stale"], ["T2", "T45"])
        self.assertEqual(payload["verify_waiting"], WAITING)
        self.assertFalse(payload["trust_stale_next"])
        self.assertIn("T2", payload["stale_next"])
        self.assertNotIn(payload["stale_next"], payload["next"])
        self.assertIn("T1", payload["can_start"])
        self.assertNotIn("T2", payload["can_start"])
        self.assertNotIn("T45", payload["can_start"])
        self.assertNotIn("T2", payload["next"])
        self.assertNotIn("T45", payload["next"])
        self.assertEqual((root / "verify.md").read_bytes(), before)
        rows = {row["task"]: row for row in payload["rows"]}
        self.assertEqual(rows["T2"]["bucket"], "done")
        self.assertTrue(rows["T2"].get("stale_verify"))
        self.assertNotEqual(rows["T2"]["bucket"], "needs-verify")

    def test_merged_mark_on_the_task_line(self):
        root = slice_dir()
        (root / "tasks.md").write_text(
            "# Tasks\n\n- [ ] T2: export the receipt (PR 12, merged) (spec: A1)\n",
            encoding="utf-8",
        )
        (root / "spec.md").write_text("# Spec\n\n## Open questions\n", encoding="utf-8")
        (root / "verify.md").write_text(
            "# Verify\n\n## Tasks — overview (dependency order)\n\n"
            "| T# | Title | Status | Verify |\n| --- | --- | --- | --- |\n"
            "| T2 | export the receipt | Not implemented | |\n",
            encoding="utf-8",
        )
        payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["verify_stale"], ["T2"])
        self.assertIn("(T2)", payload["verify_waiting"])
        self.assertNotIn("T2", payload["can_start"])

    def test_stale_next_when_the_row_is_already_verified(self):
        root = slice_dir()
        (root / "tasks.md").write_text(
            "# Tasks\n\n- [x] T2: export the receipt (spec: A1)\n",
            encoding="utf-8",
        )
        (root / "spec.md").write_text("# Spec\n\n## Open questions\n", encoding="utf-8")
        (root / "verify.md").write_text(
            "# Verify\n\nNext: /crav1-build-tasks T2, because they are not built.\n\n"
            "## Tasks — overview (dependency order)\n\n"
            "| T# | Title | Status | Verify |\n| --- | --- | --- | --- |\n"
            "| T2 | export the receipt | Implemented, verified | unit |\n",
            encoding="utf-8",
        )
        before = (root / "verify.md").read_bytes()
        payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["verify_stale"], ["T2"])
        self.assertEqual(
            payload["verify_waiting"],
            "Waiting: /crav1-verify-build-against-spec orders-api - "
            "verify.md is behind tasks.md (T2)",
        )
        self.assertNotIn(payload["stale_next"], payload["next"] or "")
        self.assertFalse(payload["trust_stale_next"])
        self.assertEqual((root / "verify.md").read_bytes(), before)

    def test_an_open_task_is_not_behind(self):
        root = slice_dir()
        (root / "tasks.md").write_text(
            "# Tasks\n\n- [ ] T1: record the order (spec: A1)\n",
            encoding="utf-8",
        )
        (root / "spec.md").write_text("# Spec\n\n## Open questions\n", encoding="utf-8")
        (root / "verify.md").write_text(
            "# Verify\n\nNext: /crav1-build-tasks T1, because they are not built.\n\n"
            "## Tasks — overview (dependency order)\n\n"
            "| T# | Title | Status | Verify |\n| --- | --- | --- | --- |\n"
            "| T1 | record the order | Not implemented | |\n",
            encoding="utf-8",
        )
        payload = must(["readiness", "--root", str(root)])
        self.assertFalse(payload["verify_behind"])
        self.assertEqual(payload["verify_stale"], [])
        self.assertIsNone(payload["verify_waiting"])
        self.assertIsNone(payload["stale_next"])
        self.assertIn("T1", payload["can_start"])

    def test_walk_sources_do_not_write_verify(self):
        source = WALK.read_text(encoding="utf-8")
        self.assertNotIn('verify.md").write', source)
        self.assertNotIn("verify.md').write", source)
        for name in ("SKILL.md", "references/steps.md", "references/readiness.md", "references/common.md"):
            text = (SKILL / name).read_text(encoding="utf-8")
            self.assertIn("verify.md", text)
        joined = "\n".join(
            (SKILL / name).read_text(encoding="utf-8")
            for name in ("SKILL.md", "references/readiness.md", "references/common.md")
        )
        self.assertIn("never writes `verify.md`", joined.lower())
        ready = (
            ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("does not write `verify.md`", ready)


if __name__ == "__main__":
    unittest.main()
