"""1.159.0: tighten-plan and plan-from-spec compute their own ordering, batches and endings."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
CHECK = SK / "crav1-plan-from-spec/scripts/plan_check.py"
WRAPPER = SK / "crav1-tighten-plan/scripts/plan_check.py"
OFFER = SK / "crav1-tighten-plan/scripts/batch_offer.py"
ORDER = SK / "crav1-tasks-ready-to-build/scripts/task_order.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = load(CHECK, "plan_check_t1159")
bo = load(OFFER, "batch_offer_t1159")
to = load(ORDER, "task_order_t1159")

SPEC = """# Orders

## Acceptance criteria

- [ ] The refund goes back to the original card.
- [ ] Failure case: a declined refund shows an error.
- [ ] The receipt lists the order id.

## Open questions

- Should a partial refund mail the customer?
  - Blocks: T2
- Which currency rounding applies?

## Approval needed

- The partner approves applying the CI build policy.
  - Person: the partner
  - Holds: T3

## Research findings

- Card network limits. Stale since 2026-10-01.
"""
PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 3

## Linter

- ruff, `ruff check src/`, covers src/.

## Trace

| Acceptance / REQ | Tasks |
| --- | --- |
| The refund goes back to the original card | T1 |
| Failure case: a declined refund shows an error | T2 |
| The receipt lists the order id | T4 |
"""
TASKS = """# Tasks

- [ ] T1: Refund to the original card (verify: unit — refund uses the card) (spec: original card)
- [ ] T2: Show the decline error (verify: browser — error shows) (spec: declined refund) (after: T1)
- [ ] T3: Apply the build policy (host setup) (verify: infra/ado/policy.sh check prints ok) (spec: approval) (after: )
- [ ] T4: Export the receipt (verify: unit — the receipt has the id) (spec: order id) (after: T1, T3)
"""
ITEMS = [
    {"id": "P1", "issue": "T4 has no verify kind", "tag": "plan", "status": "patched",
     "options": "A add-verify, B keep", "recommendation": "A add a unit check"},
    {"id": "P4", "issue": "tasks miss the 400 path", "tag": "plan", "status": "open",
     "options": "A add a test, B keep", "recommendation": "A add a test", "current": True},
    {"id": "P2", "issue": "split T2", "tag": "plan", "status": "open",
     "options": "A split-task, B keep", "recommendation": "A split T2"},
    {"id": "P3", "issue": "rounding is undecided", "tag": "spec", "kind": "question", "status": "open"},
]


def slice_root(base: Path, plan: str = PLAN, tasks: str = TASKS) -> Path:
    root = base / "docs/specs/orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    return root


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(script), *args],
                          capture_output=True, text=True, encoding="utf-8")


def items_file(base: Path, items) -> str:
    path = base / "items.json"
    path.write_text(json.dumps(items), encoding="utf-8")
    return str(path)


class Order(unittest.TestCase):
    def test_waves_follow_the_ready_check_sort(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp))
            lines = pc.order_lines(root)
            self.assertEqual(lines[1:3], ["- Wave 1: T1, T3", "- Wave 2: T2, T4"])
            flat = [t for line in lines[1:3] for t in line.split(": ", 1)[1].split(", ")]
            sorted_ids = [f"T{n}" for n in to.analyse(to.parse(TASKS))["order"]]
            self.assertEqual(flat, sorted_ids, "same order as task_order.py")

    def test_loops_and_missing_after_are_named(self):
        tasks = TASKS.replace("(after: T1)", "(after: T4)").replace("(after: T1, T3)", "(after: T2, T9)")
        with tempfile.TemporaryDirectory() as tmp:
            text = "\n".join(pc.order_lines(slice_root(Path(tmp), tasks=tasks)))
            self.assertIn("- Loop: T2 → T4 → T2. Fix one (after: ...) mark.", text)
            self.assertIn("- T4: after: T9 names no task", text)
            self.assertNotIn("T2", text.split("\n")[1])

    def test_task_line_gaps(self):
        bad = TASKS.replace("(verify: unit — the receipt has the id) (spec: order id)", "(verify: the receipt has the id)")
        gaps = pc.line_problems(bad)
        self.assertEqual(gaps, ["T4 verify note names no kind", "T4 has no (spec: ...) mark"])
        self.assertEqual(pc.line_problems(TASKS), [], "a host setup task needs no kind")


