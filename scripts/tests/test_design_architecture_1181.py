"""1.181.0: /crav1-design-architecture and its design_run.py state machine.

Fixture: a contoso specs repo with an orders-api slice. Snapshot folders under
scripts/tests/snapshots/design-architecture/ hold the expected sandbox and
go-ahead output for the main flows (set UPDATE_DESIGN_SNAPSHOTS=1 to rewrite).
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-design-architecture"
SCRIPT = SKILL / "scripts/design_run.py"
SNAP = Path(__file__).resolve().parent / "snapshots" / "design-architecture"
TOPIC = "orders-payment-retry"

_spec = importlib.util.spec_from_file_location("design_run_1181", SCRIPT)
dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dr)

GOAL = {
    "ask": "orders should retry failed payments without blocking checkout",
    "end_goal": "Failed payments retry without checkout waiting.",
    "drivers": ["Checkout does not wait. (from you, this session)", "One team runs it. (docs/system/landscape.md)"],
    "constraints": ["ADR 0001 inline retry is accepted."],
    "criteria": ["Checkout stays fast in prod", "Can be tried in test before prod"],
    "design": "queue-in-orders-api",
    "design_title": "queue in orders-api",
    "decisions": ["Where a failed payment waits before retry", "Who owns the retry policy"],
}
SETTLE = {
    "chosen": "Retry queue owned by orders-api",
    "options": [
        {"name": "Retry queue owned by orders-api", "good": ["checkout does not wait"]},
        {"name": "Retry table polled by a scheduler", "bad": ["polling delay"], "not_chosen": "slower and adds a scheduler"},
        {"name": "Shared retry config", "yours": True, "not_chosen": "nobody owns it"},
    ],
    "why": "checkout stays fast and one team runs it",
    "drivers": ["Checkout does not wait", "One team runs it"],
    "end_state": "orders-api owns a retry queue. Checkout stays fast in prod. The queue is tried in test before prod.",
    "diagram": "flowchart LR\n  A[orders-api] -.->|planned| Q[(retry queue)]",
    "sources": ["docs/environments/test.md"],
    "deciders": "person A",
}
SETTLE2 = {
    "chosen": "orders-api owns the policy",
    "options": [{"name": "orders-api owns the policy"}, {"name": "payments service owns the policy"}],
    "why": "fewer teams on call",
    "deciders": "person A",
}
CUSTOMER = [
    "baltic cable", "balticcable", "nrcc", "fn-nrcc", "tc-amp", "bc-operations", "arvid", "cederberg", "oscar",
    "kristian", "volue", "evangelos", "krokos", "microstep", "lakshmin", "ravindran", "stretch",
]


def make_fixture(root: Path) -> None:
    (root / "docs/architecture").mkdir(parents=True)
    (root / "docs/environments").mkdir(parents=True)
    (root / "docs/system/adr").mkdir(parents=True)
    (root / "docs/specs/orders-api/adr").mkdir(parents=True)
    (root / "docs/architecture/spec.md").write_text(
        "# Architecture\n\n## Confirmed\n\n- orders-api runs on the contoso cloud account. (`infra/main.bicep`)\n\n"
        "## Accepted from a guess\n\n## Open questions\n\n- Who owns the payments service on call (person B knows)\n"
        "  - Asked: person B, 2026-11-10\n", encoding="utf-8")
    (root / "docs/environments/test.md").write_text("# test\n", encoding="utf-8")
    (root / "docs/environments/prod.md").write_text("# prod\n", encoding="utf-8")
    (root / "docs/system/adr/0001-inline-retry.md").write_text("# ADR 0001: Inline retry\n\n- Status: accepted\n", encoding="utf-8")
    (root / "docs/system/diagrams.md").write_text("# Diagrams\n", encoding="utf-8")
    (root / "docs/specs/orders-api/spec.md").write_text("# orders-api\n\n## Open questions\n\n- \n", encoding="utf-8")


def run(root, *args, headless=False, inp=None):
    argv = ["--root", str(root)] + (["--headless"] if headless else []) + list(args)
    if inp is not None:
        f = Path(root) / ".input.json"
        f.write_text(json.dumps(inp), encoding="utf-8")
        argv += ["--input", str(f)]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = dr.main(argv)
    try:
        (Path(root) / ".input.json").unlink()
    except FileNotFoundError:
        pass
    return code, out.getvalue(), err.getvalue()


def tree(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and ".git" not in p.parts and p.name != ".input.json":
            txt = p.read_text(encoding="utf-8")
            out[str(p.relative_to(root))] = re.sub(r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD", txt)
    return out


def invariants(root: Path, topic: str) -> list:
    """The script's writes agree with each other."""
    problems = []
    t = dr.Topic(root, topic)
    goal = t.goal()
    if not goal["criteria"]:
        problems.append("goal has no criteria")
    for name in t.designs():
        d = t.design(name)
        drafts = {p.name for p in (t.ddir(name) / "adr").glob("*.md")}
        for dec in d["decisions"]:
            if dec["State"] not in dr.STATES:
                problems.append(f"{name}: unknown state {dec['State']}")
            if dec["State"] == "settled":
                ref = dec.get("Draft ADR", "")
                if Path(ref).name not in drafts:
                    problems.append(f"{name}: settled decision without its draft ADR: {dec['title']}")
            if dec["State"] in ("to-question", "to-research"):
                if not any(q.get("decision") == dec["title"] for q in t.questions(name)):
                    problems.append(f"{name}: {dec['title']} points at a question that is not in questions.md")
        for q in t.questions(name):
            if not re.search(r"\([^)]*\)\s*$", q["text"]):
                problems.append(f"{name}: question without who: {q['text']}")
        for st in t.stages(name):
            if not st.get("reason"):
                problems.append(f"{name}: stage without a reason")
    if len(t.designs()) > 1:
        comp = (t.dir / "compare.md").read_text(encoding="utf-8")
        for name in t.designs():
            if name not in comp:
                problems.append(f"compare.md misses {name}")
    spec = (root / "docs/architecture/spec.md").read_text(encoding="utf-8")
    for name in t.designs():
        d = t.design(name)
        if d["status"] == "chosen":
            if f"designs/{topic}/designs/{name}/" not in spec:
                problems.append("chosen design is not copied with a Designed in link")
        elif f"designs/{topic}/designs/{name}/`" in spec:
            problems.append(f"design {name} is copied but not chosen")
    return problems


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_fixture(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def create(self):
        code, out, err = run(self.tmp, "create", "--topic", TOPIC, inp=GOAL)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def settle(self, decision="where a failed payment", data=SETTLE, design=None):
        args = ["settle", "--topic", TOPIC, "--decision", decision] + (["--design", design] if design else [])
        code, out, err = run(self.tmp, *args, inp=data)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def outside(self, before):
        after = tree(self.tmp)
        return sorted(k for k in set(after) | set(before)
                      if not k.startswith("docs/architecture/designs/") and after.get(k) != before.get(k))

    def check_snapshot(self, name):
        got = {k: v for k, v in tree(self.tmp).items()}
        folder = SNAP / name
        if os.environ.get("UPDATE_DESIGN_SNAPSHOTS"):
            shutil.rmtree(folder, ignore_errors=True)
            for rel, txt in got.items():
                (folder / rel).parent.mkdir(parents=True, exist_ok=True)
                (folder / rel).write_text(txt, encoding="utf-8")
        want = {str(p.relative_to(folder)): p.read_text(encoding="utf-8") for p in sorted(folder.rglob("*")) if p.is_file()}
        self.assertEqual(sorted(got), sorted(want), f"snapshot {name}: file list differs")
        for rel in want:
            self.assertEqual(got[rel], want[rel], f"snapshot {name}: {rel} differs")


class TestMoves(Base):
    def test_create_layout_snapshot(self):
        res = self.create()
        self.assertEqual(res["branch"], f"design/{TOPIC}")
        self.check_snapshot("create")
        self.assertEqual(invariants(self.tmp, TOPIC), [])

    def test_settle_writes_draft_adr_from_template_with_every_option(self):
        self.create()
        before = tree(self.tmp)
        res = self.settle()
        self.assertEqual(self.outside(before), [])
        adr = (self.tmp / res["adr"]).read_text(encoding="utf-8")
        self.assertIn("- Status: draft", adr)
        self.assertIn("- Deciders: person A", adr)
        for o in SETTLE["options"]:
            self.assertIn(f"- {o['name']}", adr)
        self.assertIn("Shared retry config (your idea)", adr)
        self.assertIn("## Pros and cons of the options", adr)
        self.assertIn("Not chosen: nobody owns it", adr)
        diag = (self.tmp / f"docs/architecture/designs/{TOPIC}/designs/queue-in-orders-api/diagrams.md").read_text()
        self.assertIn("-.->|planned|", diag)
        self.check_snapshot("settle")
        self.assertEqual(invariants(self.tmp, TOPIC), [])

    def test_format_round_trips(self):
        self.create()
        self.settle()
        p = self.tmp / f"docs/architecture/designs/{TOPIC}/designs/queue-in-orders-api/design.md"
        txt = p.read_text(encoding="utf-8")
        self.assertEqual(dr.render_design(dr.parse_design(txt)), txt)
        g = self.tmp / f"docs/architecture/designs/{TOPIC}/goal.md"
        self.assertEqual(dr.render_goal(dr.parse_goal(g.read_text())), g.read_text())

    def test_decisions_found_by_words_and_kept_in_sorted_place(self):
        self.create()
        run(self.tmp, "add-decision", "--topic", TOPIC, "--title", "How the user sees a payment in retry")
        d = dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api")
        titles = [x["title"] for x in d["decisions"]]
        self.assertEqual(titles, sorted(titles, key=str.casefold))
        code, _, err = run(self.tmp, "skip", "--topic", TOPIC, "--decision", "retry")
        self.assertEqual(code, 2)
        self.assertIn("no single decision", err)

    def test_two_people_adding_decisions_merge_without_conflict(self):
        self.create()
        git = lambda *a: subprocess.run(["git", *a], cwd=self.tmp, capture_output=True, text=True, check=True)
        git("init", "-q")
        git("config", "user.name", "person A")
        git("config", "user.email", "a@example.com")
        git("add", "-A")
        git("commit", "-qm", "base")
        git("checkout", "-qb", "a")
        run(self.tmp, "add-decision", "--topic", TOPIC, "--title", "Alpha decision on dead letters")
        git("commit", "-qam", "a")
        git("checkout", "-q", "-")
        git("checkout", "-qb", "b")
        run(self.tmp, "add-decision", "--topic", TOPIC, "--title", "Zulu decision on monitoring")
        git("commit", "-qam", "b")
        merged = subprocess.run(["git", "merge", "-q", "a", "-m", "m"], cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(merged.returncode, 0, merged.stdout + merged.stderr)
        d = dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api")
        self.assertEqual(len(d["decisions"]), 4)

    def test_lean_saves_progress_without_settling(self):
        self.create()
        code, _, err = run(self.tmp, "lean", "--topic", TOPIC, "--decision", "who owns",
                           inp={"options": [{"name": "orders-api"}, {"name": "payments service"}], "leaning": "orders-api, fewer teams on call"})
        self.assertEqual(code, 0, err)
        dec = dr.find_decision(dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api"), "who owns")
        self.assertEqual(dec["State"], "leaning")
        self.assertEqual(list((self.tmp / f"docs/architecture/designs/{TOPIC}/designs/queue-in-orders-api/adr").glob("*")), [])

    def test_question_needs_who_and_stays_in_sandbox(self):
        self.create()
        code, _, _ = run(self.tmp, "question", "--topic", TOPIC, "--text", "What is the peak order volume")
        self.assertEqual(code, 2)
        before = tree(self.tmp)
        code, _, err = run(self.tmp, "question", "--topic", TOPIC, "--decision", "who owns", "--kind", "research",
                           "--research", "retry-backoff", "--text", "Which backoff suits payments (research on retry backoff)")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.outside(before), [])
        spec = (self.tmp / "docs/architecture/spec.md").read_text()
        self.assertNotIn("backoff", spec)
        self.assertNotIn("Pending:", tree(self.tmp)["docs/specs/orders-api/spec.md"])
        self.assertEqual(invariants(self.tmp, TOPIC), [])
        code, _, err = run(self.tmp, "answer", "--topic", TOPIC, "--question", "backoff", "--text", "exponential")
        self.assertEqual(code, 0, err)
        dec = dr.find_decision(dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api"), "who owns")
        self.assertEqual(dec["State"], "open")

    def test_fan_out_copy_and_blank_refresh_compare(self):
        self.create()
        self.settle()
        code, _, err = run(self.tmp, "fan-out", "--topic", TOPIC, "--design", "queue-in-orders-api", "--name", "shared-retry-service", "--mode", "copy")
        self.assertEqual(code, 0, err)
        code, _, err = run(self.tmp, "fan-out", "--topic", TOPIC, "--design", "queue-in-orders-api", "--name", "scheduler-table", "--mode", "blank")
        self.assertEqual(code, 0, err)
        t = dr.Topic(self.tmp, TOPIC)
        self.assertEqual(t.designs(), ["queue-in-orders-api", "scheduler-table", "shared-retry-service"])
        copy = t.design("shared-retry-service")
        self.assertEqual(copy["end_state"], SETTLE["end_state"])
        self.assertTrue(all(x["State"] != "settled" for x in copy["decisions"]))
        self.assertEqual(t.design("scheduler-table")["decisions"], [])
        code, _, err = run(self.tmp, "compare", "--topic", TOPIC, inp={"scores": {"queue-in-orders-api": {"Checkout stays fast in prod": "yes"}}})
        comp = (t.dir / "compare.md").read_text()
        self.assertIn("| Checkout stays fast in prod | yes | unknown | unknown |", comp)
        self.settle(design="shared-retry-service")
        self.assertIn("| Checkout stays fast in prod | yes |", (t.dir / "compare.md").read_text())
        self.check_snapshot("fan-out")
        self.assertEqual(invariants(self.tmp, TOPIC), [])

    def test_stage_after_end_state_and_needs_another_look(self):
        self.create()
        self.settle()
        code, _, err = run(self.tmp, "stage", "--topic", TOPIC, inp={"stages": [
            {"name": "Retry in test", "reason": "can ship the retry in test without a new queue in prod"},
            {"name": "Retry in prod", "reason": "needs the queue in prod", "waits_on": "person A decides whether prod may use the new queue"}]})
        self.assertEqual(code, 0, err)
        st = dr.Topic(self.tmp, TOPIC).stages("queue-in-orders-api")
        self.assertEqual([s["name"] for s in st], ["Retry in test", "Retry in prod"])
        self.assertEqual(st[1]["waits_on"], "person A decides whether prod may use the new queue")
        data = dict(SETTLE2, end_state=SETTLE["end_state"] + " A dead-letter path catches retries that keep failing.")
        self.settle("who owns", data)
        st = dr.Topic(self.tmp, TOPIC).stages("queue-in-orders-api")
        self.assertTrue(all(s["state"] == "needs another look" for s in st))
        self.assertEqual(invariants(self.tmp, TOPIC), [])

    def test_park_and_resume_continue_at_first_open_decision(self):
        self.create()
        self.settle()
        run(self.tmp, "park", "--topic", TOPIC)
        self.assertEqual(dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api")["status"], "parked")
        code, out, err = run(self.tmp, "resume", "--topic", TOPIC)
        res = json.loads(out)
        self.assertEqual(res["next_decision"], "Who owns the retry policy")
        self.assertEqual(res["reopened"], [])

    def test_resume_reopens_only_the_decision_whose_source_changed(self):
        self.create()
        self.settle()
        self.settle("who owns", dict(SETTLE2, sources=["docs/system/adr/0001-inline-retry.md"]))
        (self.tmp / "docs/environments/test.md").write_text("# test\n\nNow runs on a new account.\n")
        code, out, err = run(self.tmp, "resume", "--topic", TOPIC)
        res = json.loads(out)
        self.assertEqual([r["decision"] for r in res["reopened"]], ["Where a failed payment waits before retry"])
        d = dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api")
        self.assertEqual(dr.find_decision(d, "who owns")["State"], "settled")
        self.assertIn("docs/environments/test.md changed", dr.find_decision(d, "where a failed")["Reopened"])
        self.assertEqual(res["next_decision"], "Where a failed payment waits before retry")

    def test_revisit_needs_a_separate_yes(self):
        self.create()
        data = dict(SETTLE, reverses="ADR 0001 inline retry")
        code, _, err = run(self.tmp, "settle", "--topic", TOPIC, "--decision", "where a failed", inp=data)
        self.assertEqual(code, 2)
        self.assertIn("revisit", err)
        code, _, err = run(self.tmp, "settle", "--topic", TOPIC, "--decision", "where a failed", "--revisit-yes", inp=data)
        self.assertEqual(code, 0, err)

    def test_compare_topics_only_when_asked_with_picked_criteria(self):
        self.create()
        run(self.tmp, "create", "--topic", "event-bus", inp=dict(GOAL, design="bus-on-existing-hosting", decisions=[]))
        inp = {"criteria": ["Runs on the existing contoso cloud account"]}
        code, _, err = run(self.tmp, "compare-topics", "--topics", TOPIC, "event-bus", inp=inp)
        self.assertEqual(code, 2)
        goal_before = (self.tmp / f"docs/architecture/designs/{TOPIC}/goal.md").read_text()
        code, out, err = run(self.tmp, "compare-topics", "--topics", TOPIC, "event-bus", "--asked", inp=inp)
        self.assertEqual(code, 0, err)
        f = self.tmp / f"docs/architecture/designs/_compare/{TOPIC}-event-bus.md"
        self.assertIn("Runs on the existing contoso cloud account", f.read_text())
        self.assertEqual(goal_before, (self.tmp / f"docs/architecture/designs/{TOPIC}/goal.md").read_text())
        self.assertFalse((self.tmp / f"docs/architecture/designs/{TOPIC}/compare.md").exists())


class TestGuards(Base):
    def test_writer_refuses_outside_sandbox_before_go_ahead(self):
        w = dr.Writer(self.tmp, TOPIC)
        for rel in ("docs/architecture/spec.md", "docs/architecture/left-out.md", "docs/system/adr/0002-x.md",
                    "docs/system/diagrams.md", "docs/specs/orders-api/plan.md", "docs/specs/orders-api/tasks.md",
                    "docs/specs/orders-api/verify.md", "docs/specs/orders-api/spec.md", "docs/architecture/designs/event-bus/goal.md"):
            with self.assertRaises(dr.Refused, msg=rel):
                w.write(self.tmp / rel, "x")
        w.write(self.tmp / f"docs/architecture/designs/{TOPIC}/scratch.md", "ok")

    def test_headless_route_without_word_prints_missing_choice(self):
        before = tree(self.tmp)
        code, _, err = run(self.tmp, "route", headless=True)
        self.assertEqual(code, 2)
        self.assertEqual(err.strip(), "Missing choice. Use one of: <idea text>, resume, park, status, prepare.")
        self.assertEqual(tree(self.tmp), before)

    def test_run_without_user_is_forced_to_prepare(self):
        code, out, _ = run(self.tmp, "route", "--word", "go-ahead", headless=True)
        self.assertEqual(out.strip(), "prepare")
        self.create()
        before = tree(self.tmp)
        for args in (["settle", "--topic", TOPIC, "--decision", "where"], ["stage", "--topic", TOPIC],
                     ["go-ahead", "--topic", TOPIC, "--accept-findings"], ["create", "--topic", "x"],
                     ["question", "--topic", TOPIC, "--text", "x (person A)"]):
            code, _, err = run(self.tmp, *args, headless=True, inp=SETTLE if args[0] in ("settle", "stage") else None)
            self.assertEqual(code, 2, args)
            self.assertIn("may only prepare", err)
        self.assertEqual(tree(self.tmp), before)
        code, _, err = run(self.tmp, "lean", "--topic", TOPIC, "--decision", "who owns", headless=True,
                           inp={"options": [{"name": "orders-api"}], "recommended": "orders-api", "leaning": "orders-api"})
        self.assertEqual(code, 0, err)
        dec = dr.find_decision(dr.Topic(self.tmp, TOPIC).design("queue-in-orders-api"), "who owns")
        self.assertEqual(dec["State"], "open")
        self.assertEqual(dec["Recommended"], "orders-api")
        self.assertEqual(list((self.tmp / "docs/system/adr").glob("*")), [self.tmp / "docs/system/adr/0001-inline-retry.md"])

    def test_unknown_word_names_the_words(self):
        code, _, err = run(self.tmp, "route", "--word", "new")
        self.assertEqual(code, 2)
        self.assertIn("resume, park, status, fan-out, stage-it, go-ahead, compare-topics, prepare", err)


class TestGoAhead(Base):
    def ready(self, fan=True):
        self.create()
        self.settle()
        self.settle("who owns", SETTLE2)
        run(self.tmp, "question", "--topic", TOPIC, "--text", "May prod use the new queue (person A decides)")
        if fan:
            run(self.tmp, "fan-out", "--topic", TOPIC, "--design", "queue-in-orders-api", "--name", "shared-retry-service", "--mode", "copy")
            self.settle(design="shared-retry-service")

    def test_review_flags_gap_conflict_and_missing_decision_and_writes_nothing(self):
        self.create()
        data = dict(SETTLE, end_state="orders-api owns a retry queue in staging.")
        self.settle(data=data)
        (self.tmp / "docs/system/landscape.md").write_text("# Landscape\n\n- Not allowed: staging\n")
        before = tree(self.tmp)
        code, out, err = run(self.tmp, "go-ahead", "--topic", TOPIC)
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        kinds = sorted({f["kind"] for f in res["findings"]})
        self.assertEqual(kinds, ["conflict", "gap", "missing-decision"])
        self.assertFalse(res["copied"])
        self.assertEqual(tree(self.tmp), before)

    def test_go_ahead_copies_only_the_chosen_design(self):
        self.ready()
        before = tree(self.tmp)
        code, out, err = run(self.tmp, "go-ahead", "--topic", TOPIC, "--design", "queue-in-orders-api")
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        self.assertTrue(res["copied"], res)
        spec = (self.tmp / "docs/architecture/spec.md").read_text()
        self.assertEqual(spec.count("### queue in orders-api (topic orders-payment-retry)"), 1)
        self.assertIn(f"Designed in: `docs/architecture/designs/{TOPIC}/designs/queue-in-orders-api/`", spec)
        self.assertLess(spec.index("## Decided, not built yet"), spec.index("## Open questions"))
        self.assertIn("- May prod use the new queue (person A decides)", spec)
        self.assertEqual(dr._confirmed(spec), dr._confirmed(before["docs/architecture/spec.md"]))
        self.assertIn("  - Asked: person B, 2026-11-10", spec)
        adrs = sorted(p.name for p in (self.tmp / "docs/system/adr").glob("*.md"))
        self.assertEqual(adrs, ["0001-inline-retry.md", "0002-orders-api-owns-the-policy.md" if False else adrs[1], adrs[2]])
        self.assertEqual(len(adrs), 3)
        for name in adrs[1:]:
            txt = (self.tmp / "docs/system/adr" / name).read_text()
            self.assertIn("- Status: accepted", txt)
            self.assertIn(f"- Designed in: `docs/architecture/designs/{TOPIC}/designs/queue-in-orders-api/`", txt)
            self.assertRegex(txt, r"^# ADR 000[23]:")
        t = dr.Topic(self.tmp, TOPIC)
        self.assertEqual(t.design("shared-retry-service")["status"], "rejected")
        self.assertTrue((t.ddir("shared-retry-service") / "adr").glob("*.md"))
        live = (self.tmp / "docs/system/diagrams.md").read_text()
        self.assertIn("## queue in orders-api (planned)", live)
        self.assertIn("-.->|planned|", live)
        changed = self.outside(before)
        self.assertEqual(sorted(c for c in changed if not c.startswith("docs/system/adr/")),
                         ["docs/architecture/spec.md", "docs/system/diagrams.md"])
        self.check_snapshot("go-ahead")
        self.assertEqual(invariants(self.tmp, TOPIC), [])

    def test_go_ahead_into_one_slice(self):
        self.ready(fan=False)
        code, out, err = run(self.tmp, "go-ahead", "--topic", TOPIC, "--slice", "orders-api")
        self.assertEqual(code, 0, err)
        adrs = sorted(p.name for p in (self.tmp / "docs/specs/orders-api/adr").glob("*.md"))
        self.assertEqual(len(adrs), 2)
        self.assertTrue(adrs[0].startswith("0001-"))
        self.assertIn("- Spec: `../spec.md`", (self.tmp / "docs/specs/orders-api/adr" / adrs[0]).read_text())
        self.assertIn("## queue in orders-api (planned)", (self.tmp / "docs/specs/orders-api/diagrams.md").read_text())

    def test_second_go_ahead_writes_nothing(self):
        self.ready(fan=False)
        run(self.tmp, "go-ahead", "--topic", TOPIC)
        before = tree(self.tmp)
        code, _, err = run(self.tmp, "go-ahead", "--topic", TOPIC, "--design", "queue-in-orders-api")
        self.assertEqual(code, 2)
        self.assertEqual(tree(self.tmp), before)

    def test_architecture_spec_template_gets_the_heading_when_missing(self):
        self.ready(fan=False)
        (self.tmp / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- a fact. (`x`)\n")
        run(self.tmp, "go-ahead", "--topic", TOPIC)
        spec = (self.tmp / "docs/architecture/spec.md").read_text()
        self.assertIn("## Decided, not built yet", spec)
        self.assertTrue(spec.rstrip().endswith("- May prod use the new queue (person A decides)"))
        self.assertIn("## Confirmed\n\n- a fact. (`x`)\n", spec)


class TestEndings(Base):
    def check_shape(self, text):
        lines = text.splitlines()
        self.assertTrue(lines[0].startswith("Run next:"))
        self.assertNotIn("Next:", text.replace("Run next:", ""))
        for i, line in enumerate(lines):
            if "`" in line and line.startswith("`"):
                self.assertTrue(line.startswith("`") and line.endswith("`") and line.count("`") == 2, line)
                self.assertTrue(lines[i - 1].endswith(":") and "`" not in lines[i - 1], lines[i - 1])

    def golden(self, name, state):
        text = dr.ending(dict(state, topic=TOPIC))
        self.check_shape(text)
        path = SNAP / "endings" / f"{name}.txt"
        if os.environ.get("UPDATE_DESIGN_SNAPSHOTS"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.assertEqual(text, path.read_text(encoding="utf-8"))
        return text

    def test_mid_design_parked(self):
        t = self.golden("parked", {"phase": "design", "parked": True, "reason": "Two of three decisions are settled; the topic is parked.",
                                   "waiting": "person A's answer on peak order volume, before the retry limits can be decided.", "uncommitted": 4})
        self.assertIn("`/crav1-design-architecture resume orders-payment-retry`", t)

    def test_after_go_ahead_push_then_pr_and_no_planning(self):
        t = self.golden("go-ahead", {"phase": "go-ahead", "waiting": "person A's decision on whether prod may use the new queue.", "uncommitted": 7})
        self.assertLess(t.index("git push -u origin design/orders-payment-retry"), t.index("gh pr create --base main --head design/orders-payment-retry"))
        for cmd in ("/crav1-tighten-spec", "/crav1-plan-from-spec", "/crav1-review-plan", "/crav1-tighten-plan"):
            self.assertNotIn(cmd, t)

    def test_after_merge_slice_then_no_slice(self):
        t = self.golden("merged-slice", {"phase": "merged", "slices": ["orders-api"]})
        self.assertIn("`/crav1-tighten-spec orders-api`", t)
        t = self.golden("merged-no-slice", {"phase": "merged", "no_slice": True})
        self.assertIn("`/crav1-plan-from-spec`", t)

    def test_other_endings(self):
        self.assertIn("`/crav1-add-to-spec fact`", self.golden("requirement", {"phase": "design", "routed_requirement": True}))
        self.assertIn("ask research retry-backoff", self.golden("research", {"phase": "design", "research_topic": "retry-backoff"}))
        self.assertEqual(dr.ending({"topic": TOPIC, "phase": "design"}), "Run next: nothing needed now.\n")
        self.assertEqual(dr.ending({"topic": TOPIC, "phase": "merged"}), "Run next: nothing needed now.\n")


class TestKitWiring(unittest.TestCase):
    def test_skills_yaml_entry_text(self):
        y = (ROOT / "docs/reference/skills.yaml").read_text(encoding="utf-8")
        i = y.index("- name: crav1-design-architecture\n")
        block = y[i:y.index("\n- name:", i + 1)]
        for line in ("  lane: cross-cutting", "  group: Specify", "  starter: false", "  stage: preview", "  since: 1.181.0",
                     "  walkthrough: docs/from-design-architecture.md"):
            self.assertIn(line, block)
        words = re.findall(r'word: "([^"]+)"', block)
        self.assertTrue(all(re.fullmatch(r"[a-z]+(-[a-z]+)*", w) for w in words), words)
        others = set(re.findall(r'word: "([^"]+)"', y[:i] + y[i + len(block):]))
        self.assertEqual(sorted(set(words) & others - {"park"}), [], "choice words clash")

    def test_question_skills_read_the_architecture_spec(self):
        for name in ("crav1-show-or-ask-open-questions", "crav1-resolve-open-questions"):
            txt = (ROOT / f".cursor/skills/crav1/{name}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("docs/architecture/spec.md", txt, name)
            self.assertIn("Never read `docs/architecture/designs/`", txt, name)

    def test_other_skills_ignore_the_designs_folder(self):
        skills = ROOT / ".cursor/skills/crav1"
        for p in skills.rglob("*"):
            if not p.is_file() or "__pycache__" in p.parts or p.suffix not in (".md", ".py"):
                continue
            rel = p.relative_to(skills)
            if rel.parts[0] in ("crav1-design-architecture", "crav1-docs"):
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if "architecture/designs" in line:
                    self.assertRegex(line, r"(?i)never read|ignore|no other skill", f"{rel}: {line}")

    def test_endings_in_skill_text_have_no_next_line(self):
        for p in SKILL.rglob("*.md"):
            for line in p.read_text(encoding="utf-8").splitlines():
                self.assertFalse(re.match(r"^\s*Next:", line), f"{p.name}: {line}")

    def test_no_customer_names_in_new_files(self):
        files = list(SKILL.rglob("*")) + [Path(__file__), ROOT / "docs/from-design-architecture.md"] + list(SNAP.rglob("*"))
        for p in files:
            if p.is_file() and "__pycache__" not in p.parts:
                low = p.read_text(encoding="utf-8").lower()
                hits = [w for w in CUSTOMER if re.search(rf"\b{re.escape(w)}\b", low) and p != Path(__file__)]
                self.assertEqual(hits, [], str(p))

    def test_adr_asset_is_the_template_copy(self):
        self.assertEqual((SKILL / "assets/adr.md").read_bytes(), (ROOT / "docs/specs/_template/adr.md").read_bytes())

    def test_skill_md_size_and_description(self):
        txt = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(txt.split()), 2000)
        desc = re.search(r"description: >-\n(.*?)\n[a-z-]+:", txt, re.S).group(1)
        self.assertLessEqual(len(desc.split()), 60)


class TestMermaid(Base):
    @unittest.skipUnless(shutil.which("node") and (ROOT / "scripts/mermaid").is_dir(), "mermaid checker not installed")
    def test_written_diagrams_pass_the_mermaid_check(self):
        self.create()
        self.settle()
        run(self.tmp, "go-ahead", "--topic", TOPIC, "--accept-findings")
        live = (self.tmp / "docs/system/diagrams.md").read_text()
        self.assertIn("```mermaid", live)
        self.assertRegex(live, r"-\.->\|planned\|")


if __name__ == "__main__":
    unittest.main()
