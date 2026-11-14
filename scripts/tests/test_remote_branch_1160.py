"""1.160.0: a task-line branch that is only on origin, or is the head of an open pull request, is offered.

The branch is checked in the code repo, which can be a separate checkout from the specs repo.
"""
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_map_wrapper_1160", ROOT / "scripts/build-map.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
bm = wrapper.load()

SPEC = "# Orders\n\n## Open questions\n\n- None.\n"
PLAN = """# Plan

## Approach

1. PR 71 gets readme. (T5)

## Risks

- None.
"""
BRANCH = "feature/orders-incoming-table"
TASKS = f"- [ ] T5: PR 71: READMEs describe the incoming table on {BRANCH} from develop\n"


def git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc


class RemoteBranch(unittest.TestCase):
    def setUp(self):
        self._env = {k: os.environ.get(k) for k in ("CRAV1_GH", "CRAV1_NO_REMOTE_CHECK")}
        os.environ["CRAV1_GH"] = ""
        os.environ.pop("CRAV1_NO_REMOTE_CHECK", None)
        self.tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self.tmp.name)
        self.repo = tmp / "orders-api"
        self.bare = tmp / "origin.git"
        subprocess.run(["git", "init", "--bare", "-b", "main", str(self.bare)], capture_output=True, check=True)
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "person-a@contoso.example")
        git(self.repo, "config", "user.name", "Person A")
        git(self.repo, "config", "commit.gpgsign", "false")
        (self.repo / "readme.md").write_text("orders-api\n", encoding="utf-8")
        git(self.repo, "add", "readme.md")
        git(self.repo, "commit", "-m", "init")
        git(self.repo, "remote", "add", "origin", str(self.bare))
        git(self.repo, "push", "-u", "origin", "main")
        git(self.repo, "checkout", "-b", BRANCH)
        git(self.repo, "commit", "--allow-empty", "-m", "incoming table")
        git(self.repo, "push", "-u", "origin", BRANCH)
        git(self.repo, "checkout", "main")
        git(self.repo, "branch", "-D", BRANCH)

    def tearDown(self):
        for key, value in self._env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def offer(self):
        return bm.recommendation("orders", SPEC, PLAN, TASKS, 5, repo=self.repo)

    def fake_gh(self, rows):
        script = pathlib.Path(self.tmp.name) / "gh"
        script.write_text(
            f"#!{sys.executable}\nimport sys\nsys.stdout.write({rows!r})\n",
            encoding="utf-8",
        )
        script.chmod(0o755)
        os.environ["CRAV1_GH"] = str(script)
        bm._REMOTE_CACHE.clear()

    def assert_task_branch(self, offer):
        self.assertEqual(offer["name"], BRANCH)
        self.assertEqual(offer["source"], "task line")
        self.assertEqual(offer["base"], "develop")
        self.assertEqual(offer["checkout"], BRANCH)
        self.assertIn("checkout creates the local tracking branch", offer["because"])
        self.assertNotIn("deleted", offer["because"])

    def test_local_deleted_tracking_ref_kept(self):
        offer = self.offer()
        self.assert_task_branch(offer)
        self.assertIn(f"{BRANCH} is on origin only", offer["because"])
        self.assertEqual(bm.branch_fate(BRANCH, SPEC, TASKS, self.repo, "develop"), "remote")

    def test_local_deleted_no_tracking_ref_reads_ls_remote(self):
        # The live case: no local branch, no origin/<branch> ref, reflog names it.
        git(self.repo, "update-ref", "-d", f"refs/remotes/origin/{BRANCH}")
        offer = self.offer()
        self.assert_task_branch(offer)
        self.assertIn(f"{BRANCH} is on origin only", offer["because"])
        text = bm.format_offer(offer)
        self.assertEqual(
            text,
            f"{BRANCH}\nsource: task line\nfrom: develop\n"
            f"because: {BRANCH} is on origin only; checkout creates the local tracking branch\n"
            f"checkout: {BRANCH}",
        )

    def test_truly_gone_gets_a_new_branch(self):
        git(self.repo, "push", "origin", "--delete", BRANCH)
        self.fake_gh("[]")
        offer = self.offer()
        self.assertNotEqual(offer["name"], BRANCH)
        self.assertEqual(offer["source"], "build map")
        self.assertIn(f"{BRANCH} was deleted locally and on the remote", offer["because"])
        self.assertIsNone(offer["checkout"])

    def test_open_pr_head_wins(self):
        git(self.repo, "push", "origin", "--delete", BRANCH)
        self.fake_gh(f'[{{"number": 71, "headRefName": "{BRANCH}"}}]')
        offer = self.offer()
        self.assertEqual(offer["name"], BRANCH)
        self.assertEqual(offer["source"], "task line")
        self.assertIn("PR 71 is open from it", offer["because"])
        self.assertEqual(offer["checkout"], BRANCH)

    def test_open_pr_head_wins_over_merged_tip(self):
        git(self.repo, "merge", "--no-ff", "-m", "merge", f"origin/{BRANCH}")
        git(self.repo, "commit", "--allow-empty", "-m", "later")
        self.assertEqual(bm.branch_fate(BRANCH, SPEC, TASKS, self.repo, None), "merged")
        self.fake_gh(f'[{{"number": 71, "headRefName": "{BRANCH}"}}]')
        bm._REMOTE_CACHE.clear()
        self.assertEqual(bm.branch_fate(BRANCH, SPEC, TASKS, self.repo, None, [71]), "remote")

    def test_other_pr_head_does_not_count(self):
        git(self.repo, "push", "origin", "--delete", BRANCH)
        self.fake_gh('[{"number": 72, "headRefName": "feature/orders-other"}]')
        offer = self.offer()
        self.assertNotEqual(offer["name"], BRANCH)

    def test_remote_check_off_keeps_old_behaviour(self):
        git(self.repo, "update-ref", "-d", f"refs/remotes/origin/{BRANCH}")
        os.environ["CRAV1_NO_REMOTE_CHECK"] = "1"
        offer = self.offer()
        self.assertNotEqual(offer["name"], BRANCH)

    def test_cli_prints_checkout_line(self):
        git(self.repo, "update-ref", "-d", f"refs/remotes/origin/{BRANCH}")
        folder = self.repo / "docs/specs/orders"
        folder.mkdir(parents=True)
        (folder / "spec.md").write_text(SPEC, encoding="utf-8")
        (folder / "plan.md").write_text(PLAN, encoding="utf-8")
        (folder / "tasks.md").write_text(TASKS, encoding="utf-8")
        text, code = bm.run_dir(folder, recommend="T5")
        self.assertEqual(code, 0)
        self.assertEqual(text.splitlines()[0], BRANCH)
        self.assertIn(f"checkout: {BRANCH}", text)


