"""1.141.0: Approval needed holds, the Approved line, and the ready check."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
SCRIPT = SK / "crav1-record-approval/scripts/approval_needed.py"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
ORDER = SK / "crav1-tasks-ready-to-build/scripts/task_order.py"

PLAN = """# Plan: the slice

Reviewed: 2026-11-12, P# open: 0

## Approach

1. Record the decision. (T1)
2. Apply the policy. (T4)

## Risks
"""

TASKS = """# Tasks

- [ ] T1: Record the decision (after: )
- [ ] T2: Store the card (after: )
- [ ] T4: Apply the CI build policy (host setup) (after: )
- [ ] T5: Note the policy (after: T4)
"""

SPEC = """# Spec

## Constraints

- The partner gives a yes before the CI build policy script is applied.

## Open questions

- Which currency for refunds?
  - Blocks: none

## Approval needed

- The partner approves applying the CI build policy.
  - Person: the partner
  - Holds: T4

## Match

- Repo: widgets https://github.com/example/widgets
"""

APPROVED = (
    '  - Approved: the partner, 2026-10-02, '
    'https://github.com/example/widgets/pull/12#discussion_r9, '
    '"Yes, apply the policy." (accepted by Alex 2026-11-12)'
)


def run_py(script: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def readiness(root: Path) -> dict:
    proc = run_py(WALK, ["readiness", "--full", "--root", str(root)])
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    if proc.returncode != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


def write_slice(root: Path, spec: str = SPEC, tasks: str = TASKS, plan: str = PLAN) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")


class Parser(unittest.TestCase):
    def test_an_unapproved_item_holds_only_its_tasks(self):
        proc = run_py(SCRIPT, [])  # help
        self.assertEqual(proc.returncode, 0)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root)
            proc = run_py(SCRIPT, [str(root / "spec.md"), str(root / "tasks.md")])
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["items"][0]["who"], "the partner")
        self.assertEqual(payload["items"][0]["tasks"], ["T4"])
        self.assertTrue(payload["items"][0]["holding"])
        self.assertFalse(payload["items"][0]["approved"])
        gate = payload["gates"][0]
        self.assertEqual(gate["who"], "The partner")
        self.assertIn("CI build policy", gate["what"])
        self.assertTrue(gate["already"])
        self.assertEqual(gate["holds"], [])

    def test_a_constraint_with_no_item_suggests_the_host_setup_task(self):
        spec = SPEC.replace("## Approval needed\n\n- The partner approves applying the CI build policy.\n  - Person: the partner\n  - Holds: T4\n\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, spec)
            proc = run_py(SCRIPT, [str(root / "spec.md"), str(root / "tasks.md")])
        gate = json.loads(proc.stdout)["gates"][0]
        self.assertFalse(gate["already"])
        self.assertIn("T4", gate["holds"])
        self.assertNotIn("T1", gate["holds"])

    def test_a_matching_approved_line_clears_the_hold(self):
        spec = SPEC.replace("  - Holds: T4\n", "  - Holds: T4\n" + APPROVED + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, spec)
            proc = run_py(SCRIPT, [str(root / "spec.md"), str(root / "tasks.md")])
        item = json.loads(proc.stdout)["items"][0]
        self.assertTrue(item["approved"])
        self.assertFalse(item["holding"])
        self.assertEqual(item["tasks"], ["T4"])

    def test_a_different_person_does_not_clear_the_hold(self):
        other = APPROVED.replace("the partner", "a colleague", 1)
        spec = SPEC.replace("  - Holds: T4\n", "  - Holds: T4\n" + other + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, spec)
            proc = run_py(SCRIPT, [str(root / "spec.md"), str(root / "tasks.md")])
        item = json.loads(proc.stdout)["items"][0]
        self.assertFalse(item["approved"])
        self.assertTrue(item["holding"])

    def test_crlf_round_trip_keeps_crlf_and_both_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root)
            raw = (root / "spec.md").read_bytes().replace(b"\n", b"\r\n")
            (root / "spec.md").write_bytes(raw)
            added = run_py(SCRIPT, [
                "add-item", "--root", str(root), "--person", "a colleague",
                "--what", "turning the extra flag on", "--holds", "T2", "--yes",
            ])
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
            body = (root / "spec.md").read_bytes()
            self.assertIn(b"\r\n", body)
            self.assertNotIn(b"\n", body.replace(b"\r\n", b""))
            shown = run_py(SCRIPT, [
                "show", "--root", str(root), "--person", "a colleague",
                "--source-date", "2026-10-02", "--source", "mail",
                "--quote", "Yes, turn it on.", "--recorder", "Alex",
                "--accepted", "2026-11-12", "--yes",
            ])
            payload = json.loads(shown.stdout)
            self.assertTrue(payload["ok"], payload)
            self.assertIn("2026-10-02", payload["line"])
            self.assertIn("2026-11-12", payload["line"])
            self.assertEqual(payload["constraints"], [])
            refused = run_py(SCRIPT, [
                "write", "--root", str(root), "--person", "a colleague",
                "--source-date", "2026-10-02", "--source", "mail",
                "--quote", "Yes, turn it on.", "--recorder", "Alex",
                "--accepted", "2026-11-12",
            ])
            self.assertNotEqual(refused.returncode, 0)
            self.assertNotIn(b"Approved:", (root / "spec.md").read_bytes())
            wrote = run_py(SCRIPT, [
                "write", "--root", str(root), "--person", "a colleague",
                "--source-date", "2026-10-02", "--source", "mail",
                "--quote", "Yes, turn it on.", "--recorder", "Alex",
                "--accepted", "2026-11-12", "--yes",
            ])
            self.assertEqual(wrote.returncode, 0, wrote.stdout)
            text = (root / "spec.md").read_bytes()
            self.assertIn(b"Approved:", text)
            self.assertNotIn(b"\n", text.replace(b"\r\n", b""))
            again = run_py(SCRIPT, [
                "write", "--root", str(root), "--person", "a colleague",
                "--source-date", "2026-10-02", "--source", "mail",
                "--quote", "Yes, turn it on.", "--recorder", "Alex",
                "--accepted", "2026-11-12", "--yes",
            ])
            self.assertEqual(json.loads(again.stdout)["status"], "already")
            self.assertEqual(text.count(b"Approved:"), (root / "spec.md").read_bytes().count(b"Approved:"))


class Ready(unittest.TestCase):
    def test_ready_partial_names_the_person_and_lets_other_tasks_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root)
            payload = readiness(root)
            self.assertEqual(payload["result"], "ready-partial")
            self.assertIn("T1", payload["can_start"])
            self.assertIn("T2", payload["can_start"])
            self.assertIn("T4", payload["held"])
            self.assertIn("T5", payload["held"])
            self.assertNotIn("T4", payload["can_start"])
            line = payload["waiting_line"]
            self.assertIn("an approval", line)
            self.assertIn("the partner", line.lower())
            gate = next(row for row in payload["gates"] if row["task"] == "T4")
            self.assertTrue(gate["refused"])
            self.assertIn("show-or-ask-open-questions", payload["waiting_next"])
            asked = SPEC.replace(
                "  - Person: the partner\n",
                "  - Person: the partner\n"
                "  - Asked: 2026-11-01, mail to the partner. Question 1. Date from the user's yes.\n",
            )
            (root / "spec.md").write_text(asked, encoding="utf-8")
            asked_payload = readiness(root)
            self.assertIn("record-approval", asked_payload["waiting_next"])

    def test_approved_clears_the_hold_and_does_not_tick(self):
        spec = SPEC.replace("  - Holds: T4\n", "  - Holds: T4\n" + APPROVED + "\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, spec)
            payload = readiness(root)
            tasks = (root / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("T4", payload["can_start"])
        self.assertNotIn("T4", payload["held"])
        self.assertIn("- [ ] T4:", tasks)

    def test_an_approval_edit_does_not_reopen_the_walk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, SPEC.replace("## Approval needed\n\n- The partner approves applying the CI build policy.\n  - Person: the partner\n  - Holds: T4\n\n", ""))
            for index, step in enumerate((
                "review-architecture",
                "tighten-spec",
                "resolve-open-questions",
                "plan-from-spec",
                "review-and-tighten-plan",
                "tasks-ready-to-build",
            )):
                result = "ready" if step == "tasks-ready-to-build" else "done"
                proc = run_py(WALK, [
                    "record", "--root", str(root), "--slice", "docs/specs/widgets",
                    "--step", step, "--result", result,
                    "--when", f"2026-11-12T12:0{index}:00+00:00", "--yes",
                ])
                self.assertEqual(proc.returncode, 0, proc.stdout)
            spec = (root / "spec.md").read_text(encoding="utf-8")
            spec = spec.replace(
                "## Match\n",
                "## Approval needed\n\n- The partner approves applying the CI build policy.\n"
                "  - Person: the partner\n  - Holds: T4\n\n## Match\n",
            )
            (root / "spec.md").write_text(spec, encoding="utf-8")
            proc = run_py(WALK, ["resume", "--root", str(root), "--no-playbook"])
            payload = json.loads(proc.stdout)
        self.assertTrue(payload.get("ok"), payload)
        for row in payload["steps"]:
            if row.get("id") == "playbook":
                self.assertEqual(row.get("status"), "skipped")
                continue
            self.assertEqual(row.get("status"), "keep", row.get("id"))

    def test_task_order_lists_waiting_on_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root)
            proc = run_py(ORDER, [str(root / "tasks.md")])
        text = proc.stdout
        self.assertIn("Waiting on approval", text)
        self.assertIn("T4", text.split("Waiting on approval", 1)[1].split("Blocked", 1)[0])
        ready = text.split("Waits in order", 1)[0]
        self.assertNotIn("T4", ready)
        self.assertIn("T1", ready)


class Rules(unittest.TestCase):
    def test_the_skills_keep_approved_and_still_require_a_yes_to_apply(self):
        record = (SK / "crav1-record-approval/SKILL.md").read_text(encoding="utf-8")
        line = (SK / "crav1-record-approval/references/line.md").read_text(encoding="utf-8")
        resolve = (SK / "crav1-resolve-open-questions/SKILL.md").read_text(encoding="utf-8")
        plan = (SK / "crav1-plan-from-spec/references/write.md").read_text(encoding="utf-8")
        build = (SK / "crav1-build-tasks/references/approval-needed.md").read_text(encoding="utf-8")
        run = (SK / "crav1-build-tasks/branches/one-task/references/run.md").read_text(encoding="utf-8")
        ask = (SK / "crav1-show-or-ask-open-questions/references/approval.md").read_text(encoding="utf-8")
        self.assertIn("`accept`", record)
        self.assertIn("does not satisfy the constraint", line.lower())
        self.assertIn("Never remove an `Approved:` line", resolve)
        self.assertIn("## Approval needed", plan)
        self.assertIn("Do not write `Approved:`", plan)
        self.assertIn("add-item", build)
        self.assertIn("Nothing is sent", ask)
        self.assertIn("matching `Approved:` line", run)
        self.assertIn("Do not return `blocked` for this.", run)
        self.assertIn("Answered:", run)
        self.assertLessEqual(len(record.split()), 2000)
        for banned in ("contoso", "orders-api", "person A"):
            for path in (record, line, build, ask):
                self.assertNotIn(banned, path)


if __name__ == "__main__":
    unittest.main()
