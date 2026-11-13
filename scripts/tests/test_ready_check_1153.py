"""1.153.0: task-line branch in the map, one Run next command, brief output, waiting counts, orphan verify rows."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BUILD_MAP = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load(BUILD_MAP, "build_map_1153")
wp = load(WALK, "walk_progress_1153")

SPEC = """# Orders

## Open questions

- Which currency for refunds? Waiting for person A.
  - Blocks: T25
- Does the partner need a specific certificate authority? Waiting for the partner.
  - Blocks: T34
- Who gets the expiry alert? Waiting for person B.
  - Blocks: T35
"""

PLAN = """# Plan

Reviewed: 2026-11-13, P# open: 0

## Approach

1. One commit cleanup on main, then merge main into develop. (T2, T4)
2. Incoming tests that follow the code. (T43)
3. Later work that waits. (T8, T25, T28, T34, T35)

## Risks
"""

TASKS = """# Tasks

Repo: orders-api.

Branches (each from the base named, never one shared `feat/<slug>` branch): `feat/orders-one-commit-cleanup-main` from `origin/main` (T2, PR 78, merged 2026-11-11); `chore/merge-main-into-develop` (T4); `feature/orders-api-fixes-and-openapi-doc` (T43, and T8 on that branch).

- [x] T2: One commit cleanup on feat/orders-one-commit-cleanup-main from origin/main (PR 78, merged)
- [ ] T4: Merge main into develop after feat/orders-one-commit-cleanup-main, on chore/merge-main-into-develop
- [x] T7: Land the first cut (PR 80, merged)
- [ ] T8: Take develop into the open PR (after: T4, T5)
- [ ] T43: Add the incoming tests that follow the code on feature/orders-api-fixes-and-openapi-doc (after: )
- [ ] T5: Write the READMEs (after: T4)
- [ ] T25: Trust the header only from the front end (after: T8)
- [ ] T28: Split the pipeline (after: T8)
- [ ] T34: Use a fixed hostname (after: T8)
- [ ] T35: Send the expiry alert (after: T8)
"""

VERIFY = """# Verify

## Tasks

| Id | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| T2 | Cleanup | Implemented, verified | pr 78 |
| T7 | First cut | Implemented, verified | pr 80 |
| T44 | HTTP 400 and no ACK for XML that cannot be parsed | Not implemented | |
"""


def git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc


def init_repo(repo):
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "person-a@contoso.example")
    git(repo, "config", "user.name", "Person A")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "readme.md").write_text("orders-api\n", encoding="utf-8")
    git(repo, "add", "readme.md")
    git(repo, "commit", "-m", "init")
    git(repo, "branch", "develop")


def write_slice(root, tasks=TASKS, spec=SPEC, plan=PLAN, verify=VERIFY):
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    if verify is not None:
        (root / "verify.md").write_text(verify, encoding="utf-8")


def record_resolve(root):
    must([
        "record", "--root", str(root), "--slice", "docs/specs/orders-api",
        "--step", "resolve-open-questions", "--result", "done", "--yes",
    ])


def run_walk(args, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(WALK), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )
    return proc


def must(args):
    proc = run_walk(args)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr + proc.stdout)
    return json.loads(proc.stdout)


class TaskLineBranchWinsInTheMap(unittest.TestCase):
    def test_paragraph_and_task_line_keep_an_open_task_off_a_merged_sibling(self):
        result = bm.build("orders-api", SPEC, PLAN, TASKS, verify_text=VERIFY)
        names = {task["id"]: branch["name"] for branch in result["branches"] for task in branch["tasks"]}
        self.assertEqual(names[2], "feat/orders-one-commit-cleanup-main")
        self.assertEqual(names[4], "chore/merge-main-into-develop")
        self.assertNotEqual(names[4], names[2])
        four = next(branch for branch in result["branches"] if 4 in branch["task_ids"])
        self.assertEqual(four["name"], "chore/merge-main-into-develop")
        # The own-branch row must not claim it was built on the merged cleanup branch.
        self.assertNotIn("built on feat/orders-one-commit-cleanup-main", four.get("note") or "")
        self.assertNotIn("Task text names chore/merge-main-into-develop", four.get("note") or "")

    def test_paragraph_wins_even_when_the_open_task_line_omits_its_branch(self):
        tasks = """# Tasks

