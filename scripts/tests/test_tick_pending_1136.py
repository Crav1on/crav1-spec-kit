"""1.136.0: a merged unticked task is not a verify loop, and the tick starts no worker."""

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
ORDER = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py"
BUILD_MAP = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/build_map.py"
WHEN = "2026-11-12T09:00:00+00:00"

PLAN = """# Plan: the slice

Reviewed: 2026-11-12, P# open: 0

## Risks
"""

SPEC = """# Orders export

Playbook: docs/playbooks/orders-export.md

Work item: 78 — orders export

## Match

- Branch: orders-api feat/orders-export (PR 78) merged

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to the partner. Question 1.
  - Blocks: T7
"""

TASKS = """# Tasks

- [ ] T2: export the receipt (PR 78, merged) (branch: feat/orders-export) (spec: A1)
- [ ] T3: record the order (branch: feat/orders-record) (after: ) (spec: A2)
- [ ] T6: send the mail (branch: feat/orders-mail) (after: ) (spec: A3)
- [ ] T7: choose the currency (after: ) (spec: A4)
"""

VERIFY_PENDING = """# Verify

## TL;DR

| | Count | Ids |
| --- | --- | --- |
| Implemented, verified, tick pending | 1 | T2 |
| Not implemented | 3 | T3, T6, T7 |

Next: /crav1-build-tasks T3 (on `feat/orders-record`)
Next: /crav1-build-tasks T6 (on `feat/orders-mail`)

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | export the receipt | Implemented, verified, tick pending | unit |
| T3 | record the order | Not implemented | |
| T6 | send the mail | Not implemented | |
| T7 | choose the currency | Not implemented | |
"""

VERIFY_NOT = """# Verify

## TL;DR

| | Count | Ids |
| --- | --- | --- |
| Not implemented | 4 | T2, T3, T6, T7 |

Next: /crav1-build-tasks T3 (on `feat/orders-record`)
Next: /crav1-build-tasks T6 (on `feat/orders-mail`)

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T2 | export the receipt | Not implemented | |
| T3 | record the order | Not implemented | |
| T6 | send the mail | Not implemented | |
| T7 | choose the currency | Not implemented | |
"""


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


def write_slice(root: Path, verify: str) -> None:
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    (root / "verify.md").write_text(verify, encoding="utf-8")


def record_resolve(root: Path) -> None:
    must_json(WALK, [
        "record", "--root", str(root), "--slice", "docs/specs/orders-export",
        "--step", "resolve-open-questions", "--result", "done",
        "--when", WHEN, "--yes",
    ])


