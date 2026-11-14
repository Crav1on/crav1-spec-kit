"""1.155.0: build a whole branch in one walk."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/branch_run.py"
CLAIMS = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/claims.py"
TASK_ORDER = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


br = load(RUN, "branch_run_test")
claims = load(CLAIMS, "claims_test_1155")

SPEC = """# Spec

The receipt lists the order id.

## Approval needed

- Stop the prod function app
  - Person: person B
  - Holds: T6

## Open questions

- Which retry count should the export use?
  - Blocks: T4
"""

PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Build the pipeline. (T1, T2, T3, T4, T5, T6, T7)

## Risks
"""

TASKS = """# Tasks

- [x] T1: Persist the decision (branch: feat/orders-cicd) (after: )
- [ ] T3: Add the test stage (branch: feat/orders-cicd) (after: T2)
- [ ] T2: Add the build pipeline (branch: feat/orders-cicd) (after: T1)
- [ ] T5: Publish the artifact (branch: feat/orders-cicd) (after: T3)
- [ ] T7: Switch dev to the new pipeline (branch: feat/orders-dev-switch) (after: T5)
"""


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check)


def write_slice(base: Path, tasks: str = TASKS, spec: str = SPEC) -> Path:
    root = base / "docs" / "specs" / "orders-api"
    root.mkdir(parents=True, exist_ok=True)
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    return root


def cli(*args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(RUN), *args], capture_output=True, text=True, check=False)
    return proc.returncode, json.loads(proc.stdout or "{}")


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        write_slice(self.base)
        self.specs = self.base / "docs" / "specs"

    def test_task_stays_one_task(self):
        out = br.parse_args(["orders-api", "T5"], self.specs)
        self.assertEqual(out["mode"], "task")
        self.assertEqual(out["tasks"], ["T5"])
        self.assertEqual(out["slug"], "orders-api")

    def test_branch_argument(self):
        out = br.parse_args(["orders-api", "feat/orders-cicd"], self.specs)
        self.assertEqual(out["mode"], "branch")
        self.assertEqual(out["branch"], "feat/orders-cicd")

    def test_chain_is_reserved_not_offered(self):
        out = br.parse_args(["orders-api", "chain", "pipeline"], self.specs)
        self.assertFalse(out["ok"])
        self.assertEqual(out["code"], "chain")

    def test_branch_and_task_together_is_refused(self):
        out = br.parse_args(["feat/orders-cicd", "T5"], self.specs)
        self.assertFalse(out["ok"])


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.root = write_slice(self.base)

    def test_open_tasks_in_task_order(self):
        plan = br.branch_plan(self.root, "feat/orders-cicd")
        self.assertTrue(plan["ok"])
        self.assertEqual(plan["open"], ["T2", "T3", "T5"])
        self.assertEqual(plan["done"], ["T1"])

    def test_unknown_branch(self):
        plan = br.branch_plan(self.root, "feat/orders-nothing")
        self.assertFalse(plan["ok"])
        self.assertEqual(plan["code"], "branch")


class StopTests(unittest.TestCase):
    def _plan(self, extra_line: str, spec: str = SPEC):
        base = Path(tempfile.mkdtemp())
        root = write_slice(base, TASKS + extra_line + "\n", spec)
        plan = br.branch_plan(root, "feat/orders-cicd", "person A")
        return {row["id"]: row["stop"] for row in plan["tasks"]}

    def test_open_question_stops(self):
        stops = self._plan("- [ ] T4: Retry the export (branch: feat/orders-cicd) (after: T3)")
        self.assertEqual(stops["T4"]["kind"], "question")

    def test_missing_stakeholder_yes_stops(self):
        stops = self._plan("- [ ] T6: Stop the prod app (branch: feat/orders-cicd) (after: T5)")
        self.assertEqual(stops["T6"]["kind"], "approval")
        self.assertIn("person B", stops["T6"]["line"])

    def test_recorded_yes_does_not_stop(self):
        spec = SPEC.replace(
            "  - Holds: T6\n",
            '  - Holds: T6\n  - Approved: person B, 2026-11-12, chat, "yes" (accepted by person A 2026-11-12)\n',
        )
        stops = self._plan("- [ ] T6: Stop the prod app (branch: feat/orders-cicd) (after: T5)", spec)
        self.assertIsNone(stops["T6"])

    def test_manual_secret_and_live_stop(self):
        for mark in ("(manual, secret)", "(host setup)", "(Runs live)"):
            stops = self._plan(f"- [ ] T8: Set the key {mark} (branch: feat/orders-cicd) (after: T5)")
            self.assertEqual(stops["T8"]["kind"], "manual", mark)

    def test_tests_red_after_fair_try_stops(self):
        keep = br.after({"task": "T2", "next": "T3", "tests": "red", "attempts": 1})
        self.assertFalse(keep["stop"])
        self.assertEqual(keep["action"], "fix")
        stop = br.after({"task": "T2", "next": "T3", "tests": "red", "attempts": 3})
        self.assertTrue(stop["stop"])
        self.assertEqual(stop["kind"], "tests")

    def test_out_of_scope_stops(self):
        out = br.after({"task": "T2", "next": "T3", "tests": "green", "out_of_scope": "rename the shared logger"})
        self.assertTrue(out["stop"])
        self.assertEqual(out["kind"], "scope")

    def test_always_stops_before_merge(self):
        out = br.after({"task": "T5", "next": None, "tests": "green"})
        self.assertTrue(out["stop"])
        self.assertEqual(out["kind"], "merge")

    def test_next_task_stop_is_reported(self):
        out = br.after({"task": "T3", "next": "T4", "tests": "green",
                        "next_stop": {"kind": "question", "line": "T4 has an open question"}})
        self.assertTrue(out["stop"])
        self.assertEqual(out["task"], "T4")

    def test_keep_going_prints_one_progress_line(self):
        out = br.after({"task": "T9", "next": "T10", "tests": "green", "done_in_session": 1})
        self.assertFalse(out["stop"])
        self.assertEqual(out["line"], "T9 done, tests green, starting T10")

    def test_fresh_session_hint_is_soft(self):
        cmd = "/crav1-build-walk orders-api feat/orders-cicd"
        out = br.after({"task": "T5", "next": "T6", "tests": "green", "done_in_session": 3, "command": cmd})
        self.assertFalse(out["stop"])
        self.assertIn("fresh session", out["line"])
        self.assertIn(cmd, out["line"])
        two = br.after({"task": "T5", "next": "T6", "tests": "green", "done_in_session": 2, "hint_every": 2})
        self.assertIn("fresh session", two["line"])
        one = br.after({"task": "T5", "next": "T6", "tests": "green", "done_in_session": 1, "hint_every": 2})
        self.assertIsNone(one["hint"])


class ClaimAndResumeTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.root = write_slice(self.base)

    def test_start_without_yes_writes_nothing(self):
        out = br.start(self.root, "feat/orders-cicd", "person A", yes=False)
        self.assertFalse(out["wrote"])
        self.assertFalse((self.root / "claims.md").exists())
        self.assertEqual(out["card"]["words"], ["yes", "stop"])

    def test_one_claim_line_names_every_open_task(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        text = (self.root / "claims.md").read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.startswith("In progress:")]
        self.assertEqual(len(lines), 1)
        self.assertRegex(lines[0], r"^In progress: feat/orders-cicd, T2, T3, T5, person A, since \S+$")

    def test_branch_claim_reads_as_1151_claim(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        parsed = claims.parse_claims((self.root / "claims.md").read_text(encoding="utf-8"))
        self.assertEqual(parsed["claims"][0]["tasks"], ["T2", "T3", "T5"])
        self.assertEqual(parsed["notes"], [])
        rendered = claims.render_claims(parsed["claims"])
        self.assertEqual(claims.parse_claims(rendered)["claims"][0]["tasks"], ["T2", "T3", "T5"])

    def test_ready_check_shows_all_claimed_tasks_in_progress(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        proc = subprocess.run([sys.executable, str(TASK_ORDER), str(self.root), "--json"],
                              capture_output=True, text=True, check=False)
        data = json.loads(proc.stdout)
        held = {row["id"] if isinstance(row["id"], str) else f"T{row['id']}" for row in data.get("waiting_in_progress", [])}
        self.assertTrue({"T2", "T3", "T5"} <= held, data)

    def test_resume_reuses_claim_and_repeats_nothing(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        before = (self.root / "claims.md").read_text(encoding="utf-8")
        br.record(self.root, "feat/orders-cicd", "T2", "a1b2c3d4e5f6", "green")
        again = br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        self.assertTrue(again["resume"])
        self.assertEqual(again["claim"], "reuse")
        self.assertIsNone(again["card"])
        self.assertEqual(again["next_task"], "T3")
        self.assertEqual(again["built"], ["T2"])
        self.assertEqual((self.root / "claims.md").read_text(encoding="utf-8"), before)

    def test_someone_elses_claim_stops_start(self):
        claims.add_claim(self.root, "feat/orders-cicd", ["T3"], "person B")
        out = br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        self.assertFalse(out["ok"])
        self.assertEqual(out["code"], "claimed")
        self.assertIn("person B", out["line"])

    def test_guard_stops_on_new_claim_by_someone_else(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        path = self.root / "claims.md"
        path.write_text(path.read_text(encoding="utf-8").replace(", T5,", ",") +
                        "In progress: feat/orders-other, T5, person B, since 2026-11-13T10:00:00+01:00\n",
                        encoding="utf-8")
        out = br.guard(self.root, "feat/orders-cicd", "person A")
        self.assertTrue(out["stop"])
        self.assertEqual(out["kind"], "claimed")
        self.assertEqual(out["who"], "person B")

    def test_guard_stops_on_changed_task_and_ignores_ticks(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        tasks = self.root / "tasks.md"
        ticked = tasks.read_text(encoding="utf-8").replace("- [ ] T2:", "- [x] T2:").replace(
            "Add the build pipeline (branch", "Add the build pipeline (PR 12) (branch")
        tasks.write_text(ticked, encoding="utf-8")
        self.assertFalse(br.guard(self.root, "feat/orders-cicd", "person A")["stop"])
        tasks.write_text(ticked.replace("Publish the artifact", "Publish the signed artifact"), encoding="utf-8")
        out = br.guard(self.root, "feat/orders-cicd", "person A")
        self.assertTrue(out["stop"])
        self.assertEqual(out["kind"], "changed")
        self.assertEqual(out["task"], "T5")


class PushPerTaskTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        bare = self.base / "remote.git"
        subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)], check=True, capture_output=True)
        self.repo = self.base / "work"
        subprocess.run(["git", "clone", str(bare), str(self.repo)], check=True, capture_output=True)
        for key, value in (("user.email", "person-a@example.com"), ("user.name", "person A"), ("commit.gpgsign", "false")):
            git(self.repo, "config", key, value)
        self.root = write_slice(self.repo)
        git(self.repo, "checkout", "-b", "feat/orders-cicd")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-m", "Start")
        self.bare = bare

    def test_record_without_run_yes_never_pushes(self):
        out = br.record(self.root, "feat/orders-cicd", "T2", "a1b2c3d", "green", self.repo, push=True)
        self.assertFalse(out["ok"])
        listed = subprocess.run(["git", "--git-dir", str(self.bare), "branch"], capture_output=True, text=True)
        self.assertNotIn("feat/orders-cicd", listed.stdout)

    def test_each_task_is_pushed_without_a_card(self):
        br.start(self.root, "feat/orders-cicd", "person A", yes=True)
        for task in ("T2", "T3"):
            (self.repo / f"{task}.txt").write_text(task, encoding="utf-8")
            git(self.repo, "add", f"{task}.txt")
            git(self.repo, "commit", "-m", f"Build {task}")
            sha = git(self.repo, "rev-parse", "HEAD").stdout.strip()
            out = br.record(self.root, "feat/orders-cicd", task, sha, "green", self.repo, push=True)
            self.assertTrue(out["ok"], out)
            self.assertTrue(out["pushed"], out)
            remote = subprocess.run(["git", "--git-dir", str(self.bare), "rev-parse", "feat/orders-cicd"],
                                    capture_output=True, text=True).stdout.strip()
            self.assertEqual(remote, git(self.repo, "rev-parse", "HEAD").stdout.strip())
        run = br.load_run(self.root, "feat/orders-cicd")
        self.assertEqual([row["task"] for row in run["built"]], ["T2", "T3"])
        self.assertEqual(run["next"], "T5")


class EndingTests(unittest.TestCase):
    def test_merge_stop_order(self):
        out = br.ending({
            "slug": "orders-api", "branch": "feat/orders-cicd", "pr": 12, "base": "develop",
            "built": [{"task": "T2", "title": "Add the build pipeline", "commit": "a1b2c3d4e5f6", "tests": "green"},
                      {"task": "T3", "commit": "b2c3d4e5f6a1", "tests": "green"}],
            "skipped": [{"task": "T4", "why": "open question on the retry count"}],
            "verify_behind": ["T2 is still Not implemented"],
            "ready_branches": [{"branch": "feat/orders-dev-switch", "tasks": ["T7"]}],
        })
        text = out["ending"]
        self.assertTrue(text.startswith("Run next:"))
        self.assertLess(text.index("Run next:"), text.index("Built on"))
        self.assertLess(text.index("Built on"), text.index("Left:"))
        self.assertIn("\n`/crav1-build-walk orders-api feat/orders-cicd`\nmerge PR 12 into develop", text)
        self.assertIn("\n`/crav1-build-walk orders-api feat/orders-dev-switch`\n", text)
        self.assertIn("- T2 Add the build pipeline: commit a1b2c3d, tests green", text)
        self.assertIn("- Skipped T4: open question", text)
        self.assertFalse(out["merges"])
        for line in text.splitlines():
            if line.startswith("`"):
                self.assertRegex(line, r"^`[^`]+`$")

    def test_no_pr_offers_open_pr(self):
        out = br.ending({"branch": "feat/orders-cicd", "built": []})
        self.assertIn("`/crav1-open-pr`", out["ending"])

    def test_mid_run_stop_offers_the_same_command(self):
        out = br.ending({"slug": "orders-api", "branch": "feat/orders-cicd",
                         "stop": {"kind": "tests", "line": "T3 tests or lint are still red after 3 tries"}})
        self.assertIn("`/crav1-build-walk orders-api feat/orders-cicd`", out["ending"])
        self.assertIn("- Stopped: T3 tests", out["ending"])


class CliTests(unittest.TestCase):
    def test_cli_parse_and_after(self):
        base = Path(tempfile.mkdtemp())
        write_slice(base)
        code, out = cli("parse", "--root", str(base / "docs" / "specs"), "--args", "orders-api feat/orders-cicd")
        self.assertEqual(code, 0)
        self.assertEqual(out["mode"], "branch")
        state = base / "after.json"
        state.write_text(json.dumps({"task": "T9", "next": "T10", "tests": "green"}), encoding="utf-8")
        code, out = cli("after", "--json", str(state))
        self.assertEqual(out["line"], "T9 done, tests green, starting T10")


if __name__ == "__main__":
    unittest.main()
