"""1.182.0: a second task on an existing branch progress file is recorded and
counted everywhere; ado_threads reads org, project and repo from the git
remote; one wording for verified and waiting for the tick; one verify row
keeps the whole-file spec stamp; the walk asks before fast-forwarding a code
branch that is behind origin; finalize-commit asks before setting
core.hooksPath."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
SNAP = ROOT / "scripts/tests/snapshots/orders-api-second-task/spec"


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SK / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ts = load("crav1-tasks-ready-to-build/scripts/task_state.py", "ts_1182")
bm = load("crav1-tasks-ready-to-build/scripts/build_map.py", "bm_1182")
bw = load("crav1-build-walk/scripts/build_walk.py", "bw_1182")
wp = load("crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py", "wp_1182")
ado = load("crav1-review-pr/scripts/ado_threads.py", "ado_1182")
rs = load("crav1-build-walk/scripts/repo_sync.py", "rs_1182")
BW = SK / "crav1-build-walk/scripts/build_walk.py"
VR = SK / "crav1-verify-build-against-spec/scripts/verify_rows.py"
WP = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"

OLD_FILE = """# Build progress

Walk: build-walk
Slice: docs/specs/orders-api/
Branch: feat/orders-cicd
Owner: other
Tasks: T43 Add the build pipeline
Cut from: develop
Merge list: none

- Step: build T43
  Done: 2026-11-15T10:00:00+01:00
  Result: done at 3f9c2a1

- Step: build T47
  Done: 2026-11-16T14:00:00+01:00
  Result: done at 8b1e4d7
