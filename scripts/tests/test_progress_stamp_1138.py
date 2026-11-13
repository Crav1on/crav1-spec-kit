"""1.138.0: a checkbox tick or a (PR n) on a branch line is progress.

It does not reopen a walk step, and it does not ask to clear. A sentence
change still reopens. An older stamp, with no Content stamp line, matches
those same progress edits. Line endings do not count.

The not-ready result with a non-empty can_start list is a hard hit (here,
reopened steps) while other tasks stay in the ready bucket. The six questions
do not hold T3 or T7, and they do not hold the whole slice. Once the progress
edits stop reopening steps, that slice is ready-partial.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-12T09:00:00+00:00"

PLAN = """# Plan: orders export

Reviewed: 2026-11-12, P# open: 0

## Risks
"""

SPEC = """# Orders export

The receipt lists the order id.

## Match

- Branch: orders-api feat/orders-export (PR 78) merged
- Branch: orders-api feat/orders-record

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to person A. Question 1.
  - Blocks: T8
- Which lane prints the label?
  - Asked: 2026-10-10, mail to person A. Question 2.
  - Blocks: T9
- Which file holds the manifest?
  - Blocks: T10
- Which stamp goes on the carton?
  - Blocks: T11
- Which tray holds the form?
  - Blocks: T12
- Which ink is already chosen?
  - Blocks: none (later phase)
"""

TASKS = """# Tasks