class TickPending(unittest.TestCase):
    def test_merged_tick_pending_is_not_behind_and_ticks_with_no_worker(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        write_slice(root, VERIFY_PENDING)
        record_resolve(root)
        payload = must_json(WALK, ["readiness", "--full", "--root", str(root)])
        self.assertFalse(payload["verify_behind"])
        self.assertIsNone(payload["verify_waiting"])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(payload["can_start"], ["T3", "T6"])
        self.assertNotIn("T2", payload["can_start"])
        self.assertIn("T7", payload["held"])
        before = (root / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("- [ ] T2:", before)
        ticked = must_json(TICK, ["--root", str(root), "T2", "--yes"])
        self.assertEqual(ticked["task"], "T2")
        self.assertTrue(ticked["ticked"])
        self.assertFalse(ticked["worker"])
        after = (root / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("- [x] T2:", after)
        self.assertIn("- [ ] T3:", after)
        self.assertIn("- [ ] T6:", after)
        self.assertNotIn("worker started", after.lower())

    def test_next_naming_a_merged_unticked_task_is_not_behind(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        verify = VERIFY_PENDING.replace(
            "Next: /crav1-build-tasks T3 (on `feat/orders-record`)\n"
            "Next: /crav1-build-tasks T6 (on `feat/orders-mail`)\n",
            "Next: /crav1-build-tasks T2, because only the tick is left.\n",
        )
        write_slice(root, verify)
        record_resolve(root)
        payload = must_json(WALK, ["readiness", "--full", "--root", str(root)])
        self.assertFalse(payload["verify_behind"])
        self.assertIsNone(payload["stale_next"])
        self.assertEqual(payload["result"], "ready-partial")

    def test_not_implemented_is_behind_but_verify_drift_is_not_not_ready(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        write_slice(root, VERIFY_PENDING)
        record_resolve(root)
        must_json(WALK, [
            "record", "--root", str(root), "--slice", "docs/specs/orders-export",
            "--step", "tasks-ready-to-build", "--result", "ready-partial",
            "--when", WHEN, "--yes",
        ])
        (root / "verify.md").write_text(VERIFY_NOT, encoding="utf-8")
        payload = must_json(WALK, ["readiness", "--full", "--root", str(root)])
        self.assertTrue(payload["verify_behind"])
        self.assertIn("T2", payload["verify_stale"])
        self.assertEqual(payload["result"], "ready-partial")
        self.assertNotEqual(payload["result"], "not-ready")
        self.assertEqual(payload["can_start"], ["T3", "T6"])
        self.assertEqual(payload["reopened"], [])
        resumed = must_json(WALK, ["resume", "--root", str(root)])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["tasks-ready-to-build"]["status"], "keep")

    def test_ticked_task_still_not_implemented_or_named_in_next_is_behind(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        tasks = TASKS.replace("- [ ] T2:", "- [x] T2:", 1)
        (root / "spec.md").write_text("# Orders export\n\n## Open questions\n", encoding="utf-8")
        (root / "plan.md").write_text(PLAN, encoding="utf-8")
        (root / "tasks.md").write_text(tasks, encoding="utf-8")
        (root / "verify.md").write_text(
            "# Verify\n\nNext: /crav1-build-tasks T2\n\n"
            "## Tasks — overview (dependency order)\n\n"
            "| T# | Title | Status | Verify |\n| --- | --- | --- | --- |\n"
            "| T2 | export the receipt | Not implemented | |\n",
            encoding="utf-8",
        )
        payload = must_json(WALK, ["readiness", "--full", "--root", str(root)])
        self.assertTrue(payload["verify_behind"])
        self.assertEqual(payload["verify_stale"], ["T2"])
        self.assertIn("T2", payload["stale_next"])

    def test_tick_only_ticks_a_merged_row_when_the_slice_is_not_ready(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        (root / "spec.md").write_text("# Orders export\n\n## Open questions\n", encoding="utf-8")
        (root / "plan.md").write_text(PLAN, encoding="utf-8")
        (root / "tasks.md").write_text(
            "# Tasks\n\n"
            "- [ ] T2: export the receipt (PR 78, merged)\n"
            "- [ ] T3: record the order (after: T4)\n"
            "- [ ] T4: send the mail (after: T3)\n",
            encoding="utf-8",
        )
        (root / "verify.md").write_text(VERIFY_PENDING, encoding="utf-8")
        ready = must_json(WALK, ["readiness", "--full", "--root", str(root)])
        self.assertEqual(ready["result"], "not-ready")
        ticked = must_json(TICK, ["--root", str(root), "T2", "--yes"])
        self.assertEqual(ticked["task"], "T2")
        self.assertEqual(ticked["result"], "not-ready")
        self.assertTrue(ticked["ticked"])
        self.assertFalse(ticked["worker"])
        text = (root / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("- [x] T2:", text)
        self.assertIn("- [ ] T3:", text)
        self.assertIn("- [ ] T4:", text)
        code, out, err = run(TICK, ["--root", str(root), "T3", "--yes"])
        self.assertEqual(code, 2, err + out)
        refused = json.loads(out)
        self.assertEqual(refused["code"], "not-tick-only")
        self.assertFalse(refused["worker"])
        self.assertFalse(refused["ticked"])


class NeedsTickOrder(unittest.TestCase):
    def test_task_order_cli_lists_needs_tick(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        (root / "spec.md").write_text(SPEC, encoding="utf-8")
        (root / "tasks.md").write_text(TASKS, encoding="utf-8")
        code, out, err = run(ORDER, [str(root / "tasks.md")])
        self.assertEqual(code, 0, err + out)
        self.assertIn("Needs tick", out)
        self.assertIn("- T2: export the receipt", out)
        ready = out.split("Waits in order", 1)[0]
        self.assertNotIn("T2:", ready)
        self.assertNotIn("Next: T2", out)
        self.assertIn("- T3: record the order", out)


class ResolveSpec(unittest.TestCase):
    def test_folder_hyphen_and_space_match_first(self):
        root = Path(tempfile.mkdtemp())
        folder = root / "orders-1-0"
        folder.mkdir()
        (folder / "spec.md").write_text("# Something else\n", encoding="utf-8")
        other = root / "orders-export"
        other.mkdir()
        (other / "spec.md").write_text("# Orders 1.0\n", encoding="utf-8")
        payload = must_json(RESOLVE, ["orders 1.0", "--root", str(root), "--json"])
        self.assertEqual(payload["slug"], "orders-1-0")
        self.assertEqual(payload["how"], "folder")

    def test_unique_playbook_and_title(self):
        root = Path(tempfile.mkdtemp())
        export = root / "slice-a"
        export.mkdir()
        (export / "spec.md").write_text(
            "# Receipts\n\nPlaybook: docs/playbooks/orders-export.md\n",
            encoding="utf-8",
        )
        archive = root / "slice-b"
        archive.mkdir()
        (archive / "spec.md").write_text("# Archive the receipt\n", encoding="utf-8")
        by_playbook = must_json(RESOLVE, ["orders-export", "--root", str(root), "--json"])
        self.assertEqual(by_playbook["slug"], "slice-a")
        self.assertEqual(by_playbook["how"], "playbook")
        by_title = must_json(RESOLVE, ["Archive the receipt", "--root", str(root), "--json"])
        self.assertEqual(by_title["slug"], "slice-b")
        self.assertEqual(by_title["how"], "title")

    def test_unique_work_item_name(self):
        root = Path(tempfile.mkdtemp())
        folder = root / "slice-a"
        folder.mkdir()
        (folder / "spec.md").write_text(
            "# Receipts\n\nWork item: 78 — orders export\n",
            encoding="utf-8",
        )
        payload = must_json(RESOLVE, ["orders export", "--root", str(root), "--json"])
        self.assertEqual(payload["slug"], "slice-a")
        self.assertIn("work-item", payload["how"])

    def test_several_matches_stop(self):
        root = Path(tempfile.mkdtemp())
        for name in ("slice-a", "slice-b"):
            folder = root / name
            folder.mkdir()
            (folder / "spec.md").write_text("# Orders export\n", encoding="utf-8")
        code, out, err = run(RESOLVE, ["Orders export", "--root", str(root)])
        self.assertEqual(code, 2, err + out)
        self.assertIn("Several spec folders match", out)
        self.assertIn("slice-a", out)
        self.assertIn("slice-b", out)
        self.assertNotIn("docs/specs/slice-a\n", out)


class RecommendFolder(unittest.TestCase):
    def test_recommend_on_a_tasks_file_names_the_parent(self):
        root = Path(tempfile.mkdtemp()) / "orders-export"
        root.mkdir()
        tasks = root / "tasks.md"
        tasks.write_text("- [ ] T1: record the order\n", encoding="utf-8")
        code, out, err = run(BUILD_MAP, [str(tasks), "--recommend", "T1"])
        self.assertEqual(code, 2, err + out)
        self.assertIn("A spec folder is required", out)
        self.assertIn(str(root), out)


if __name__ == "__main__":
    unittest.main()
