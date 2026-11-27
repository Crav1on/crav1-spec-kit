"""1.177.2: the ready check asks each waiting PR's own host whether it
merged (read-only), records a merged PR as a merge-pr result so its tasks
are done in the same run, says when a PR was closed without merging or its
code repo is not recorded, records the code repo with `code-repo`, and says
whether --write-map changed the map."""

from __future__ import annotations

import contextlib
import io
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
import test_review_batch_1176b as rb  # noqa: E402

wp = rb.wp
pc = wp.pr_common_mod()
ADO_REPO = "https://dev.azure.com/contoso/Orders/_git/orders-api"
REPOS = ("# Repos\n\n| Repo | Role | Merges into | URL |\n| --- | --- | --- | --- |\n"
         f"| orders-api | code | develop | {ADO_REPO} |\n"
         "| orders-web | code | main | https://github.com/contoso/orders-web |\n")
SHA = "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"


def specs_repo(tmp: str, repos: str | None = REPOS) -> Path:
    """<tmp>/docs/specs/orders with PR 71 (yours) and PR 82 (person B's)."""
    (Path(tmp) / "docs").mkdir()
    root = rb.two_pr_slice(str(Path(tmp) / "docs"))
    if repos:
        (Path(tmp) / "docs/system").mkdir()
        (Path(tmp) / "docs/system/repos.md").write_text(repos, encoding="utf-8")
    return root


