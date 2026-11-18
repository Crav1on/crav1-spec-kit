"""1.189.0: /crav1-design-architecture fixes from a live design session review.

Stored order (decisions and questions), typed endings, lean driver matching,
card rules with a kit-lint check, inputs and notes in the topic folder, a scope
round with detail decisions last, planned work read in Step 1, refused unknown
input keys, design-branch aware create and resume, and small fixes.
Generic fixture only (orders-platform). Design snapshot `design-order-notes-fixes`.
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
SKILL = ROOT / ".cursor/skills/crav1/crav1-design-architecture"
_spec = importlib.util.spec_from_file_location("design_run_1189", SKILL / "scripts/design_run.py")
dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dr)
_lspec = importlib.util.spec_from_file_location("kit_lint_1189", ROOT / "scripts/kit-lint.py")
kl = importlib.util.module_from_spec(_lspec)
_lspec.loader.exec_module(kl)

T = "orders-platform"
GOAL = {"ask": "split the orders platform", "end_goal": "Orders run as their own platform.",
        "drivers": ["Checkout does not wait (docs/system/landscape.md)", "One team runs orders: fewer people on call"],
        "constraints": [], "criteria": ["Checkout stays fast in prod"], "design": "platform-first",
        "decisions": ["Where orders live", {"title": "Resource group names", "detail": True}, "Alerting owner", "Data in test"]}


def run(root, *args, inp=None, inp_path=None):
    argv = ["--root", str(root)] + list(args)
    if inp is not None:
        f = Path(inp_path) if inp_path else Path(root) / "docs/architecture/designs" / "inputs.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(inp), encoding="utf-8")
        argv += ["--input", str(f)]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = dr.main(argv)
    if inp is not None:
        f.unlink(missing_ok=True)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "docs/architecture").mkdir(parents=True)
        (self.tmp / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- orders-api runs.\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ok(self, *args, **kw):
        code, out, err = run(self.tmp, *args, **kw)
        self.assertEqual(code, 0, err)
        return json.loads(out) if out.strip().startswith("{") else out

    def refused(self, *args, **kw):
        code, out, err = run(self.tmp, *args, **kw)
        self.assertEqual(code, 2, out)
        return err

    def create(self, goal=GOAL):
        return self.ok("create", "--topic", T, inp=goal)

    def titles(self):
        return [d["title"] for d in dr.Topic(self.tmp, T).design("platform-first")["decisions"]]


class TestStoredOrder(Base):
    def test_decisions_keep_the_order_added_and_resume_takes_the_first_open(self):
        self.create()
        self.assertEqual(self.titles(), ["Where orders live", "Resource group names", "Alerting owner", "Data in test"])
        self.ok("add-decision", "--topic", T, "--title", "Backup policy")
        self.assertEqual(self.titles()[-1], "Backup policy")
        self.assertEqual(self.ok("resume", "--topic", T)["next_decision"], "Where orders live")

    def test_z_before_a_stays(self):
        self.create(dict(GOAL, decisions=["Zone layout", "Access model"]))
        self.assertEqual(self.ok("resume", "--topic", T)["next_decision"], "Zone layout")

    def test_questions_keep_the_order_asked(self):
        self.create()
        self.ok("question", "--topic", T, "--text", "Who pays for the zone (person B decides)")
        self.ok("question", "--topic", T, "--text", "Are backups needed in test (person A knows)")
        self.ok("question", "--topic", T, "--text", "Who pays for the zone (person B decides)", "--stage", "first")
        qs = [q["text"] for q in dr.Topic(self.tmp, T).questions("platform-first")]
        self.assertEqual(qs, ["Who pays for the zone (person B decides)", "Are backups needed in test (person A knows)"])

    def test_change_goal_reorder_is_stored_in_design_md(self):
        self.create()
        self.ok("change-goal", "--topic", T, "--reason", "data first", "--yes",
                inp={"decisions": ["Data in test", "Where orders live", "Resource group names", "Alerting owner"]})
        self.assertEqual(self.titles(), ["Data in test", "Where orders live", "Resource group names", "Alerting owner"])


class TestEnding(unittest.TestCase):
    def end(self, **state):
        return dr.ending(dict({"topic": T, "phase": "design", "open": True}, **state))

    def test_waiting_list_is_one_line_per_item(self):
        out = self.end(waiting=["person A (subscription layout)", "person B (budget)"])
        self.assertIn("Waiting: person A (subscription layout)\nWaiting: person B (budget)\n", out)
        self.assertNotIn("['", out)

    def test_waiting_string_is_one_line(self):
        self.assertIn("Waiting: person A to decide the layout\n", self.end(waiting="person A to decide the layout"))

    def test_uncommitted_types(self):
        self.assertIn("Uncommitted: files in docs/architecture/designs/orders-platform/.", self.end(uncommitted=True))
        self.assertIn("Uncommitted: 1 file.", self.end(uncommitted=1))
        self.assertIn("Uncommitted: 3 files.", self.end(uncommitted=3))
        self.assertIn("Uncommitted: 2 files: `a.md`, `b.md`.", self.end(uncommitted=["a.md", "b.md"]))
        self.assertIn("Uncommitted: the design folder.", self.end(uncommitted="the design folder"))
        out = self.end(uncommitted=False, waiting=False)
        self.assertNotIn("True", out)
        self.assertNotIn("Uncommitted", out)
        self.assertTrue(out.startswith("Run next:\n"))

    def test_inputs_md_documents_the_types(self):
        text = (SKILL / "references/inputs.md").read_text(encoding="utf-8")
        self.assertIn("one `Waiting:` line per item", text)
        self.assertIn("a count, a list of paths, true for the topic folder", text)


class TestLeanDrivers(Base):
    def test_short_names_match_existing_drivers(self):
        self.create()
        before = dr.Topic(self.tmp, T).design("platform-first")["drivers"]
        self.ok("lean", "--topic", T, "--decision", "where orders", inp={"drivers": ["Checkout does not wait", "One team runs orders"], "leaning": "x"})
        d = dr.Topic(self.tmp, T).design("platform-first")
        self.assertEqual(d["drivers"], before)
        self.assertEqual(d["decisions"][0]["Drivers"], "Checkout does not wait; One team runs orders")

    def test_a_new_driver_is_added_once(self):
        self.create()
        for _ in range(2):
            self.ok("lean", "--topic", T, "--decision", "where orders", inp={"drivers": ["Try it in test first (from you, this session)"]})
        self.assertEqual(dr.Topic(self.tmp, T).design("platform-first")["drivers"].count("Try it in test first (from you, this session)"), 1)


class TestCards(unittest.TestCase):
    def test_skill_cards_pass_the_design_card_check(self):
        self.assertEqual(kl.design_card_problems(str(ROOT)), [])

    def test_check_flags_too_many_options_type_only_and_two_questions(self):
        text = ("Card: Which one?\n- **A (Recommended)** (`a`): settle with A now. Why: fits.\n- **B** (`b`): settle with B now.\n"
                "- **C** (`c`): settle with C now.\n- **D** (`d`): settle with D now.\n- **Keep talking** (`discuss`): talk it through more.\n\n"
                "Card: Create it? And name it?\n- **Yes (Recommended)** (`yes`): create the topic now. Why: ready.\n- **Change it**: type what to change here.\n")
        hits = [why for _, why in kl.design_card_hits(text)]
        self.assertTrue(any("5 options" in h for h in hits))
        self.assertTrue(any("Keep talking" in h for h in hits))
        self.assertTrue(any("Change it" in h for h in hits))
        self.assertTrue(any("more than one question" in h for h in hits))

    def test_flow_says_one_question_and_empty_other_is_asked_again(self):
        flow = (SKILL / "references/flow.md").read_text(encoding="utf-8")
        self.assertIn("One question per card", flow)
        self.assertIn("An empty Other, with no text, is a missing answer: ask that one question again.", flow)
        opts = (SKILL / "references/options.md").read_text(encoding="utf-8")
        self.assertIn("An empty Other is asked again; it is never an answer.", opts)


class TestInputsAndNotes(Base):
    def test_input_outside_the_repo_is_refused(self):
        outside = Path(tempfile.mkdtemp()) / "goal.json"
        try:
            err = self.refused("create", "--topic", T, inp=GOAL, inp_path=outside)
            self.assertIn("never in a temp folder", err)
        finally:
            shutil.rmtree(outside.parent, ignore_errors=True)

    def test_input_in_the_topic_inputs_folder_is_fine(self):
        self.ok("create", "--topic", T, inp=GOAL, inp_path=self.tmp / "docs/architecture/designs" / T / "inputs/goal.json")

    def test_note_appends_to_notes_md_and_is_allowed_in_prepare(self):
        self.create()
        self.ok("note", "--topic", T, "--kind", "scan", "--title", "improvement scan", inp={"items": ["shared deploy template: already planned (orders-api T4)", "alerts per env"]})
        self.ok("--headless", "note", "--topic", T, "--kind", "vision", "--title", "target sketch", "--text", "One platform per team.")
        text = (self.tmp / "docs/architecture/designs" / T / "notes.md").read_text(encoding="utf-8")
        self.assertIn("scan: improvement scan", text)
        self.assertIn("- alerts per env", text)
        self.assertIn("vision: target sketch\n\nOne platform per team.", text)

    def test_flow_saves_notes_before_parking(self):
        flow = (SKILL / "references/flow.md").read_text(encoding="utf-8")
        self.assertIn("`park` first saves anything discussed but not yet in a script move with `note`", flow)
        self.assertIn("inputs/<move>.json", flow)


class TestScopeAndDetail(Base):
    def test_detail_decision_comes_after_the_big_ones(self):
        self.create(dict(GOAL, decisions=[{"title": "Resource group names", "detail": True}, "Where orders live"]))
        self.assertEqual(self.ok("resume", "--topic", T)["next_decision"], "Where orders live")
        self.ok("skip", "--topic", T, "--decision", "where orders")
        self.assertEqual(self.ok("resume", "--topic", T)["next_decision"], "Resource group names")

    def test_flow_has_a_scope_round_in_framing(self):
        flow = (SKILL / "references/flow.md").read_text(encoding="utf-8")
        self.assertIn("Scope round, inside the framing: before any detailed decision", flow)
        self.assertIn("big shape first and detail last", flow)


class TestPlannedWork(unittest.TestCase):
    def test_step_1_reads_plans_tasks_and_build_maps(self):
        flow = (SKILL / "references/flow.md").read_text(encoding="utf-8")
        for name in ("plan.md", "tasks.md", "build-map.md"):
            self.assertIn(name, flow)
        self.assertIn("never propose it again", flow)
        self.assertIn("**Overlaps**", (SKILL / "references/options.md").read_text(encoding="utf-8"))


class TestInputKeys(Base):
    def test_unknown_keys_are_refused_by_name(self):
        err = self.refused("create", "--topic", T, inp=dict(GOAL, notes_to_replay=["x"], extra=1))
        self.assertIn("extra, notes_to_replay", err)
        self.create()
        err = self.refused("change-goal", "--topic", T, "--reason", "r", inp={"criteria": ["x"], "leans": {}})
        self.assertIn("leans", err)

    def test_notes_key_is_saved_with_note(self):
        self.create(dict(GOAL, notes=["D2 leans to one group per env", "small fix: tag names"]))
        text = (self.tmp / "docs/architecture/designs" / T / "notes.md").read_text(encoding="utf-8")
        self.assertIn("- D2 leans to one group per env", text)
        self.ok("change-goal", "--topic", T, "--reason", "add a criterion", "--yes", inp={"criteria": ["Checkout stays fast in prod", "Cheap"], "notes": "kept the old order"})
        self.assertIn("kept the old order", (self.tmp / "docs/architecture/designs" / T / "notes.md").read_text(encoding="utf-8"))


class TestBranches(Base):
    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.tmp, capture_output=True, text=True, check=True).stdout.strip()

    def init(self):
        self.git("init", "-q", "-b", "main")
        self.git("-c", "user.name=person A", "-c", "user.email=a@example.com", "commit", "-q", "--allow-empty", "-m", "start")

    def commit(self, msg):
        self.git("add", "-A")
        self.git("-c", "user.name=person A", "-c", "user.email=a@example.com", "commit", "-q", "-m", msg)

    def test_create_makes_the_design_branch(self):
        self.init()
        res = self.create()
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), f"design/{T}")
        self.assertEqual(res["branch_state"], "created from main")

    def test_create_refuses_when_the_branch_exists_elsewhere(self):
        self.init()
        self.git("branch", f"design/{T}")
        err = self.refused("create", "--topic", T, inp=GOAL)
        self.assertTrue(err.startswith("Run next:\n"))
        self.assertIn("Switch to the design branch:\n`git switch design/orders-platform`", err)

    def test_resume_on_the_wrong_branch_names_the_design_branch(self):
        self.init()
        self.create()
        self.commit("design")
        self.git("switch", "-q", "main")
        err = self.refused("resume", "--topic", T)
        self.assertEqual(err.strip(), "Run next:\nThe orders platform topic is on its design branch design/orders-platform, not on main.\n\n"
                         "Switch to the design branch:\n`git switch design/orders-platform`")

    def test_linked_topic_is_cut_from_the_base_branch(self):
        self.init()
        self.create()
        self.commit("base")
        self.git("switch", "-q", "main")
        res = self.ok("create", "--topic", "orders-target", "--builds-on", T, inp={"ask": "target", "criteria": ["x"]})
        self.assertEqual(res["branch_state"], f"created from design/{T}")
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "design/orders-target")


class TestSmallFixes(Base):
    def test_small_fix_is_listed_and_copied_at_go_ahead(self):
        self.create()
        self.ok("small-fix", "--topic", T, "--text", "Rename the test queue to orders-test")
        self.refused("small-fix", "--topic", T, "--text", "Rename the test queue to orders-test")
        text = (self.tmp / "docs/architecture/designs" / T / "designs/platform-first/design.md").read_text(encoding="utf-8")
        self.assertIn("## Small fixes", text)
        self.assertEqual(len(self.titles()), 4)
        self.ok("go-ahead", "--topic", T, "--accept-findings")
        spec = (self.tmp / "docs/architecture/spec.md").read_text(encoding="utf-8")
        self.assertIn("Small fixes (no design choice):\n- Rename the test queue to orders-test", spec)


class TestSnapshot(unittest.TestCase):
    def test_design_order_notes_fixes_snapshot(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/snapshot-check.py"), "--only", "design-order-notes-fixes"],
                              capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("design-order-notes-fixes: matches", proc.stdout)


if __name__ == "__main__":
    unittest.main()