- [ ] T2: export the receipt (PR 78, merged) (branch: feat/orders-export) (after: ) (spec: A1)
- [ ] T3: record the order (branch: feat/orders-record) (after: ) (spec: A2)
- [ ] T6: send the mail (branch: feat/orders-mail) (after: ) (spec: A3)
- [ ] T7: file the copy (branch: feat/orders-file) (after: ) (spec: A4)
- [ ] T8: choose the currency (after: ) (spec: A5)
- [ ] T9: choose the lane (after: ) (spec: A6)
- [ ] T10: write the manifest (after: ) (spec: A7)
- [ ] T11: choose the stamp (after: ) (spec: A8)
- [ ] T12: choose the tray (after: ) (spec: A9)
"""

VERIFY = """# Verify

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | export the receipt | Implemented, verified, tick pending | unit |
| T3 | record the order | Not implemented | |
| T6 | send the mail | Not implemented | |
| T7 | file the copy | Not implemented | |
"""

STEPS = (
    "tighten-spec",
    "resolve-open-questions",
    "plan-from-spec",
    "review-and-tighten-plan",
    "tasks-ready-to-build",
)


def run(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(WALK), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def must(args: list[str]) -> dict:
    code, out, err = run(args)
    try:
        payload = json.loads(out or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(err + out) from exc
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload or err or out)
    return payload


def write_slice(root: Path, spec: str = SPEC, tasks: str = TASKS) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    (root / "verify.md").write_text(VERIFY, encoding="utf-8")


def fresh() -> Path:
    root = Path(tempfile.mkdtemp()) / "orders-export"
    root.mkdir()
    write_slice(root)
    return root


def record_walk(root: Path) -> None:
    for index, step in enumerate(STEPS):
        result = "ready-partial" if step == "tasks-ready-to-build" else "done"
        when = f"2026-11-12T09:{index:02d}:00+00:00"
        must([
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", step, "--result", result, "--when", when, "--yes",
        ])


def statuses(root: Path) -> dict[str, str]:
    payload = must(["resume", "--root", str(root), "--no-playbook"])
    return {row["id"]: row["status"] for row in payload["steps"]}


def tick_t6(tasks: str) -> str:
    return tasks.replace("- [ ] T6:", "- [x] T6:", 1)


def add_branch_pr(spec: str) -> str:
    return spec.replace(
        "- Branch: orders-api feat/orders-record\n",
        "- Branch: orders-api feat/orders-record (PR 73)\n",
        1,
    )


def add_task_pr(tasks: str) -> str:
    return tasks.replace(
        "- [x] T6: send the mail (branch: feat/orders-mail) (after: ) (spec: A3)\n",
        "- [x] T6: send the mail (branch: feat/orders-mail) (after: ) (spec: A3) (PR 73)\n",
        1,
    )


def to_crlf(path: Path) -> None:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    path.write_bytes(raw)


def hx(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()[:12]


def hx_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def load_walk():
    spec = importlib.util.spec_from_file_location("walk_progress_1138", WALK)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {WALK}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def old_progress(root: Path, *, split: bool) -> str:
    """A 1.137 stamp (split) or an older whole-file stamp. No Content stamp."""
    mod = load_walk()
    spec_text = (root / "spec.md").read_text(encoding="utf-8")
    body, questions = mod.spec_parts(spec_text)
    versions = {
        "spec": hx((root / "spec.md").read_bytes()),
        "plan": hx((root / "plan.md").read_bytes()),
        "tasks": hx((root / "tasks.md").read_bytes()),
        "verify": hx((root / "verify.md").read_bytes()),
        "spec_body": hx_text(body),
        "questions": hx_text(questions),
    }
    lines = [
        "# Walk progress",
        "",
        "Walk: tighten-and-plan-ready-to-build",
        "Slice: docs/specs/orders-export/",
        "",
    ]
    for index, step in enumerate(STEPS):
        result = "ready-partial" if step == "tasks-ready-to-build" else "done"
        lines.append(f"- Step: {step}")
        lines.append(f"  Done: 2026-11-11T09:{index:02d}:00+00:00")
        lines.append(f"  Result: {result}")
        lines.append(f"  Spec version: {versions['spec']}")
        if step in ("plan-from-spec", "review-and-tighten-plan", "tasks-ready-to-build"):
            lines.append(f"  Plan version: {versions['plan']}")
            lines.append(f"  Tasks version: {versions['tasks']}")
        if step == "tasks-ready-to-build":
            lines.append(f"  Verify version: {versions['verify']}")
        if split:
            lines.append(f"  Spec body: {versions['spec_body']}")
            lines.append(f"  Questions version: {versions['questions']}")
        lines.append("")
    return "\n".join(lines)


class ProgressStamp(unittest.TestCase):
    def test_tick_only_does_not_reopen(self):
        root = fresh()
        record_walk(root)
        (root / "tasks.md").write_text(tick_t6(TASKS), encoding="utf-8")
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)
        self.assertIn("Content stamp: normalized", (root / "walk-progress.md").read_text(encoding="utf-8"))

    def test_branch_pr_does_not_reopen(self):
        root = fresh()
        record_walk(root)
        (root / "spec.md").write_text(add_branch_pr(SPEC), encoding="utf-8")
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)

    def test_tick_and_branch_pr_and_task_note_do_not_reopen(self):
        root = fresh()
        record_walk(root)
        (root / "spec.md").write_text(add_branch_pr(SPEC), encoding="utf-8")
        (root / "tasks.md").write_text(add_task_pr(tick_t6(TASKS)), encoding="utf-8")
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)
        payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(payload["reopened"], [])
        self.assertEqual(payload["can_start"], ["T3", "T7"])
        self.assertIsNone(payload["because"])

    def test_crlf_does_not_reopen(self):
        root = fresh()
        record_walk(root)
        for name in ("spec.md", "plan.md", "tasks.md", "verify.md"):
            to_crlf(root / name)
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)

    def test_a_sentence_change_still_reopens(self):
        root = fresh()
        record_walk(root)
        text = (root / "spec.md").read_text(encoding="utf-8")
        (root / "spec.md").write_text(
            text.replace(
                "The receipt lists the order id.",
                "The receipt lists the order id and the lane.",
            ),
            encoding="utf-8",
        )
        status = statuses(root)
        for step in STEPS:
            if step == "resolve-open-questions":
                self.assertEqual(status[step], "keep", step)
                continue
            self.assertEqual(status[step], "reopen", step)
        payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "not-ready")
        self.assertEqual(payload["can_start"], ["T3", "T6", "T7"])
        self.assertIn("Reopened:", payload["because"])
        self.assertIn("not a start", payload["because"])
        self.assertNotIn("can start now", payload["next"])
        self.assertIn("rerun or clear", payload["next"])

    def test_a_match_branch_rename_does_not_reopen(self):
        root = fresh()
        record_walk(root)
        text = (root / "spec.md").read_text(encoding="utf-8")
        (root / "spec.md").write_text(
            text.replace("feat/orders-record", "feat/orders-record-v2"),
            encoding="utf-8",
        )
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)
        payload = must(["resume", "--root", str(root), "--no-playbook"])
        self.assertTrue(payload["restamp_only"])
        self.assertIn("Changed: Match. Reopen: none.", payload["reopen_line"])

    def test_old_split_stamp_matches_progress_and_the_next_record_upgrades(self):
        root = fresh()
        (root / "walk-progress.md").write_text(old_progress(root, split=True), encoding="utf-8")
        self.assertNotIn("Content stamp:", (root / "walk-progress.md").read_text(encoding="utf-8"))
        (root / "spec.md").write_text(add_branch_pr(SPEC), encoding="utf-8")
        (root / "tasks.md").write_text(add_task_pr(tick_t6(TASKS)), encoding="utf-8")
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)
        must([
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", "tasks-ready-to-build", "--result", "ready-partial",
            "--when", WHEN, "--yes",
        ])
        text = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Content stamp: normalized", text)
        (root / "tasks.md").write_text(
            (root / "tasks.md").read_text(encoding="utf-8").replace("- [ ] T3:", "- [x] T3:", 1),
            encoding="utf-8",
        )
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)

    def test_old_whole_file_stamp_matches_progress(self):
        root = fresh()
        (root / "walk-progress.md").write_text(old_progress(root, split=False), encoding="utf-8")
        (root / "spec.md").write_text(add_branch_pr(SPEC), encoding="utf-8")
        (root / "tasks.md").write_text(tick_t6(TASKS), encoding="utf-8")
        status = statuses(root)
        for step in STEPS:
            self.assertEqual(status[step], "keep", step)

    def test_old_stamp_one_tick_on_a_long_task_list(self):
        root = fresh()
        lines = ["# Tasks", ""]
        for number in range(1, 17):
            lines.append(f"- [ ] T{number}: step {number} (after: ) (spec: A{number})")
        tasks = "\n".join(lines) + "\n"
        (root / "tasks.md").write_text(tasks, encoding="utf-8")
        (root / "walk-progress.md").write_text(old_progress(root, split=True), encoding="utf-8")
        (root / "tasks.md").write_text(tasks.replace("- [ ] T6:", "- [x] T6:", 1), encoding="utf-8")
        status = statuses(root)
        self.assertEqual(status["review-and-tighten-plan"], "keep")
        self.assertEqual(status["tasks-ready-to-build"], "keep")

    def test_questions_with_blocks_stay_ready_partial_after_progress_edits(self):
        root = fresh()
        record_walk(root)
        before = must(["readiness", "--root", str(root)])
        self.assertEqual(before["result"], "ready-partial")
        self.assertEqual(before["can_start"], ["T3", "T6", "T7"])
        for tid in ("T8", "T9", "T10", "T11", "T12"):
            self.assertIn(tid, before["held"])
        (root / "spec.md").write_text(add_branch_pr(SPEC), encoding="utf-8")
        (root / "tasks.md").write_text(tick_t6(TASKS), encoding="utf-8")
        payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(payload["can_start"], ["T3", "T7"])
        self.assertEqual(payload["reopened"], [])
        self.assertIsNone(payload["because"])
        self.assertNotIn("whole slice", "\n".join(payload["held_lines"]).lower())

    def test_a_whole_slice_question_is_named_and_nothing_can_start(self):
        root = fresh()
        spec = SPEC.replace(
            "- Which ink is already chosen?\n  - Blocks: none (later phase)\n",
            "- Who signs the export?\n  - Blocks: whole slice\n",
        )
        (root / "spec.md").write_text(spec, encoding="utf-8")
        record_walk(root)
        payload = must(["readiness", "--root", str(root)])
        self.assertEqual(payload["result"], "not-ready")
        self.assertEqual(payload["can_start"], [])
        self.assertIn("whole slice", payload["because"].lower())
        self.assertIn("Holds the whole slice.", "\n".join(payload["held_lines"]))


if __name__ == "__main__":
    unittest.main()
