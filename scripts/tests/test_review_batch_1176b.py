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


import test_branch_run_1155 as brt  # noqa: E402

br = brt.br


def clone_pair(base_dir: Path, name: str) -> Path:
    bare = base_dir / f"{name}.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)], check=True, capture_output=True)
    work = base_dir / name
    subprocess.run(["git", "clone", str(bare), str(work)], check=True, capture_output=True)
    for key, value in (("user.email", "person-a@example.com"), ("user.name", "person A"), ("commit.gpgsign", "false")):
        brt.git(work, "config", key, value)
    return work


class TwoRepoRecord(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.specs = clone_pair(self.base, "specs")
        self.code = clone_pair(self.base, "code")
        self.root = brt.write_slice(self.specs)
        (self.root / "verify.md").write_text("# Verify\n", encoding="utf-8")
        (self.root / "work-item.md").write_text("# Work item\n\nAB#2 Orders CI/CD\n", encoding="utf-8")
        brt.git(self.specs, "add", "-A")
        brt.git(self.specs, "commit", "-m", "Start")
        brt.git(self.specs, "push", "-u", "origin", "main")
        brt.git(self.code, "checkout", "-b", "feat/orders-cicd")
        (self.code / "a.txt").write_text("a", encoding="utf-8")
        brt.git(self.code, "add", "-A")
        brt.git(self.code, "commit", "-m", "Build T2")
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        brt.git(self.specs, "add", "-A")
        brt.git(self.specs, "commit", "-m", "Claim")

    def test_code_repo_passed_as_repo_no_longer_crashes(self):
        sha = brt.git(self.code, "rev-parse", "HEAD").stdout.strip()
        (self.root / "verify.md").write_text("# Verify\n\n- T2 evidence\n", encoding="utf-8")
        out = br.record(self.root, "feat/orders-cicd", "T2", sha, "green", self.code, push=True)
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["code_repo"], str(self.code.resolve()))
        self.assertEqual(out["specs_repo"], str(self.specs.resolve()))
        self.assertIn("docs/specs/orders-api/verify.md", out["files"])
        self.assertTrue(out["code_pushed"] and out["specs_pushed"], out)
        message = brt.git(self.specs, "log", "-1", "--format=%B").stdout
        self.assertIn("Record T2 on feat/orders-cicd with its verify evidence", message)
        self.assertIn("AB#2", message)
        self.assertEqual(brt.git(self.specs, "status", "--porcelain").stdout.strip(), "")

    def test_bad_specs_repo_writes_nothing(self):
        before = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        progress = br.progress_path(self.root, "feat/orders-cicd").read_text(encoding="utf-8")
        out = br.record(self.root, "feat/orders-cicd", "T2", "a1b2c3d", "green",
                        specs_repo=self.code, code_repo=self.code)
        self.assertFalse(out["ok"])
        self.assertEqual(out["code"], "specs-repo")
        self.assertIn("Nothing was written", out["line"])
        self.assertEqual((self.root / "walk-progress.md").read_text(encoding="utf-8"), before)
        self.assertEqual(br.progress_path(self.root, "feat/orders-cicd").read_text(encoding="utf-8"), progress)
