"""1.179.0: the ready check reaches Azure DevOps on Windows (az.cmd by its
full path, no prompts, 20 s), says why when a host cannot be read instead of
asking who opened the PR, writes answers into the PR's own build-progress
file, and offers people, never `other` or a team, as owner choices."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import test_pr_state_11772 as ps  # noqa: E402

wp = ps.wp
pc = ps.pc
rb = ps.rb
SK = Path(__file__).resolve().parents[2] / ".cursor/skills/crav1"
ADO_PR = f"{ps.ADO_REPO}/pullrequest/71"
WIN_AZ = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.CMD"
REAL_RUN = subprocess.run


def proc(out="", err="", code=0):
    return subprocess.CompletedProcess([], code, out, err)


def no_lookup_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in ("CRAV1_NO_HOST_LOOKUP", "CRAV1_HOST_TIMEOUT")}


def ref(_root, pr):
    return {"status": "ok", "host": "azure", "number": int(pr), "url": f"{ps.ADO_REPO}/pullrequest/{pr}"}


def strip_author(root: Path, name: str = "feat--orders-readme.md") -> Path:
    log = root / "build-progress" / name
    log.write_text(re.sub(r"(?m)^(PR author|Opened by):.*\n", "", log.read_text(encoding="utf-8")), encoding="utf-8")
    return root


class WindowsAz(unittest.TestCase):
    info = {"host": "azure", "number": 71, "url": ADO_PR}

    def test_full_path_from_which_is_run(self):
        seen = []

        def run(cmd, *a, **k):
            seen.append((list(cmd), k))
            if cmd[0] == "az":
                raise FileNotFoundError(2, "The system cannot find the file specified")
            return proc(json.dumps({"status": "completed", "sha": ps.SHA, "closed": "2026-11-14T10:00:00Z",
                                    "author": "Person A"}))
        which = lambda name: WIN_AZ if name in ("az", "az.cmd") else None  # noqa: E731
        with mock.patch.object(pc.shutil, "which", side_effect=which), \
                mock.patch.object(pc.subprocess, "run", side_effect=run):
            got = pc.host_lookup(self.info)
            self.assertEqual(pc.host_author(self.info), "Person A")
        self.assertEqual(got["error"], None)
        self.assertEqual(got["ok"]["state"], "merged")
        self.assertEqual(got["ok"]["author"], "Person A")
        self.assertTrue(all(cmd[0] == WIN_AZ for cmd, _k in seen), "never the bare name")

    def test_cmd_found_when_only_az_cmd_is_on_path(self):
        which = lambda name: WIN_AZ if name == "az.cmd" else None  # noqa: E731
        with mock.patch.object(pc.shutil, "which", side_effect=which):
            self.assertEqual(pc._host_cli("azure"), WIN_AZ)

    def test_no_prompt_utf8_detect_false_20_seconds(self):
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/az"), \
                mock.patch.dict(os.environ, no_lookup_env(), clear=True), \
                mock.patch.object(pc.subprocess, "run", return_value=proc('{"status": "active"}')) as run:
            pc.host_lookup(self.info)
        cmd, kw = run.call_args[0][0], run.call_args[1]
        self.assertIs(kw["stdin"], subprocess.DEVNULL)
        self.assertEqual(kw["encoding"], "utf-8")
        self.assertEqual(kw["timeout"], 20)
        self.assertEqual(kw["env"]["AZURE_EXTENSION_USE_DYNAMIC_INSTALL"], "no")
        self.assertEqual(cmd[cmd.index("--detect") + 1], "false")
        self.assertIn("https://dev.azure.com/contoso", cmd)

    def test_gh_keeps_8_seconds_and_override(self):
        info = {"host": "github", "number": 82, "url": "https://github.com/contoso/orders-web/pull/82"}
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/gh"), \
                mock.patch.dict(os.environ, no_lookup_env(), clear=True), \
                mock.patch.object(pc.subprocess, "run", return_value=proc('{"state": "OPEN"}')) as run:
            pc.host_lookup(info)
            self.assertEqual(run.call_args[1]["timeout"], 8)
            os.environ["CRAV1_HOST_TIMEOUT"] = "45"
            pc.host_lookup(info)
            self.assertEqual(run.call_args[1]["timeout"], 45)


class LookupReason(unittest.TestCase):
    info = {"host": "azure", "number": 71, "url": ADO_PR}

    def lookup(self, **kw):
        with mock.patch.object(pc.shutil, "which", return_value="/usr/bin/az"), \
                mock.patch.object(pc.subprocess, "run", **kw):
            return pc.host_lookup(self.info)

    def test_stderr_maps_to_a_code(self):
        samples = {
            "ERROR: Please run 'az login' to setup account.": "not-signed-in",
            "ERROR: TF400813: The user is not authorized to access this resource.": "not-signed-in",
            "AADSTS700082: The refresh token has expired.": "not-signed-in",
            "ERROR: 'repos' is misspelled or not recognized by the system.": "extension-missing",
            "The command requires the extension azure-devops. It will be installed first.": "extension-missing",
            "ERROR: TF401180: The requested pull request was not found.": "not-found",
            "ERROR: something else went wrong": "host-error",
        }
        for err, code in samples.items():
            got = self.lookup(return_value=proc("", err, 1))
            self.assertEqual(got["error"], code, err)
            self.assertIsNone(got["ok"])
            self.assertTrue(got["detail"])

    def test_other_failures(self):
        self.assertEqual(self.lookup(side_effect=subprocess.TimeoutExpired("az", 20))["error"], "timeout")
        got = self.lookup(side_effect=FileNotFoundError(2, "The system cannot find the file specified"))
        self.assertEqual(got["error"], "cli-not-runnable")
        self.assertIn("cannot find", got["detail"])
        self.assertEqual(self.lookup(return_value=proc("not json"))["error"], "bad-output")
        self.assertEqual(self.lookup(return_value=proc(""))["error"], "bad-output")
        self.assertEqual(self.lookup(return_value=proc('{"status": "notSet"}'))["error"], "unknown-status")
        with mock.patch.object(pc.shutil, "which", return_value=None):
            self.assertEqual(pc.host_lookup(self.info)["error"], "cli-missing")
            self.assertIsNone(pc.host_state(self.info))
        self.assertEqual(pc.host_lookup({"host": "other", "number": 71}), {"ok": None, "error": None, "detail": ""})


@contextlib.contextmanager
def host_fails(error: str, detail: str = "ERROR: Please run 'az login' to setup account."):
    got = {"ok": None, "error": error, "detail": detail}
    with mock.patch.dict(os.environ, no_lookup_env(), clear=True), \
            mock.patch.object(wp, "host_pr_ref", side_effect=ref), \
            mock.patch.object(pc, "host_lookup", return_value=got):
        yield


class HostNotReached(unittest.TestCase):
    def test_ready_check_says_why_and_does_not_ask_the_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = strip_author(ps.specs_repo(tmp))
            with host_fails("not-signed-in"):
                out = ps.ready_json(root)
            self.assertEqual(out["ask_first"], "host")
            self.assertEqual(out["owner_unknown"], [])
            self.assertNotIn("owner_choices", out)
            self.assertEqual([(i["pr"], i["error"]) for i in out["host_unread"]],
                             [(71, "not-signed-in"), (82, "not-signed-in")])
            ending = out["ending"]
            self.assertIn("**Catch up first**", ending)
            self.assertIn("Azure DevOps was not reached for PR 71 and PR 82: not signed in. Sign in to Azure DevOps:\n"
                          "`az login`\nThen run the ready check again:\n`/crav1-tasks-ready-to-build ", ending)
            self.assertIn("owner unknown: Azure DevOps not reached", ending)
            self.assertNotIn("owner not recorded", ending)
            self.assertNotRegex(ending, r"(?m)^Next:")
            self.assertLess(ending.index("`az login`"), ending.index("Merge these PRs"))

    def test_extension_missing_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            with host_fails("extension-missing", "ERROR: 'repos' is misspelled or not recognized by the system."):
                text = ps.ready(root)
            self.assertIn("Add the Azure DevOps extension:\n`az extension add --name azure-devops`\n", text)

    def test_timeout_has_no_fix_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            with host_fails("timeout", "no answer within 20 s"):
                text = ps.ready(root)
            self.assertIn("it did not answer within 20 s. Run the ready check again:\n`/crav1-tasks-ready-to-build ",
                          text)

    def test_pr_author_says_host_unread(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = strip_author(ps.specs_repo(tmp))
            buf = io.StringIO()
            with host_fails("cli-not-runnable", "[WinError 2] The system cannot find the file specified"), \
                    contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as stop:
                wp.main(["pr-author", "--root", str(root), "--pr", "71"])
            self.assertEqual(stop.exception.code, 1)
            data = json.loads(buf.getvalue())
            self.assertEqual(data["status"], "host-unread")
            self.assertEqual(data["error"], "cli-not-runnable")
            self.assertIn("Azure DevOps could not be reached", data["line"])
            self.assertEqual(data["fix"]["command"], "az --version")
            self.assertEqual(data["choices"][-1], "Don't know")

    def test_simulated_windows_end_to_end(self):
        """which() finds az.CMD and a bare `az` cannot start: PR 71 is still read as merged."""
        def run(cmd, *a, **k):
            if cmd and cmd[0] == "az":
                raise FileNotFoundError(2, "The system cannot find the file specified")
            if cmd and cmd[0] == WIN_AZ:
                number = int(cmd[cmd.index("--id") + 1])
                status = "completed" if number == 71 else "active"
                return proc(json.dumps({"status": status, "sha": ps.SHA if number == 71 else None,
                                        "closed": "2026-11-14T10:00:00Z" if number == 71 else None,
                                        "author": "Person A" if number == 71 else "person B"}))
            return REAL_RUN(cmd, *a, **k)
        real_which = pc.shutil.which
        which = lambda name, *a, **k: WIN_AZ if name in ("az", "az.cmd") else real_which(name, *a, **k)  # noqa: E731
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            with mock.patch.dict(os.environ, no_lookup_env(), clear=True), \
                    mock.patch.object(wp, "host_pr_ref", side_effect=ref), \
                    mock.patch.object(pc.shutil, "which", side_effect=which), \
                    mock.patch.object(pc.subprocess, "run", side_effect=run):
                out = ps.ready_json(root)
            self.assertEqual(out["pr_state"]["merged"], [71])
            self.assertEqual(out["host_unread"], [])
            self.assertNotIn("1. PR 71", out["ending"])
            self.assertIn("- Step: merge-pr", ps.readme_log(root))


OWN = ("# Build progress\n\nBranch: feature/orders-incoming-table\nOwner: self\nTasks: T5\n\n"
       "- Step: open-pr\n  Result: PR 71\n\n- Step: wait-merge\n  Result: PR 71 open\n")
OTHER = ("# Build progress\n\nBranch: feature/orders-api-fixes\nOwner: self\nTasks: T8\n\n"
         "- Step: open-pr\n  Result: PR 73\n\n"
         "- Step: wait-merge\n  Result: take in develop after PR 71; PR 73 open\n")


def two_files(tmp: str) -> tuple[Path, Path, Path]:
    root = Path(tmp) / "spec"
    bp = root / "build-progress"
    bp.mkdir(parents=True)
    own = bp / "feature--orders-incoming-table.md"
    other = bp / "feature--orders-api-fixes.md"
    own.write_text(OWN, encoding="utf-8")
    other.write_text(OTHER, encoding="utf-8")
    return root, own, other


class RightFile(unittest.TestCase):
    def test_each_pr_author_lands_in_its_own_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, own, other = two_files(tmp)
            self.assertEqual(wp.record_pr_author(root, 71, "Person A"), own)
            self.assertEqual(wp.record_pr_author(root, 73, "Person A"), other)
            for path in (own, other):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count("PR author: Person A"), 1, path)
                self.assertLess(text.index("PR author:"), text.index("- Step:"), "header only")
            self.assertEqual(wp.pr_author(root, 71, own.read_text(encoding="utf-8")), "Person A")
            self.assertEqual(wp._progress_file_for(root, 71), own)
            self.assertEqual(wp.record_code_repo(root, 71, ps.ADO_REPO), own)
            self.assertNotIn("Code repo", other.read_text(encoding="utf-8"))

    def test_branch_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, own, other = two_files(tmp)
            self.assertEqual(wp.record_pr_author(root, 71, "Person B", branch="feature/orders-api-fixes"), other)

    def test_merge_waits_take_the_files_own_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _own, _other = two_files(tmp)
            waits = wp.progress_merge_waits(root)
            self.assertEqual(waits["T5"]["pr"], 71)
            self.assertEqual(waits["T8"]["pr"], 73)
            # A later step that names another PR does not move the wait.
            (root / "build-progress/feature--orders-api-fixes.md").write_text(
                OTHER + "\n- Step: comment\n  Result: replied; merge after PR 71\n", encoding="utf-8")
            self.assertEqual(wp.progress_merge_waits(root)["T8"]["pr"], 73)

    def test_several_matches_are_ambiguous(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, own, other = two_files(tmp)
            other.write_text(OTHER.replace("PR 73", "PR 71"), encoding="utf-8")
            self.assertIsNone(wp.record_pr_author(root, 71, "Person A"))
            env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
            out = subprocess.run([sys.executable, str(rb.WALK), "pr-author", "--root", str(root), "--pr", "71",
                                  "--name", "Person A"], capture_output=True, text=True, check=False, env=env)
            data = json.loads(out.stdout)
            self.assertEqual((out.returncode, data["status"]), (1, "ambiguous"))
            self.assertIn("--branch", data["line"])
            out = subprocess.run([sys.executable, str(rb.WALK), "pr-author", "--root", str(root), "--pr", "71",
                                  "--name", "Person A", "--branch", "feature/orders-incoming-table"],
                                 capture_output=True, text=True, check=False, env=env)
            self.assertEqual(json.loads(out.stdout)["commit"], "build-progress/feature--orders-incoming-table.md")

    def test_no_file_creates_the_branch_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "spec"
            root.mkdir()
            path = wp.record_pr_author(root, 71, "Person A", branch="feat/orders-readme")
            self.assertEqual(path, root / "build-progress/feat--orders-readme.md")
            self.assertEqual(path.read_text(encoding="utf-8"),
                             "# Build progress\n\nBranch: feat/orders-readme\nPR author: Person A\n")
            self.assertIsNone(wp.record_pr_author(root, 99, "Person A"), "no branch, no file: nothing written")

    def test_answers_say_which_file_to_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
            out = subprocess.run([sys.executable, str(rb.WALK), "pr-author", "--root", str(root), "--pr", "71",
                                  "--name", "Person A"], capture_output=True, text=True, check=False, env=env)
            data = json.loads(out.stdout)
            self.assertEqual(data["commit"], "build-progress/feat--orders-readme.md")
            self.assertIn("Commit this file with the specs", data["line"])
            self.assertIn("rerun", data)
            out = subprocess.run([sys.executable, str(rb.WALK), "code-repo", "--root", str(root), "--pr", "71",
                                  "--repo", "orders-api"], capture_output=True, text=True, check=False, env=env)
            data = json.loads(out.stdout)
            self.assertEqual(data["commit"], "build-progress/feat--orders-readme.md")
            self.assertIn("Commit this file with the specs", data["line"])


class OwnerChoices(unittest.TestCase):
    def test_owner_marker_is_never_a_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            (root / "build-progress/feat--orders-switch.md").write_text(
                "# Build progress\n\nWalk: build-walk\nBranch: feat/orders-switch\nOwner: other\n", encoding="utf-8")
            (root / "build-progress/feat--orders-more.md").write_text(
                "# Build progress\n\nBranch: feat/orders-more\nOwner: Other\nPR author: other\n", encoding="utf-8")
            choices = wp.owner_choices(root)
            self.assertNotIn("other", [c.lower() for c in choices])
            self.assertEqual(choices[-1], "Don't know")

    def test_question_owners_are_offered_but_not_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            rows = [{"task": "T9", "bucket": "blocked", "who": "Person C"},
                    {"task": "T10", "bucket": "waiting", "who": "the project team"},
                    {"task": "T11", "bucket": "blocked", "who": "CONTOSO"},
                    {"task": "T12", "bucket": "waiting", "who": "Orders support team"},
                    {"task": "T13", "bucket": "ready", "who": "Person D"}]
            choices = wp.owner_choices(root, rows)
            self.assertIn("Person C", choices)
            for name in ("the project team", "CONTOSO", "Orders support team", "Person D", "other"):
                self.assertNotIn(name, choices)
            self.assertEqual(choices[-1], "Don't know")

    def test_is_group(self):
        for name in ("the project team", "The vendor", "CONTOSO", "Ops group"):
            self.assertTrue(wp.is_group(name), name)
        for name in ("Person A", "person B", "Ana Lind"):
            self.assertFalse(wp.is_group(name), name)


class Docs(unittest.TestCase):
    def test_pr_owner_docs(self):
        text = (SK / "crav1-tasks-ready-to-build/references/pr-owner.md").read_text(encoding="utf-8")
        self.assertLess(text.index("## Repo first"), text.index("## Host not reached (1.179.0)"))
        self.assertLess(text.index("## Host not reached (1.179.0)"), text.index("## Owner"))
        self.assertIn("20-second timeout", text)
        self.assertIn("`host_unread`", text)
        self.assertIn("only in the `pr-author` and `code-repo` answers", text)
        self.assertNotIn("edit the file", text.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
