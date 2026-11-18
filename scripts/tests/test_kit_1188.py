"""1.188.0: /crav1-design-architecture change-goal and linked topics (--builds-on).

Generic fixture only: a contoso specs repo with an orders-platform base topic
and an orders-target topic that builds on it. Design snapshots
`design-goal-change` and `design-linked-topics` run through
scripts/snapshot-check.py.
"""
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-design-architecture/scripts/design_run.py"
_spec = importlib.util.spec_from_file_location("design_run_1188", SCRIPT)
dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dr)

BASE = "orders-platform"
LINKED = "orders-target"
GOAL = {"ask": "split the orders platform", "end_goal": "Orders run as their own platform.",
        "drivers": ["One team runs orders."], "constraints": ["Orders stay in one SQL store."],
        "criteria": ["Checkout stays fast in prod", "Can be tried in test before prod"],
        "design": "platform-first", "decisions": ["Where orders live", "Who releases orders", "How test gets data"]}
SQL = {"chosen": "One SQL database for orders", "options": [{"name": "One SQL database for orders"}, {"name": "Event log per service"}],
       "why": "the SQL store is already there", "deciders": "person A"}
PIPE = {"chosen": "A pipeline releases orders", "options": [{"name": "A pipeline releases orders"}, {"name": "Releases by hand"}],
        "why": "releases repeat the same way", "deciders": "person A"}
DATA = {"chosen": "Made-up data", "options": [{"name": "Made-up data"}, {"name": "Copy of prod data"}],
        "why": "no prod data in test", "deciders": "person A"}
TGOAL = {"ask": "the target on top of the platform", "end_goal": "The target reads orders.", "criteria": ["Does not block the platform"],
         "design": "target-first", "decisions": ["How the target reads orders"]}


