"""1.154.0: name dependency loops, map and ready check agree, wave order, held labels, no stray Next line."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BUILD_MAP = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"
LINT = ROOT / "scripts/kit-lint.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load(BUILD_MAP, "build_map_1154")
lint = load(LINT, "kit_lint_1154")

SPEC = """# Orders

## Open questions

- Which fixed hostname does the partner allow? Waiting for person A.
  - Blocks: T30
"""

PLAN = """# Plan

Reviewed: 2026-11-14, P# open: 0

## Approach

1. Base work. (T1)
"""

# feat/orders-cicd and feat/orders-dev-switch wait for each other:
# T14 (cicd) waits for T13 (dev-switch), and T13 waits for T12 (cicd).
TASKS = """# Tasks

- [ ] T1: Base work on feat/orders-base (after: )
- [ ] T12: Pipeline prep on feat/orders-cicd (after: T1)
- [ ] T13: Switch the day on feat/orders-dev-switch (after: T12)
- [ ] T14: Repoint the pipeline on feat/orders-cicd (after: T13)
- [ ] T20: Key storage on feat/orders-keys (after: T14)
- [ ] T21: Other work on feat/orders-other (after: )
- [ ] T30: Fixed hostname on feat/orders-static-host (after: T14)
"""

LOOP_LINE = (
    "Loop: feat/orders-cicd and feat/orders-dev-switch wait for each other: "
    "T14 on feat/orders-cicd waits for T13 on feat/orders-dev-switch, and "
    "T13 on feat/orders-dev-switch waits for T12 on feat/orders-cicd. "
    "Fix one of these lines in tasks.md."
)


def by_name(result):
    return {branch["name"]: branch for branch in result["branches"]}


def wave_problems(result):
    rows = by_name(result)
    loop_of = {}
    for index, loop in enumerate(result.get("loops") or []):
        for name in loop["branches"]:
            loop_of[name] = index
    bad = []
    for branch in result["branches"]:
        for dep in branch["waits"]:
            same_loop = branch["name"] in loop_of and loop_of.get(dep) == loop_of[branch["name"]]
            if same_loop:
                continue
            if not branch["wave"] > rows[dep]["wave"]:
                bad.append((branch["name"], branch["wave"], dep, rows[dep]["wave"]))
    return bad


def run_walk(args):
    return subprocess.run(
        [sys.executable, str(WALK), *args], capture_output=True, text=True, check=False
    )


def write_slice(root, tasks=TASKS, spec=SPEC, plan=PLAN):
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")


def readiness(root, *extra):
    record = run_walk([
        "record", "--root", str(root), "--slice", "docs/specs/orders-api",
        "--step", "resolve-open-questions", "--result", "done", "--yes",
    ])
    assert record.returncode == 0, record.stderr + record.stdout
    proc = run_walk(["readiness", "--root", str(root), "--skip-sync", *extra])
    assert proc.returncode == 0, proc.stderr + proc.stdout
    return json.loads(proc.stdout)


class LoopIsNamed(unittest.TestCase):
    def test_map_names_both_branches_and_each_task_line(self):
        result = bm.build("orders-api", SPEC, PLAN, TASKS)
        self.assertEqual(result["loop_lines"], [LOOP_LINE])
        self.assertIn(LOOP_LINE, result["markdown"])
        self.assertIn(LOOP_LINE, result["summary"])
        self.assertEqual(result["loops"][0]["branches"], ["feat/orders-cicd", "feat/orders-dev-switch"])
        self.assertEqual(result["loops"][0]["tasks"], [12, 13, 14])
        self.assertIn('subgraph inloop["In a loop"]', result["markdown"])
        rows = by_name(result)
        self.assertEqual(rows["feat/orders-cicd"]["status"], "blocked")
        self.assertIn("Ready now: blocked, in a loop", result["markdown"])

    def test_implicit_wait_says_it_is_the_task_just_before(self):
        tasks = """# Tasks

- [ ] T1: Base work on feat/orders-a
- [ ] T2: Second step on feat/orders-b
- [ ] T3: Third step on feat/orders-a
"""
        result = bm.build("orders-api", "", PLAN, tasks)
        line = result["loop_lines"][0]
        self.assertIn("feat/orders-a and feat/orders-b wait for each other", line)
        self.assertIn("T3 on feat/orders-a waits for T2 on feat/orders-b (the task just before it, no (after:) mark)", line)
        self.assertIn("T2 on feat/orders-b waits for T1 on feat/orders-a", line)

    def test_three_branch_loop_lists_every_wait(self):
        tasks = """# Tasks

