"""1.151.0: build-walk claims, pull before reading, and settle-and-push."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/claims.py"
SYNC = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/repo_sync.py"
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
TASK_ORDER = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py"

PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Record the decision. (T2)
2. Export the receipt. (T3)

## Risks
"""

SPEC = """# Spec

The receipt lists the order id.

## Open questions
"""

TASKS = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-api-record) (after: )
- [ ] T2: Record the decision (branch: feat/orders-api-host-setup) (after: )
- [ ] T3: Export the receipt (branch: feat/orders-api-export) (after: )
"""

VERIFY = """# Verify

## Tasks — overview (dependency order)

| T# | Title | Status | Verify |
| --- | --- | --- | --- |
| T1 | Persist the decision | Implemented, verified | |
"""


def run_py(script: Path, args: list[str], cwd: Path | None = None) -> tuple[int, dict, str]:
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd) if cwd else None,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    return proc.returncode, payload, proc.stderr or ""


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def init_repo(path: Path, name: str = "person A") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.email", "person-a@example.com")
    git(path, "config", "user.name", name)
    git(path, "config", "commit.gpgsign", "false")
    return path


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def pair_repos(base: Path) -> tuple[Path, Path]:
    """A local 'origin' and a clone that can go ahead, behind, or diverged."""
    origin = init_repo(base / "origin")
    (origin / "README.md").write_text("start\n", encoding="utf-8")
    commit_all(origin, "Start")
    # bare remote
    bare = base / "remote.git"
    subprocess.run(["git", "clone", "--bare", str(origin), str(bare)], check=True, capture_output=True)
    work = base / "work"
    subprocess.run(["git", "clone", str(bare), str(work)], check=True, capture_output=True)
    git(work, "config", "user.email", "person-a@example.com")
    git(work, "config", "user.name", "person A")
    git(work, "config", "commit.gpgsign", "false")
    return work, bare


def write_slice(root: Path) -> Path:
    spec = root / "docs" / "specs" / "orders-api"
    spec.mkdir(parents=True, exist_ok=True)
    (spec / "spec.md").write_text(SPEC, encoding="utf-8")
    (spec / "plan.md").write_text(PLAN, encoding="utf-8")
    (spec / "tasks.md").write_text(TASKS, encoding="utf-8")
    (spec / "verify.md").write_text(VERIFY, encoding="utf-8")
    return spec


class ClaimsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = write_slice(self.tmp)

    def test_add_list_and_clear(self):
        code, payload, err = run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T27",
            "--user", "person A",
            "--since", "2026-11-13T15:50:00+01:00",
        ])
        self.assertEqual(code, 0, err)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["added"]["tasks"], ["T27"])
        self.assertTrue((self.root / "claims.md").is_file())
        text = (self.root / "claims.md").read_text(encoding="utf-8")
        self.assertIn("In progress: feat/orders-api-host-setup, T27, person A, since 2026-11-13T15:50:00+01:00", text)
        code, listed, _ = run_py(CLAIMS, ["list", "--root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertEqual(listed["ids"], ["T27"])
        self.assertEqual(listed["claims"][0]["phrase"], "in progress by person A since 2026-11-13")
        self.assertFalse(listed["warnings"])
        code, cleared, _ = run_py(CLAIMS, [
            "clear", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T27",
        ])
        self.assertEqual(code, 0)
        self.assertEqual(cleared["claims"], [])
        self.assertFalse((self.root / "claims.md").exists())

    def test_age_warning_never_autoclears(self):
        since = "2026-11-09T10:00:00+01:00"
        run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T27",
            "--user", "person A",
            "--since", since,
        ])
        code, listed, _ = run_py(CLAIMS, [
            "list", "--root", str(self.root),
            "--now", "2026-11-13T16:00:00+01:00",
        ])
        self.assertEqual(code, 0)
        self.assertTrue(listed["claims"][0]["stale"])
        self.assertTrue(listed["warnings"])
        self.assertIn("release claim", listed["warnings"][0])
        self.assertTrue((self.root / "claims.md").is_file())
        self.assertIn("T27", (self.root / "claims.md").read_text(encoding="utf-8"))

    def test_age_days_configurable(self):
        run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--since", "2026-11-12T10:00:00+00:00",
            "--age-days", "1",
        ])
        text = (self.root / "claims.md").read_text(encoding="utf-8")
        self.assertIn("Claim max age: 1 days", text)
        _, listed, _ = run_py(CLAIMS, [
            "list", "--root", str(self.root),
            "--now", "2026-11-13T12:00:00+00:00",
            "--age-days", "1",
        ])
        self.assertTrue(listed["claims"][0]["stale"])

    def test_other_user_conflict(self):
        run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--since", "2026-11-13T15:50:00+01:00",
        ])
        code, payload, _ = run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person B",
        ])
        self.assertNotEqual(code, 0)
        self.assertEqual(payload["code"], "claimed")
        self.assertIn("person A", payload["line"])

    def test_same_user_refreshes(self):
        run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--since", "2026-11-13T10:00:00+01:00",
        ])
        code, payload, _ = run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--since", "2026-11-13T16:00:00+01:00",
        ])
        self.assertEqual(code, 0)
        self.assertEqual(payload["claims"][0]["since"], "2026-11-13T16:00:00+01:00")

    def test_headless_stops(self):
        code, payload, _ = run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--headless",
        ])
        self.assertNotEqual(code, 0)
        self.assertEqual(payload["code"], "headless")
        self.assertIn("yes", payload["line"])
        self.assertFalse((self.root / "claims.md").exists())

    def test_preserve_keeps_claimed_line(self):
        before = TASKS
        after = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-api-record) (after: )
- [ ] T2: REWRITTEN the decision (branch: feat/other) (after: T1)
- [ ] T4: A new later task (branch: feat/orders-api-export) (after: )
"""
        before_path = self.root / "before.md"
        after_path = self.root / "after.md"
        before_path.write_text(before, encoding="utf-8")
        after_path.write_text(after, encoding="utf-8")
        code, payload, _ = run_py(CLAIMS, [
            "preserve", "--before", str(before_path), "--after", str(after_path),
            "--tasks", "T2",
        ])
        self.assertEqual(code, 0)
        self.assertIn("T2: Record the decision (branch: feat/orders-api-host-setup)", payload["text"])
        self.assertNotIn("REWRITTEN", payload["text"])
        self.assertIn("T4: A new later task", payload["text"])
        self.assertEqual(payload["kept"], ["T2"])
        self.assertIn("Kept claimed tasks: T2.", payload["line"])

    def test_preserve_restores_removed_and_renumbered(self):
        before = TASKS
        after = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-api-record) (after: )
