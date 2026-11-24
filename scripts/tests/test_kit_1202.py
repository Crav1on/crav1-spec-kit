"""1.202.0: vendor trees, the Held list, and the script-computed open count.

Generic fixtures only (orders-api, contoso, person A).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
MAP = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"
PLAN = SK / "crav1-plan-from-spec/scripts/plan_check.py"
SYNC = ROOT / "scripts/sync-crav1-vendors.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class HeldList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bm = load(MAP, "build_map_t1202")
        cls.wp = load(WALK, "walk_progress_t1202")

    def test_after_wait_on_an_unbuilt_task_is_in_held(self):
        built = {"branches": [{
            "name": "feat/orders-export",
            "section": "wave",
            "wave": 1,
            "tasks": [
                {"id": 8, "full": "Export orders", "short": "Export orders", "done": False, "waits_on": []},
                {"id": 17, "full": "Notify on export", "short": "Notify on export", "done": False, "waits_on": [8]},
            ],
        }]}
        rows = [
            {"task": "T8", "bucket": "ready"},
            {"task": "T17", "bucket": "waits-in-order", "reason": "waits on T8 (recorded)"},
        ]
        text = "\n".join(self.bm.report_by_branch(built, rows)["held_lines"])
        self.assertIn("T17 Notify on export — waits on T8", text)
        self.assertNotIn("T8 Export orders", text)

    def test_a_task_the_map_missed_is_still_listed(self):
        built = {"branches": []}
        rows = [{"task": "T17", "bucket": "waits-in-order", "reason": "waits on T8 (recorded)"}]
        text = "\n".join(self.bm.report_by_branch(built, rows)["held_lines"])
        self.assertIn("T17 — waits on T8", text)

    def test_own_pr_reason_is_on_the_held_line_once(self):
        root = Path(tempfile.mkdtemp()) / "docs" / "specs" / "orders-api"
        root.mkdir(parents=True)
        (root / "spec.md").write_text("# Orders API\n\n## Problem\n\nx\n", encoding="utf-8")
        (root / "plan.md").write_text("# Plan\n\nReviewed: 2026-11-19, P# open: 0\n", encoding="utf-8")
        (root / "tasks.md").write_text(
            "# Tasks\n\n- [ ] T13 Add the export endpoint (branch: feat/orders-export)\n"
            "- [ ] T30 Retry failed orders (branch: feat/orders-retry)\n",
            encoding="utf-8",
        )
        (root / "claims.md").write_text(
            "# Claims\n\nIn progress: feat/orders-retry, T30, person A, since 2026-11-19T09:00:00+01:00\n",
            encoding="utf-8",
        )
        (root / "build-progress").mkdir()
        (root / "build-progress/feat--orders-retry.md").write_text(
            "# Build progress\n\nBranch: feat/orders-retry\nOwner: self\nTasks: T30\n\n"
            "- Step: open-pr\n  Done: 2026-11-20\n  Result: done (PR 85)\n",
            encoding="utf-8",
        )
        proc = subprocess.run(
            [sys.executable, str(WALK), "readiness", "--root", str(root), "--user", "person A", "--skip-sync", "--full"],
            capture_output=True, text=True,
        )
        out = json.loads(proc.stdout)
        sentence = "T30 is yours and waits for PR 85's merge."
        held = "\n".join(out["held_lines"])
        self.assertIn(sentence, held, held)
        self.assertNotIn("— held", held)
        self.assertEqual(out["ending"].count(sentence), 1, out["ending"])


    def test_held_phrase_own_pr_keeps_the_inline_reason(self):
        # 1.202.0 merged with 1.201.1: a task waiting on its own PR.
        row = {"reason": "", "task": "T30", "own_pr_open": 85}
        self.assertEqual(self.bm.held_phrase(row), "T30 is yours and waits for PR 85's merge.")
        row = {"reason": "", "task": "T30", "own_pr_open": 85, "merge_wait": {"pr": 85}}
        self.assertEqual(self.bm.held_phrase(row), "T30 is yours and waits for PR 85's merge.")

    def test_held_phrase_other_pr_wait_says_waits_to_merge(self):
        # 1.201.1 wording for a wait that is not the task's own PR.
        self.assertEqual(self.bm.held_phrase({"reason": "", "merge_wait": {"pr": 87}}), "waits for PR 87 to merge")
        self.assertEqual(self.bm.held_phrase({"reason": "held", "pr": 12}), "waits for PR 12 to merge")


class OpenCount(unittest.TestCase):
    def test_the_script_counts_distinct_findings(self):
        mod = load(PLAN, "plan_check_t1202")
        review = "See the plan.\n\nP1 — plan — T2 has no verify.\nP2 — spec — auth is open.\nP1 is the same finding.\n"
        self.assertEqual(mod.open_findings(review), 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.md"
            path.write_text(review, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(PLAN), "open-count", "--review", str(path)],
                capture_output=True, text=True,
            )
        self.assertEqual(proc.stdout, "open: 2\n", proc.stderr)
        text = (SK / "crav1-tighten-and-plan-ready-to-build/references/steps.md").read_text(encoding="utf-8")
        self.assertIn("open-count", text)
        self.assertIn("Do not count the `P#` lines yourself", text)


class VendorGenerate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sync = load(SYNC, "sync_vendors_t1202")

    def test_a_skill_is_tuned_and_deterministic(self):
        source = (SK / "crav1-review-plan/SKILL.md").read_text(encoding="utf-8")
        codex = self.sync.transform_skill(source, "codex", "1.202.0", ".agents/skills")
        again = self.sync.transform_skill(source, "codex", "1.202.0", ".agents/skills")
        self.assertEqual(codex, again)
        body = codex.split("---", 2)[2].lstrip("\n")
        self.assertTrue(body.startswith("Read `../crav1-docs/reference/kit-rules.md` first."))
        self.assertIn("crav1-vendor: codex", codex)
        self.assertIn("crav1-version: 1.202.0", codex)
        self.assertNotIn("icon:", codex.split("metadata:", 1)[0])
        self.assertIsNone(self.sync.COMMAND.search(codex))
        self.assertIn("$crav1-tighten-plan", codex)
        self.assertNotIn("AGENTS.md", codex)
        copilot = self.sync.transform_skill(source, "copilot", "1.202.0", ".github/skills")
        self.assertIn("/crav1-tighten-plan", copilot)
        self.assertNotIn("$crav1-", copilot)
        self.assertIn("--vendor copilot", copilot)

    def test_committed_trees_pass_lint(self):
        problems = self.sync.lint(ROOT)
        self.assertEqual(problems, [], "\n".join(problems[:20]))
        codex = ROOT / "vendors/codex"
        copilot = ROOT / "vendors/copilot"
        self.assertFalse(list(codex.rglob("AGENTS.md")))
        self.assertFalse(list(copilot.rglob("AGENTS.md")))
        yaml_files = list(codex.rglob("openai.yaml"))
        self.assertEqual(len(yaml_files), 45)
        self.assertFalse((codex / ".agents/skills/crav1-help/agents/openai.yaml").exists())
        self.assertFalse((codex / ".agents/skills/crav1-update-kit/agents/openai.yaml").exists())
        instructions = (copilot / ".github/instructions/crav1.instructions.md").read_text(encoding="utf-8")
        self.assertIn('applyTo: "**"', instructions)
        cards = (codex / ".agents/skills/crav1-docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("numbered list", cards)