- [ ] T1: First on feat/orders-a (after: T3)
- [ ] T2: Second on feat/orders-b (after: T1)
- [ ] T3: Third on feat/orders-c (after: T2)
"""
        result = bm.build("orders-api", "", PLAN, tasks)
        line = result["loop_lines"][0]
        self.assertTrue(line.startswith("Loop: feat/orders-a, feat/orders-b and feat/orders-c wait for each other in a loop: "))
        for piece in ("T1 on feat/orders-a waits for T3 on feat/orders-c",
                      "T2 on feat/orders-b waits for T1 on feat/orders-a",
                      "T3 on feat/orders-c waits for T2 on feat/orders-b"):
            self.assertIn(piece, line)

    def test_no_loop_no_loop_line(self):
        tasks = TASKS.replace("(after: T13)", "(after: T12)").replace(
            "T13: Switch the day on feat/orders-dev-switch (after: T12)",
            "T13: Switch the day on feat/orders-dev-switch (after: T1)",
        )
        result = bm.build("orders-api", SPEC, PLAN, tasks)
        self.assertEqual(result["loop_lines"], [])
        self.assertNotIn("Loop:", result["markdown"])


class DownstreamKeepsItsState(unittest.TestCase):
    def test_branch_after_a_loop_keeps_its_wave_and_state(self):
        result = bm.build("orders-api", SPEC, PLAN, TASKS)
        rows = by_name(result)
        keys = rows["feat/orders-keys"]
        self.assertEqual(keys["section"], "wave")
        self.assertEqual(keys["status"], "waits in order")
        self.assertGreater(keys["wave"], rows["feat/orders-cicd"]["wave"])
        host = rows["feat/orders-static-host"]
        self.assertEqual(host["section"], "wave")
        self.assertEqual(host["status"], "waiting on a question")
        self.assertEqual(rows["feat/orders-other"]["status"], "ready")
        blocked = result["markdown"].split("## Blocked", 1)[1]
        self.assertNotIn("feat/orders-keys", blocked)
        self.assertNotIn("feat/orders-static-host", blocked)


class WaveOrder(unittest.TestCase):
    def test_live_shape_never_puts_a_branch_before_what_it_waits_for(self):
        # A long chain to feat/orders-vault, and a short branch that waits on
        # it. Before 1.154.0 a partial wave from the short side could land
        # earlier than the chain end when a loop sat upstream.
        tasks = """# Tasks

- [ ] T1: Base work on feat/orders-base (after: )
- [ ] T12: Pipeline prep on feat/orders-cicd (after: T1)
- [ ] T13: Switch the day on feat/orders-dev-switch (after: T12)
- [ ] T14: Repoint the pipeline on feat/orders-cicd (after: T13)
- [ ] T40: Step one on feat/orders-s1 (after: T14)
- [ ] T41: Step two on feat/orders-s2 (after: T40)
- [ ] T42: Step three on feat/orders-s3 (after: T41)
- [ ] T43: Vault keys on feat/orders-vault (after: T42)
- [ ] T44: Key storage on feat/orders-key-storage (after: T1, T43)
"""
        result = bm.build("orders-api", "", PLAN, tasks)
        self.assertEqual(wave_problems(result), [])
        rows = by_name(result)
        self.assertGreater(rows["feat/orders-key-storage"]["wave"], rows["feat/orders-vault"]["wave"])
        self.assertEqual(rows["feat/orders-key-storage"]["section"], "wave")

    def test_random_graphs_keep_wave_order_outside_loops(self):
        rng = random.Random(1154)
        for _ in range(60):
            count = rng.randint(3, 12)
            lines = ["# Tasks", ""]
            for number in range(1, count + 1):
                deps = rng.sample(range(1, count + 1), k=rng.randint(0, 2))
                deps = [dep for dep in deps if dep != number]
                branch = f"feat/orders-b{rng.randint(1, max(2, count // 2))}"
                after = ", ".join(f"T{dep}" for dep in deps)
                lines.append(f"- [ ] T{number}: Work {number} on {branch} (after: {after})")
            result = bm.build("orders-api", "", PLAN, "\n".join(lines) + "\n")
            self.assertEqual(wave_problems(result), [], "\n".join(lines))
            for branch in result["branches"]:
                self.assertIsNotNone(branch["wave"])


class ReadyCheckAgreesWithTheMap(unittest.TestCase):
    def test_loop_tasks_are_blocked_in_both_and_named_in_the_ending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            payload = readiness(root, "--write-map")
            brief = run_walk(["readiness", "--root", str(root), "--skip-sync", "--brief"])
            mapped = (root / "build-map.md").read_text(encoding="utf-8")
        self.assertEqual(payload["result"], "ready-partial")
        self.assertEqual(sorted(payload["can_start"]), ["T1", "T21"])
        for task in ("T12", "T13", "T14"):
            self.assertNotIn(task, payload["can_start"])
            row = next(row for row in payload["rows"] if row["task"] == task)
            self.assertEqual(row["bucket"], "blocked")
        self.assertEqual(payload["counts"]["blocked"], 3)
        self.assertEqual(payload["loop_lines"], [LOOP_LINE])
        self.assertIn(LOOP_LINE, payload["ending"])
        self.assertIn(LOOP_LINE, mapped)
        self.assertTrue(payload["ending"].startswith("Run next:"))
        self.assertNotIn("/crav1-build-walk T12", payload["ending"])
        self.assertNotIn("\nNext:", payload["ending"])
        # Tasks off the loop keep their real state.
        rows = {row["task"]: row for row in payload["rows"]}
        self.assertEqual(rows["T20"]["bucket"], "waits-in-order")
        self.assertEqual(rows["T30"]["bucket"], "waiting")
        brief_payload = json.loads(brief.stdout)
        self.assertIn(LOOP_LINE, brief_payload["ending"])
        self.assertIn("Blocked 3", brief_payload["counts"]["line"])

    def test_only_loop_tasks_left_is_not_ready(self):
        tasks = """# Tasks

