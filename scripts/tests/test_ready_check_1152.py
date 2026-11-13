"""1.152.0: ready-check fixes for merged-branch detection, script paths, titles, and output."""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
CHECK = ROOT / "scripts" / "check-script-invocations.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "build_map_1152")
to = load(SK / "crav1-tasks-ready-to-build/scripts/task_order.py", "task_order_1152")
qb = load(SK / "crav1-tasks-ready-to-build/scripts/question_blocks.py", "question_blocks_1152")
an = load(SK / "crav1-record-approval/scripts/approval_needed.py", "approval_needed_1152")
check = load(CHECK, "check_script_invocations_1152")

SPEC = """# Orders

## Open questions

- Which channel is used for the receipt?
  - Blocks: none
"""

PLAN = """# Plan

## Approach

1. Add the host setup. (T1, T8, T43)
2. Switch the runner. (T28)

## Risks

- None for this slice.
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


def run_script(path, args, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(path), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )
    return proc


class MergedBranchDetection(unittest.TestCase):
    def test_future_acceptance_wording_is_not_a_recorded_merge(self):
        line = "Take in develop on feat/orders-api-host-setup (PR 12) to be merged into develop"
        self.assertFalse(bm._pr_merged_line(line))
        self.assertFalse(to.pr_merged(line))
        self.assertTrue(to.pr_merged("export the receipt (PR 78, merged)"))
        self.assertTrue(to.pr_merged("export the receipt (PR 78) merged"))

    def test_git_not_merged_keeps_the_task_line_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "orders-api"
            init_repo(repo)
            git(repo, "checkout", "-b", "feat/orders-api-host-setup")
            (repo / "host.md").write_text("host\n", encoding="utf-8")
            git(repo, "add", "host.md")
            git(repo, "commit", "-m", "host")
            git(repo, "checkout", "main")
            # A later open task mentions a future merge of this PR, and a
            # person's name, which must not invent a branch or skip the real one.
            tasks = (
                "- [x] T1: Land the first cut (PR 12) to be merged into develop "
                "(branch: feat/orders-api-host-setup)\n"
                "- [ ] T8: Take develop into PR 12, then it is merged into develop "
                "(branch: feat/orders-api-host-setup) (after: )\n"
                "- [ ] T43: Jordan Ellis writes the incoming tests that follow the code "
                "on feat/orders-api-host-setup (PR 12) (after: )\n"
            )
            offer = bm.recommendation("orders-api", SPEC, PLAN, tasks, 43, repo=repo)
            self.assertEqual(offer["name"], "feat/orders-api-host-setup")
            self.assertEqual(offer["source"], "task line")
            self.assertIsNone(offer["because"])
            self.assertNotIn("jordan", offer["name"])
            self.assertNotIn("ellis", offer["name"])
            eight = bm.recommendation("orders-api", SPEC, PLAN, tasks, 8, repo=repo)
            self.assertEqual(eight["name"], "feat/orders-api-host-setup")

    def test_git_proved_merge_still_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "orders-api"
            init_repo(repo)
            git(repo, "checkout", "-b", "feat/orders-one-commit-cleanup-main")
            (repo / "cleanup.md").write_text("cleanup\n", encoding="utf-8")
            git(repo, "add", "cleanup.md")
            git(repo, "commit", "-m", "cleanup")
            git(repo, "checkout", "main")
            git(repo, "merge", "--no-ff", "-m", "merge cleanup", "feat/orders-one-commit-cleanup-main")
            tasks = "- [ ] T1: Clean the commit on feat/orders-one-commit-cleanup-main from main\n"
            plan = "# Plan\n\n## Approach\n\n1. One commit cleanup on main. (T1)\n"
            offer = bm.recommendation("orders", SPEC, plan, tasks, 1, repo=repo)
            self.assertNotEqual(offer["name"], "feat/orders-one-commit-cleanup-main")
            self.assertEqual(offer["source"], "new")
            self.assertIn("feat/orders-one-commit-cleanup-main is already merged", offer["because"])

    def test_offline_keeps_the_task_line_branch(self):
        tasks = "- [ ] T43: Add the incoming tests on feat/orders-api-host-setup from develop\n"
        offer = bm.recommendation("orders-api", SPEC, PLAN, tasks, 43)
        self.assertEqual(offer["name"], "feat/orders-api-host-setup")
        self.assertEqual(offer["source"], "task line")
        self.assertIsNone(offer["because"])
        recorded = "- [ ] T43: Add the incoming tests on feat/orders-api-host-setup (PR 12, merged)\n"
        checked = bm.recommendation("orders-api", SPEC, PLAN, recorded, 43)
        self.assertEqual(checked["name"], "feat/orders-api-host-setup")
        self.assertIn("could not check whether feat/orders-api-host-setup is merged", checked["because"])

    def test_fallback_name_drops_person_names_and_stays_short(self):
        name = bm._fresh_name(
            "orders-api",
            "Jordan Ellis writes the incoming tests that follow the code and builds the PR",
            set(),
            set(),
            task_id=43,
        )
        self.assertNotIn("jordan", name)
        self.assertNotIn("ellis", name)
        self.assertTrue(name.startswith("feat/orders-api-"))
        self.assertLessEqual(len(name.split("-")), 8)


class ScriptPathsAndCli(unittest.TestCase):
    def test_wrappers_run_the_build_walk_script(self):
        wrapper = SK / "crav1-tasks-ready-to-build/scripts/repo_sync.py"
        proc = run_script(wrapper, ["-h"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("repo_sync.py", proc.stdout)

    def test_approval_needed_accepts_a_folder_and_errors_clearly(self):
        script = SK / "crav1-record-approval/scripts/approval_needed.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "spec.md").write_text("# Spec\n\n## Approval needed\n", encoding="utf-8")
            proc = run_script(script, [str(root)])
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertIn("items", payload)
            missing = run_script(script, [str(root / "missing")])
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("spec.md not found", missing.stdout)
            self.assertNotIn("PermissionError", missing.stdout + missing.stderr)
            self.assertNotIn("Traceback", missing.stdout + missing.stderr)

    def test_question_blocks_accepts_a_folder_and_exits_zero_when_questions_exist(self):
        script = SK / "crav1-tasks-ready-to-build/scripts/question_blocks.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "spec.md").write_text(
                "# Spec\n\n## Open questions\n\n- Which inbox?\n  - Blocks: T1\n",
                encoding="utf-8",
            )
            (root / "plan.md").write_text("# Plan\n\n## Risks\n", encoding="utf-8")
            (root / "tasks.md").write_text("- [ ] T1: Record the decision\n", encoding="utf-8")
            proc = run_script(script, [str(root)])
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["questions"])
            missing = run_script(script, [str(root / "nope")])
            self.assertEqual(missing.returncode, 2)
            self.assertIn("spec.md not found", missing.stdout)
            self.assertNotIn("Traceback", missing.stdout + missing.stderr)

    def test_task_order_accepts_a_folder(self):
        script = SK / "crav1-tasks-ready-to-build/scripts/task_order.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "tasks.md").write_text("- [ ] T1: Record the decision\n", encoding="utf-8")
            proc = run_script(script, [str(root)])
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("T1: Record the decision", proc.stdout)

    def test_documented_script_path_must_exist(self):
        problems = check._missing_script_paths(str(ROOT))
        self.assertEqual(problems, [])
        with tempfile.TemporaryDirectory() as tmp:
            kit = pathlib.Path(tmp)
            skill = kit / ".cursor" / "skills" / "crav1" / "crav1-demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "Run `<interpreter> -X utf8 scripts/repo_sync.py status --repo <specs-repo>`.\n",
                encoding="utf-8",
            )
            found = check._missing_script_paths(str(kit))
            self.assertTrue(any("repo_sync.py is missing from crav1-demo/scripts" in item for item in found))
            (skill / "SKILL.md").write_text(
                "Run `scripts/repo_sync.py status --repo <specs-repo>` (skill `crav1-build-walk`).\n",
                encoding="utf-8",
            )
            # The named skill is also missing in this kit, so it still fails.
            named = check._missing_script_paths(str(kit))
            self.assertTrue(named)
            other = kit / ".cursor" / "skills" / "crav1" / "crav1-build-walk" / "scripts"
            other.mkdir(parents=True)
            (other / "repo_sync.py").write_text("# ok\n", encoding="utf-8")
            self.assertEqual(check._missing_script_paths(str(kit)), [])


class TitlesAndOutput(unittest.TestCase):
    def test_blank_backtick_title_uses_readable_words(self):
        rest = "`feat/orders-api-host-setup` (after: T12) (step: 2)"
        self.assertEqual(bm.short_name(rest), "work")
        rest = "`GetDocuments` (branch: feat/orders-api-host-setup) (after: T12)"
        self.assertEqual(bm.short_name(rest), "GetDocuments")
        line = "- [ ] T28: `feat/orders-api-functions` (after: T12)\n"
        parsed = to.parse(line)
        self.assertEqual(parsed[0]["title"], "work")
        self.assertNotEqual(parsed[0]["title"].strip("`"), "")

    def test_short_name_cuts_at_a_word_boundary_with_ellipsis(self):
        rest = (
            "Check that metadata read from the incoming request is stored "
            "beside the receipt and kept for later audit"
        )
        name = bm.short_name(rest)
        self.assertTrue(name.endswith("..."))
        self.assertNotIn(" audi", name)  # not mid-word
        self.assertLessEqual(len(name), 83)
        full = bm.short_name(rest, trim=False)
        self.assertFalse(full.endswith("..."))
        self.assertIn("later audit", full)

    def test_next_lines_match_run_next(self):
        labels = ["T43 incoming tests that follow the code"]
        line = bm.ready_next_line(labels, "feat/orders-api-host-setup", slug="orders-api")
        self.assertTrue(line.startswith("`/crav1-build-walk orders-api T43`"))
        self.assertIn("\nbranch feat/orders-api-host-setup, T43 incoming tests that follow the code\n", line)
        self.assertIn("/crav1-build-tasks builds one task without the walk.", line)
        self.assertNotIn("Next: /crav1-build-walk T43", line)
        self.assertNotIn("because that work is on", line)

    def test_task_order_defaults_to_short_labels(self):
        script = SK / "crav1-tasks-ready-to-build/scripts/task_order.py"
        long_title = "Record the decision " + ("details " * 40) + "trailer-zzzend"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "tasks.md"
            path.write_text(f"- [ ] T1: {long_title}\n", encoding="utf-8")
            short = run_script(script, [str(path)])
            full = run_script(script, [str(path), "--full"])
        self.assertEqual(short.returncode, 0, short.stderr)
        self.assertEqual(full.returncode, 0, full.stderr)
        self.assertLess(len(short.stdout), len(full.stdout))
        self.assertIn("...", short.stdout)
        self.assertIn("trailer-zzzend", full.stdout)
        self.assertNotIn("trailer-zzzend", short.stdout.split("Order:", 1)[0])

    def test_map_summary_counts_only_ready_branches(self):
        plan = """# Plan

