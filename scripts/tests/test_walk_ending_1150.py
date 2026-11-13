"""1.150.0: walk endings print held lines and a Run next block.

The command for a ready branch is alone on its line. The ready check's own
reopened step is not a blocker. Clear with nothing new is unchanged.
"""

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

The receipt lists the order id.

## Open questions

- Which currency for refunds? Waiting for person A.
  - Asked: 2026-10-10, mail to person A. Question 1.
  - Blocks: T3

## Match

- Repo: orders-api https://github.com/contoso/orders-api
- Branch: orders-api feat/orders-api-record (PR 12)
"""

TASKS = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-api-record) (after: )
- [ ] T2: Record the decision (branch: feat/orders-api-record) (after: )
- [ ] T5: Store the card (branch: feat/orders-api-record) (after: )
- [ ] T6: Email the receipt (branch: feat/orders-api-export) (after: )
- [ ] T3: Choose the currency (branch: feat/orders-api-currency) (after: )
- [ ] T4: Archive the receipt (branch: feat/orders-api-archive) (after: T3)
"""

VERIFY = """# Verify

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T1 | Persist the decision | Not implemented | |
"""

COMMAND = re.compile(r"^`/crav1-build-walk(?: [a-z0-9][a-z0-9-]*)? T\d+(?:, T\d+)*`$")


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


OPEN_TASKS = "\n".join(line for line in TASKS.splitlines() if not line.startswith("- [x]")) + "\n"


def write_slice(root: Path, tasks: str = TASKS, spec: str = SPEC, plan: str = PLAN, verify: str | None = VERIFY) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    if verify is not None:
        (root / "verify.md").write_text(verify, encoding="utf-8")


def record(root: Path, step: str, result: str = "done") -> None:
    must([
        "record", "--root", str(root), "--slice", "docs/specs/orders-api",
        "--step", step, "--result", result, "--yes",
    ])


def record_walk(root: Path) -> None:
    record(root, "review-architecture", "nothing-to-do")
    record(root, "tighten-spec")
    record(root, "resolve-open-questions")
    record(root, "plan-from-spec")
    record(root, "review-and-tighten-plan")
    record(root, "tasks-ready-to-build", "ready-partial")


def command_lines(ending: str) -> list[str]:
    return [line for line in ending.splitlines() if line.startswith("`/crav1-build-walk")]


def assert_complete(test: unittest.TestCase, ending: str, slug: str | None) -> None:
    """Each Run next command stands alone in a new session.

    The code span is only the command, the T#s for that branch, and the slug
    when a fresh session cannot infer the slice. The branch and the short
    name stay on the next line.
    """
    lines = ending.splitlines()
    commands = command_lines(ending)
    test.assertGreaterEqual(len(commands), 1)
    for index, line in enumerate(lines):
        if line not in commands:
            continue
        test.assertRegex(line, COMMAND)
        inner = line.strip("`")
        test.assertNotIn("because", inner)
        test.assertNotIn("feat/", inner)
        test.assertNotIn("branch", inner)
        args = inner.split()
        test.assertEqual(args[0], "/crav1-build-walk")
        detail = lines[index + 1]
        test.assertTrue(detail.startswith("branch "))
        command_ids = re.findall(r"T\d+", inner)
        detail_ids = re.findall(r"T\d+", detail)
        test.assertEqual(command_ids, detail_ids)
        test.assertGreaterEqual(len(command_ids), 1)
        if slug:
            test.assertIn(slug, args)
            test.assertEqual(args[1], slug)
        else:
            test.assertTrue(args[1].startswith("T"))


