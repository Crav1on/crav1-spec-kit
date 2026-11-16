"""1.176.0 review batch (part 2): ordered merge list, two-repo record,
verified-on-branch status, ending from build-progress, ADO body limit."""

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
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import test_walk_owner_claims_1175 as base  # noqa: E402


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wp = load(WALK, "walk_progress_1176b")

README_PROGRESS = """# Build progress

Walk: build-walk
Branch: feat/orders-readme
Owner: self
Tasks: T5 Orders README

- Step: open-pr
  Done: 2026-11-16T10:00:00+01:00
  Result: PR 71

- Step: wait-merge
  Done: 2026-11-16T10:05:00+01:00
  Result: waiting (PR 71)
"""


def two_pr_slice(tmp: str, t9_after: str = "T1", extra: str = "") -> Path:
    root = base.make_slice(tmp, user="person A")
    tasks = base.TASKS.replace("(after: T1)\n", f"(after: {t9_after})\n", 1)
    tasks += ("- [ ] T5: Orders README (branch: feat/orders-readme) (after: )\n"
              "- [ ] T6: Orders README links (branch: feat/orders-links) (after: T5)\n") + extra
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    (root / "claims.md").write_text(base.CLAIMS + "In progress: feat/orders-readme, T5, person A, since 2026-11-16T09:00:00+01:00\n", encoding="utf-8")
    (root / "build-progress" / "feat--orders-readme.md").write_text(README_PROGRESS, encoding="utf-8")
    base.stopped_walk(root)
    return root


def ending(root: Path) -> str:
    proc = subprocess.run([sys.executable, str(WALK), "readiness", "--root", str(root), "--skip-sync"],
                          capture_output=True, text=True, check=False)
    payload = json.loads(proc.stdout)
    return payload["ending"]


class OrderedMergeList(unittest.TestCase):
    def test_owners_and_unblocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = two_pr_slice(tmp)
            prs = wp.open_prs(root)
            self.assertEqual(prs[71]["owner"], "yours")
            self.assertEqual(prs[82]["owner"], "person B")
            text = ending(root)
            self.assertIn("Merge these PRs, in this order:\n"
                          "1. PR 71 (yours, feat/orders-readme): ticks T5, then T6 can start.\n"
                          "2. PR 82 (person B's, feat/orders-cicd): ticks T9 to T12, then T13 can start.", text)
            self.assertNotIn("Waiting: PR 71 to merge", text)
            self.assertNotIn("built, and wait for PR 82", text)
            self.assertNotIn("Next:", text.replace("Run next:", ""))
            self.assertIn("- feat/orders-cicd: built, PR 82 open", text)

    def test_a_pr_others_depend_on_comes_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            extra = "- [ ] T14: Orders alerts (branch: feat/orders-alerts) (after: T12)\n"
            root = two_pr_slice(tmp, extra=extra)
            order = [item["pr"] for item in wp.merge_order(wp.build_rows(root), wp.open_prs(root))]
            self.assertEqual(order, [82, 71], "more unblocked tasks wins a tie")
        with tempfile.TemporaryDirectory() as tmp:
            extra = "- [ ] T14: Orders alerts (branch: feat/orders-alerts) (after: T12)\n"
            root = two_pr_slice(tmp, t9_after="T1, T5", extra=extra)
            order = [item["pr"] for item in wp.merge_order(wp.build_rows(root), wp.open_prs(root))]
            self.assertEqual(order, [71, 82], "a PR the other depends on comes first")