def ready(root: Path, *extra: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        wp.main(["readiness", "--root", str(root), "--skip-sync", "--text", *extra])
    return buf.getvalue()


def ready_json(root: Path) -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        wp.main(["readiness", "--root", str(root), "--skip-sync", "--full"])
    return json.loads(buf.getvalue())


def readme_log(root: Path) -> str:
    return (root / "build-progress/feat--orders-readme.md").read_text(encoding="utf-8")


def host(states: dict, url_of=None):
    """Mock the PR's host: resolve says where, host_state says what."""
    def ref(_root, pr):
        return {"status": "ok", "host": "azure", "number": int(pr), "url": f"{ADO_REPO}/pullrequest/{pr}"}

    def state(info, _repo=None, timeout=None):
        return states.get(info["number"])
    return contextlib.ExitStack(), ref, state


def lookup_of(state):
    """host_lookup (1.179.0) from a host_state stand-in: a missing state is a host that timed out."""
    def lookup(info, _repo=None, timeout=None):
        got = state(info, _repo)
        return {"ok": got, "error": None if got else "timeout", "detail": "" if got else "no answer within 20 s"}
    return lookup


@contextlib.contextmanager
def fake_host(states: dict):
    _stack, ref, state = host(states)
    env = {k: v for k, v in os.environ.items() if k != "CRAV1_NO_HOST_LOOKUP"}
    with mock.patch.dict(os.environ, env, clear=True), \
            mock.patch.object(wp, "host_pr_ref", side_effect=ref), \
            mock.patch.object(pc, "host_lookup", side_effect=lookup_of(state)), \
            mock.patch.object(pc, "host_author", return_value=None):
        yield


class HostState(unittest.TestCase):
    def run_with(self, host_name: str, payload, code: int = 0):
        proc = subprocess.CompletedProcess([], code, json.dumps(payload), "")
        tool = "gh" if host_name == "github" else "az"
        with mock.patch.object(pc.shutil, "which", return_value=f"/usr/bin/{tool}"), \
                mock.patch.object(pc.subprocess, "run", return_value=proc) as run:
            url = ("https://github.com/contoso/orders-web/pull/82" if host_name == "github"
                   else f"{ADO_REPO}/pullrequest/82")
            out = pc.host_state({"host": host_name, "number": 82, "url": url})
        return out, run.call_args[0][0]

    def test_github_merged_and_closed(self):
        out, cmd = self.run_with("github", {"state": "MERGED", "mergeCommit": {"oid": SHA},
                                            "mergedAt": "2026-11-14T10:00:00Z"})
        self.assertEqual(out, {"state": "merged", "sha": SHA, "date": "2026-11-14"})
        self.assertEqual(cmd[0], "/usr/bin/gh", "the full CLI path, never the bare name (1.179.0)")
        self.assertEqual(cmd[1:3], ["pr", "view"])
        self.assertIn("contoso/orders-web", cmd)
        out, _ = self.run_with("github", {"state": "CLOSED", "mergeCommit": None, "closedAt": "2026-11-13T09:00:00Z"})
        self.assertEqual(out["state"], "closed")

    def test_azure_completed_and_abandoned(self):
        out, cmd = self.run_with("azure", {"status": "completed", "sha": SHA, "closed": "2026-11-14T10:00:00Z"})
        self.assertEqual(out, {"state": "merged", "sha": SHA, "date": "2026-11-14"})
        self.assertEqual(cmd[0], "/usr/bin/az", "the full CLI path, never the bare name (1.179.0)")
        self.assertEqual(cmd[1:4], ["repos", "pr", "show"])
        self.assertEqual(cmd[cmd.index("--detect") + 1], "false")
        self.assertIn("https://dev.azure.com/contoso", cmd)
        out, _ = self.run_with("azure", {"status": "abandoned", "sha": None, "closed": "2026-11-13T09:00:00Z"})
        self.assertEqual(out["state"], "closed")
        out, _ = self.run_with("azure", {"status": "active", "sha": None, "closed": None})
        self.assertEqual(out["state"], "open")

    def test_unreadable_host_is_none(self):
        with mock.patch.object(pc.shutil, "which", return_value=None):
            self.assertIsNone(pc.host_state({"host": "azure", "number": 82}))
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/gh"), \
                mock.patch.object(pc.subprocess, "run", side_effect=subprocess.TimeoutExpired("gh", 8)):
            self.assertIsNone(pc.host_state({"host": "github", "number": 82}))
        out, _ = self.run_with("azure", {}, code=1)
        self.assertIsNone(out)

    def test_pr_common_stays_read_only(self):
        self.assertNotIn("write_text", Path(pc.__file__).read_text(encoding="utf-8"))


class MergedOnHost(unittest.TestCase):
    def test_merged_pr_ticks_tasks_and_leaves_the_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = specs_repo(tmp)
            with fake_host({71: {"state": "merged", "sha": SHA, "date": "2026-11-14"}}):
                text = ready(root, "--write-map")
            log = readme_log(root)
            self.assertIn(f"- Step: merge-pr\n  Done: ", log)
            self.assertIn(f"Result: merged (PR 71, merge commit {SHA}, merged on host 2026-11-14)", log)
            self.assertNotIn("T5 Orders README — waits for PR 71", text)
            self.assertNotIn("1. PR 71", text)
            self.assertIn("1. PR 82 (person B's, feat/orders-cicd)", text)
            self.assertNotIn("Merge your PR 71", text)
            self.assertIn("Ask the PR owners to merge, in this order:\n- person B: PR 82", text)
            rows = {row["task"]: row for row in wp.build_rows(root) if row.get("task")}
            self.assertEqual(rows["T5"]["bucket"], "done")
            self.assertNotEqual(rows["T6"]["bucket"], "waiting")
            build_map = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertIn("~~Orders README (T5)~~ ✓ done", build_map)
            self.assertEqual(wp.map_mod().progress_shas(root).get(5), SHA[:12])
            self.assertIn("Build map: docs/specs/orders/build-map.md (updated)", text)
            # The next run finds nothing new: no second merge result, map unchanged.
            with fake_host({71: {"state": "merged", "sha": SHA, "date": "2026-11-14"}}):
                again = ready(root, "--write-map")
            self.assertEqual(readme_log(root).count("- Step: merge-pr"), 1)
            self.assertIn("Build map: docs/specs/orders/build-map.md (unchanged, nothing new since the last write)", again)

    def test_github_merge_without_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = specs_repo(tmp)
            with fake_host({82: {"state": "merged", "sha": None, "date": "2026-11-15"}}):
                out = ready_json(root)
            self.assertEqual(out["pr_state"]["merged"], [82])
            log = (root / "build-progress/feat--orders-cicd.md").read_text(encoding="utf-8")
            self.assertIn("Result: merged (PR 82, merged on host 2026-11-15)", log)
            self.assertNotIn("PR 82 (person B's", out["ending"])
            self.assertIn("- feat/orders-cicd: merged", "\n".join(wp.branch_run_lines(root, include_merged=True)))


class ClosedAndUnreadable(unittest.TestCase):
    def test_closed_without_merging(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = specs_repo(tmp)
            before = readme_log(root)
            with fake_host({71: {"state": "closed", "sha": None, "date": "2026-11-13"}}):
                text = ready(root)
            self.assertIn("Waiting: PR 71 was closed without merging; its tasks are not done.", text)
            self.assertNotIn("1. PR 71", text)
            self.assertEqual(readme_log(root), before)
            rows = {row["task"]: row for row in wp.build_rows(root) if row.get("task")}
            self.assertNotEqual(rows["T5"]["bucket"], "done")

    def test_unreadable_host_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = specs_repo(tmp)
            with mock.patch.dict(os.environ, {"CRAV1_NO_HOST_LOOKUP": "1"}):
                baseline = ready(root)
            before = readme_log(root)
            with fake_host({}):
                text = ready(root)
            # 1.179.0: nothing is recorded, and Catch up first says why the
            # host was not read instead of staying silent.
            self.assertNotIn("Azure DevOps was not reached", baseline)
            self.assertIn("Azure DevOps was not reached for PR 71 and PR 82: it did not answer within 20 s.", text)
            self.assertEqual(readme_log(root), before)
            self.assertIn("1. PR 71 (yours, feat/orders-readme)", text)


class CodeRepoUnknown(unittest.TestCase):
    def test_marker_then_code_repo_then_lookups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = specs_repo(tmp)
            env = {k: v for k, v in os.environ.items() if k != "CRAV1_NO_HOST_LOOKUP"}
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(pc, "host_author", return_value=None):
                out = ready_json(root)
            self.assertEqual(out["pr_state"]["unhosted"], [71, 82])
            self.assertEqual([item["pr"] for item in out["code_repo_unknown"]], [71, 82])
            self.assertIn("Waiting: PR 71 and PR 82: code repo not recorded, so the host was not asked whether they merged.",
                          out["ending"])
            choices = subprocess.run([sys.executable, str(rb.WALK), "code-repo", "--root", str(root), "--pr", "71"],
                                     capture_output=True, text=True, check=False)
            self.assertEqual([c["name"] for c in json.loads(choices.stdout)["choices"]], ["orders-api", "orders-web"])
            proc = subprocess.run([sys.executable, str(rb.WALK), "code-repo", "--root", str(root), "--pr", "71",
                                   "--repo", "orders-api"], capture_output=True, text=True, check=False)
            self.assertEqual(json.loads(proc.stdout)["status"], "recorded", proc.stderr)
            self.assertIn(f"PR author: person A\nCode repo: {ADO_REPO}\n", readme_log(root))
            # resolve, from the repo root, now finds PR 71 on Azure DevOps.
            res = subprocess.run([sys.executable, str(Path(pc.__file__)), "resolve", "--ref", "pr71", "--root", tmp,
                                  "--remote-url", "https://github.com/contoso/specs.git"],
                                 capture_output=True, text=True, check=False)
            res = json.loads(res.stdout)
            self.assertEqual((res["status"], res["host"], res["url"]), ("ok", "azure", f"{ADO_REPO}/pullrequest/71"))
            # The owner lookup uses it.
            log = readme_log(root).replace("PR author: person A\n", "")
            (root / "build-progress/feat--orders-readme.md").write_text(log, encoding="utf-8")
            named = {"ok": {"state": "open", "sha": None, "date": None, "author": "person C"}, "error": None, "detail": ""}
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(pc, "host_lookup", return_value=named) as author:
                self.assertEqual(wp.host_pr_author(root, 71), "person C")
            self.assertEqual(author.call_args[0][0]["url"], f"{ADO_REPO}/pullrequest/71")
            # And the state lookup: merged on the host ticks T5 in the same run.
            done = subprocess.CompletedProcess([], 0, json.dumps({"status": "completed", "sha": SHA,
                                                                   "closed": "2026-11-14T10:00:00Z"}), "")
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(pc.shutil, "which", return_value="/usr/bin/az"), \
                    mock.patch.object(pc.subprocess, "run", return_value=done), \
                    mock.patch.object(pc, "host_author", return_value=None):
                out = ready_json(root)
            self.assertEqual(out["pr_state"]["merged"], [71])
            self.assertEqual(out["pr_state"]["unhosted"], [82])
            self.assertNotIn("1. PR 71", out["ending"])
            self.assertIn("PR 82: code repo not recorded", out["ending"])

    def test_unknown_repo_name_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = specs_repo(tmp)
            proc = subprocess.run([sys.executable, str(rb.WALK), "code-repo", "--root", str(root), "--pr", "71",
                                   "--repo", "billing-api"], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(json.loads(proc.stdout)["status"], "unknown-repo")
            self.assertNotIn("Code repo:", readme_log(root))


if __name__ == "__main__":
    unittest.main()
