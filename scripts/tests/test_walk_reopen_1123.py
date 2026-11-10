"""1.123.0: a step inside the walk does not reopen earlier steps.

An outside change reopens only the steps that change affects. A reopened
step blocks the ready check until it is rerun or cleared with nothing new.
The script stamps Done as a full timestamp.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tighten_plan_walk import WHEN, must, run  # noqa: E402

DONE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")


class InsideWalk(unittest.TestCase):
    def setUp(self):
        import tempfile

        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "spec.md").write_text("spec v1\n", encoding="utf-8")
        (self.root / "plan.md").write_text("plan v1\n", encoding="utf-8")
        (self.root / "tasks.md").write_text("tasks v1\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def record(self, step: str, result: str = "done"):
        return must([
            "record", "--root", str(self.root), "--slice", "docs/specs/orders-retry",
            "--step", step, "--result", result, "--when", WHEN, "--yes",
        ])

    def statuses(self):
        payload = must(["resume", "--root", str(self.root), "--no-playbook"])
        return {row["id"]: row["status"] for row in payload["steps"]}, payload["continue_from"]

    def test_later_spec_steps_do_not_reopen_earlier_ones(self):
        self.record("review-architecture")
        (self.root / "spec.md").write_text("spec v2\n", encoding="utf-8")
        self.record("tighten-spec")
        (self.root / "spec.md").write_text("spec v3\n", encoding="utf-8")
        self.record("resolve-open-questions")
        status, nxt = self.statuses()
        self.assertEqual(status["review-architecture"], "keep")
        self.assertEqual(status["tighten-spec"], "keep")
        self.assertEqual(status["resolve-open-questions"], "keep")
        self.assertEqual(nxt, "plan-from-spec")
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        # Earlier Done times stay. The script does not restamp them.
        self.assertEqual(text.count(f"Done: {WHEN}"), 3)

    def test_later_plan_step_does_not_reopen_plan_from_spec(self):
        self.record("review-architecture", "nothing-to-do")
        self.record("tighten-spec", "nothing-to-do")
        self.record("resolve-open-questions", "nothing-to-do")
        self.record("plan-from-spec")
        (self.root / "plan.md").write_text("plan v2\n", encoding="utf-8")
        (self.root / "tasks.md").write_text("tasks v2\n", encoding="utf-8")
        self.record("review-and-tighten-plan")
        status, nxt = self.statuses()
        self.assertEqual(status["plan-from-spec"], "keep")
        self.assertEqual(status["review-and-tighten-plan"], "keep")
        self.assertEqual(nxt, "tasks-ready-to-build")

    def test_in_walk_extra_is_recorded_and_does_not_reopen(self):
        self.record("review-architecture")
        self.record("tighten-spec")
        (self.root / "spec.md").write_text("spec after security review\n", encoding="utf-8")
        before, nxt = self.statuses()
        self.assertEqual(before["tighten-spec"], "reopen")
        self.assertEqual(nxt, "tighten-spec")
        self.record("review-security")
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("- Extra: review-security", text)
        self.assertNotIn("- Step: review-security", text)
        payload = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in payload["steps"]}
        self.assertEqual(by_id["review-architecture"]["status"], "keep")
        self.assertEqual(by_id["tighten-spec"]["status"], "keep")
        self.assertEqual(by_id["review-security"]["status"], "keep")
        self.assertTrue(by_id["review-security"]["extra"])
        self.assertEqual(payload["continue_from"], "resolve-open-questions")
        (self.root / "spec.md").write_text("spec after tighten\n", encoding="utf-8")
        self.record("resolve-open-questions")
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("- Extra: review-security", text)
        status, nxt = self.statuses()
        self.assertEqual(status["tighten-spec"], "keep")
        self.assertEqual(status["resolve-open-questions"], "keep")
        self.assertEqual(nxt, "plan-from-spec")

    def test_in_walk_extra_plan_write_does_not_reopen_the_plan_review(self):
        self.record("review-architecture", "nothing-to-do")
        self.record("tighten-spec", "nothing-to-do")
        self.record("resolve-open-questions", "nothing-to-do")
        self.record("plan-from-spec")
        self.record("review-and-tighten-plan")
        (self.root / "plan.md").write_text("plan after the data model\n", encoding="utf-8")
        (self.root / "tasks.md").write_text("tasks after the data model\n", encoding="utf-8")
        self.record("model-data")
        status, nxt = self.statuses()
        self.assertEqual(status["plan-from-spec"], "keep")
        self.assertEqual(status["review-and-tighten-plan"], "keep")
        self.assertEqual(nxt, "tasks-ready-to-build")
        self.assertIn("- Extra: model-data", (self.root / "walk-progress.md").read_text(encoding="utf-8"))

    def test_cover_is_optional_for_an_outside_write_and_names_no_extra(self):
        self.record("review-architecture")
        self.record("tighten-spec")
        (self.root / "spec.md").write_text("spec edited outside the walk\n", encoding="utf-8")
        code, payload = run(["cover", "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "needs-yes")
        must(["cover", "--root", str(self.root), "--yes"])
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertNotIn("- Extra:", text)
        status, nxt = self.statuses()
        self.assertEqual(status["review-architecture"], "keep")
        self.assertEqual(status["tighten-spec"], "keep")
        self.assertEqual(nxt, "resolve-open-questions")

    def test_unknown_extra_is_rejected(self):
        code, payload = run([
            "record", "--root", str(self.root), "--step", "not-an-extra",
            "--result", "done", "--yes",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "step")

    def test_architecture_reopens_only_when_it_is_the_latest_spec_step(self):
        self.record("review-architecture")
        (self.root / "spec.md").write_text("spec from outside\n", encoding="utf-8")
        status, nxt = self.statuses()
        self.assertEqual(status["review-architecture"], "reopen")
        self.assertEqual(nxt, "review-architecture")

    def test_outside_spec_change_skips_architecture_and_reopens_the_rest(self):
        self.record("review-architecture")
        self.record("tighten-spec")
        self.record("resolve-open-questions")
        self.record("plan-from-spec")
        (self.root / "spec.md").write_text("spec from add-to-spec\n", encoding="utf-8")
        payload = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in payload["steps"]}
        self.assertEqual(by_id["review-architecture"]["status"], "keep")
        self.assertEqual(by_id["tighten-spec"]["status"], "reopen")
        self.assertEqual(by_id["resolve-open-questions"]["status"], "reopen")
        self.assertEqual(by_id["plan-from-spec"]["status"], "reopen")
        self.assertEqual(by_id["plan-from-spec"]["changed"], ["spec"])
        self.assertEqual(payload["continue_from"], "tighten-spec")

    def test_outside_plan_change_does_not_reopen_spec_steps_or_plan_from_spec(self):
        self.record("review-architecture", "nothing-to-do")
        self.record("tighten-spec")
        self.record("resolve-open-questions", "nothing-to-do")
        self.record("plan-from-spec")
        self.record("review-and-tighten-plan")
        (self.root / "plan.md").write_text("plan edited by hand\n", encoding="utf-8")
        payload = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in payload["steps"]}
        self.assertEqual(by_id["tighten-spec"]["status"], "keep")
        self.assertEqual(by_id["plan-from-spec"]["status"], "keep")
        self.assertEqual(by_id["review-and-tighten-plan"]["status"], "reopen")
        self.assertEqual(by_id["review-and-tighten-plan"]["changed"], ["plan"])
        self.assertEqual(payload["continue_from"], "review-and-tighten-plan")

    def test_outside_tasks_change_reopens_the_plan_review_not_plan_from_spec(self):
        self.record("review-architecture", "nothing-to-do")
        self.record("tighten-spec", "nothing-to-do")
        self.record("resolve-open-questions", "nothing-to-do")
        self.record("plan-from-spec")
        self.record("review-and-tighten-plan")
        self.record("tasks-ready-to-build", "ready")
        (self.root / "tasks.md").write_text("tasks edited by hand\n", encoding="utf-8")
        payload = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in payload["steps"]}
        self.assertEqual(by_id["plan-from-spec"]["status"], "keep")
        self.assertEqual(by_id["review-and-tighten-plan"]["status"], "reopen")
        self.assertIn("tasks", by_id["review-and-tighten-plan"]["changed"])
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "reopen")
        self.assertEqual(payload["continue_from"], "review-and-tighten-plan")

    def test_clear_nothing_new_keeps_done_and_unblocks_that_step(self):
        self.record("review-architecture")
        self.record("tighten-spec")
        (self.root / "spec.md").write_text("spec from outside\n", encoding="utf-8")
        code, payload = run(["clear", "--root", str(self.root), "--step", "tighten-spec"])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "needs-yes")
        code, payload = run([
            "clear", "--root", str(self.root), "--step", "review-architecture", "--yes",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "not-reopened")
        must(["clear", "--root", str(self.root), "--step", "tighten-spec", "--yes"])
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Result: done", text)
        self.assertEqual(text.count(f"Done: {WHEN}"), 2)
        status, nxt = self.statuses()
        self.assertEqual(status["tighten-spec"], "keep")
        self.assertEqual(status["review-architecture"], "keep")
        self.assertEqual(nxt, "resolve-open-questions")

    def test_reopened_step_blocks_ready(self):
        self.record("tighten-spec")
        (self.root / "spec.md").write_text("spec from outside\n", encoding="utf-8")
        rows = self.root / "rows.json"
        rows.write_text(json.dumps({"rows": [
            {"bucket": "ready", "task": "T1"},
            {"bucket": "done", "task": "T2"},
        ]}), encoding="utf-8")
        blocked = must(["readiness", "--json", str(rows), "--root", str(self.root)])
        self.assertFalse(blocked["ready"])
        self.assertFalse(blocked["start_build"])
        self.assertEqual(len(blocked["reopened"]), 1)
        row = blocked["reopened"][0]
        self.assertEqual(row["step"], "tighten-spec")
        self.assertEqual(row["command"], "/crav1-tighten-spec")
        self.assertTrue(row["can_jump_back"])
        self.assertEqual(row["clear"], "nothing new")
        self.assertEqual(row["kind"], "blocker")
        self.assertIn(row, blocked["jump_back"])
        must(["clear", "--root", str(self.root), "--step", "tighten-spec", "--yes"])
        clear = must(["readiness", "--json", str(rows), "--root", str(self.root)])
        self.assertTrue(clear["ready"])
        self.assertEqual(clear["reopened"], [])

    def test_record_stamps_a_full_timestamp_and_rejects_a_date(self):
        stamped = must([
            "record", "--root", str(self.root), "--slice", "docs/specs/orders-retry",
            "--step", "tighten-spec", "--result", "done", "--yes",
        ])
        self.assertRegex(stamped["when"], DONE)
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn(f"Done: {stamped['when']}", text)
        code, payload = run([
            "record", "--root", str(self.root), "--step", "resolve-open-questions",
            "--result", "done", "--when", "2026-11-09", "--yes",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "when")
        self.assertNotIn("Done: 2026-11-09\n", (self.root / "walk-progress.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