class Recap(unittest.TestCase):
    def test_recap_order_and_next_lines_match_the_reference(self):
        ref = (SK / "crav1-plan-from-spec/references/recap.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp))
            facts = Path(tmp) / "facts.json"
            facts.write_text(json.dumps({"built_pieces": [{"piece": "refund client", "choice": "already there"}],
                                         "branch_read": "feat/orders-api at abc1234"}), encoding="utf-8")
            proc = run(CHECK, "recap", "--root", str(root), "--branch", "feat/orders-api",
                       "--facts", str(facts), "--uncommitted", "2")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = proc.stdout
            heads = ["Written: ", "Tasks: 4. Acceptance lines with no task: none", "Order (", "Built piece: refund client: already there",
                     "Branch read: ", "Verify notes with no kind, and other task-line gaps: none",
                     "Kept security checks with no task: none", "Kept-open questions parked as risks:",
                     "Approval needed:", "Stale research under Risks: Card network limits",
                     "These notes name the checks.", "Linter: ruff", "Next: ", "Uncommitted: 2 files"]
            positions = [out.index(h) for h in heads]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("- Should a partial refund mail the customer? Blocks: T2", out)
            self.assertIn("- Which currency rounding applies? No Blocks line.", out)
            nxt = [l for l in out.splitlines() if l.startswith("Next:")]
            self.assertEqual(nxt, ["Next: /crav1-review-plan, because the plan is written and not reviewed."])
            self.assertIn(nxt[0], ref)
            spec_branch = run(CHECK, "recap", "--root", str(root), "--branch", "spec/orders-api").stdout
            line = [l for l in spec_branch.splitlines() if l.startswith("Next:")]
            self.assertEqual(line, ["Next: /crav1-open-pr, because this specify-only branch is not on the default branch yet."])
            self.assertIn(line[0], ref)
            self.assertNotIn("tighten-plan", out)
            self.assertNotIn("/crav1-build", out)

    def test_untraced_line_and_no_linter(self):
        plan = PLAN.replace("| The receipt lists the order id | T4 |\n", "").replace(
            "- ruff, `ruff check src/`, covers src/.", "- This repo has no linter or checker for the code these tasks touch.")
        tasks = TASKS.replace("(spec: order id)", "(spec: export)")
        with tempfile.TemporaryDirectory() as tmp:
            out = run(CHECK, "recap", "--root", str(slice_root(Path(tmp), plan=plan, tasks=tasks)), "--branch", "feat/x").stdout
            self.assertIn("Acceptance lines with no task: The receipt lists the order id.", out)
            self.assertIn("Build is not named until you add a linter or choose to go on without one.", out)


class Queue(unittest.TestCase):
    def test_index_counts_and_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = run(WRAPPER, "queue", "--items", items_file(Path(tmp), ITEMS)).stdout
            self.assertTrue(out.startswith("Findings: 4 (3 plan, 1 spec). Open: 2 plan, 1 spec. Done: 1 patched."))
            rows = [l for l in out.splitlines() if l.startswith("- P")]
            self.assertEqual([r.split()[1] for r in rows], ["P2", "P4", "P3"], "plan first, in P# order")
            self.assertTrue(rows[1].endswith("← current"))
            self.assertIn("spec, skipped for plan: /crav1-resolve-open-questions", rows[2])
            self.assertNotIn("Next:", out, "no ending while a plan P# is open")

    def test_empty_queue_next_line_is_one_of_the_reference_lines(self):
        ref = (SK / "crav1-tighten-plan/references/issues.md").read_text(encoding="utf-8")
        allowed = re.findall(r"`(Next: [^`]+)`", ref.split("## Empty queue", 1)[1].split("\n## ", 1)[0])
        self.assertEqual(len(allowed), 4)
        done = [dict(i, status="patched") for i in ITEMS if i["tag"] == "plan"]
        cases = [
            (done + [{"id": "P9", "issue": "a spec gap", "tag": "spec", "kind": "defect", "status": "skipped"}], PLAN, False, 0),
            (done + [ITEMS[3]], PLAN, False, 1),
            (done, PLAN, False, 2),
            (done, PLAN.replace("- ruff, `ruff check src/`, covers src/.", "- None: this repo has no linter for this code."), False, 3),
            (done, PLAN.replace("- ruff, `ruff check src/`, covers src/.", "- None: this repo has no linter for this code."), True, 2),
        ]
        for items, plan, went_on, want in cases:
            with tempfile.TemporaryDirectory() as tmp:
                root = slice_root(Path(tmp), plan=plan)
                args = ["queue", "--items", items_file(Path(tmp), items), "--root", str(root)]
                if went_on:
                    args.append("--went-on-without-linter")
                out = run(CHECK, *args).stdout
                nxt = [l for l in out.splitlines() if l.startswith("Next:")]
                self.assertEqual(len(nxt), 1, out)
                self.assertTrue(nxt[0].startswith(allowed[want]), (nxt[0], allowed[want]))
                if want == 3:
                    self.assertNotIn("/crav1-build", out)

    def test_batch_is_batch_offer_for_open_plan_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(WRAPPER, "batch", "--items", items_file(Path(tmp), ITEMS))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = [{k: i[k] for k in ("id", "issue", "options", "recommendation")} for i in ITEMS if i["id"] in ("P2", "P4")]
            rows.sort(key=lambda r: r["id"])
            self.assertEqual(proc.stdout, bo.offer("Tighten-plan batch", rows))
            self.assertLess(proc.stdout.index("| Id | Issue | Options | Recommendation |"), proc.stdout.index("Card: "))
            self.assertIn("P4 tasks miss the 400 path: A add a test", proc.stdout)
            self.assertNotIn("table above", proc.stdout)
            none = run(WRAPPER, "batch", "--items", items_file(Path(tmp), [dict(ITEMS[0])]))
            self.assertEqual(none.returncode, 2)
            self.assertEqual(none.stdout, "", "no open plan P#, no card")


class Reviewed(unittest.TestCase):
    def test_lowers_count_keeps_date_never_adds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp))
            self.assertIn("would be 1", run(CHECK, "reviewed", "--root", str(root), "--open", "1").stdout)
            self.assertIn("P# open: 3", (root / "plan.md").read_text(encoding="utf-8"))
            run(CHECK, "reviewed", "--root", str(root), "--open", "1", "--write")
            self.assertIn("Reviewed: 2026-11-11, P# open: 1", (root / "plan.md").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp), plan=PLAN.replace("Reviewed: 2026-11-11, P# open: 3\n", ""))
            out = run(CHECK, "reviewed", "--root", str(root), "--open", "0", "--write").stdout
            self.assertIn("none added", out)
            self.assertNotIn("Reviewed:", (root / "plan.md").read_text(encoding="utf-8"))


