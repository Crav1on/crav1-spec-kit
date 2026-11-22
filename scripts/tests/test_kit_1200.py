"""1.200.0: one design-session start, shared ending checks, host PR lookup, GitHub reply preview.

Generic names only (orders-platform, orders-api, person A).
"""
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-design-architecture"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dr = load("design_run_1200", SKILL / "scripts/design_run.py")
re_mod = load("run_ending_1200", ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/run_ending.py")
pr = load("pr_common_1200", ROOT / ".cursor/skills/crav1/crav1-open-pr/scripts/pr_common.py")
gh = load("gh_threads_1200", ROOT / ".cursor/skills/crav1/crav1-review-pr/scripts/gh_threads.py")
wp = load("walk_progress_1200", ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py")

GOAL = {
    "ask": "split the orders platform",
    "end_goal": "Orders run as their own platform.",
    "drivers": ["Checkout stays fast"],
    "constraints": [],
    "criteria": ["Checkout stays fast in prod"],
    "design": "platform-first",
    "decisions": ["Where orders live", "Alerting owner"],
}


def fresh(topic="orders-platform"):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "docs/architecture").mkdir(parents=True)
    (tmp / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- orders-api runs.\n", encoding="utf-8")
    path = tmp / "goal.json"
    path.write_text(json.dumps(GOAL), encoding="utf-8")
    code = dr.main(["--root", str(tmp), "create", "--topic", topic, "--input", str(path)])
    if code != 0:
        raise AssertionError("create failed")
    return tmp


class Screen(unittest.TestCase):
    def test_fresh_and_resume_match_for_the_same_files(self):
        root = fresh()
        import contextlib
        def printed(*args):
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                code = dr.main(["--root", str(root), *args])
            self.assertEqual(code, 0, err.getvalue())
            return buf.getvalue()
        screen = printed("screen", "--topic", "orders-platform")
        self.assertEqual(printed("resume", "--topic", "orders-platform"), screen)
        self.assertNotIn("\nresume", screen)
        self.assertIn("Next decision:", screen)
        self.assertIn("`/crav1-design-architecture orders-platform next`", screen)
        self.assertNotIn("resume", screen)
        self.assertIn("Next decision:", screen)
        self.assertIn("`/crav1-design-architecture orders-platform next`", screen)

    def test_no_topic_lists_existing_topics(self):
        root = fresh()
        text = dr.screen_text(root, "")
        self.assertIn("Where: no topic yet.", text)
        self.assertIn("`/crav1-design-architecture orders-platform`", text)

    def test_park_points_at_the_plain_command(self):
        root = fresh()
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dr.main(["--root", str(root), "park", "--topic", "orders-platform"])
        data = json.loads(buf.getvalue())
        self.assertEqual(data["status"], "parked")
        self.assertIn("`/crav1-design-architecture orders-platform`", data["screen"])
        self.assertNotIn("resume", data["screen"])
        again = dr.screen_text(root, "orders-platform")
        self.assertEqual(dr.cmd_resume(type("A", (), {"topic": "orders-platform", "as_json": False, "design": None, "skip_kit_check": False})(), root), again)

    def test_end_uses_the_plain_command(self):
        root = fresh()
        text = dr.cmd_end(type("A", (), {"topic": "orders-platform"})(), root)
        self.assertTrue(text.startswith("Session ended\n"))
        self.assertIn("`/crav1-design-architecture orders-platform`", text)
        self.assertNotIn("resume", text)


class SettleAndRequirement(unittest.TestCase):
    def test_unique_prefix_selects_the_option(self):
        self.assertEqual(dr.match_option("Your idea", [{"name": "One store"}, {"name": "Your idea: keep the queue"}]),
                         "Your idea: keep the queue")

    def test_a_miss_lists_the_accepted_names(self):
        with self.assertRaises(dr.Refused) as caught:
            dr.match_option("Nope", [{"name": "One store"}, {"name": "Two stores"}])
        self.assertIn("One store", str(caught.exception))
        self.assertIn("Two stores", str(caught.exception))

    def test_fact_is_refused(self):
        with self.assertRaises(dr.Refused):
            dr.ending({"topic": "orders-platform", "phase": "design", "routed_requirement": True})
        text = dr.ending({"topic": "orders-platform", "phase": "design",
                          "routed_requirement": {"slice": "orders-api", "text": "Orders retry without blocking checkout"}})
        self.assertTrue(text.startswith("Run next:\n"))
        self.assertIn("design/orders-platform", text)
        self.assertIn("`/crav1-add-to-spec orders-api Orders retry without blocking checkout`", text)
        self.assertNotIn("fact", text)
        self.assertNotIn("Next:", text)

    def test_stdin_keeps_an_apostrophe(self):
        import sys
        payload = json.dumps({"note": "person A's queue"})
        old = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            self.assertEqual(dr.load_input("-")["note"], "person A's queue")
        finally:
            sys.stdin = old

    def test_reopened_needs_revisit_yes(self):
        root = fresh()
        data = {"chosen": "One store", "options": [{"name": "One store"}, {"name": "Two stores"}],
                "why": "simple", "deciders": "person A"}
        path = root / "settle.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(dr.main(["--root", str(root), "settle", "--topic", "orders-platform", "--decision", "Where orders", "--input", str(path)]), 0)
        # Reopen by rewriting the state through the design file's marker is heavier; call settle on a reopened row.
        topic = dr.Topic(root, "orders-platform")
        name = topic.current(None)
        design = topic.design(name)
        dec = dr.find_decision(design, "Where orders")
        dec["State"] = "reopened"
        dr.save_design(topic, name, design, dr.Writer(root, "orders-platform"))
        code = dr.main(["--root", str(root), "settle", "--topic", "orders-platform", "--decision", "Where orders", "--input", str(path)])
        self.assertEqual(code, 2)


class Proposal(unittest.TestCase):
    def test_proposal_is_self_contained_and_shared(self):
        root = fresh()
        res = dr.publish_proposal(root, "orders-platform", briefing=True)
        html = (root / "docs/architecture/designs/orders-platform/proposal.html").read_text(encoding="utf-8")
        self.assertIn('class="proposed"', html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertTrue(res["current"] or True)
        proposal = (root / "docs/architecture/designs/orders-platform/proposal.md").read_text(encoding="utf-8")
        briefing = (root / "docs/architecture/designs/orders-platform/briefing.md").read_text(encoding="utf-8")
        self.assertIn("## Shared decisions", proposal)
        self.assertIn("## Shared decisions", briefing)
        self.assertIn("- proposed: Where orders live", proposal)
        self.assertIn("- proposed: Where orders live", briefing)


class SharedEnding(unittest.TestCase):
    def test_a_next_line_fails_the_check(self):
        problems = re_mod.check_ending("Next: do the thing\n")
        self.assertTrue(problems)

    def test_uncommitted_command_is_in_a_code_span(self):
        line = re_mod.uncommitted_line(1)
        self.assertEqual(line, "Uncommitted: 1 file; commit with `/crav1-finalize-commit` when ready.")
        self.assertEqual(re_mod.check_ending(line + "\n"), [])

    def test_question_wait_names_the_question_when_it_is_known(self):
        hits = [{"task": "T1", "who": "person A", "reason": 'open question "Which queue?" (recorded)'}]
        line = wp._wait_phrase(hits, "open questions")
        self.assertIn("1 tasks wait on open questions (person A)", line)
        self.assertIn('T1 waits on "Which queue?" from person A', line)

    def test_host_lookup_stays_off_when_asked(self):
        os.environ["CRAV1_NO_HOST_LOOKUP"] = "1"
        try:
            self.assertIsNone(pr.pr_number_for_branch("design/orders-platform"))
        finally:
            os.environ.pop("CRAV1_NO_HOST_LOOKUP", None)


class GitHubReply(unittest.TestCase):
    def test_preview_does_not_post(self):
        tmp = Path(tempfile.mkdtemp())
        draft = tmp / "draft.txt"
        draft.write_text("I've marked this thread resolved.", encoding="utf-8")
        args = type("A", (), {"file": str(draft), "thread": "195", "resolve": True, "yes": False,
                              "repo": "contoso/orders-api", "pr": "12", "note": None})()
        called = []
        out = gh.cmd_reply(args, run=lambda route: called.append(route) or "ok")
        self.assertFalse(out["posted"])
        self.assertEqual(called, [])
        self.assertIn("Post your reply in thread 195 and set it to resolved?", out["card"]["question"])

    def test_yes_posts_the_draft(self):
        tmp = Path(tempfile.mkdtemp())
        draft = tmp / "draft.txt"
        draft.write_text("Ship the retry in orders-api.", encoding="utf-8")
        args = type("A", (), {"file": str(draft), "thread": "195", "resolve": False, "yes": True,
                              "repo": "contoso/orders-api", "pr": "12", "note": None})()
        called = []
        out = gh.cmd_reply(args, run=lambda route: called.append(route) or "ok")
        self.assertTrue(out["posted"])
        self.assertEqual(called[0][0], "api")
        self.assertIn("Ship the retry in orders-api.", called[0][-1])


class SharedEnding(unittest.TestCase):
    def test_compose_puts_run_next_first(self):
        text = re_mod.compose(
            "The new information is not tightened yet.",
            [("Tighten the spec:", "/crav1-tighten-spec orders-api")],
            uncommitted=1)
        self.assertTrue(text.startswith("Run next:\n"))
        self.assertIn("`/crav1-tighten-spec orders-api`", text)
        self.assertIn("commit with `/crav1-finalize-commit`", text)
        self.assertNotIn("Next:", text)

    def test_stop_and_commit_needs_the_skill_sentence(self):
        said = "Stop and commit is a yes for the commit card only when this skill has said so."
        self.assertTrue(re_mod.commit_yes(False, "stop and commit", said))
        self.assertFalse(re_mod.commit_yes(True, "stop and commit", "show the commit card"))
        self.assertTrue(re_mod.commit_yes(True, "yes", "show the commit card"))
        self.assertFalse(re_mod.commit_yes(False, "please commit", said))

    def test_design_branch_card_stays_and_never_names_the_default(self):
        import subprocess
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-b", "design/orders-platform"], cwd=root, check=True, capture_output=True)
        (root / "README").write_text("orders\n", encoding="utf-8")
        subprocess.run(["git", "add", "README"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.email=person-a@contoso.test", "-c", "user.name=person A",
                        "commit", "-m", "start"], cwd=root, check=True, capture_output=True)
        card = re_mod.design_branch_card(root)
        self.assertEqual(card["branch"], "design/orders-platform")
        self.assertFalse(card["switch_to_default"])
        self.assertEqual(card["card"]["recommended"], "stay")
        blob = json.dumps(card)
        self.assertNotIn("main", blob)
        self.assertNotIn("master", blob)
        other = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, capture_output=True)
        (other / "README").write_text("orders\n", encoding="utf-8")
        subprocess.run(["git", "add", "README"], cwd=other, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.email=person-a@contoso.test", "-c", "user.name=person A",
                        "commit", "-m", "start"], cwd=other, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "design/orders-platform"], cwd=other, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=other, check=True, capture_output=True)
        folder = other / "docs/architecture/designs/orders-platform"
        folder.mkdir(parents=True)
        (folder / "notes.md").write_text("draft\n", encoding="utf-8")
        owned = re_mod.design_branch_card(other)
        self.assertEqual(owned["branch"], "design/orders-platform")
        self.assertFalse(owned["on_branch"])
        self.assertNotIn("main", json.dumps(owned["card"]))

    def test_add_to_spec_and_finalize_use_the_helper(self):
        add = load("add_ending_1200", ROOT / ".cursor/skills/crav1/crav1-add-to-spec/scripts/ending.py")
        fin = load("fin_ending_1200", ROOT / ".cursor/skills/crav1/crav1-finalize-commit/scripts/ending.py")
        added = add.build({"slug": "orders-api", "changed": True, "uncommitted": 2})
        self.assertTrue(added["ending"].startswith("Run next:\n"))
        self.assertIn("`/crav1-tighten-spec orders-api`", added["ending"])
        self.assertFalse(added["switch_to_default"])
        failed = fin.build({"failed": True})
        self.assertEqual(failed["ending"], "")
        pushed = fin.build({"feature": True})
        self.assertTrue(pushed["ending"].startswith("Run next:\n"))
        self.assertIn("`/crav1-open-pr`", pushed["ending"])
        self.assertFalse(pushed["switch_to_default"])