def run(root, *args, inp=None):
    argv = ["--root", str(root)] + list(args)
    if inp is not None:
        f = Path(root) / ".input.json"
        f.write_text(json.dumps(inp), encoding="utf-8")
        argv += ["--input", str(f)]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = dr.main(argv)
    (Path(root) / ".input.json").unlink(missing_ok=True)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "docs/architecture").mkdir(parents=True)
        (self.tmp / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- orders-api runs.\n", encoding="utf-8")
        self.ok("create", "--topic", BASE, inp=GOAL)
        self.ok("settle", "--topic", BASE, "--decision", "where orders live", inp=SQL)
        self.ok("settle", "--topic", BASE, "--decision", "who releases", inp=PIPE)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ok(self, *args, inp=None):
        code, out, err = run(self.tmp, *args, inp=inp)
        self.assertEqual(code, 0, err)
        return json.loads(out) if out.strip().startswith("{") else out

    def refused(self, *args, inp=None):
        code, out, err = run(self.tmp, *args, inp=inp)
        self.assertEqual(code, 2, out)
        return err

    def files(self):
        return {str(p.relative_to(self.tmp)): p.read_text(encoding="utf-8") for p in sorted(self.tmp.rglob("*.md"))}

    def design(self, topic=BASE, name="platform-first"):
        return {d["title"]: d for d in dr.Topic(self.tmp, topic).design(name)["decisions"]}


class TestChangeGoal(Base):
    NEW = {"constraints": [], "criteria": ["Checkout stays fast in prod", "Can be tried in test before prod", "Does not block the target"]}

    def test_headless_is_refused_and_writes_nothing(self):
        before = self.files()
        err = self.refused("--headless", "change-goal", "--topic", BASE, "--reason", "SQL is out", "--yes", inp=self.NEW)
        self.assertIn("change-goal needs the user", err)
        self.assertEqual(self.files(), before)

    def test_without_yes_shows_old_and_new_and_writes_nothing(self):
        before = self.files()
        res = self.ok("change-goal", "--topic", BASE, "--reason", "SQL is out", inp=self.NEW)
        self.assertTrue(res["preview"])
        self.assertEqual(res["old"]["constraints"], ["Orders stay in one SQL store."])
        self.assertEqual(res["new"]["constraints"], [])
        self.assertEqual(self.files(), before)

    def test_change_is_logged_in_goal_md(self):
        self.ok("change-goal", "--topic", BASE, "--reason", "SQL is out", "--yes", inp=self.NEW)
        g = dr.Topic(self.tmp, BASE).goal()
        self.assertEqual(g["constraints"], [])
        self.assertIn("Does not block the target", g["criteria"])
        self.assertIn(": SQL is out", g["changes"])
        self.assertIn("Removed constraint: Orders stay in one SQL store.", g["changes"])
        self.assertIn("Added criterion: Does not block the target", g["changes"])
        self.assertEqual(g["decisions"][:3], ["How test gets data", "Where orders live", "Who releases orders"])

    def test_settled_decision_naming_a_removed_constraint_is_flagged(self):
        res = self.ok("change-goal", "--topic", BASE, "--reason", "SQL is out", "--yes", inp=self.NEW)
        self.assertEqual([f["decision"] for f in res["flagged"]], ["Where orders live"])
        d = self.design()
        self.assertEqual(d["Where orders live"]["State"], "reopened")
        self.assertIn("goal changed", d["Where orders live"]["Reopened"])
        self.assertEqual(d["Who releases orders"]["State"], "settled")
        self.assertEqual(self.ok("resume", "--topic", BASE)["next_decision"], "Where orders live")

    def test_reopen_list_and_rename_flag_settled_decisions(self):
        res = self.ok("change-goal", "--topic", BASE, "--reason", "names", "--yes",
                      inp={"renames": {"Who releases orders": "Who ships orders"}, "reopen": ["Where orders live"]})
        self.assertEqual(sorted(f["decision"] for f in res["flagged"]), ["Where orders live", "Who ships orders"])
        d = self.design()
        self.assertEqual(d["Who ships orders"]["Renamed from"], "Who releases orders")
        self.assertEqual(d["Who ships orders"]["State"], "reopened")

    def test_drop_keeps_the_decision_marked_dropped(self):
        self.ok("change-goal", "--topic", BASE, "--reason", "test data is out", "--yes",
                inp={"decisions": ["Where orders live", "Who releases orders"]})
        d = self.design()
        self.assertEqual(d["How test gets data"]["State"], "dropped")
        self.assertIn("test data is out", d["How test gets data"]["Dropped"])
        g = dr.Topic(self.tmp, BASE).goal()
        self.assertEqual(g["dropped"], {"How test gets data": "test data is out"})
        self.assertIn("How test gets data", g["decisions"])
        findings = self.ok("review", "--topic", BASE)["findings"]
        self.assertFalse(any("How test gets data" in f["text"] for f in findings))
        self.assertIn("refused", "refused " + self.refused("lean", "--topic", BASE, "--decision", "how test", inp={"leaning": "x"}))

    def test_reorder_is_logged_and_resume_follows_goal_order(self):
        self.ok("change-goal", "--topic", BASE, "--reason", "billing first", "--yes",
                inp={"decisions": ["Who releases orders", "How billing reads orders", "Where orders live", "How test gets data"]})
        g = dr.Topic(self.tmp, BASE).goal()
        self.assertIn("Reordered decisions", g["changes"])
        self.assertIn("Added decision: How billing reads orders", g["changes"])
        self.assertEqual(self.ok("resume", "--topic", BASE)["next_decision"], "How billing reads orders")

    def test_open_questions_and_leans_on_surviving_decisions_are_kept(self):
        self.ok("lean", "--topic", BASE, "--decision", "how test", inp={"options": [{"name": "Made-up data"}], "leaning": "Made-up data"})
        self.ok("question", "--topic", BASE, "--decision", "how test", "--text", "May test hold prod orders (person B decides)")
        self.ok("change-goal", "--topic", BASE, "--reason", "SQL is out", "--yes", inp=self.NEW)
        d = self.design()
        self.assertEqual(d["How test gets data"]["Leaning"], "Made-up data")
        self.assertEqual(len(dr.Topic(self.tmp, BASE).questions("platform-first")), 1)

    def test_same_goal_is_refused(self):
        self.refused("change-goal", "--topic", BASE, "--reason", "nothing", "--yes", inp={})


class TestLinkedTopics(Base):
    def link(self):
        return self.ok("create", "--topic", LINKED, "--builds-on", BASE, inp=TGOAL)

    def test_create_records_builds_on_branch_and_fixed_inputs(self):
        res = self.link()
        self.assertEqual(res["branch_from"], f"design/{BASE}")
        self.assertEqual(res["git"], [f"git switch design/{BASE}", f"git switch -c design/{LINKED}"])
        self.assertEqual(res["update_from_base"], f"git merge design/{BASE}")
        text = (self.tmp / f"docs/architecture/designs/{LINKED}/goal.md").read_text(encoding="utf-8")
        self.assertIn(f"- Builds on: {BASE}", text)
        g = dr.Topic(self.tmp, LINKED).goal()
        self.assertEqual([x.split(": ")[0] for x in g["fixed"]], ["Where orders live", "Who releases orders"])
        self.assertIn("One SQL database for orders", g["fixed"][0])

    def test_unknown_base_is_refused(self):
        self.refused("create", "--topic", LINKED, "--builds-on", "no-such-topic", inp=TGOAL)

    def test_resume_shows_decisions_settled_in_the_base_since_last_run(self):
        self.link()
        self.ok("settle", "--topic", BASE, "--decision", "how test", inp=DATA)
        res = self.ok("resume", "--topic", LINKED)
        self.assertEqual(len(res["base_settled_since"]), 1)
        self.assertTrue(res["base_settled_since"][0].startswith("How test gets data: Made-up data"))
        self.assertEqual(self.ok("resume", "--topic", LINKED)["base_settled_since"], [])

    def test_local_change_of_a_base_decision_is_refused_with_a_revisit(self):
        self.link()
        err = self.refused("settle", "--topic", LINKED, "--decision", "where orders live", inp=SQL)
        self.assertIn("settled in the base topic orders-platform", err)
        self.assertIn("revisit --topic orders-target", err)
        self.refused("add-decision", "--topic", LINKED, "--title", "Where orders live")
        res = self.ok("revisit", "--topic", LINKED, "--decision", "where orders live", "--reason", "the target needs a read copy")
        self.assertEqual(res["revisit"]["decision"], "Where orders live")
        d = self.design()
        self.assertEqual(d["Where orders live"]["State"], "reopened")
        self.assertIn("revisit from topic orders-target", d["Where orders live"]["Reopened"])
        self.assertTrue(res["ending"].startswith("Run next:\n"))
        self.assertIn("`/crav1-design-architecture resume orders-platform`", res["ending"])
        self.assertNotIn("Next:", res["ending"].replace("Run next:", ""))
        self.assertEqual(self.ok("resume", "--topic", LINKED)["base_reopened_since"][0].split(": ")[0], "Where orders live")

    def test_revisit_needs_a_linked_topic(self):
        self.refused("revisit", "--topic", BASE, "--decision", "where", "--reason", "x")

    def test_status_shows_links_both_ways(self):
        self.link()
        links = self.ok("status")["links"]
        self.assertEqual(links[LINKED]["builds_on"], BASE)
        self.assertEqual(links[BASE]["built_on_by"], [LINKED])

    def _git(self, *args):
        subprocess.run(["git", *args], cwd=self.tmp, check=True, capture_output=True)

    def test_go_ahead_waits_for_the_base_design_pr_to_merge(self):
        self.link()
        err = self.refused("go-ahead", "--topic", LINKED, "--accept-findings")
        self.assertTrue(err.startswith("Run next:\n"))
        self.assertIn("Waiting: go-ahead on orders-platform", err)
        self.ok("go-ahead", "--topic", BASE, "--accept-findings")
        self._git("init", "-q", "-b", "main")
        self._git("-c", "user.name=person A", "-c", "user.email=a@example.com", "commit", "-q", "--allow-empty", "-m", "start")
        err = self.refused("go-ahead", "--topic", LINKED, "--accept-findings")
        self.assertIn("Waiting: the orders-platform design pull request (design/orders-platform) to merge into main.", err)
        self.assertIn("`/crav1-design-architecture resume orders-target`", err)
        self._git("add", "-A")
        self._git("-c", "user.name=person A", "-c", "user.email=a@example.com", "commit", "-q", "-m", "merge design")
        res = self.ok("go-ahead", "--topic", LINKED, "--accept-findings")
        self.assertTrue(res["copied"])
        spec = (self.tmp / "docs/architecture/spec.md").read_text(encoding="utf-8")
        self.assertIn("Builds on: topic orders-platform", spec)

    def test_base_merged_flag_allows_go_ahead_without_git(self):
        self.link()
        self.ok("go-ahead", "--topic", BASE, "--accept-findings")
        self.refused("go-ahead", "--topic", LINKED, "--accept-findings")
        self.assertTrue(self.ok("go-ahead", "--topic", LINKED, "--accept-findings", "--base-merged")["copied"])


class TestDesignSnapshots(unittest.TestCase):
    def test_design_snapshots_match(self):
        for name in ("design-goal-change", "design-linked-topics"):
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/snapshot-check.py"), "--only", name],
                                  capture_output=True, text=True, encoding="utf-8", timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn(f"{name}: matches", proc.stdout)


if __name__ == "__main__":
    unittest.main()