Branches: `feat/orders-one-commit-cleanup-main` from `origin/main` (T2, PR 78, merged); `chore/merge-main-into-develop` (T4).

- [x] T2: One commit cleanup on feat/orders-one-commit-cleanup-main (PR 78, merged)
- [ ] T4: Merge main into develop after the cleanup on feat/orders-one-commit-cleanup-main
"""
        plan = "# Plan\n\n## Approach\n\n1. Cleanup, then merge main into develop. (T2, T4)\n"
        result = bm.build("orders-api", SPEC, plan, tasks)
        names = {task["id"]: branch["name"] for branch in result["branches"] for task in branch["tasks"]}
        self.assertEqual(names[4], "chore/merge-main-into-develop")
        self.assertEqual(names[2], "feat/orders-one-commit-cleanup-main")

    def test_git_proved_merge_uses_the_other_task_line_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "orders-api"
            init_repo(repo)
            git(repo, "checkout", "-b", "feat/orders-one-commit-cleanup-main")
            (repo / "cleanup.md").write_text("cleanup\n", encoding="utf-8")
            git(repo, "add", "cleanup.md")
            git(repo, "commit", "-m", "cleanup")
            git(repo, "checkout", "main")
            git(repo, "merge", "--no-ff", "-m", "merge cleanup", "feat/orders-one-commit-cleanup-main")
            result = bm.build("orders-api", SPEC, PLAN, TASKS, verify_text=VERIFY, repo=repo)
            names = {task["id"]: branch["name"] for branch in result["branches"] for task in branch["tasks"]}
            self.assertEqual(names[4], "chore/merge-main-into-develop")
            offer = bm.recommendation("orders-api", SPEC, PLAN, TASKS, 4, repo=repo)
            self.assertEqual(offer["name"], "chore/merge-main-into-develop")
            self.assertEqual(offer["source"], "task line")

    def test_held_lines_use_the_task_line_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            record_resolve(root)
            (root / "claims.md").write_text(
                "In progress: chore/merge-main-into-develop, T4, person A, since 2026-11-13T15:50:00+01:00\n",
                encoding="utf-8",
            )
            payload = must(["readiness", "--root", str(root), "--skip-sync"])
        held = "\n".join(payload["held_lines"])
        self.assertIn("`chore/merge-main-into-develop`", held)
        self.assertIn("T4", held)
        self.assertNotIn("`feat/orders-one-commit-cleanup-main`", held.split("T4")[0][-80:] if "T4" in held else held)
        # T4 must not be listed under the merged cleanup branch.
        for line in payload["held_lines"]:
            if "T4 " in line or line.endswith("T4") or "T4 Merge" in line or "T4 " in line:
                if "T4" in line:
                    if "chore/merge-main-into-develop" in line:
                        continue
                    self.assertNotIn("feat/orders-one-commit-cleanup-main", line)


class EndingCommandOnce(unittest.TestCase):
    def test_ending_contains_the_walk_command_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            record_resolve(root)
            # Claim T4 so only T43 can start; the bug was one ready task
            # printed in both Run next and a trailing Next: line.
            (root / "claims.md").write_text(
                "In progress: chore/merge-main-into-develop, T4, person A, since 2026-11-13T15:50:00+01:00\n",
                encoding="utf-8",
            )
            payload = must(["readiness", "--root", str(root), "--skip-sync"])
        ending = payload["ending"]
        self.assertTrue(ending.startswith("Run next:"), ending)
        self.assertEqual(payload["can_start"], ["T43"])
        self.assertEqual(ending.count("/crav1-build-walk"), 1)
        self.assertEqual(ending.count("`/crav1-build-walk"), 1)
        self.assertIn("/crav1-build-tasks builds one task without the walk.", ending)
        self.assertLess(ending.index("Run next:"), ending.index("/crav1-build-tasks builds one task"))
        self.assertNotIn("Next: /crav1-build-walk", ending)
        self.assertNotIn("/crav1-build-walk", payload["next"] or "")
        self.assertEqual(payload["next_lines"], ["/crav1-build-tasks builds one task without the walk."])
        # The alternative must not repeat the command.
        self.assertNotIn("/crav1-build-walk", "\n".join(payload["next_lines"]))


class BriefOutput(unittest.TestCase):
    def test_brief_is_under_8kb_for_a_45_task_slice(self):
        lines = ["# Tasks\n", "\n", "Branches: `feat/orders-api-host-setup` (T1).\n", "\n"]
        for i in range(1, 46):
            after = " (after: )" if i == 1 else f" (after: T{i - 1})"
            title = f"Step {i} records the decision and stores the receipt details for later audit " * 3
            lines.append(f"- [{'x' if i <= 3 else ' '}] T{i}: {title}{after}\n")
        tasks = "".join(lines)
        plan_bits = ["# Plan\n\nReviewed: 2026-11-13, P# open: 0\n\n## Approach\n\n"]
        plan_bits.append("1. Host setup. (T1)\n")
        for i in range(2, 46):
            plan_bits.append(f"{i}. Follow-on work {i}. (T{i})\n")
        plan = "".join(plan_bits)
        verify_rows = ["# Verify\n\n## Tasks\n\n| Id | Requirement | Status | Evidence |\n| --- | --- | --- | --- |\n"]
        for i in range(1, 4):
            verify_rows.append(f"| T{i} | Work {i} | Implemented, verified | sha |\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root, tasks=tasks, spec="# Orders\n\n## Open questions\n", plan=plan, verify="".join(verify_rows))
            record_resolve(root)
            brief = run_walk(["readiness", "--root", str(root), "--skip-sync", "--brief", "--write-map"])
            full = run_walk(["readiness", "--root", str(root), "--skip-sync"])
        self.assertEqual(brief.returncode, 0, brief.stderr + brief.stdout)
        self.assertEqual(full.returncode, 0, full.stderr + full.stdout)
        self.assertLess(len(brief.stdout.encode("utf-8")), 8000)
        payload = json.loads(brief.stdout)
        self.assertEqual(set(payload) >= {"ok", "result", "counts", "ending", "claim_warnings"}, True)
        self.assertNotIn("rows", payload)
        self.assertNotIn("gates", payload)
        self.assertIn("Ready", payload["counts"]["line"])
        self.assertIn("Done 3", payload["counts"]["line"])
        self.assertTrue(payload["ending"].startswith("Run next:"), payload["ending"][:200])
        # build_map default is the one-line path; --write-map on brief keeps that path.
        self.assertTrue(str(payload.get("build_map") or payload.get("build_map_wrote") or "").endswith("build-map.md"))

    def test_build_map_defaults_to_the_one_line_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            proc = subprocess.run(
                [sys.executable, str(BUILD_MAP), str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        lines = [line for line in proc.stdout.strip().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, proc.stdout)
        self.assertIn("build-map.md", lines[0])
        self.assertNotIn("# ", proc.stdout)


class WaitingLineCountsDirectHolds(unittest.TestCase):
    def test_waiting_line_counts_only_open_questions_not_dependents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            record_resolve(root)
            payload = must(["readiness", "--root", str(root), "--skip-sync"])
        line = payload["waiting_line"] or ""
        # T25, T34, T35 are direct question holds. T8, T28 and others wait on tasks.
        self.assertIn("3 tasks wait on open questions", line)
        self.assertIn("person A", line)
        self.assertIn("the partner", line)
        self.assertIn("person B", line)
        self.assertNotIn("36 tasks", line)
        self.assertNotIn("6 tasks wait on open questions", line)
        # Dependents are still held, just not in this count.
        self.assertGreaterEqual(len(payload["held"]), 3)


class OrphanVerifyRow(unittest.TestCase):
    def test_orphan_verify_row_gets_a_waiting_line_and_does_not_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            record_resolve(root)
            before = (root / "verify.md").read_text(encoding="utf-8")
            payload = must(["readiness", "--root", str(root), "--skip-sync"])
            after = (root / "verify.md").read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertIn("T44", payload.get("orphan_tasks") or [])
        self.assertIn("verify.md has a row for T44, which is not in tasks.md", payload.get("orphan_waiting") or "")
        self.assertIn("verify.md has a row for T44, which is not in tasks.md", payload["ending"])
        self.assertIn("/crav1-verify-build-against-spec", payload["orphan_waiting"])
        self.assertIn("/crav1-tighten-plan", payload["orphan_waiting"])


if __name__ == "__main__":
    unittest.main()
