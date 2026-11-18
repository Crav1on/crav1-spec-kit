"""1.191.0: /crav1-design-architecture resolves the repo's default branch instead of assuming origin/main.

origin/HEAD first; else origin/main, then origin/master; with none the check is
skipped with a reason and never crashes. The branch-behind card, its Run next,
the kit-behind check and the go-ahead texts name the real branch, never a rebase.
Generic fixture only (orders-platform, person A).
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_kit_1189 import GOAL, T, Base, GitHelpers, dr  # noqa: E402

WF = ".cursor/skills/crav1/crav1-docs/reference/workflow.md"


class Repo(GitHelpers, Base):
    def setUp(self):
        super().setUp()
        for k, v in (("GIT_AUTHOR_NAME", "person A"), ("GIT_AUTHOR_EMAIL", "a@example.com"),
                     ("GIT_COMMITTER_NAME", "person A"), ("GIT_COMMITTER_EMAIL", "a@example.com"), ("CRAV1_NO_FETCH", "1")):
            p = patch.dict(os.environ, {k: v})
            p.start()
            self.addCleanup(p.stop)

    def start(self, default="master"):
        self.git("init", "-q", "-b", default)
        self.git("commit", "-q", "--allow-empty", "-m", "start")
        self.create()
        self.commit("design")
        self.git("switch", "-q", default)
        self.git("commit", "-q", "--allow-empty", "-m", f"{default} moves on")
        self.git("switch", "-q", f"design/{T}")

    def resolve(self):
        dr._DEFAULT.clear()
        return dr.default_branch(self.tmp)


class TestDefaultBranch(Repo):
    def test_master_default_via_origin_head(self):
        self.start("master")
        self.git("update-ref", "refs/remotes/origin/master", "master")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master")
        self.assertEqual(self.resolve(), ("origin/master", ""))
        st = self.ok("branch-behind", "--topic", T)
        self.assertEqual(st["state"], "behind")
        self.assertEqual(st["behind"], {"origin/master": 1})
        self.assertIn("Merge origin/master into design/orders-platform", st["card"]["question"])
        self.assertIn("Merge master into the design branch:\n`git merge --no-ff origin/master`", st["ending"])
        self.assertNotIn("origin/main", st["ending"])
        self.assertNotIn("rebase", st["card"]["question"] + st["card"]["options"][0]["label"])
        self.assertIn("never rebase", st["ending"])
        res = self.ok("branch-behind", "--topic", T, "--yes")
        self.assertEqual(res["merged"], ["origin/master"])

    def test_origin_head_wins_over_main(self):
        self.start("develop")
        self.git("update-ref", "refs/remotes/origin/main", "develop~1")
        self.git("update-ref", "refs/remotes/origin/develop", "develop")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/develop")
        self.assertEqual(self.resolve(), ("origin/develop", ""))
        self.assertEqual(self.ok("branch-behind", "--topic", T)["behind"], {"origin/develop": 1})

    def test_unset_origin_head_falls_back_to_main_then_master(self):
        self.start("master")
        self.git("update-ref", "refs/remotes/origin/master", "master")
        self.assertEqual(self.resolve(), ("origin/master", ""))
        self.git("update-ref", "refs/remotes/origin/main", "master")
        self.assertEqual(self.resolve(), ("origin/main", ""))

    def test_neither_skips_with_a_reason(self):
        self.start("master")
        ref, why = self.resolve()
        self.assertEqual(ref, "")
        self.assertIn("no default branch found", why)
        st = self.ok("branch-behind", "--topic", T)
        self.assertEqual(st["state"], "in-step")
        self.assertIn("no default branch found", st["skipped"])
        self.assertIsNone(st["card"])
        self.ok("resume", "--topic", T)

    def test_not_a_repo_never_crashes(self):
        self.assertEqual(dr.default_branch(self.tmp)[0], "")


class TestKitBehindMaster(Repo):
    def test_kit_behind_master_names_master(self):
        wf = self.tmp / WF
        wf.parent.mkdir(parents=True)
        self.git("init", "-q", "-b", "master")
        wf.write_text("# Workflow\n\nKit version: 1.189.0\n", encoding="utf-8")
        self.commit("kit 1.189")
        self.create()
        self.commit("design")
        self.git("switch", "-q", "master")
        wf.write_text("# Workflow\n\nKit version: 1.191.0\n", encoding="utf-8")
        self.commit("kit 1.191")
        self.git("update-ref", "refs/remotes/origin/master", "master")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master")
        self.git("switch", "-q", f"design/{T}")
        res = self.ok("resume", "--topic", T)
        self.assertTrue(res["kit_check"]["kit_behind_main"])
        self.assertEqual(res["kit_check"]["default_branch"], "origin/master")
        self.assertIn("merge master into the branch", " ".join(res["kit_check"]["problems"]))
        self.assertIn("behind origin/master", res["note"])
        self.assertEqual(res["branch_sync"]["behind"], {"origin/master": 1})
        self.assertEqual(res["written"], [])


class TestTextsNameTheBranch(Repo):
    def test_go_ahead_ending_uses_the_default_branch(self):
        self.start("master")
        self.git("update-ref", "refs/remotes/origin/master", "master")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master")
        f = Path(self.tmp.parent) / f"{self.tmp.name}-state.json"
        out = self.ok("ending", "--topic", T, inp={"phase": "go-ahead"}, inp_path=f)
        self.assertIn("`gh pr create --base master --head design/orders-platform`", out)
        self.assertIn("design is on master", dr.ending({"topic": T, "phase": "merged", "no_slice": True, "default_branch": "master"}))

    def test_no_repo_keeps_main_in_text(self):
        self.assertIn("--base main", dr.ending({"topic": T, "phase": "go-ahead"}))


if __name__ == "__main__":
    import unittest
    unittest.main()
