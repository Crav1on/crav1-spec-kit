"""1.173.0: done hashes come from each task's own evidence, full Held names,
the open-questions Run next label, and finalize-commit endings."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bm = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "build_map_1173")
wp = load(SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py", "walk_progress_1173")
lint = load(ROOT / "scripts/kit-lint.py", "kit_lint_1173")

TASKS = """# Tasks

- [x] T4: Orders README names the retry table (after: )
- [ ] T20: Orders CI/CD: infra Bicep for dev, test and prod (after: )
- [x] T27: Stop the prod orders-api until the partner reaches PROD (after: )
- [ ] T43: Incoming body with only tag and content, metadata read from the XML (after: )
"""

PLAN = """# Plan: orders

## Approach

1. README. (T4)
2. CI/CD. (T20)
3. Stop prod. (T27)
4. Incoming body. (T43)
"""

# The verify.md shape that broke 1.172.0: a Date line that names T4 and T27
# and then a newer, unrelated commit for T43, and a gaps note with it too.
VERIFY = """# Verify

Date: 2026-11-15, second run (T4 and T27 rechecked after their merges); T43 added 2026-11-15 from its build at local `abc9d01`

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T4 | Orders README | Implemented, verified | merged in PR 81, `4c0ffee` |
| T27 | Stop prod | Implemented, verified | merged in PR 80, `1234567` |
| T43 | Incoming body | Implemented, verified, tick pending | local `abc9d01`, not pushed |

## Gaps

- T43 and T27: the test for T43 is only at local `abc9d01`.
"""

PROGRESS = """# Build progress

Walk: build-walk
Branch: feat/orders-stop-prod
Owner: self
Tasks: T27 Stop the prod orders-api
Cut from: develop
Merge list: none

- Step: build
  Done: 2026-11-14T13:00:00+00:00
  Result: done (PR 80, 1234567, branch deleted)
"""


def done_marks(text: str) -> dict:
    return bm.map_marks(text)


class OwnHashes(unittest.TestCase):
    def test_verify_sha_reads_only_the_task_row(self):
        self.assertEqual(bm.verify_sha(VERIFY, 27), "1234567")
        self.assertEqual(bm.verify_sha(VERIFY, 4), "4c0ffee")
        self.assertEqual(bm.verify_sha(VERIFY, 43), "abc9d01")
        self.assertIsNone(bm.verify_sha(VERIFY, 20))

    def test_verify_sha_prefers_the_merge_commit(self):
        row = "| T7 | Retry | Implemented, verified | built at `abc1234`, merge commit `def5678` |"
        self.assertEqual(bm.verify_sha(row, 7), "def5678")

    def test_run_dir_keeps_each_task_on_its_own_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "orders"
            (root / "build-progress").mkdir(parents=True)
            (root / "tasks.md").write_text(TASKS, encoding="utf-8")
            (root / "plan.md").write_text(PLAN, encoding="utf-8")
            (root / "spec.md").write_text("# Spec\n", encoding="utf-8")
            (root / "verify.md").write_text(VERIFY, encoding="utf-8")
            (root / "build-progress" / "feat--orders-stop-prod.md").write_text(PROGRESS, encoding="utf-8")
            text, code = bm.run_dir(root)
            self.assertEqual(code, 0, text)
            first = (root / "build-map.md").read_text(encoding="utf-8")
            marks = done_marks(first)
            self.assertEqual(marks.get(27), "1234567")
            self.assertEqual(marks.get(4), "4c0ffee")
            self.assertNotIn("abc9d01", first)
            # A second write never swaps them.
            bm.run_dir(root)
            again = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertEqual(done_marks(again), marks)

    def test_build_progress_merge_hash_wins_over_verify(self):
        progress = {27: "1234567"}
        task = {"id": 27, "rest": "Stop prod", "map": None, "branch": None}
        verify = "| T27 | Stop prod | Implemented, verified | local `abc9d01` |"
        self.assertEqual(bm.done_evidence(task, "feat/orders-stop-prod", {}, verify, progress), "1234567")

    def test_no_own_hash_keeps_the_existing_mark(self):
        task = {"id": 4, "rest": "Orders README", "map": None, "branch": None}
        verify = "Date: 2026-11-15 (T4 rechecked); T43 at `abc9d01`\n"
        existing = bm.map_marks("- Tasks: ~~T4 Orders README~~ ✓ done (4c0ffee)\n")
        self.assertEqual(bm.done_evidence(task, "feat/orders-readme", {}, verify, {}, existing), "4c0ffee")

    def test_map_marks_reads_a_pr_link(self):
        marks = bm.map_marks("~~T1 Persist~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))")
        self.assertEqual(marks[1], "[PR 12](https://github.com/contoso/orders-api/pull/12)")


class FullHeldNames(unittest.TestCase):
    def test_held_and_ready_lines_use_the_full_name(self):
        long_name = "READMEs describe the receipts table, malformed partner payloads and the retry rules for the orders service"
        task = {"id": 5, "short": long_name[:77] + "...", "full": long_name, "label": "T5 " + long_name[:77] + "...",
                "run_label": "T5 " + long_name, "done": False, "walk": 0}
        branch = {"name": "feat/orders-readme", "tasks": [task], "wave": 1}
        built = {"branches": [branch]}
        rows = [{"task": "T5", "bucket": "waiting", "reason": "waits on the open question"}]
        report = bm.report_by_branch(built, rows)
        held = "\n".join(report["held_lines"])
        self.assertIn("T5 " + long_name, held)
        self.assertNotIn("...", held)


class OpenQuestionsLabel(unittest.TestCase):
    def test_label_is_above_the_command(self):
        entry = wp._run_from_clause("/crav1-show-or-ask-open-questions orders-api, because the questions are not asked yet.")
        self.assertEqual(entry, "Ask the open questions, which haven't been asked yet:\n`/crav1-show-or-ask-open-questions orders-api`")

    def test_every_run_entry_puts_the_command_last_alone(self):
        entry = wp._run_entry("git push", "the specs repo is 1 commit ahead of origin.")
        label, command = entry.split("\n")
        self.assertEqual(command, "`git push`")
        self.assertTrue(label[0].isupper() and label.endswith(":"))


class FinalizeCommitEndings(unittest.TestCase):
    def test_every_ending_is_run_next_or_nothing(self):
        skill = (SK / "crav1-finalize-commit/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Every ending of this skill is Run next or nothing", skill)
        self.assertIn("`stop`", skill)
        self.assertEqual(lint.run_next_only_problems(str(ROOT)), [])

    def test_lint_catches_a_next_line(self):
        self.assertEqual(lint.run_next_only_hits("ok\nNext: /crav1-open-pr, because.\n"), [2])
        self.assertEqual(lint.run_next_only_hits("End with `Next: nothing needed now.`\n"), [1])
        self.assertEqual(lint.run_next_only_hits("never a `Next:` line\n"), [])

    def test_kit_rewritten_files_still_ask(self):
        words = (SK / "crav1-finalize-commit/references/choice-words.md").read_text(encoding="utf-8")
        self.assertIn("Kit-rewritten files (1.173.0)", words)
        self.assertIn("`stop` recommended", words)


if __name__ == "__main__":
    unittest.main()