- [x] T1: Base work on feat/orders-base (after: )
- [ ] T12: Pipeline prep on feat/orders-cicd (after: T1)
- [ ] T13: Switch the day on feat/orders-dev-switch (after: T12)
- [ ] T14: Repoint the pipeline on feat/orders-cicd (after: T13)
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root, tasks=tasks, spec="# Orders\n")
            payload = readiness(root)
        self.assertEqual(payload["result"], "not-ready")
        self.assertEqual(payload["can_start"], [])
        self.assertIn("Loop: feat/orders-cicd and feat/orders-dev-switch", payload["ending"])
        self.assertNotIn("Run next:", payload["ending"])


class HeldLineLabel(unittest.TestCase):
    def test_held_lines_show_the_wave_never_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root)
            payload = readiness(root)
        held = "\n".join(payload["held_lines"])
        self.assertIn("`feat/orders-static-host` (wave ", held)
        self.assertNotIn("(blocked)", held)

    def test_no_loop_and_no_blocked_count_never_says_blocked(self):
        tasks = """# Tasks

- [ ] T1: Base work on feat/orders-base (after: )
- [ ] T30: Fixed hostname on feat/orders-static-host (after: T1)
- [ ] T31: After the hostname on feat/orders-after-host (after: T30)
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "orders-api"
            root.mkdir()
            write_slice(root, tasks=tasks)
            payload = readiness(root)
        self.assertEqual(payload["counts"]["blocked"], 0)
        held = "\n".join(payload["held_lines"])
        self.assertTrue(held)
        self.assertNotIn("(blocked)", held)
        self.assertNotIn("(blocked)", payload["ending"])

    def test_where_says_in_a_loop(self):
        self.assertEqual(bm._where({"loop": True, "wave": 2, "section": "blocked"}), "in a loop")
        self.assertEqual(bm._where({"wave": 3, "section": "blocked"}), "wave 3")


class NoStrayNextLine(unittest.TestCase):
    def test_lint_flags_a_next_line_after_waiting(self):
        bad = "The full Next lines stay after the Waiting lines. They still recommend the walk."
        self.assertTrue(lint.stray_next_hits(bad))
        example = "`Next: /crav1-build-walk T2 Record the decision, because that work is on feat/orders-api-record.`"
        self.assertTrue(lint.stray_next_hits(example))
        self.assertFalse(lint.stray_next_hits(example, ready_check=False))
        ok = "Never add a `Next:` line after the Waiting lines (1.153.0)."
        self.assertFalse(lint.stray_next_hits(ok))

    def test_no_skill_reference_tells_the_agent_to_write_a_next_line_after_waiting(self):
        self.assertEqual(lint.stray_next_problems(str(ROOT)), [])

    def test_tighten_and_plan_references_use_run_next(self):
        folder = SK / "crav1-tighten-and-plan-ready-to-build"
        for path in [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("full Next line", text, path.name)
            self.assertNotIn("Next: /crav1-build-walk", text, path.name)


if __name__ == "__main__":
    unittest.main()