- [ ] T9: Record the decision (branch: feat/orders-api-host-setup) (after: )
"""
        before_path = self.root / "before.md"
        after_path = self.root / "after.md"
        before_path.write_text(before, encoding="utf-8")
        after_path.write_text(after, encoding="utf-8")
        _, payload, _ = run_py(CLAIMS, [
            "preserve", "--before", str(before_path), "--after", str(after_path),
            "--tasks", "T2,T3",
        ])
        self.assertIn("- [ ] T2: Record the decision (branch: feat/orders-api-host-setup) (after: )", payload["text"])
        self.assertIn("- [ ] T3: Export the receipt (branch: feat/orders-api-export) (after: )", payload["text"])
        self.assertNotIn("T9:", payload["text"])
        self.assertEqual(payload["kept"], ["T2", "T3"])

    def test_stamp_strip_drops_claim_lines(self):
        text = "# Tasks\n\nIn progress: feat/orders-api-host-setup, T2, person A, since 2026-11-13T15:50:00+01:00\n- [ ] T2: Record the decision\n"
        path = self.root / "mixed.md"
        path.write_text(text, encoding="utf-8")
        code, payload, _ = run_py(CLAIMS, ["stamp-strip", "--path", str(path)])
        self.assertEqual(code, 0)
        self.assertNotIn("In progress:", payload["text"])
        self.assertIn("T2: Record the decision", payload["text"])
        self.assertTrue(payload["changed"])


class ReadinessClaimTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = write_slice(self.tmp)

    def test_claimed_task_is_held_and_not_in_run_next(self):
        run_py(CLAIMS, [
            "add", "--root", str(self.root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--since", "2026-11-13T15:50:00+01:00",
        ])
        code, payload, err = run_py(WALK, ["readiness", "--full", "--root", str(self.root)])
        self.assertEqual(code, 0, err + json.dumps(payload)[:500])
        self.assertIn("T2", payload.get("held") or [])
        self.assertNotIn("T2", payload.get("can_start") or [])
        ending = payload.get("ending") or ""
        self.assertIn("in progress by person A since 2026-11-13", ending)
        self.assertNotRegex(ending, r"`/crav1-build-walk(?: orders-api)? T2`")
        # T3 is still a start
        self.assertIn("T3", payload.get("can_start") or [])
        self.assertIn("`/crav1-build-walk", ending)

    def test_stamp_ignores_claim_lines(self):
        sys.path.insert(0, str(WALK.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("walk_progress", WALK)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        base = "# Tasks\n\n- [ ] T2: Record the decision\n"
        with_claim = base + "In progress: feat/orders-api-host-setup, T2, person A, since 2026-11-13T15:50:00+01:00\n"
        self.assertEqual(mod.normalize_text("tasks", base), mod.normalize_text("tasks", with_claim))
        self.assertEqual(mod.version_text(mod.normalize_text("tasks", base)), mod.version_text(mod.normalize_text("tasks", with_claim)))


class TaskOrderClaimTests(unittest.TestCase):
    def test_task_order_lists_claim_as_waiting(self):
        tmp = Path(tempfile.mkdtemp())
        root = write_slice(tmp)
        run_py(CLAIMS, [
            "add", "--root", str(root),
            "--branch", "feat/orders-api-host-setup",
            "--tasks", "T2",
            "--user", "person A",
            "--since", "2026-11-13T15:50:00+01:00",
        ])
        proc = subprocess.run(
            [sys.executable, str(TASK_ORDER), str(root / "tasks.md")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = proc.stdout
        self.assertIn("Waiting, in progress", out)
        self.assertIn("T2", out)
        self.assertIn("in progress by person A since 2026-11-13", out)
        # Ready should not include T2
        ready_block = out.split("Waits in order")[0]
        self.assertNotIn("T2:", ready_block)


class SyncTests(unittest.TestCase):
    def test_behind_stops_with_pull_ending(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, bare = pair_repos(Path(tmp))
            # Advance origin
            other = Path(tmp) / "other"
            subprocess.run(["git", "clone", str(bare), str(other)], check=True, capture_output=True)
            git(other, "config", "user.email", "person-a@example.com")
            git(other, "config", "user.name", "person A")
            git(other, "config", "commit.gpgsign", "false")
            (other / "extra.md").write_text("upstream\n", encoding="utf-8")
            commit_all(other, "Upstream ahead")
            git(other, "push", "origin", "HEAD")
            code, payload, err = run_py(SYNC, ["status", "--repo", str(work)])
            self.assertNotEqual(code, 0, err)
            self.assertEqual(payload["state"], "behind")
            self.assertTrue(payload["stop"])
            self.assertFalse(payload["continue"])
            self.assertIn("`git pull --no-rebase`", payload["ending"])
            self.assertIn("Run next:", payload["ending"])
            self.assertNotIn("rebase", payload["ending"].split("never rebase")[0][-20:] + "x")

    def test_ahead_continues_with_waiting(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, _bare = pair_repos(Path(tmp))
            (work / "local.md").write_text("ahead\n", encoding="utf-8")
            commit_all(work, "Local ahead")
            code, payload, err = run_py(SYNC, ["status", "--repo", str(work)])
            self.assertEqual(code, 0, err)
            self.assertEqual(payload["state"], "ahead")
            self.assertTrue(payload["continue"])
            self.assertEqual(payload["ahead"], 1)
            self.assertIn("Waiting: push the specs repo (1 commit ahead of origin).", payload["waiting"])

    def test_diverged_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, bare = pair_repos(Path(tmp))
            (work / "local.md").write_text("ahead\n", encoding="utf-8")
            commit_all(work, "Local ahead")
            other = Path(tmp) / "other"
            subprocess.run(["git", "clone", str(bare), str(other)], check=True, capture_output=True)
            git(other, "config", "user.email", "person-a@example.com")
            git(other, "config", "user.name", "person A")
            git(other, "config", "commit.gpgsign", "false")
            (other / "extra.md").write_text("upstream\n", encoding="utf-8")
            commit_all(other, "Upstream ahead")
            git(other, "push", "origin", "HEAD")
            code, payload, err = run_py(SYNC, ["status", "--repo", str(work)])
            self.assertNotEqual(code, 0, err)
            self.assertEqual(payload["state"], "diverged")
            self.assertTrue(payload["stop"])
            self.assertIn("Run next:", payload["ending"])
            self.assertIn("`git pull --no-rebase`", payload["ending"])

    def test_no_upstream_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_repo(Path(tmp) / "solo")
            (repo / "README.md").write_text("solo\n", encoding="utf-8")
            commit_all(repo, "Start")
            code, payload, err = run_py(SYNC, ["status", "--repo", str(repo)])
            self.assertEqual(code, 0, err)
            self.assertEqual(payload["state"], "no-upstream")
            self.assertTrue(payload["continue"])
            self.assertIn("no upstream", payload["message"])

    def test_settle_lists_written_and_leaves_foreign(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, _bare = pair_repos(Path(tmp))
            spec = write_slice(work)
            (spec / "verify.md").write_text(VERIFY + "\nupdated\n", encoding="utf-8")
            (spec / "notes-from-walk.md").write_text("note\n", encoding="utf-8")
            (work / "foreign.txt").write_text("leave me\n", encoding="utf-8")
            written = [
                str((spec / "verify.md").relative_to(work)),
                str((spec / "notes-from-walk.md").relative_to(work)),
            ]
            code, payload, err = run_py(SYNC, [
                "settle", "--repo", str(work),
                "--written", *written,
            ])
            self.assertEqual(code, 0, err)
            self.assertIn("docs/specs/orders-api/verify.md", payload["written"])
            self.assertIn("docs/specs/orders-api/notes-from-walk.md", payload["written"])
            self.assertIn("foreign.txt", payload["foreign"])
            self.assertTrue(payload["commit_needed"])

    def test_ahead_count_after_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, _bare = pair_repos(Path(tmp))
            spec = write_slice(work)
            (spec / "verify.md").write_text(VERIFY + "\nupdated\n", encoding="utf-8")
            rel = "docs/specs/orders-api/verify.md"
            code, payload, err = run_py(SYNC, [
                "commit", "--repo", str(work),
                "--written", rel,
                "--message", "Record the walk in the specs repo",
                "--yes",
            ])
            self.assertEqual(code, 0, err)
            self.assertTrue(payload["committed"])
            self.assertEqual(payload["ahead"], 1)
            self.assertIn("1 commit ahead", payload["waiting"])
            # foreign not involved
            status = git(work, "status", "--porcelain").stdout
            self.assertNotIn("verify.md", status)

    def test_behind_merge_then_conflict_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, bare = pair_repos(Path(tmp))
            (work / "shared.md").write_text("local\n", encoding="utf-8")
            commit_all(work, "Local shared")
            other = Path(tmp) / "other"
            subprocess.run(["git", "clone", str(bare), str(other)], check=True, capture_output=True)
            git(other, "config", "user.email", "person-a@example.com")
            git(other, "config", "user.name", "person A")
            git(other, "config", "commit.gpgsign", "false")
            (other / "shared.md").write_text("upstream\n", encoding="utf-8")
            commit_all(other, "Upstream shared")
            git(other, "push", "origin", "HEAD")
            code, payload, err = run_py(SYNC, ["merge-upstream", "--repo", str(work), "--yes"])
            self.assertNotEqual(code, 0, err)
            self.assertTrue(payload.get("conflict"))
            self.assertIn("shared.md", payload.get("files") or [])
            self.assertIn("Stopped", payload["line"])

    def test_behind_merges_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, bare = pair_repos(Path(tmp))
            other = Path(tmp) / "other"
            subprocess.run(["git", "clone", str(bare), str(other)], check=True, capture_output=True)
            git(other, "config", "user.email", "person-a@example.com")
            git(other, "config", "user.name", "person A")
            git(other, "config", "commit.gpgsign", "false")
            (other / "extra.md").write_text("upstream\n", encoding="utf-8")
            commit_all(other, "Upstream ahead")
            git(other, "push", "origin", "HEAD")
            code, payload, err = run_py(SYNC, ["merge-upstream", "--repo", str(work), "--yes"])
            self.assertEqual(code, 0, err)
            self.assertTrue(payload["merged"])
            self.assertTrue((work / "extra.md").is_file())

    def test_headless_push_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, _bare = pair_repos(Path(tmp))
            code, payload, _ = run_py(SYNC, ["push", "--repo", str(work), "--headless"])
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["code"], "headless")
            self.assertIn("yes", payload["line"])

    def test_no_repo_is_silent_continue(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, payload, err = run_py(SYNC, ["status", "--repo", tmp])
            self.assertEqual(code, 0, err)
            self.assertEqual(payload["state"], "no-repo")
            self.assertTrue(payload["continue"])
            self.assertIsNone(payload.get("ending"))


class ReadinessSyncTests(unittest.TestCase):
    def test_readiness_stops_when_behind(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, bare = pair_repos(Path(tmp))
            spec = write_slice(work)
            commit_all(work, "Add the slice")
            git(work, "push", "origin", "HEAD")
            other = Path(tmp) / "other"
            subprocess.run(["git", "clone", str(bare), str(other)], check=True, capture_output=True)
            git(other, "config", "user.email", "person-a@example.com")
            git(other, "config", "user.name", "person A")
            git(other, "config", "commit.gpgsign", "false")
            (other / "extra.md").write_text("upstream\n", encoding="utf-8")
            commit_all(other, "Upstream ahead")
            git(other, "push", "origin", "HEAD")
            code, payload, err = run_py(WALK, ["readiness", "--full", "--root", str(spec)])
            self.assertEqual(payload.get("sync", {}).get("state"), "behind", err + json.dumps(payload)[:800])
            self.assertTrue(payload.get("stop"))
            self.assertIn("git pull --no-rebase", payload.get("ending") or "")
            self.assertEqual(payload.get("can_start") or [], [])
            # does not write the map when stopped
            self.assertFalse((spec / "build-map.md").exists())


if __name__ == "__main__":
    unittest.main()