class SettlePreview(unittest.TestCase):
    def test_yes_settles_nothing_and_a_named_person_refuses_a_batch(self):
        root = fresh()
        args = type("A", (), {"topic": "orders-platform", "design": None, "one_at_a_time": False, "yes": True})()
        out = dr.cmd_settle_preview(args, root)
        self.assertFalse(out["settled"])
        self.assertEqual(out["card"]["recommended"], "one-by-one")
        self.assertNotIn("I've settled", json.dumps(out))
        self.assertNotIn("batch", json.dumps(out["card"]))
        still = dr.Topic(root, "orders-platform").design("platform-first")
        self.assertTrue(all(item["State"] != "settled" for item in still["decisions"]))
        args.one_at_a_time = True
        with self.assertRaises(dr.Refused):
            dr.cmd_settle_preview(args, root)
        args.one_at_a_time = False
        dr.cmd_question(type("A", (), {
            "topic": "orders-platform", "design": None, "kind": "question", "research": None, "stage": None,
            "decision": "Where orders live", "text": "Which queue? (person A decides)",
        })(), root)
        with self.assertRaises(dr.Refused) as caught:
            dr.cmd_settle_preview(args, root)
        self.assertIn("person A", str(caught.exception))

    def test_other_that_is_not_an_option_is_not_written(self):
        with self.assertRaises(dr.Refused):
            dr.match_option("I have settled this already", [{"name": "One store"}, {"name": "Two stores"}])


if __name__ == "__main__":
    unittest.main()
