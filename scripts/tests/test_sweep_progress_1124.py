"""1.124.0: sweep progress is the state machine for the linked-repo sweep.

Scope leaves out proposed rows, rows with no URL, and the specs repo.
The specs repo's branches are never items. A failed fetch skips that repo.
The budget defaults to 20 minutes and will not go past 45. Auto flow cannot
record a spec write. The ending keeps the commit on Uncommitted.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / ".cursor/skills/crav1/crav1-update-specs-from-changes-and-prs/scripts/sweep_progress.py"
)
WHEN = "2026-11-10T10:00:00+00:00"
MID = "2026-11-10T10:19:00+00:00"
STOP = "2026-11-10T10:20:00+00:00"
SPECS = "https://github.com/example/orders-specs"
REPOS = """# Repos

| Repo | Purpose | Status | URL | Merges into | Work items go to |
| --- | --- | --- | --- | --- | --- |
| orders-api | API | active | https://github.com/example/orders-api.git | develop | |
| orders-web | Web | active | https://github.com/example/orders-web | main | |
| orders-specs | Specs | active | https://github.com/example/orders-specs | main | |
| billing | Later | proposed | | | |
| catalog | Later | active | | | |
| future | Later | proposed | https://github.com/example/future | main | |
| trunk-api | API | active | https://dev.azure.com/Example/Shop/_git/trunk-api | trunk | |
"""


def run(root: Path, args: list[str]) -> tuple[int, dict]:
    env = os.environ.copy()
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.pop("PYTHONPYCACHEPREFIX", None)
    command, rest = args[0], args[1:]
    if command != "read-line":
        rest = ["--root", str(root), *rest]
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), command, *rest],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"stdout": proc.stdout, "stderr": proc.stderr}
    if proc.returncode not in {0, 1, 2, 3}:
        raise AssertionError(proc.stderr or proc.stdout)
    if proc.returncode != 0 and "error" not in payload:
        payload = {"stdout": proc.stdout, "stderr": proc.stderr, **payload}
    return proc.returncode, payload


def make_root(repos: str = REPOS) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    folder = root / "docs" / "system"
    folder.mkdir(parents=True)
    (folder / "repos.md").write_text(repos, encoding="utf-8")
    return tmp


class SweepProgress(unittest.TestCase):
    def setUp(self):
        self.tmp = make_root()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, *args: str) -> dict:
        code, payload = run(self.root, list(args))
        self.assertEqual(code, 0, payload)
        return payload

    def start(self, *extra: str) -> dict:
        return self.call(
            "start",
            "--flow",
            "manual-flow",
            "--specs-url",
            SPECS,
            "--when",
            WHEN,
            "--yes",
            *extra,
        )

    def fetch(self, repo: str, result: str = "ok", **kwargs: str) -> dict:
        args = ["note-fetch", "--repo", repo, "--result", result, "--when", WHEN, "--yes"]
        if "open" in kwargs:
            args += ["--open", kwargs["open"]]
        if "detail" in kwargs:
            args += ["--detail", kwargs["detail"]]
        return self.call(*args)

    def progress(self) -> str:
        return (self.root / "docs" / "system" / "sweep-progress.md").read_text(encoding="utf-8")

    def test_scope_excludes_proposed_rows_without_a_url_and_the_specs_repo(self):
        payload = self.call("scope", "--specs-url", "https://GitHub.com/example/orders-specs.git")
        names = [row["name"] for row in payload["repos"]]
        self.assertEqual(names, ["orders-api", "orders-web", "trunk-api"])
        reasons = {row["name"]: row["reason"] for row in payload["out"]}
        self.assertEqual(reasons["billing"], "proposed")
        self.assertEqual(reasons["catalog"], "no url")
        self.assertEqual(reasons["future"], "proposed")
        self.assertEqual(payload["specs_repo"]["name"], "orders-specs")
        self.assertFalse(payload["specs_repo"]["included"])
        self.assertFalse(payload["specs_repo"]["branches"])
        api = next(row for row in payload["repos"] if row["name"] == "orders-api")
        self.assertEqual(api["host"], "github")
        self.assertTrue(api["branches"])
        trunk = next(row for row in payload["repos"] if row["name"] == "trunk-api")
        self.assertEqual(trunk["host"], "azure")
        self.assertEqual(trunk["merges_into"], "trunk")

    def test_azure_url_matches_the_visualstudio_form(self):
        payload = self.call(
            "scope",
            "--specs-url",
            "https://example.visualstudio.com/Shop/_git/trunk-api",
            "--repo",
            "trunk-api",
        )
        self.assertEqual(payload["specs_repo"]["name"], "trunk-api")
        self.assertTrue(payload["specs_repo"]["included"])
        self.assertFalse(payload["repos"][0]["branches"])
        self.assertTrue(payload["repos"][0]["comments"])

    def test_named_repo_narrows_and_a_missing_name_fails(self):
        payload = self.call("scope", "--specs-url", SPECS, "--repo", "orders-web")
        self.assertEqual([row["name"] for row in payload["repos"]], ["orders-web"])
        code, payload = run(self.root, ["scope", "--specs-url", SPECS, "--repo", "nope"])
        self.assertEqual(code, 1)
        self.assertEqual(payload["error"], "unknown-repo")

    def test_specs_repo_branch_is_refused_and_a_pull_request_is_allowed(self):
        self.call(
            "start",
            "--flow",
            "manual-flow",
            "--specs-url",
            SPECS,
            "--include-specs-comments",
            "yes",
            "--when",
            WHEN,
            "--yes",
        )
        self.fetch("orders-specs")
        code, payload = run(
            self.root,
            [
                "add-item",
                "--kind",
                "branch",
                "--repo",
                "orders-specs",
                "--ref",
                "feat/kit-docs",
                "--yes",
            ],
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["error"], "specs-branches")
        added = self.call(
            "add-item", "--kind", "pr", "--repo", "orders-specs", "--ref", "12", "--draft", "--yes"
        )
        self.assertIn("pr orders-specs 12 all", added["command"])
        self.assertNotIn("review-pr", added["command"])

    def test_auto_flow_refuses_to_pull_the_specs_repo_in_with_a_flag(self):
        code, payload = run(
            self.root,
            [
                "start",
                "--flow",
                "auto-flow",
                "--specs-url",
                SPECS,
                "--include-specs-comments",
                "yes",
                "--when",
                WHEN,
                "--yes",
            ],
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["error"], "auto-specs-out")
        self.assertFalse((self.root / "docs" / "system" / "sweep-progress.md").exists())

    def test_base_branches_are_rejected(self):
        self.start()
        self.fetch("orders-api")
        for ref in ("main", "master", "develop", "release/1.2"):
            code, payload = run(
                self.root,
                ["add-item", "--kind", "branch", "--repo", "orders-api", "--ref", ref, "--yes"],
            )
            self.assertEqual(payload["error"], "base-branch", ref)
            self.assertEqual(code, 1)
        self.fetch("trunk-api")
        code, payload = run(
            self.root,
            ["add-item", "--kind", "branch", "--repo", "trunk-api", "--ref", "trunk", "--yes"],
        )
        self.assertEqual(payload["error"], "base-branch")

    def test_failed_fetch_skips_the_repo_and_lists_waiting(self):
        self.start()
        self.fetch("orders-web", "failed", detail="login expired")
        code, payload = run(
            self.root,
            ["add-item", "--kind", "branch", "--repo", "orders-web", "--ref", "feat/orders-ui", "--yes"],
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["error"], "fetch-failed")
        ending = self.call("ending", "--files", "1")
        self.assertEqual(
            ending["waiting"],
            ["Waiting: orders-web, because fetch failed (login expired)."],
        )
        self.assertNotIn("finalize-commit", ending["next"])
        self.assertIn("/crav1-finalize-commit", ending["uncommitted"])

    def test_signed_out_allows_a_branch_and_blocks_a_pull_request(self):
        self.start()
        self.fetch("orders-api", "signed-out")
        added = self.call(
            "add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-retry", "--yes"
        )
        self.assertFalse(added["duplicate"])
        code, payload = run(
            self.root,
            ["add-item", "--kind", "pr", "--repo", "orders-api", "--ref", "71", "--yes"],
        )
        self.assertEqual(payload["error"], "signed-out")
        self.assertEqual(code, 1)

    def test_first_sweep_has_no_closed_since_list(self):
        self.start()
        self.fetch("orders-api", open="71,74")
        code, payload = run(
            self.root,
            [
                "add-item",
                "--kind",
                "pr",
                "--repo",
                "orders-api",
                "--ref",
                "70",
                "--closed-since",
                "--yes",
            ],
        )
        self.assertEqual(payload["error"], "no-earlier-sweep")
        self.assertEqual(code, 1)

    def test_a_pull_request_covers_its_head_branch(self):
        self.start()
        self.fetch("orders-api", open="71")
        self.call(
            "add-item",
            "--kind",
            "branch",
            "--repo",
            "orders-api",
            "--ref",
            "feat/orders-retry",
            "--yes",
        )
        self.call(
            "add-item",
            "--kind",
            "pr",
            "--repo",
            "orders-api",
            "--ref",
            "71",
            "--head-branch",
            "feat/orders-retry",
            "--draft",
            "--yes",
        )
        text = self.progress()
        self.assertIn("| dropped |", text)
        self.assertIn("reason: covered by pr 71", text)
        code, payload = run(
            self.root,
            [
                "add-item",
                "--kind",
                "branch",
                "--repo",
                "orders-api",
                "--ref",
                "feat/orders-retry",
                "--yes",
            ],
        )
        self.assertEqual(payload["error"], "covered-by-pr")
        self.assertEqual(code, 1)

    def test_resume_does_not_redo_a_done_item(self):
        self.start()
        self.fetch("orders-api")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-retry", "--yes")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-audit", "--yes")
        ident = "orders-api/branch/feat/orders-audit"
        self.call("begin-item", "--id", ident, "--now", MID, "--yes")
        self.call("complete", "--id", ident, "--outcome", "notes+synced-at", "--now", MID, "--yes")
        again = self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-audit", "--yes")
        self.assertTrue(again["duplicate"])
        self.assertEqual(again["status"], "done")
        resumed = self.call(
            "start",
            "--flow",
            "manual-flow",
            "--specs-url",
            SPECS,
            "--when",
            "2026-11-10T11:00:00+00:00",
            "--yes",
        )
        self.assertTrue(resumed["resumed"])
        self.assertEqual(resumed["next_item"]["id"], "orders-api/branch/feat/orders-retry")
        self.assertEqual(resumed["counts"]["done"], 1)
        self.assertIn("Started: 2026-11-10T11:00:00+00:00", self.progress())

    def test_drop_and_sorted_ids(self):
        self.start()
        self.fetch("orders-api")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/z", "--yes")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/a", "--yes")
        self.call("drop", "--id", "orders-api/branch/feat/z", "--yes")
        text = self.progress()
        self.assertLess(text.index("feat/a"), text.index("feat/z"))
        resumed = self.call("resume", "--now", MID)
        self.assertEqual(resumed["next_item"]["ref"], "feat/a")
        self.assertEqual(resumed["counts"]["dropped"], 1)

    def test_budget_defaults_to_20_and_clamps_at_45(self):
        payload = self.start()
        self.assertEqual(payload["budget_minutes"], 20)
        self.assertFalse(payload["clamped"])
        self.call("finish", "--yes")
        payload = self.call(
            "start",
            "--flow",
            "manual-flow",
            "--specs-url",
            SPECS,
            "--budget",
            "90",
            "--when",
            WHEN,
            "--yes",
        )
        self.assertTrue(payload["clamped"])
        self.assertEqual(payload["budget_minutes"], 45)
        self.assertIn("Hard stop minutes: 45", self.progress())

    def test_budget_stops_a_new_item_and_lets_the_current_one_finish(self):
        self.start()
        self.fetch("orders-api")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-retry", "--yes")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-audit", "--yes")
        current = "orders-api/branch/feat/orders-audit"
        self.call("begin-item", "--id", current, "--now", MID, "--yes")
        code, payload = run(
            self.root,
            ["begin-item", "--id", "orders-api/branch/feat/orders-retry", "--now", STOP, "--yes"],
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["error"], "item-open")
        done = self.call("complete", "--id", current, "--outcome", "synced-at", "--now", STOP, "--yes")
        self.assertTrue(done["stop"])
        code, payload = run(
            self.root,
            ["begin-item", "--id", "orders-api/branch/feat/orders-retry", "--now", STOP, "--yes"],
        )
        self.assertEqual(code, 3)
        self.assertEqual(payload["error"], "budget")
        self.call("pause", "--yes")
        ending = self.call("ending", "--files", "2")
        self.assertIn("manual-flow, because 1 item is still pending", ending["next"])
        self.assertNotIn("finalize-commit", ending["next"])
        self.assertIn("2 files", ending["uncommitted"])

    def test_auto_flow_cannot_record_a_spec_write(self):
        self.call(
            "start",
            "--flow",
            "auto-flow",
            "--specs-url",
            SPECS,
            "--repo",
            "orders-api",
            "--when",
            WHEN,
            "--yes",
        )
        self.fetch("orders-api")
        self.call(
            "add-item",
            "--kind",
            "pr",
            "--repo",
            "orders-api",
            "--ref",
            "74",
            "--head-branch",
            "feat/orders-retry",
            "--yes",
        )
        ident = "orders-api/pr/74"
        self.call("begin-item", "--id", ident, "--now", MID, "--yes")
        code, payload = run(
            self.root,
            ["complete", "--id", ident, "--outcome", "spec", "--yes"],
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["error"], "auto-no-spec")
        self.call(
            "complete",
            "--id",
            ident,
            "--outcome",
            "proposal",
            "--slug",
            "orders-retry",
            "--proposal",
            "The retry window moves from 20 s to 30 s.",
            "--now",
            MID,
            "--yes",
        )
        ending = self.call("ending", "--files", "1")
        self.assertEqual(
            ending["proposals"],
            ["orders-api pr 74 on orders-retry: The retry window moves from 20 s to 30 s."],
        )
        self.assertIn("manual-flow orders-api, because 1 spec change is still a proposal", ending["next"])
        self.assertNotIn("finalize-commit", ending["next"])

    def test_a_written_question_points_next_at_resolve(self):
        self.start()
        self.fetch("orders-api")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-retry", "--yes")
        ident = "orders-api/branch/feat/orders-retry"
        self.call("begin-item", "--id", ident, "--now", MID, "--yes")
        self.call(
            "complete",
            "--id",
            ident,
            "--outcome",
            "spec",
            "--slug",
            "orders-export,orders-retry",
            "--conflict",
            "--now",
            MID,
            "--yes",
        )
        ending = self.call("ending", "--files", "0")
        self.assertEqual(
            ending["next"],
            "Next: /crav1-resolve-open-questions orders-export, orders-retry, because this sweep left a conflict or an open question unsettled.",
        )
        self.assertIsNone(ending["uncommitted"])

    def test_read_line_and_needs_yes(self):
        code, payload = run(
            self.root,
            [
                "read-line",
                "--head",
                "7b41a0c",
                "--push",
                "6",
                "--comment-time",
                "2026-10-26T15:03Z",
                "--date",
                "2026-10-27",
            ],
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            payload["line"],
            "- Read: sweep | 7b41a0c, push 6, newest comment 2026-10-26T15:03Z | 2026-10-27",
        )
        self.start()
        before = self.progress()
        code, payload = run(
            self.root,
            ["note-fetch", "--repo", "orders-api", "--result", "ok", "--when", WHEN],
        )
        self.assertEqual(code, 2)
        self.assertEqual(payload["error"], "needs-yes")
        self.assertEqual(self.progress(), before)

    def test_a_finished_run_keeps_the_open_list_for_the_next_sweep(self):
        self.start()
        self.fetch("orders-api", open="74,71")
        self.call("finish", "--yes")
        self.call(
            "start",
            "--flow",
            "manual-flow",
            "--specs-url",
            SPECS,
            "--when",
            "2026-11-10T12:00:00+00:00",
            "--yes",
        )
        text = self.progress()
        self.assertIn("## Last sweep", text)
        self.assertIn(f"Inventory at: {WHEN}", text.split("## Last sweep", 1)[1])
        self.assertIn("- orders-api | open 71,74", text)
        self.fetch("orders-api", open="74")
        added = self.call(
            "add-item",
            "--kind",
            "pr",
            "--repo",
            "orders-api",
            "--ref",
            "71",
            "--closed-since",
            "--yes",
        )
        self.assertEqual(added["status"], "pending")

    def test_a_different_scope_does_not_wipe_the_queue_until_replace(self):
        self.start()
        self.fetch("orders-api")
        self.call("add-item", "--kind", "branch", "--repo", "orders-api", "--ref", "feat/orders-retry", "--yes")
        code, payload = run(
            self.root,
            [
                "start",
                "--flow",
                "auto-flow",
                "--repo",
                "orders-web",
                "--specs-url",
                SPECS,
                "--when",
                MID,
                "--yes",
            ],
        )
        self.assertEqual(payload["error"], "scope-differs")
        self.assertEqual(code, 1)
        self.assertIn("feat/orders-retry", self.progress())
        replaced = self.call(
            "start",
            "--flow",
            "auto-flow",
            "--repo",
            "orders-web",
            "--specs-url",
            SPECS,
            "--when",
            MID,
            "--replace",
            "--yes",
        )
        self.assertFalse(replaced["resumed"])
        self.assertNotIn("feat/orders-retry", self.progress())
        self.assertIn("Flow: auto-flow", self.progress())

    def test_rate_limit_is_waiting_and_the_run_can_continue(self):
        self.start()
        self.fetch("orders-api", open="71,74")
        self.call("add-item", "--kind", "pr", "--repo", "orders-api", "--ref", "71", "--yes")
        self.call("add-item", "--kind", "pr", "--repo", "orders-api", "--ref", "74", "--yes")
        self.call("begin-item", "--id", "orders-api/pr/71", "--now", MID, "--yes")
        self.call(
            "skip",
            "--id",
            "orders-api/pr/71",
            "--reason",
            "host rate limit on pr 71",
            "--waiting",
            "--now",
            MID,
            "--yes",
        )
        resumed = self.call("resume", "--now", MID)
        self.assertEqual(resumed["next_item"]["ref"], "74")
        self.assertIn("rate limit", resumed["waiting"][0])

    def test_written_lines_match_the_marks(self):
        import yaml

        marks = yaml.safe_load((ROOT / "docs/reference/marks.yaml").read_text(encoding="utf-8"))["marks"]
        patterns = {mark["id"]: re.compile(mark["pattern"]) for mark in marks}
        self.start()
        self.fetch("orders-web", "missing", detail="no checkout found")
        self.fetch("orders-api", open="71")
        self.call(
            "add-item",
            "--kind",
            "pr",
            "--repo",
            "orders-api",
            "--ref",
            "71",
            "--draft",
            "--head-branch",
            "feat/orders-retry",
            "--yes",
        )
        ident = "orders-api/pr/71"
        self.call("begin-item", "--id", ident, "--now", MID, "--yes")
        self.call(
            "complete",
            "--id",
            ident,
            "--outcome",
            "proposal",
            "--slug",
            "orders-retry",
            "--proposal",
            "The retry window moves from 20 s to 30 s.",
            "--now",
            MID,
            "--yes",
        )
        text = self.progress()
        item = next(line for line in text.splitlines() if line.startswith("- orders-api/pr/71"))
        proposal = next(line for line in text.splitlines() if line.startswith("- orders-api pr 71"))
        waiting = next(line for line in text.splitlines() if "| no checkout |" in line)
        self.assertRegex(item, patterns["sweep-item"])
        self.assertRegex(proposal, patterns["sweep-proposal"])
        self.assertRegex(waiting, patterns["sweep-waiting"])
        code, payload = run(
            self.root,
            ["read-line", "--head", "7b41a0c", "--push", "6", "--comment-time", "none", "--date", "2026-10-27"],
        )
        self.assertRegex(payload["line"], patterns["read-sweep"])
        self.assertEqual(code, 0)

    def test_running_the_script_writes_no_pycache(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            script_dir = base / "scripts"
            script_dir.mkdir()
            target = script_dir / "sweep_progress.py"
            target.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
            env = os.environ.copy()
            env.pop("PYTHONDONTWRITEBYTECODE", None)
            env.pop("PYTHONPYCACHEPREFIX", None)
            proc = subprocess.run(
                [sys.executable, str(target), "read-line", "--head", "abc", "--push", "1", "--comment-time", "none", "--date", "2026-11-10"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(proc.returncode, 0)
            found = [path for path in base.rglob("*") if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}]
            self.assertEqual(found, [])


class SweepRouting(unittest.TestCase):
    def test_skill_routes_one_flow_at_a_time(self):
        skill = (
            ROOT
            / ".cursor/skills/crav1/crav1-update-specs-from-changes-and-prs/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("references/manual-flow.md", skill)
        self.assertIn("references/auto-flow.md", skill)
        self.assertIn("Do not open `references/auto-flow.md`", skill)
        self.assertIn("Do not open `references/manual-flow.md`", skill)
        self.assertIn("run-ending.md", skill)
        description = skill.split("---", 2)[1]
        words = description.split()
        self.assertLessEqual(len(words), 60)
        body = skill.split("---", 2)[2]
        self.assertLess(len(body.split()), 2000)
        common = (
            ROOT
            / ".cursor/skills/crav1/crav1-update-specs-from-changes-and-prs/references/common.md"
        ).read_text(encoding="utf-8")
        self.assertIn("- Read: sweep |", common)
        self.assertIn("does not run", skill.lower() + common.lower())
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("DEFAULT_BUDGET_MINUTES = 20", script)
        self.assertIn("HARD_STOP_MINUTES = 45", script)
        self.assertIn("sys.dont_write_bytecode = True", script)


if __name__ == "__main__":
    unittest.main()