class SkillText(unittest.TestCase):
    CAPS = {"crav1-tighten-plan": 1120, "crav1-plan-from-spec": 1150}

    def test_word_caps(self):
        for skill, cap in self.CAPS.items():
            n = len((SK / skill / "SKILL.md").read_text(encoding="utf-8").split())
            self.assertLessEqual(n, cap, f"{skill} is {n} words")
            self.assertGreaterEqual(n, 800, f"{skill}: rules must stay findable")

    def test_moved_rules_are_findable(self):
        def tree(skill):
            folder = SK / skill
            return "\n".join(p.read_text(encoding="utf-8") for p in [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))])
        tp, pf = tree("crav1-tighten-plan"), tree("crav1-plan-from-spec")
        for rule in (
            "- `T#` too big to verify alone (“add authentication”)",
            "**Spec** tag: the plan is fine or cannot be honest until `spec.md` changes.",
            "Remaining `P#` titles only. Mark the current one. Note plan vs spec.",
            "`Next: /crav1-build-tasks, because the plan issues are done.` A new chat, with `plan.md`, `tasks.md`, and `spec.md` attached.",
            "A plan that already says none is not a `P#` by itself.",
            "This line is the only `plan.md` change this skill makes outside the picked patches.",
            "At most **one** alternate suggestion, then they must pick a patch letter, `ask`, `keep`, or `send-to-spec`.",
            "Never write `table above` unless that table is in this reply. Never ask the card without the table.",
        ):
            self.assertIn(rule, tp)
        for rule in (
            "- **Constraints** — from spec constraints + accepted ADRs only",
            "- **Requirements trace** — table: acceptance / REQ id → task ids",
            "Its verify is the script's `check` part reading the live setting",
            "A secret is a manual task: the plan names what to create and where, never a value.",
            "- Task count and any acceptance line with no task, not marked `already there`, and not `left as committed` (must be none, or the plan failed)",
            "Do not name tighten-plan or build in this ending.",
            "Do not start coding in this chat.",
        ):
            self.assertIn(rule, pf)

    def test_skills_print_the_script_output_as_is(self):
        for skill in self.CAPS:
            text = (SK / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("scripts/plan_check.py", text)
            self.assertIn("as-is", text)
            self.assertIn("never write a second `Next` line", text)

    def test_every_tree_ships_plan_check(self):
        for tree in (SK, ROOT / "plugins/crav1/skills", ROOT / ".claude/skills"):
            for skill in self.CAPS:
                self.assertTrue((tree / skill / "scripts/plan_check.py").is_file(), f"{tree}/{skill}")
        self.assertEqual(run(WRAPPER, "--help").returncode, 0)


if __name__ == "__main__":
    unittest.main()