"""


def copy_snapshot(tmp: str, last_step: str | None = None) -> Path:
    root = Path(tmp) / "docs/specs/orders-api"
    shutil.copytree(SNAP, root)
    if last_step == "verify":
        path = root / "build-progress/feat--orders-cicd.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.split("\n- Step: commit", 1)[0].rstrip() + "\n", encoding="utf-8")
    return root


class SecondTaskState(unittest.TestCase):
    def test_build_step_counts_whatever_the_header_says(self):
        found = ts.progress_tasks(OLD_FILE)
        self.assertEqual(found["listed"], ["T43"])
        self.assertEqual(found["built"], ["T43", "T47"])
        self.assertEqual(found["all"], ["T43", "T47"])

    def test_a_failed_build_step_is_not_built(self):
        text = OLD_FILE.replace("Result: done at 8b1e4d7", "Result: failed, tests red")
        found = ts.progress_tasks(text)
        self.assertEqual(found["built"], ["T43"])
        self.assertIn("T47", found["all"])

    def test_build_map_counts_both_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build-progress").mkdir()
            (root / "build-progress/feat--orders-cicd.md").write_text(OLD_FILE, encoding="utf-8")
            walk = bm.progress_state(root)["feat/orders-cicd"]
            self.assertEqual(walk["built"], {43, 47})
            self.assertEqual(walk["tasks"], {43, 47})

    def test_a_merge_marks_both_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build-progress").mkdir()
            merged = OLD_FILE + "\n- Step: merge-pr\n  Done: x\n  Result: merged PR 21 at 9a8b7c6\n"
            (root / "build-progress/feat--orders-cicd.md").write_text(merged, encoding="utf-8")
            tasks = bm.parse_tasks("- [ ] T43 Add the build pipeline\n- [ ] T47 Add the deploy stage\n")
            states = bm.apply_task_states(tasks, bm.progress_state(root))
            self.assertEqual(states, {"T43": ts.TICK_PENDING, "T47": ts.TICK_PENDING})


class SecondTaskWalk(unittest.TestCase):
    def run_bw(self, *args):
        proc = subprocess.run([sys.executable, str(BW), *args], capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout or "{}")

    def test_record_accepts_build_task_and_adds_it_to_the_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "orders-api"
            root.mkdir()
            (root / "tasks.md").write_text(
                "- [ ] T43 Add the build pipeline (branch: feat/orders-cicd)\n"
                "- [ ] T47 Add the deploy stage (after: T43) (branch: feat/orders-cicd)\n", encoding="utf-8")
            code, _ = self.run_bw("progress", "init", "--root", str(root), "--branch", "feat/orders-cicd",
                                  "--owner", "other", "--tasks", "T43", "--yes")
            self.assertEqual(code, 0)
            code, out = self.run_bw("progress", "record", "--root", str(root), "--branch", "feat/orders-cicd",
                                    "--step", "build T47", "--result", "done at 8b1e4d7", "--yes")
            self.assertEqual(code, 0, out)
            text = (root / "build-progress/feat--orders-cicd.md").read_text(encoding="utf-8")
            self.assertIn("Tasks: T43 Add the build pipeline, T47 Add the deploy stage", text)
            self.assertIn("- Step: build T47", text)
            code, out = self.run_bw("next", "--root", str(root), "--branch", "feat/orders-cicd")
            self.assertEqual(out["phase"], "verify")
            self.assertIn("T43 and T47", out["lead"])
            self.assertIn("T47 Add the deploy stage", out["ending"])
            self.assertTrue(out["ending"].startswith("Run next:"))

    def test_record_still_refuses_an_unknown_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "orders-api"
            root.mkdir()
            self.run_bw("progress", "init", "--root", str(root), "--branch", "feat/x", "--tasks", "T1", "--yes")
            code, out = self.run_bw("progress", "record", "--root", str(root), "--branch", "feat/x",
                                    "--step", "deploy", "--result", "done", "--yes")
            self.assertNotEqual(code, 0)
            self.assertIn("build <task>", out["line"])

    def test_older_file_reads_both_tasks(self):
        info = bw.read_progress(OLD_FILE)
        self.assertEqual(info["task_ids"], ["T43", "T47"])
        self.assertEqual(bw.phase_from_progress(info), "verify")

    def test_header_is_not_touched_when_the_task_is_listed(self):
        self.assertEqual(bw.add_header_tasks(OLD_FILE, Path("."), ["T43"]), OLD_FILE)


class SecondTaskReadyCheck(unittest.TestCase):
    def readiness(self, root: Path) -> str:
        proc = subprocess.run([sys.executable, str(WP), "readiness", "--root", str(root), "--text",
                               "--user", "Person C", "--no-fetch"], capture_output=True, text=True)
        if "unrecognized arguments" in proc.stderr:
            proc = subprocess.run([sys.executable, str(WP), "readiness", "--root", str(root), "--text",
                                   "--user", "Person C"], capture_output=True, text=True)
        return proc.stdout + proc.stderr

    def test_built_task_is_not_startable_before_the_comment_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_snapshot(tmp, last_step="verify")
            text = self.readiness(root)
            self.assertNotIn("T47 is yours; the walk resumes it.", text)
            self.assertIn("T47 Add the deploy stage — waits for PR 21 to merge", text)
            self.assertNotIn("`/crav1-build-walk orders-api T47`", text)

    def test_snapshot_merge_list_ticks_both_and_dependant_waits_on_the_merge(self):
        reply = (SNAP.parent / "expected/reply.txt").read_text(encoding="utf-8")
        self.assertIn("ticks T43 and T47, then T48 can start.", reply)
        self.assertIn("you added T47,", reply)
        self.assertIn("T48 Add smoke tests — held, waits on PR 21 to merge (T47, recorded)", reply)
        self.assertNotIn("is yours; the walk resumes it", reply)
        build_map = (SNAP.parent / "expected/build-map.md").read_text(encoding="utf-8")
        self.assertIn("class b1,b2,key2 waiting", build_map)


class AdoRoute(unittest.TestCase):
    def args(self, **kw):
        base = {"org": None, "project": None, "repo": None, "code_repo": ".", "from_file": None}
        base.update(kw)
        return type("A", (), base)()

    def test_route_from_the_remote(self):
        old = ado.remote_url
        ado.remote_url = lambda _repo: "https://contoso@dev.azure.com/contoso/Orders/_git/orders-api"
        try:
            args = self.args()
            ado.fill_route(args)
            self.assertEqual((args.org, args.project, args.repo),
                             ("https://dev.azure.com/contoso", "Orders", "orders-api"))
            args = self.args(project="Other", repo="other-repo")
            ado.fill_route(args)
            self.assertEqual((args.org, args.project, args.repo), ("https://dev.azure.com/contoso", "Other", "other-repo"))
        finally:
            ado.remote_url = old

    def test_ssh_and_visualstudio_remotes(self):
        self.assertEqual(ado.remote_route("git@ssh.dev.azure.com:v3/contoso/Orders/orders-api")["repo"], "orders-api")
        self.assertEqual(ado.remote_route("https://contoso.visualstudio.com/Orders/_git/orders-api")["org"],
                         "https://dev.azure.com/contoso")
        self.assertEqual(ado.remote_route("https://github.com/contoso/orders-api.git"), {})

    def test_post_passes_the_route(self):
        seen = []
        old_url, old_az = ado.remote_url, ado.run_az
        ado.remote_url = lambda _repo: "https://dev.azure.com/contoso/Orders/_git/orders-api"
        ado.run_az = lambda cmd: seen.append(cmd) or b'{"id": 7}'
        try:
            with tempfile.TemporaryDirectory() as tmp:
                block = Path(tmp) / "block.md"
                block.write_text("Looks good.", encoding="utf-8")
                from io import StringIO
                out, sys.stdout = sys.stdout, StringIO()
                try:
                    code = ado.main(["post", "--pr", "21", "--file", str(block), "--yes"])
                finally:
                    sys.stdout = out
            self.assertEqual(code, 0)
            cmd = seen[0]
            self.assertIn("project=Orders", cmd)
            self.assertIn("repositoryId=orders-api", cmd)
            self.assertEqual(cmd[cmd.index("--org") + 1], "https://dev.azure.com/contoso")
        finally:
            ado.remote_url, ado.run_az = old_url, old_az


VERIFY = (
    "# Verify\n\n| | Count | Ids |\n| --- | --- | --- |\n"
    "| Implemented, verified | 1 | T1 |\n| Implemented, verified, tick pending | 0 | |\n"
    "| Implemented, verified on branch | 1 | T2 |\n| Not implemented | 1 | T3 |\n\n"
    "| T# | Title | Status | Verify |\n| --- | --- | --- | --- |\n"
    "| T1 | One | Implemented, verified | pass |\n"
    "| T2 | Two | Implemented, verified on branch | pass at 61dc1ce on feat/orders-cicd, PR 21 open |\n"
    "| T3 | Three | Not implemented | none |\n\n"
    "## Row tips\n\nWritten by `scripts/verify_rows.py`.\n\nSpec stamp: 0123456789ab\n\n- T1: feat/orders-cicd 1111111\n"
)


class OneWording(unittest.TestCase):
    def test_task_state_reads_both(self):
        for status in ("Implemented, verified on branch", "Implemented, verified, tick pending"):
            self.assertEqual(ts.task_state(False, False, status)["state"], ts.MERGE_WAIT)
            self.assertEqual(ts.task_state(False, True, status)["state"], ts.TICK_PENDING)
            self.assertTrue(ts.is_waiting_status(status))
        self.assertEqual(ts.new_status("Implemented, verified on branch"), "Implemented, verified, tick pending")

    def set_row(self, tmp, *extra, status="Implemented, verified on branch"):
        folder = Path(tmp)
        for name in ("spec.md", "plan.md", "tasks.md"):
            (folder / name).write_text(f"# {name}\n", encoding="utf-8")
        path = folder / "verify.md"
        if not path.exists():
            path.write_text(VERIFY, encoding="utf-8")
        proc = subprocess.run([sys.executable, str(VR), "set", "--file", str(path), "--task", "T3",
                               "--status", status, "--evidence", "pass at 2c3d4e5 on feat/orders-cicd, PR 21 open",
                               "--branch", "feat/orders-cicd", "--tip", "2c3d4e5", *extra, "--yes"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return path.read_text(encoding="utf-8")

    def test_only_the_one_wording_is_written_and_old_rows_are_rewritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = self.set_row(tmp)
            self.assertNotIn("verified on branch", text)
            self.assertIn("| T2 | Two | Implemented, verified, tick pending |", text)
            self.assertIn("| T3 | Three | Implemented, verified, tick pending |", text)
            self.assertIn("| Implemented, verified, tick pending | 2 | T2, T3 |", text)

    def test_one_row_keeps_the_spec_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = self.set_row(tmp, status="Implemented, verified, tick pending")
            self.assertIn("Spec stamp: 0123456789ab", text)
            self.assertIn("- T3: feat/orders-cicd 2c3d4e5", text)

    def test_all_rows_moves_the_spec_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = self.set_row(tmp, "--all-rows", status="Implemented, verified, tick pending")
            self.assertNotIn("Spec stamp: 0123456789ab", text)
            self.assertIn("Spec stamp: ", text)

    def test_verified_on_branch_reads_the_new_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "verify.md").write_text(VERIFY.replace("Implemented, verified on branch | pass",
                                                              "Implemented, verified, tick pending | pass"),
                                              encoding="utf-8")
            self.assertEqual(wp.verified_on_branch(Path(tmp)), {"T2"})


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "Person A", "GIT_AUTHOR_EMAIL": "a@example.com",
                        "GIT_COMMITTER_NAME": "Person A", "GIT_COMMITTER_EMAIL": "a@example.com"})


class CodeBehind(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        origin = Path(self.tmp) / "origin.git"
        git(self.tmp, "init", "-q", "--bare", str(origin))
        self.one = Path(self.tmp) / "one"
        git(self.tmp, "clone", "-q", str(origin), str(self.one))
        git(self.one, "checkout", "-q", "-b", "feat/orders-cicd")
        (self.one / "a.txt").write_text("a\n", encoding="utf-8")
        git(self.one, "add", "a.txt")
        git(self.one, "commit", "-q", "-m", "a")
        git(self.one, "push", "-q", "-u", "origin", "feat/orders-cicd")
        self.two = Path(self.tmp) / "two"
        git(self.tmp, "clone", "-q", "-b", "feat/orders-cicd", str(origin), str(self.two))
        (self.one / "b.txt").write_text("b\n", encoding="utf-8")
        git(self.one, "add", "b.txt")
        git(self.one, "commit", "-q", "-m", "b")
        git(self.one, "push", "-q")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_behind_is_a_card_not_a_silent_fast_forward(self):
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.two, capture_output=True, text=True).stdout
        out = rs.code_behind(self.two)
        self.assertEqual(out["state"], "behind")
        self.assertEqual(out["behind"], 1)
        self.assertTrue(out["stop"])
        self.assertEqual(out["card"]["words"], ["fast-forward", "stop"])
        for word in out["card"]["words"]:
            self.assertRegex(word, r"^[a-z]+(-[a-z]+)*$")
        self.assertTrue(out["ending"].startswith("Run next:\n\n"))
        self.assertNotIn("Next:", out["ending"].replace("Run next:", ""))
        label, command = out["ending"].split("\n\n", 1)[1].split("\n")
        self.assertTrue(label.endswith(":"))
        self.assertTrue(command.startswith("`") and command.endswith("`"))
        after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.two, capture_output=True, text=True).stdout
        self.assertEqual(head, after)

    def test_yes_fast_forwards(self):
        from io import StringIO
        out, sys.stdout = sys.stdout, StringIO()
        try:
            code = rs.main(["code-behind", "--repo", str(self.two), "--yes"])
            printed = sys.stdout.getvalue()
        finally:
            sys.stdout = out
        self.assertEqual(code, 0, printed)
        self.assertTrue(json.loads(printed)["fast_forwarded"])
        self.assertTrue((self.two / "b.txt").is_file())

    def test_in_step_goes_on(self):
        out = rs.code_behind(self.one)
        self.assertEqual(out["state"], "in-step")
        self.assertFalse(out["stop"])
        self.assertIsNone(out["card"])

    def test_steps_doc_names_the_check(self):
        text = (SK / "crav1-build-walk/references/steps.md").read_text(encoding="utf-8")
        self.assertIn("repo_sync.py code-behind --repo <code repo>", text)
        self.assertIn("never fast-forward or pull silently", text)


class HooksPathIsAsked(unittest.TestCase):
    def test_trailer_hook_asks_before_setting_hooks_path(self):
        text = (SK / "crav1-finalize-commit/references/trailer-hook.md").read_text(encoding="utf-8")
        self.assertIn("Card: Turn on this repo's commit hook?", text)
        self.assertIn("`turn-on-hook`", text)
        self.assertIn("`skip-hook`", text)
        self.assertIn("never set it silently", text)
        self.assertNotIn("(a teammate's first run) and say so in one line. Do not ask.", text)
        skill = (SK / "crav1-finalize-commit/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`core.hooksPath` is never set silently", skill)
        self.assertNotIn("gets the config line without a question", skill)


if __name__ == "__main__":
    unittest.main()