class EndingBlock(unittest.TestCase):
    def test_run_next_comes_before_waiting_and_the_command_is_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root)
            record(root, "resolve-open-questions")
            payload = must(["readiness", "--root", str(root)])
        ending = payload["ending"]
        self.assertEqual(payload["result"], "ready-partial")
        self.assertLess(ending.index("Run next:"), ending.index("Waiting:"))
        self.assertLess(ending.index("Waiting:"), ending.index("\nNext:"))
        self.assertIn("verify.md is behind tasks.md (T1)", ending)
        assert_complete(self, ending, "orders-api")
        lines = ending.splitlines()
        commands = command_lines(ending)
        self.assertGreaterEqual(len(commands), 2)
        # A blank line separates branch entries.
        first = lines.index(commands[0])
        second = lines.index(commands[1])
        self.assertEqual(lines[second - 1], "")
        for held in payload["held_lines"]:
            self.assertIn(held, ending)
            self.assertRegex(held, r"T\d+ \S")
        self.assertIn("person A", "\n".join(payload["held_lines"]))
        self.assertNotIn("above", ending.lower())
        self.assertNotIn("listed above", ending.lower())
        for line in payload["next_lines"]:
            self.assertIn(line, ending)
            self.assertGreater(ending.index(line), ending.index("Run next:"))

    def test_not_ready_waiting_ending_prints_each_held_line(self):
        spec = SPEC.replace("  - Blocks: T3\n", "  - Blocks: whole slice\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, spec=spec, verify=None)
            record(root, "resolve-open-questions")
            payload = must(["readiness", "--root", str(root)])
        ending = payload["ending"]
        self.assertEqual(payload["result"], "not-ready")
        self.assertNotIn("Run next:", ending)
        self.assertTrue(payload["held_lines"])
        for held in payload["held_lines"]:
            self.assertIn(held, ending)
        self.assertIn("Waiting:", ending)
        self.assertNotIn("above", ending.lower())
        self.assertNotIn("listed above", ending.lower())

    def test_one_spec_omits_the_slug_and_two_specs_keep_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / "docs" / "specs" / "orders-api"
            one.mkdir(parents=True)
            write_slice(one, tasks=OPEN_TASKS, verify=None)
            record(one, "resolve-open-questions")
            alone = must(["readiness", "--root", str(one)])
            other = Path(tmp) / "docs" / "specs" / "orders-export"
            other.mkdir()
            write_slice(other, tasks=OPEN_TASKS, verify=None)
            many = must(["readiness", "--root", str(one)])
        assert_complete(self, alone["ending"], None)
        for line in command_lines(alone["ending"]):
            self.assertNotIn("orders-api", line)
        assert_complete(self, many["ending"], "orders-api")
        for line in command_lines(many["ending"]):
            self.assertNotIn("orders-export", line)


class SelfReopen(unittest.TestCase):
    def test_only_the_ready_check_reopen_stays_ready_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, tasks=OPEN_TASKS, verify=None)
            record_walk(root)
            tasks = (root / "tasks.md").read_text(encoding="utf-8")
            (root / "tasks.md").write_text(
                tasks.replace("Store the card", "Store the card now"),
                encoding="utf-8",
            )
            must(["clear", "--root", str(root), "--step", "review-and-tighten-plan", "--yes"])
            payload = must(["readiness", "--root", str(root)])
            resumed = must(["resume", "--root", str(root), "--no-playbook"])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertIsNone(payload["because"])
        self.assertFalse(payload["recommend_jump"])
        self.assertEqual(
            [hit["step"] for hit in payload["reopened"]],
            [],
        )
        self.assertEqual(payload["replaced"], "The earlier tasks-ready-to-build record is replaced.")
        self.assertEqual(payload["ending"].count(payload["replaced"]), 1)
        self.assertLess(payload["ending"].index("Run next:"), payload["ending"].index("Held:"))
        assert_complete(self, payload["ending"], "orders-api")
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "reopen")
        self.assertEqual(by_id["review-and-tighten-plan"]["status"], "keep")

    def test_self_plus_another_reopened_step_is_still_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, tasks=OPEN_TASKS, verify=None)
            record_walk(root)
            tasks = (root / "tasks.md").read_text(encoding="utf-8")
            (root / "tasks.md").write_text(
                tasks.replace("Store the card", "Store the card now"),
                encoding="utf-8",
            )
            payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "not-ready")
        steps = [hit["step"] for hit in payload["reopened"]]
        self.assertIn("review-and-tighten-plan", steps)
        self.assertNotIn("tasks-ready-to-build", steps)
        self.assertIn("review-and-tighten-plan", payload["because"])
        self.assertNotIn("tasks-ready-to-build", payload["because"])
        self.assertIsNone(payload["replaced"])
        self.assertNotIn("The earlier tasks-ready-to-build record is replaced.", payload["ending"])
        self.assertNotIn("Run next:", payload["ending"])
        for held in payload["held_lines"]:
            self.assertIn(held, payload["ending"])
        self.assertTrue(payload["recommend_jump"])

    def test_nothing_new_clear_path_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, tasks=OPEN_TASKS, verify=None)
            record_walk(root)
            tasks = (root / "tasks.md").read_text(encoding="utf-8")
            (root / "tasks.md").write_text(
                tasks.replace("Store the card", "Store the card now"),
                encoding="utf-8",
            )
            code, missing = run(["clear", "--root", str(root), "--step", "tasks-ready-to-build"])
            self.assertEqual(code, 2)
            self.assertEqual(missing["code"], "needs-yes")
            cleared_plan = must([
                "clear", "--root", str(root), "--step", "review-and-tighten-plan", "--yes",
            ])
            self.assertEqual(cleared_plan["confirmation"], "nothing new")
            text = (root / "walk-progress.md").read_text(encoding="utf-8")
            self.assertIn("Result: done", text)
            self.assertIn("Result: ready-partial", text)
            cleared = must([
                "clear", "--root", str(root), "--step", "tasks-ready-to-build", "--yes",
            ])
            self.assertEqual(cleared["confirmation"], "nothing new")
            self.assertEqual(cleared["cleared"], "tasks-ready-to-build")
            text = (root / "walk-progress.md").read_text(encoding="utf-8")
            self.assertIn("Result: ready-partial", text)
            self.assertNotIn("Result: not-ready", text)
            payload = must(["readiness", "--root", str(root)])
            code, again = run([
                "clear", "--root", str(root), "--step", "tasks-ready-to-build", "--yes",
            ])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertIsNone(payload["replaced"])
        self.assertEqual(payload["reopened"], [])
        self.assertEqual(code, 1)
        self.assertEqual(again["code"], "not-reopened")


if __name__ == "__main__":
    unittest.main()