def make_repo(path):
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.email", "person-a@contoso.example")
    git(path, "config", "user.name", "Person A")
    git(path, "config", "commit.gpgsign", "false")
    (path / "readme.md").write_text(path.name + "\n", encoding="utf-8")
    git(path, "add", "readme.md")
    git(path, "commit", "-m", "init")


class SeparateRepos(unittest.TestCase):
    """Specs in specs-platform, code in a sibling orders-ops checkout."""

    def setUp(self):
        self._env = {k: os.environ.get(k) for k in ("CRAV1_GH", "CRAV1_NO_REMOTE_CHECK")}
        os.environ["CRAV1_GH"] = ""
        os.environ.pop("CRAV1_NO_REMOTE_CHECK", None)
        self.tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self.tmp.name)
        self.specs = tmp / "specs-platform"
        self.code = tmp / "orders-ops"
        bare = tmp / "orders-ops.git"
        subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)], capture_output=True, check=True)
        make_repo(self.specs)
        # The same name was once checked out and deleted in the specs repo, so
        # its reflog names it: the old check called it deleted.
        git(self.specs, "checkout", "-b", BRANCH)
        git(self.specs, "checkout", "main")
        git(self.specs, "branch", "-D", BRANCH)
        make_repo(self.code)
        git(self.code, "remote", "add", "origin", str(bare))
        git(self.code, "push", "-u", "origin", "main")
        git(self.code, "checkout", "-b", BRANCH)
        git(self.code, "commit", "--allow-empty", "-m", "incoming table")
        git(self.code, "push", "-u", "origin", BRANCH)
        git(self.code, "checkout", "main")
        git(self.code, "branch", "-D", BRANCH)
        git(self.code, "update-ref", "-d", f"refs/remotes/origin/{BRANCH}")
        self.folder = self.specs / "docs/specs/orders"
        self.folder.mkdir(parents=True)
        (self.folder / "plan.md").write_text(PLAN, encoding="utf-8")

    def tearDown(self):
        for key, value in self._env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def write(self, tasks, spec=SPEC):
        (self.folder / "spec.md").write_text(spec, encoding="utf-8")
        (self.folder / "tasks.md").write_text(tasks, encoding="utf-8")

    def recommend(self, code_repo=None):
        text, code = bm.run_dir(self.folder, recommend="T5", code_repo=code_repo)
        self.assertEqual(code, 0)
        return text

    def test_specs_repo_alone_used_to_say_deleted(self):
        self.write(TASKS)
        text = self.recommend()
        self.assertIn("was deleted locally and on the remote", text)

    def test_repo_line_in_tasks_checks_the_sibling(self):
        self.write("Repo: orders-ops\n\n" + TASKS)
        text = self.recommend()
        self.assertEqual(
            text,
            f"{BRANCH}\nsource: task line\nfrom: develop\n"
            f"because: {BRANCH} is on origin only; checkout creates the local tracking branch\n"
            f"repo: ../orders-ops\n"
            f"checkout: {BRANCH}",
        )

    def test_branch_mark_repo_prefix_checks_the_sibling(self):
        self.write(f"- [ ] T5: PR 71: READMEs describe the incoming table (branch: orders-ops {BRANCH})\n")
        text = self.recommend()
        self.assertEqual(text.splitlines()[0], BRANCH)
        self.assertIn(f"checkout: {BRANCH}", text)
        self.assertNotIn("deleted", text)

    def test_match_branch_line_names_the_repo(self):
        spec = SPEC + f"\n## Match\n\n- Branch: orders-ops {BRANCH} (PR 71)\n"
        self.write(TASKS, spec)
        text = self.recommend()
        self.assertEqual(text.splitlines()[0], BRANCH)
        self.assertIn(f"checkout: {BRANCH}", text)

    def test_code_repo_not_found_is_never_called_deleted(self):
        self.write("Repo: orders-billing\n\n" + TASKS)
        text = self.recommend()
        self.assertEqual(
            text,
            f"{BRANCH}\nsource: task line\nfrom: develop\nbecause: could not check orders-billing from here",
        )

    def test_explicit_code_repo_wins(self):
        moved = pathlib.Path(self.tmp.name) / "elsewhere" / "ops-checkout"
        moved.parent.mkdir()
        self.code.rename(moved)
        self.write("Repo: orders-ops\n\n" + TASKS)
        self.assertIn("could not check orders-ops from here", self.recommend())
        text = self.recommend(code_repo=str(moved))
        self.assertIn(f"checkout: {BRANCH}", text)

    def test_truly_gone_in_the_code_repo_gets_a_new_branch(self):
        git(self.code, "push", "origin", "--delete", BRANCH)
        git(self.code, "checkout", "-b", "tmp-reflog")
        git(self.code, "checkout", "-b", BRANCH)
        git(self.code, "checkout", "main")
        git(self.code, "branch", "-D", BRANCH)
        self.write("Repo: orders-ops\n\n" + TASKS)
        text = self.recommend()
        self.assertNotEqual(text.splitlines()[0], BRANCH)
        self.assertIn(f"{BRANCH} was deleted locally and on the remote", text)

    def test_walk_offer_reuses_the_code_repo_answer(self):
        walk_spec = importlib.util.spec_from_file_location("build_walk_wrapper_1160", ROOT / "scripts/build-walk.py")
        walk_wrapper = importlib.util.module_from_spec(walk_spec)
        walk_spec.loader.exec_module(walk_wrapper)
        bw = walk_wrapper.load()
        tasks = "Repo: orders-ops\n\n" + TASKS
        offer = bw.offer_for("orders", SPEC, PLAN, tasks, 5, repo=self.specs)
        self.assertEqual(offer["name"], BRANCH)
        self.assertFalse(offer["refused"])
        self.assertEqual(offer["fate"], "remote")


if __name__ == "__main__":
    unittest.main()
