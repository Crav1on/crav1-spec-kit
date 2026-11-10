"""Registry, routing, and progress-file checks for the guided walk.

These tests read the kit files and run scripts/walk_progress.py on temp folders.
They are not a live replay of the walk, and they do not apply a playbook to a spec.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"
SCRIPT = SKILL / "scripts/walk_progress.py"
LOCKED = (
    "playbook",
    "review-architecture",
    "tighten-spec",
    "resolve-open-questions",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)
WHEN = "2026-11-09T10:19:09+01:00"


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
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


class Registry(unittest.TestCase):
    def test_skill_is_registered_and_not_a_starter(self):
        text = (ROOT / "docs/reference/skills.yaml").read_text(encoding="utf-8")
        self.assertIn("- name: crav1-tighten-and-plan-ready-to-build", text)
        self.assertIn("lane: cross-cutting", text)
        self.assertIn("group: Guided walks", text)
        self.assertIn("walkthrough: docs/from-tighten-and-plan.md", text)
        starters = text.split("lanes:", 1)[0]
        self.assertNotIn("crav1-tighten-and-plan-ready-to-build", starters)
        for name in (
            "crav1-spark-to-spec",
            "crav1-ideas-to-spec",
            "crav1-bundle-to-specs",
            "crav1-existing-to-specs",
            "crav1-read-environment",
            "crav1-fix-bug",
        ):
            self.assertIn(f"- {name}", starters)
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        desc = body.split("description:", 1)[1].split("---", 1)[0]
        self.assertLessEqual(len(desc.split()), 60)
        self.assertIn("Guided walk only", body)
        self.assertIn("never runs `/crav1-build-tasks`", body)
        self.assertIn("`skip`", body)
        self.assertIn("`reapply`", body)
        cursor = 0
        for command in (
            "/crav1-review-architecture",
            "/crav1-tighten-spec",
            "/crav1-resolve-open-questions",
            "/crav1-plan-from-spec",
            "/crav1-review-plan",
            "/crav1-tighten-plan",
            "/crav1-tasks-ready-to-build",
        ):
            found = body.find(command, cursor)
            self.assertGreater(found, cursor, command)
            cursor = found
        source = SCRIPT.read_text(encoding="utf-8")
        cursor = 0
        for step in LOCKED:
            found = source.find(f'"{step}"', cursor)
            self.assertGreater(found, cursor, step)
            cursor = found
        walk = (ROOT / "docs/from-tighten-and-plan.md").read_text(encoding="utf-8")
        self.assertIn("reference/skills/crav1-tighten-and-plan-ready-to-build.md", walk)

    def test_route_stays_intact_and_walk_is_listed_on_both_lanes(self):
        workflow = (ROOT / "docs/reference/workflow.yaml").read_text(encoding="utf-8")
        new_slice = workflow.split("- id: new-info", 1)[0]
        for skill in (
            "crav1-review-architecture",
            "crav1-tighten-spec",
            "crav1-resolve-open-questions",
            "crav1-plan-from-spec",
            "crav1-review-plan",
            "crav1-tighten-plan",
            "crav1-tasks-ready-to-build",
        ):
            self.assertIn(skill, new_slice)
        self.assertNotIn("crav1-tighten-and-plan-ready-to-build", new_slice)
        self.assertIn("crav1-tighten-and-plan-ready-to-build: [/crav1-build-tasks]", workflow)
        skills = (ROOT / "docs/reference/skills.yaml").read_text(encoding="utf-8")
        self.assertIn("Inside the walk it always runs.", skills)
        self.assertIn("does not start `/crav1-build-tasks`", skills)
        guild = (ROOT / "docs/guild-routing.md").read_text(encoding="utf-8")
        self.assertIn("/crav1-tighten-and-plan-ready-to-build", guild)
        specify = guild.split("## Plan", 1)[0]
        plan = guild.split("## Plan", 1)[1].split("## Build", 1)[0]
        cross = guild.split("## Cross-cutting", 1)[1].split("## Maintainer note", 1)[0]
        self.assertNotIn("| Skill | `/crav1-tighten-and-plan-ready-to-build` |", specify)
        self.assertNotIn("| Skill | `/crav1-tighten-and-plan-ready-to-build` |", plan)
        self.assertIn("| Skill | `/crav1-tighten-and-plan-ready-to-build` |", cross)
        self.assertIn("does not start Build", specify)
        self.assertIn("does not start `/crav1-build-tasks`", plan)
        self.assertIn("does not run `/crav1-build-tasks`", cross)
        machine = guild.split("## Machine-readable map", 1)[1]
        cross_map = machine.split("cross_cutting:", 1)[1]
        self.assertIn("- crav1-tighten-and-plan-ready-to-build", cross_map)
        specify_map = machine.split("specify:", 1)[1].split("plan:", 1)[0]
        self.assertNotIn("crav1-tighten-and-plan-ready-to-build", specify_map)


class Progress(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "spec.md").write_text("spec v1\n", encoding="utf-8")
        (self.root / "plan.md").write_text("plan v1\n", encoding="utf-8")
        (self.root / "tasks.md").write_text("tasks v1\n", encoding="utf-8")
        self.playbook = self.root / "playbook.md"
        self.playbook.write_text("playbook v1\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def record(self, step: str, result: str = "done", playbook: bool = False):
        args = [
            "record",
            "--root",
            str(self.root),
            "--slice",
            "docs/specs/orders-retry",
            "--step",
            step,
            "--result",
            result,
            "--when",
            WHEN,
            "--yes",
        ]
        if playbook:
            args += ["--playbook", str(self.playbook)]
        return must(args)

    def test_record_needs_yes_and_writes_versions(self):
        code, payload = run([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN,
        ])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "needs-yes")
        self.assertFalse((self.root / "walk-progress.md").exists())
        self.record("tighten-spec")
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Walk: tighten-and-plan-ready-to-build", text)
        self.assertIn("Slice: docs/specs/orders-retry", text)
        self.assertIn("- Step: tighten-spec", text)
        self.assertIn("Result: done", text)
        self.assertIn("Spec version:", text)
        self.assertNotIn("Plan version:", text)
        versions = must(["version", "--root", str(self.root)])["versions"]
        self.assertEqual(len(versions["spec"]), 12)
        self.assertNotEqual(versions["spec"], "missing")

    def test_resume_reopens_only_affected_steps(self):
        self.record("playbook", "applied", playbook=True)
        self.record("review-architecture")
        self.record("tighten-spec")
        self.record("resolve-open-questions")
        self.record("plan-from-spec")
        self.record("review-and-tighten-plan")
        self.record("tasks-ready-to-build")
        same = must(["resume", "--root", str(self.root)])
        self.assertIsNone(same["continue_from"])
        self.assertTrue(all(row["status"] == "keep" for row in same["steps"]))

        (self.root / "spec.md").write_text("spec v2\n", encoding="utf-8")
        spec = must(["resume", "--root", str(self.root)])
        by_id = {row["id"]: row for row in spec["steps"]}
        # Architecture already has a later spec step, so a spec edit does not
        # send the walk back there (1.123.0). The steps that edit or consume
        # the spec do reopen.
        self.assertEqual(by_id["playbook"]["status"], "keep")
        self.assertEqual(by_id["review-architecture"]["status"], "keep")
        for step in ("tighten-spec", "resolve-open-questions", "plan-from-spec", "review-and-tighten-plan", "tasks-ready-to-build"):
            self.assertEqual(by_id[step]["status"], "reopen", step)
            self.assertEqual(by_id[step]["changed"], ["spec"])
        self.assertEqual(spec["continue_from"], "tighten-spec")

        (self.root / "spec.md").write_text("spec v1\n", encoding="utf-8")
        (self.root / "plan.md").write_text("plan v2\n", encoding="utf-8")
        plan = must(["resume", "--root", str(self.root)])
        by_id = {row["id"]: row for row in plan["steps"]}
        for step in ("playbook", "review-architecture", "tighten-spec", "resolve-open-questions", "plan-from-spec"):
            self.assertEqual(by_id[step]["status"], "keep", step)
        for step in ("review-and-tighten-plan", "tasks-ready-to-build"):
            self.assertEqual(by_id[step]["status"], "reopen", step)
            self.assertIn("plan", by_id[step]["changed"])
            self.assertNotIn("spec", by_id[step]["changed"])
        self.assertEqual(plan["continue_from"], "review-and-tighten-plan")

        (self.root / "plan.md").write_text("plan v1\n", encoding="utf-8")
        (self.root / "verify.md").write_text("verify v1\n", encoding="utf-8")
        verify = must(["resume", "--root", str(self.root)])
        by_id = {row["id"]: row for row in verify["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "reopen")
        self.assertEqual(by_id["tasks-ready-to-build"]["changed"], ["verify"])
        self.assertEqual(by_id["plan-from-spec"]["status"], "keep")
        self.assertEqual(verify["continue_from"], "tasks-ready-to-build")

        self.playbook.write_text("playbook v2\n", encoding="utf-8")
        (self.root / "verify.md").unlink()
        book = must(["resume", "--root", str(self.root)])
        by_id = {row["id"]: row for row in book["steps"]}
        self.assertEqual(by_id["playbook"]["status"], "reopen")
        self.assertEqual(by_id["playbook"]["changed"], ["playbook"])
        self.assertEqual(by_id["review-architecture"]["status"], "keep")

    def test_no_playbook_skips_an_unstarted_playbook_step(self):
        self.record("review-architecture", "nothing-to-do")
        resumed = must(["resume", "--root", str(self.root), "--no-playbook"])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["playbook"]["status"], "skipped")
        self.assertEqual(by_id["review-architecture"]["status"], "keep")
        self.assertEqual(resumed["continue_from"], "tighten-spec")

    def test_playbook_status_uses_only_the_progress_file(self):
        missing = must(["playbook-status", "--root", str(self.root), "--playbook", str(self.playbook)])
        self.assertEqual(missing["status"], "not-recorded")
        self.assertFalse(missing["already_applied"])
        self.record("playbook", "applied", playbook=True)
        applied = must(["playbook-status", "--root", str(self.root), "--playbook", str(self.playbook)])
        self.assertTrue(applied["already_applied"])
        self.assertEqual(applied["offer"], "skip-or-reapply")
        self.playbook.write_text("playbook changed\n", encoding="utf-8")
        changed = must(["playbook-status", "--root", str(self.root), "--playbook", str(self.playbook)])
        self.assertEqual(changed["status"], "changed")
        self.assertFalse(changed["already_applied"])

    def test_readiness_names_steps_and_never_starts_build(self):
        path = self.root / "rows.json"
        path.write_text(json.dumps({"rows": [
            {"bucket": "blocked", "task": "T7", "reason": "open question", "detail": "Which currency?"},
            {"bucket": "needs-verify", "task": "T3", "reason": "no verify.md row"},
            {"bucket": "ready", "task": "T5", "warning": "plan review unknown"},
            {"bucket": "blocked", "reason": "no plan.md"},
            {"bucket": "blocked", "task": "T4", "reason": "plan Risk blocks the slice"},
            {"bucket": "blocked", "task": "T6", "reason": "waits on T5"},
            {"bucket": "blocked", "task": "T9", "reason": "cycle T2 → T3 → T2 (recorded)"},
            {"bucket": "blocked", "task": "T10", "reason": "after: T99 names no task (recorded)"},
            {"bucket": "ready", "task": "T1", "warning": "plan review has 2 open P#"},
            {"bucket": "blocked", "task": "T8", "reason": "something new"},
        ]}), encoding="utf-8")
        payload = must(["readiness", "--json", str(path)])
        self.assertFalse(payload["ready"])
        self.assertFalse(payload["start_build"])
        by_task = {row["task"]: row for row in payload["blockers"] + payload["outside_walk"] + payload["assumptions"] + payload["unmapped"]}
        self.assertEqual(by_task["T7"]["command"], "/crav1-resolve-open-questions")
        self.assertTrue(by_task["T7"]["can_jump_back"])
        self.assertEqual(by_task["T3"]["command"], "/crav1-verify-build-against-spec")
        self.assertFalse(by_task["T3"]["can_jump_back"])
        self.assertTrue(by_task["T3"]["outside_walk"])
        self.assertEqual(by_task["T5"]["command"], "/crav1-review-plan")
        self.assertEqual(by_task["T5"]["kind"], "assumption")
        self.assertEqual(by_task[None]["command"], "/crav1-plan-from-spec")
        self.assertEqual(by_task["T4"]["step"], "review-and-tighten-plan")
        self.assertNotIn("T6", by_task)
        self.assertEqual(by_task["T9"]["command"], "/crav1-tighten-plan")
        self.assertEqual(by_task["T10"]["command"], "/crav1-tighten-plan")
        self.assertEqual(by_task["T1"]["command"], "/crav1-tighten-plan")
        self.assertIsNone(by_task["T8"]["command"])
        self.assertFalse(by_task["T8"]["can_jump_back"])

        clear = self.root / "clear.json"
        clear.write_text(json.dumps({"rows": [
            {"bucket": "ready", "task": "T1"},
            {"bucket": "done", "task": "T2"},
        ]}), encoding="utf-8")
        ready = must(["readiness", "--json", str(clear)])
        self.assertTrue(ready["ready"])
        self.assertFalse(ready["start_build"])
        self.assertEqual(ready["blockers"], [])
        self.assertEqual(ready["assumptions"], [])
        self.assertEqual(ready["outside_walk"], [])


if __name__ == "__main__":
    unittest.main()
