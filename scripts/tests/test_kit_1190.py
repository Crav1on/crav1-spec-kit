"""1.190.0: /crav1-design-architecture and /crav1-update-kit fixes from a live design session.

Decision order as Order: N with title-sorted storage, a switch-branch yes card,
saved goal files offered as change-goal, card self-correction lint, a kit version
check, a short and verified update-kit fetch, an update-kit ending that reloads
and names resume, scratch input outside inputs/, uncommitted as a count, a commit
card before the ending, a routable builds-on Run next, and inputs/ for old topics.
Generic fixture only (orders-platform, person A). Design snapshot `design-order-branch-commit`.
"""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_kit_1189 import GOAL, ROOT, SKILL, T, Base, GitHelpers, dr, kl, run

_uspec = importlib.util.spec_from_file_location("update_kit_1190", ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py")
uk = importlib.util.module_from_spec(_uspec)
_uspec.loader.exec_module(uk)
DESIGN = "docs/architecture/designs/orders-platform/designs/platform-first/design.md"


class TestOrder(Base):
    def design(self):
        return dr.Topic(self.tmp, T).design("platform-first")

    def test_stored_by_title_with_order_numbers(self):
        self.create()
        text = (self.tmp / DESIGN).read_text(encoding="utf-8")
        heads = re.findall(r"^- (.+)$", text.split("## Decisions", 1)[1], re.M)[:4]
        self.assertEqual(heads, sorted(heads, key=str.casefold))
        self.assertIn("  - Order: 1", text)
        self.assertEqual([x["title"] for x in dr.ordered(self.design()["decisions"])], [x if isinstance(x, str) else x["title"] for x in GOAL["decisions"]])

    def test_goal_md_has_no_decisions_list_and_goal_reads_order(self):
        self.create()
        self.ok("add-decision", "--topic", T, "--title", "Backup policy")
        goal = (self.tmp / "docs/architecture/designs/orders-platform/goal.md").read_text(encoding="utf-8")
        self.assertNotIn("## Decisions", goal)
        self.assertEqual(dr.Topic(self.tmp, T).goal()["decisions"][-1], "Backup policy")
        self.assertEqual(dr.find_decision(self.design(), "backup")["Order"], "5")

    def test_change_goal_rewrites_order(self):
        self.create()
        self.ok("change-goal", "--topic", T, "--reason", "data first", "--yes",
                inp={"decisions": ["Data in test", "Where orders live", "Resource group names", "Alerting owner"]})
        self.assertEqual(dr.find_decision(self.design(), "data in test")["Order"], "1")
        self.assertEqual(dr.Topic(self.tmp, T).goal()["decisions"][0], "Data in test")

    def test_parallel_adds_merge_without_conflict(self):
        GitHelpers.init(self)
        self.create()
        GitHelpers.commit(self, "base")
        self.git("switch", "-q", "-c", "side")
        self.ok("add-decision", "--topic", T, "--title", "Zebra crossing")
        GitHelpers.commit(self, "side")
        self.git("switch", "-q", f"design/{T}")
        self.ok("add-decision", "--topic", T, "--title", "Backup policy")
        GitHelpers.commit(self, "main side")
        out = subprocess.run(["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "merge", "-q", "--no-edit", "side"],
                             cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        titles = [x["title"] for x in self.design()["decisions"]]
        self.assertIn("Zebra crossing", titles)
        self.assertIn("Backup policy", titles)

    git = GitHelpers.git

    def test_old_file_migrates_from_the_goal_list(self):
        self.create()
        p = self.tmp / DESIGN
        p.write_text(re.sub(r"\n  - Order: \d+", "", p.read_text(encoding="utf-8")), encoding="utf-8")
        g = self.tmp / "docs/architecture/designs/orders-platform/goal.md"
        g.write_text(g.read_text(encoding="utf-8") + "\n## Decisions\n\n- Data in test\n- Where orders live\n- Alerting owner\n- Resource group names\n", encoding="utf-8")
        self.assertEqual(dr.Topic(self.tmp, T).goal()["decisions"], ["Data in test", "Where orders live", "Alerting owner", "Resource group names"])

    def test_old_file_without_goal_list_keeps_list_position(self):
        d = dr.parse_design("# Design: x\n\n## Decisions\n\n- B one\n  - State: open\n- A two\n  - State: open\n")
        self.assertTrue(d["migrated"])
        self.assertEqual([x["title"] for x in dr.ordered(d["decisions"])], ["B one", "A two"])


class TestSwitchBranch(GitHelpers, Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.create()
        self.commit("design")
        self.git("switch", "-q", "main")

    def test_card_then_switch_on_yes(self):
        res = self.ok("switch-branch", "--topic", T)
        self.assertEqual(res["card"]["words"], ["yes", "stop"])
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")
        res = self.ok("switch-branch", "--topic", T, "--yes")
        self.assertTrue(res["switched"])
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), f"design/{T}")

    def test_dirty_tree_is_refused_with_paths(self):
        (self.tmp / "loose.md").write_text("x", encoding="utf-8")
        err = self.refused("switch-branch", "--topic", T, "--yes")
        self.assertIn("loose.md", err)
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")

    def test_headless_is_refused(self):
        self.refused("--headless", "switch-branch", "--topic", T, "--yes")


class TestPendingGoalInputs(Base):
    def test_resume_offers_change_goal_for_a_saved_goal_file(self):
        self.create()
        f = self.tmp / "docs/architecture/designs/orders-platform/inputs/new-goal.json"
        f.write_text(json.dumps({"end_goal": "Orders run alone.", "decisions": ["Where orders live"]}), encoding="utf-8")
        res = self.ok("resume", "--topic", T)
        self.assertEqual([x["path"] for x in res["pending_goal_inputs"]], ["inputs/new-goal.json"])
        self.assertIn("never recreate the topic", res["pending_note"])
        self.ok("change-goal", "--topic", T, "--reason", "saved goal", "--yes", "--input", str(f))
        self.assertNotIn("pending_goal_inputs", self.ok("resume", "--topic", T))
        f.write_text(json.dumps({"end_goal": "Orders run alone, again."}), encoding="utf-8")
        self.assertIn("pending_goal_inputs", self.ok("resume", "--topic", T))

    def test_change_goal_copies_an_outside_input_into_inputs(self):
        self.create()
        self.ok("change-goal", "--topic", T, "--reason", "r", "--yes", inp={"end_goal": "New end."})
        folder = self.tmp / "docs/architecture/designs/orders-platform/inputs"
        self.assertEqual(len(list(folder.glob("goal-change-*.json"))), 1)
        self.assertNotIn("pending_goal_inputs", self.ok("resume", "--topic", T))

    def test_skill_says_never_recreate(self):
        text = (SKILL / "references/flow.md").read_text(encoding="utf-8")
        self.assertIn("Never offer to recreate a topic that already exists", text)


class TestCardLint(unittest.TestCase):
    def test_self_correction_and_two_questions(self):
        hits = kl.card_hits("Pick one? Or wait?", [("Move it", "deploy on the old plan, no: on the new plan")])
        self.assertTrue(any("two questions" in h for h in hits))
        self.assertTrue(any("corrects itself" in h for h in hits))
        for text in ("keep the queue, I mean the topic", "actually use the bus"):
            self.assertTrue(any("corrects itself" in h for h in kl.card_hits("Pick?", [("A", text)])))
        self.assertEqual(kl.card_hits("Pick one?", [("Keep it", "the queue stays as it is now")]), [])

    def test_rule_is_in_the_cards_reference(self):
        text = (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("corrects itself", text)


class TestKitCheck(GitHelpers, Base):
    def test_files_agree_in_the_kit(self):
        kc = dr.kit_check(self.tmp)
        self.assertTrue(kc["ok"], kc)
        self.assertEqual(kc["stated"], dr.SKILL_VERSION)

    def test_skill_md_marker_matches_script(self):
        self.assertIn(f"Skill files: {dr.SKILL_VERSION}", (SKILL / "SKILL.md").read_text(encoding="utf-8"))

    def test_older_stated_version_warns(self):
        with patch.object(dr, "SKILL_VERSION", "9.0.0"):
            kc = dr.kit_check(self.tmp)
        self.assertFalse(kc["ok"])
        self.assertEqual(kc["run"], "/crav1-update-kit")

    def test_branch_kit_behind_main_stops_resume_before_writing(self):
        wf = self.tmp / ".cursor/skills/crav1/crav1-docs/reference/workflow.md"
        wf.parent.mkdir(parents=True)
        self.init()
        wf.write_text("# Workflow\n\nKit version: 1.188.0\n", encoding="utf-8")
        self.commit("kit 1.188")
        self.create()
        self.commit("design")
        self.git("switch", "-q", "main")
        wf.write_text("# Workflow\n\nKit version: 1.190.0\n", encoding="utf-8")
        self.commit("kit 1.190")
        self.git("update-ref", "refs/remotes/origin/main", "main")
        self.git("switch", "-q", f"design/{T}")
        before = (self.tmp / DESIGN).read_text(encoding="utf-8")
        res = self.ok("--no-fetch", "resume", "--topic", T)
        self.assertTrue(res["kit_check"]["kit_behind_main"])
        self.assertEqual(res["branch_sync"]["state"], "behind")
        self.assertEqual(res["written"], [])
        self.assertEqual((self.tmp / DESIGN).read_text(encoding="utf-8"), before)
        res = self.ok("--no-fetch", "resume", "--topic", T, "--skip-kit-check")
        self.assertNotIn("before the topic is touched", res.get("note", ""))
        self.assertTrue(res["kit_check"]["kit_behind_main"])  # still warned


class TestUpdateKitFetch(unittest.TestCase):
    def test_default_dest_is_short_and_in_temp(self):
        dest = uk.default_dest("v1.190.0")
        self.assertEqual(dest.parent, Path(tempfile.gettempdir()))
        self.assertTrue(dest.name.startswith("ck11900"))

    def test_clone_uses_longpaths_and_verifies(self):
        dest = Path(tempfile.mkdtemp()) / "r"
        with patch("subprocess.run") as run_:
            run_.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
            uk.fetch_release("v1.190.0", dest, "https://example.invalid/kit.git")
        clone = run_.call_args_list[0].args[0]
        self.assertIn("core.longpaths=true", clone)
        self.assertIn("core.autocrlf=false", clone)
        self.assertEqual(run_.call_args_list[1].args[0][-2:], ["status", "--porcelain"])

    def test_incomplete_checkout_is_refused(self):
        dest = Path(tempfile.mkdtemp()) / "r"
        results = [subprocess.CompletedProcess([], 0, stdout="", stderr=""),
                   subprocess.CompletedProcess([], 0, stdout=" D .cursor/skills/crav1/a/very/long/path.md\n", stderr="")]
        with patch("subprocess.run", side_effect=results):
            with self.assertRaises(uk.Refuse) as caught:
                uk.fetch_release("v1.190.0", dest, "https://example.invalid/kit.git")
        self.assertIn("incomplete", caught.exception.message)
        self.assertIn("shorter --dest", caught.exception.message)

    def test_failed_clone_is_refused_with_reason(self):
        dest = Path(tempfile.mkdtemp()) / "r"
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 128, stdout="", stderr="fatal: Filename too long")):
            with self.assertRaises(uk.Refuse) as caught:
                uk.fetch_release("v1.190.0", dest, "https://example.invalid/kit.git")
        self.assertIn("Filename too long", caught.exception.message)


class TestUpdateKitEnding(unittest.TestCase):
    def test_reload_and_resume_for_open_topics(self):
        root = Path(tempfile.mkdtemp())
        (root / "docs/architecture/designs/orders-platform").mkdir(parents=True)
        (root / "docs/architecture/designs/orders-platform/goal.md").write_text("# Goal\n\nStatus: open\n", encoding="utf-8")
        (root / "docs/architecture/designs/orders-done").mkdir(parents=True)
        (root / "docs/architecture/designs/orders-done/goal.md").write_text("# Goal\n\nStatus: go-ahead 2026-11-01\n", encoding="utf-8")
        text = uk.ending_text(root, 3)
        self.assertTrue(text.startswith("Run next:\n"))
        self.assertIn("`Developer: Reload Window`", text)
        self.assertIn("`/crav1-design-architecture resume orders-platform`", text)
        self.assertNotIn("orders-done", text)
        self.assertNotIn("nothing needed now", text)
        self.assertIn("Uncommitted: 3 files", text)
        self.assertEqual(uk.ending_text(Path(tempfile.mkdtemp()), 0, updated=False), "Run next: nothing needed now.\n")


class TestScratchAndInputs(Base):
    def test_scratch_input_in_inputs_is_refused(self):
        self.create()
        f = self.tmp / "docs/architecture/designs/orders-platform/inputs/state.json"
        err = self.refused("ending", "--topic", T, inp={"phase": "design", "open": True}, inp_path=f)
        self.assertIn("session's temp folder", err)

    def test_scratch_input_in_temp_is_fine(self):
        self.create()
        f = Path(tempfile.mkdtemp()) / "state.json"
        out = self.ok("ending", "--topic", T, inp={"phase": "design", "open": True}, inp_path=f)
        self.assertTrue(out.startswith("Run next:"))

    def test_old_topic_gets_inputs_on_first_save(self):
        self.create()
        folder = self.tmp / "docs/architecture/designs/orders-platform/inputs"
        for f in folder.iterdir():
            f.unlink()
        folder.rmdir()
        self.ok("note", "--topic", T, "--title", "Scan", "--text", "orders-api has two queues")
        self.assertTrue((folder / "README.md").is_file())


class TestUncommitted(GitHelpers, Base):
    def test_true_is_counted_from_git_status(self):
        self.init()
        self.create()
        f = Path(tempfile.mkdtemp()) / "state.json"
        out = self.ok("ending", "--topic", T, inp={"phase": "design", "open": True, "uncommitted": True}, inp_path=f)
        n = len([x for x in self.git("status", "--porcelain", "-uall", "--", "docs/architecture/designs/orders-platform").splitlines()])
        self.assertGreater(n, 0)
        self.assertRegex(out, r"Uncommitted: \d+ files?\.")
        self.assertNotIn("True", out)

    def test_text_is_refused(self):
        with self.assertRaises(dr.Refused):
            dr.ending({"topic": T, "phase": "design", "open": True, "uncommitted": "the design folder"})


class TestCommit(GitHelpers, Base):
    def test_card_then_commit_on_yes(self):
        self.init()
        self.create()
        res = self.ok("commit", "--topic", T)
        self.assertEqual(res["card"]["words"], ["yes", "not-now"])
        self.assertTrue(res["paths"])
        res = self.ok("commit", "--topic", T, "--yes", "--message", "goal and first design",
                      )
        self.assertTrue(res["committed"])
        self.assertEqual(self.git("log", "-1", "--format=%s"), "Design orders-platform: goal and first design")
        self.assertEqual(self.ok("commit", "--topic", T)["paths"], [])

    def setUp(self):
        super().setUp()
        import os
        for k, v in (("GIT_AUTHOR_NAME", "person A"), ("GIT_AUTHOR_EMAIL", "a@example.com"),
                     ("GIT_COMMITTER_NAME", "person A"), ("GIT_COMMITTER_EMAIL", "a@example.com")):
            patcher = patch.dict(os.environ, {k: v})
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_linked_create_refuses_while_base_is_uncommitted(self):
        self.init()
        self.create()
        self.git("switch", "-q", "main")
        err = self.refused("create", "--topic", "orders-target", "--builds-on", T, inp={"ask": "target", "criteria": ["x"]})
        self.assertIn("commit the base topic", err)


class TestRunNextRoutes(Base):
    def routable(self, cmd):
        if cmd.startswith(("git ", "gh ")):
            return True
        m = re.match(r"^/(crav1-[a-z0-9-]+)(?: (.*))?$", cmd)
        if not m or not (ROOT / ".cursor/skills/crav1" / m.group(1)).is_dir():
            return False
        if m.group(1) != "crav1-design-architecture":
            return True
        words = (m.group(2) or "").split(None, 1)
        argv = ["route", "--word", words[0]] if words and words[0] in dr.START_WORDS else ["route"]
        if len(words) > 1 or (words and words[0] not in dr.START_WORDS):
            argv += ["--idea", words[1] if words and words[0] in dr.START_WORDS and len(words) > 1 else (m.group(2) or "")]
        code, out, err = run(self.tmp, *argv)
        return code == 0

    def test_every_printed_run_next_command_routes(self):
        states = [{"phase": "design", "open": True}, {"phase": "design", "parked": True, "uncommitted": 2},
                  {"phase": "go-ahead", "slices": ["orders-api"]}, {"phase": "merged"},
                  {"phase": "design", "builds_on": T, "idea": "orders target on the new platform"},
                  {"phase": "design", "question_open": True, "research_topic": "queue limits"},
                  {"phase": "design", "routed_requirement": True}]
        cmds = []
        for st in states:
            text = dr.ending(dict({"topic": T}, **st))
            cmds += re.findall(r"^`([^`]+)`$", text, re.M)
        self.assertIn(f"/crav1-design-architecture builds-on {T} orders target on the new platform", cmds)
        for cmd in cmds:
            self.assertTrue(self.routable(cmd), cmd)

    def test_builds_on_route_needs_base_and_idea(self):
        self.assertEqual(self.ok("route", "--word", "builds-on", "--idea", f"{T} orders target").strip().strip('"'), "builds-on")
        self.refused("route", "--word", "builds-on", "--idea", T)


if __name__ == "__main__":
    unittest.main()
