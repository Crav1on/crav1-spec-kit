"""1.140.0: a task-line branch wins, and a merged or deleted branch is not offered."""
import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_map_wrapper_1140", ROOT / "scripts/build-map.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
bm = wrapper.load()

SPEC = """# Orders

## Open questions

- Which channel is used for the receipt?
  - Blocks: none
"""

STEP = """# Plan

## Approach

1. One commit cleanup on main. (T2, T3)

## Risks

- None for this slice.
"""

LINES = """# Tasks

- [ ] T2: Clean the commit on feat/orders-one-commit-cleanup-main from main
- [ ] T3: Add the host setup scripts on feat/orders-host-setup-scripts from develop
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


class TaskLineWins(unittest.TestCase):
    def test_task_line_branch_beats_step_name(self):
        tasks = "- [ ] T3: Add the host setup scripts on feat/orders-host-setup-scripts from develop\n"
        plan = STEP
        offer = bm.recommendation("orders", SPEC, plan, tasks, 3)
        self.assertEqual(offer["name"], "feat/orders-host-setup-scripts")
        self.assertEqual(offer["source"], "task line")
        self.assertEqual(offer["base"], "develop")
        self.assertIsNone(offer["because"])
        text = bm.build("orders", SPEC, plan, tasks)["markdown"]
        self.assertIn("### feat/orders-host-setup-scripts", text)
        self.assertNotIn("### feat/orders-one-commit-cleanup-main", text)
        self.assertIn(
            "Plan step names feat/orders-one-commit-cleanup-main; built on feat/orders-host-setup-scripts",
            text,
        )

    def test_two_tasks_on_one_plan_step_keep_their_own_branches(self):
        offers = {
            task_id: bm.recommendation("orders", SPEC, STEP, LINES, task_id)
            for task_id in (2, 3)
        }
        self.assertEqual(offers[2]["name"], "feat/orders-one-commit-cleanup-main")
        self.assertEqual(offers[2]["source"], "task line")
        self.assertEqual(offers[2]["base"], "main")
        self.assertEqual(offers[3]["name"], "feat/orders-host-setup-scripts")
        self.assertEqual(offers[3]["source"], "task line")
        self.assertEqual(offers[3]["base"], "develop")
        self.assertNotEqual(offers[2]["name"], offers[3]["name"])
        text = bm.build("orders", SPEC, STEP, LINES)["markdown"]
        self.assertIn("### feat/orders-one-commit-cleanup-main", text)
        self.assertIn("### feat/orders-host-setup-scripts", text)

    def test_no_task_line_branch_falls_back_to_the_map(self):
        plan = "# Plan\n\n## Approach\n\n1. Send the receipt. (T3)\n"
        tasks = "- [ ] T3: Email the receipt\n"
        offer = bm.recommendation("orders", SPEC, plan, tasks, 3)
        self.assertEqual(offer["name"], "feat/orders-send-receipt")
        self.assertEqual(offer["source"], "build map")
        self.assertIsNone(offer["base"])
        self.assertIsNone(offer["because"])
        self.assertIn("### feat/orders-send-receipt", bm.build("orders", SPEC, plan, tasks)["markdown"])

    def test_line_endings_do_not_change_the_offer(self):
        plan = "# Plan\n\n## Approach\n\n1. One commit cleanup on main. (T3)\n"
        tasks = "- [ ] T3: Add the host setup scripts on feat/orders-host-setup-scripts from develop\n"
        lf = bm.recommendation("orders", SPEC, plan, tasks, 3)
        cr = bm.recommendation(
            "orders",
            SPEC.replace("\n", "\r\n"),
            plan.replace("\n", "\r\n"),
            tasks.replace("\n", "\r\n"),
            3,
        )
        self.assertEqual(lf, cr)
        self.assertEqual(lf["name"], "feat/orders-host-setup-scripts")
        self.assertNotIn("\r", lf["name"])
        self.assertNotIn("\r", lf["base"])
        left = bm.build("orders", SPEC, plan, tasks)["markdown"]
        right = bm.build(
            "orders",
            SPEC.replace("\n", "\r\n"),
            plan.replace("\n", "\r\n"),
            tasks.replace("\n", "\r\n"),
        )["markdown"]
        self.assertEqual(left.replace("\r\n", "\n"), right.replace("\r\n", "\n"))


class MergedAndDeleted(unittest.TestCase):
    def test_merged_branch_is_not_recommended(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "orders-api"
            init_repo(repo)
            git(repo, "checkout", "-b", "feat/orders-one-commit-cleanup-main")
            (repo / "cleanup.md").write_text("cleanup\n", encoding="utf-8")
            git(repo, "add", "cleanup.md")
            git(repo, "commit", "-m", "cleanup")
            git(repo, "checkout", "main")
            git(repo, "merge", "--no-ff", "-m", "merge cleanup", "feat/orders-one-commit-cleanup-main")
            # A branch that only sits on main is not merged.
            git(repo, "branch", "feat/orders-fresh")
            plan = "# Plan\n\n## Approach\n\n1. One commit cleanup on main. (T1)\n"
            tasks = "- [ ] T1: Clean the commit\n"
            offer = bm.recommendation("orders", SPEC, plan, tasks, 1, repo=repo)
            self.assertNotEqual(offer["name"], "feat/orders-one-commit-cleanup-main")
            self.assertEqual(offer["source"], "new")
            self.assertIn("feat/orders-one-commit-cleanup-main is already merged", offer["because"])

            recorded = (
                "# Orders\n\n## Match\n\n"
                "- Branch: orders-api feat/orders-one-commit-cleanup-main (PR 78) merged\n"
            )
            marked = bm.recommendation("orders", recorded, plan, tasks, 1)
            self.assertNotEqual(marked["name"], "feat/orders-one-commit-cleanup-main")
            self.assertIn("already merged", marked["because"])

            same_tip = "- [ ] T1: Start the scripts on feat/orders-fresh from main\n"
            fresh = bm.recommendation("orders", SPEC, plan, same_tip, 1, repo=repo)
            self.assertEqual(fresh["name"], "feat/orders-fresh")
            self.assertEqual(fresh["source"], "task line")
            self.assertIsNone(fresh["because"])

            named = "- [ ] T3: Add the host setup scripts on feat/orders-host-setup-scripts from develop\n"
            step = "# Plan\n\n## Approach\n\n1. One commit cleanup on main. (T3)\n"
            task_line = bm.recommendation("orders", SPEC, step, named, 3, repo=repo)
            self.assertEqual(task_line["name"], "feat/orders-host-setup-scripts")
            self.assertEqual(task_line["source"], "task line")
            self.assertEqual(task_line["base"], "develop")

            own = (
                "# Orders\n\n## Match\n\n"
                "- Branch: orders-api feat/orders-export (PR 78) merged\n"
            )
            own_tasks = "- [ ] T2: export the receipt (PR 78, merged) (branch: feat/orders-export)\n"
            own_plan = "# Plan\n\n## Approach\n\n1. Export the receipt. (T2)\n"
            mapped = bm.build("orders", own, own_plan, own_tasks)["markdown"]
            self.assertIn("### feat/orders-export", mapped)
            own_offer = bm.recommendation("orders", own, own_plan, own_tasks, 2)
            self.assertNotEqual(own_offer["name"], "feat/orders-export")
            self.assertIn("already merged", own_offer["because"])

    def test_deleted_branch_is_not_recommended(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "orders-api"
            bare = pathlib.Path(tmp) / "remote.git"
            init_repo(repo)
            bare_init = subprocess.run(
                ["git", "init", "--bare", str(bare)],
                capture_output=True,
                text=True,
                check=False,
            )
            if bare_init.returncode != 0:
                raise AssertionError(bare_init.stderr)
            git(repo, "remote", "add", "origin", str(bare))
            git(repo, "push", "-u", "origin", "main")
            git(repo, "checkout", "-b", "feat/orders-host-setup-scripts")
            git(repo, "commit", "--allow-empty", "-m", "scripts")
            git(repo, "push", "-u", "origin", "feat/orders-host-setup-scripts")
            git(repo, "checkout", "main")
            git(repo, "push", "origin", "--delete", "feat/orders-host-setup-scripts")
            git(repo, "branch", "-D", "feat/orders-host-setup-scripts")
            plan = "# Plan\n\n## Risks\n\n- None.\n"
            tasks = "- [ ] T1: Add the host setup scripts on feat/orders-host-setup-scripts from develop\n"
            offer = bm.recommendation("orders", SPEC, plan, tasks, 1, repo=repo)
            self.assertNotEqual(offer["name"], "feat/orders-host-setup-scripts")
            self.assertEqual(offer["source"], "new")
            self.assertEqual(offer["base"], "develop")
            self.assertIn(
                "feat/orders-host-setup-scripts was deleted locally and on the remote",
                offer["because"],
            )
            never = "- [ ] T1: Add the host setup scripts on feat/orders-never-created from develop\n"
            created = bm.recommendation("orders", SPEC, plan, never, 1, repo=repo)
            self.assertEqual(created["name"], "feat/orders-never-created")
            self.assertEqual(created["source"], "task line")
            self.assertEqual(created["base"], "develop")
            self.assertIsNone(created["because"])


if __name__ == "__main__":
    unittest.main()