## Approach

1. Record the decision. (T1)
2. Send the receipt. (T2)
"""
        tasks = """# Tasks

- [ ] T1: Record the decision (after: ) (spec: decision)
- [ ] T2: Send the receipt (after: T1) (spec: receipt)
"""
        result = bm.build("orders-api", SPEC, plan, tasks)
        self.assertIn("Wave 1: 1 branch, 1 can start now", result["summary"])
        self.assertIn("Wave 2: 1 branch, 0 can start now", result["summary"])
        self.assertNotIn("Wave 2: 1 branch, 1 can start now", result["summary"])

    def test_claimed_branch_is_not_counted_as_can_start(self):
        plan = """# Plan

## Approach

1. Record the decision. (T1)
"""
        tasks = "- [ ] T1: Record the decision (after: ) (branch: feat/orders-api-record)\n"
        claims = "In progress: feat/orders-api-record, T1, person A, since 2026-11-13T15:50:00+01:00\n"
        result = bm.build("orders-api", SPEC, plan, tasks, claims_text=claims)
        self.assertIn("1 branch, 0 can start now", result["summary"])


class ClaimStopDocs(unittest.TestCase):
    def test_skill_text_clears_on_done_stop_not_a_mid_walk_pause(self):
        claims = (SK / "crav1-build-walk/references/claims.md").read_text(encoding="utf-8")
        skill = (SK / "crav1-build-walk/SKILL.md").read_text(encoding="utf-8")
        layout = (ROOT / "docs/concepts/data-layout.md").read_text(encoding="utf-8")
        glossary = (ROOT / "docs/concepts/glossary.md").read_text(encoding="utf-8")
        self.assertIn("the user says `stop` and is done with this walk", claims)
        self.assertIn("`release claim`", skill)
        self.assertIn("write nothing further", skill)
        self.assertIn("stop and is done with this walk", layout)
        self.assertIn("stop and is done with this walk", glossary)


if __name__ == "__main__":
    unittest.main()
