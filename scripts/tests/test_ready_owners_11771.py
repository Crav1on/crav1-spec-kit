"""1.177.1: the ready check keeps PR waits in the merge list only, asks the
PR's own host who opened it (and records the answer), asks the PR owners to
merge when none of the listed PRs is yours, and resolve finds number-only
records from the repo root without falling back to another host."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import test_pr_ref_resolve_1177 as t77  # noqa: E402

rb = t77.rb
wp = t77.wp
we = t77.we
pc = t77.pc
PC_PATH = t77.PR_COMMON


def strip_author(root: Path) -> Path:
    log = root / "build-progress/feat--orders-readme.md"
    log.write_text(log.read_text(encoding="utf-8").replace("PR author: person A\n", ""), encoding="utf-8")
    return root


class NoDuplicateWaiting(unittest.TestCase):
    def test_merge_list_is_the_only_pr_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = rb.ending(rb.two_pr_slice(tmp))
            self.assertIn("Merge these PRs, in this order:", text)
            self.assertNotIn("Waiting: PR", text)
            self.assertNotIn("it unblocks", text)


class AskOwnersToMerge(unittest.TestCase):
    def test_entry_groups_owners_in_list_order(self):
        order = [{"pr": 82, "owner": "person B"}, {"pr": 71, "owner": "person A"},
                 {"pr": 73, "owner": "person A"}, {"pr": 75, "owner": "owner not recorded"}]
        self.assertEqual(wp.ask_owners_entry(order),
                         "Ask the PR owners to merge, in this order:\n- person B: PR 82\n"
                         "- person A: PR 71 and PR 73\n- PR 75 (owner not recorded)")

    def test_none_when_one_is_yours_or_empty(self):
        self.assertIsNone(wp.ask_owners_entry([{"pr": 71, "owner": "yours"}, {"pr": 82, "owner": "person B"}]))
        self.assertIsNone(wp.ask_owners_entry([]))

    def test_nudge_leads_resume(self):
        entry = wp.ask_owners_entry([{"pr": 82, "owner": "person B"}])
        text = we.compose(run=[entry, t77.RESUME])
        self.assertLess(text.index("Ask the PR owners to merge"), text.index("Resume the walk when the answers arrive:"))
        self.assertNotIn("Next:", text.replace("Run next:", ""))

    def test_ready_check_asks_when_none_is_yours(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = rb.ending(strip_author(rb.two_pr_slice(tmp)))
            entry = "Ask the PR owners to merge, in this order:\n- PR 71 (owner not recorded)\n- person B: PR 82"
            self.assertIn(entry, text)
            self.assertLess(text.index(entry), text.index("Held:"))
            self.assertNotIn("Merge your PR", text)

    def test_your_own_pr_still_leads(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = rb.ending(rb.two_pr_slice(tmp))
            self.assertIn("Merge your PR 71 first:", text)
            self.assertNotIn("Ask the PR owners", text)


class OwnerFromHost(unittest.TestCase):
    def test_host_author_github_and_azure(self):
        gh = subprocess.CompletedProcess([], 0, json.dumps({"author": {"login": "personb", "name": "person B"}}), "")
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/gh"), \
                mock.patch.object(pc.subprocess, "run", return_value=gh) as run:
            self.assertEqual(pc.host_author({"host": "github", "number": 82, "url": t77.GH_PR}), "person B")
            self.assertEqual(run.call_args[0][0][:3], ["/usr/bin/gh", "pr", "view"])
        az = subprocess.CompletedProcess([], 0, json.dumps("person A"), "")
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/az"), \
                mock.patch.object(pc.subprocess, "run", return_value=az) as run:
            self.assertEqual(pc.host_author({"host": "azure", "number": 82, "url": t77.ADO_PR}), "person A")
            self.assertIn("createdBy.displayName", run.call_args[0][0])

    def test_missing_cli_or_failure_is_none(self):
        with mock.patch.object(pc.shutil, "which", return_value=None):
            self.assertIsNone(pc.host_author({"host": "azure", "number": 82}))
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/gh"), \
                mock.patch.object(pc.subprocess, "run", side_effect=subprocess.TimeoutExpired("gh", 8)):
            self.assertIsNone(pc.host_author({"host": "github", "number": 82}))
        self.assertIsNone(pc.host_author({"host": "other", "number": 82}))

    def test_found_author_is_recorded_and_owns_the_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = strip_author(rb.two_pr_slice(tmp))
            info = {"status": "ok", "host": "azure", "number": 71, "url": t77.ADO_PR.replace("/82", "/71")}
            fake = mock.Mock(return_value=info)
            with mock.patch.object(wp.pr_common_mod(), "resolve_ref", fake), \
                    mock.patch.object(wp.pr_common_mod(), "host_lookup", return_value={
                        "ok": {"state": "open", "sha": None, "date": None, "author": "person C"},
                        "error": None, "detail": ""}), \
                    mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CRAV1_NO_HOST_LOOKUP", None)
                prs = wp.open_prs(root)
            self.assertEqual(prs[71]["owner"], "person C")
            log = (root / "build-progress/feat--orders-readme.md").read_text(encoding="utf-8")
            self.assertIn("Owner: self\nPR author: person C\n", log)
            self.assertEqual(wp.pr_author(root, 71, log), "person C")

    def test_pr_common_stays_read_only(self):
        self.assertNotIn("write_text", PC_PATH.read_text(encoding="utf-8"))

    def test_fallback_keeps_owner_not_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = strip_author(rb.two_pr_slice(tmp))
            with mock.patch.object(wp.pr_common_mod(), "host_author", return_value=None):
                self.assertEqual(wp.open_prs(root)[71]["owner"], "owner not recorded")

    def test_author_command_records_the_users_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = strip_author(rb.two_pr_slice(tmp))
            proc = subprocess.run([sys.executable, str(t77.WALK), "pr-author", "--root", str(root), "--pr", "71",
                                   "--name", "person D"], capture_output=True, text=True, check=False)
            self.assertEqual(json.loads(proc.stdout)["status"], "recorded")
            self.assertEqual(wp.pr_author(root, 71, (root / "build-progress/feat--orders-readme.md").read_text()), "person D")
            again = subprocess.run([sys.executable, str(t77.WALK), "pr-author", "--root", str(root), "--pr", "71",
                                    "--name", "person E"], capture_output=True, text=True, check=False)
            self.assertEqual(json.loads(again.stdout)["status"], "recorded")
            text = (root / "build-progress/feat--orders-readme.md").read_text()
            self.assertEqual(text.count("PR author:"), 1)
            self.assertIn("PR author: person E", text)


REPOS = ("# Repos\n\n| Repo | Role | Merges into | URL |\n| --- | --- | --- | --- |\n"
         "| orders-api | code | develop | https://dev.azure.com/contoso/Orders/_git/orders-api |\n")
PROGRESS = ("# Build progress\n\nWalk: build-walk\nBranch: feat/orders-cicd\nOwner: person B\n"
            "Tasks: T9 Queue\n\n- Step: open-pr\n  Result: built, PR 82 open\n")


def number_only(tmp: str, repos: str | None) -> Path:
    root = Path(tmp)
    slug = root / "docs/specs/orders-retry"
    (slug / "build-progress").mkdir(parents=True)
    (slug / "build-progress/feat--orders-cicd.md").write_text(PROGRESS, encoding="utf-8")
    if repos:
        (root / "docs/system").mkdir(parents=True)
        (root / "docs/system/repos.md").write_text(repos, encoding="utf-8")
    return root


class ResolveFromRepoRoot(unittest.TestCase):
    def run_resolve(self, root: Path, where: Path) -> dict:
        proc = subprocess.run([sys.executable, str(PC_PATH), "resolve", "--ref", "pr82", "--root", str(where),
                               "--remote-url", t77.GH_REMOTE], capture_output=True, text=True, check=False)
        return json.loads(proc.stdout)

    def test_number_only_record_and_repos_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = number_only(tmp, REPOS)
            for where in (root, root / "docs/specs", root / "docs/specs/orders-retry"):
                out = self.run_resolve(root, where)
                self.assertEqual((out["status"], out["source"], out["host"], out["tool"]),
                                 ("ok", "records", "azure", "az"), where)
                self.assertEqual(out["url"], t77.ADO_PR)

    def test_code_repo_line_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = number_only(tmp, None)
            log = root / "docs/specs/orders-retry/build-progress/feat--orders-cicd.md"
            log.write_text(PROGRESS.replace("Owner: person B\n", "Owner: person B\nCode repo: https://dev.azure.com/contoso/Orders/_git/orders-api\n"), encoding="utf-8")
            out = self.run_resolve(root, root)
            self.assertEqual((out["status"], out["url"]), ("ok", t77.ADO_PR))

    def test_number_only_with_no_host_asks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = number_only(tmp, None)
            out = self.run_resolve(root, root)
            self.assertEqual(out["status"], "ask")
            self.assertIn("PR 82 is in build-progress for feat/orders-cicd, but its host isn't recorded", out["line"])
            self.assertNotIn("github.com", json.dumps(out))
            self.assertIsNone(out["tool"])


if __name__ == "__main__":
    unittest.main()
