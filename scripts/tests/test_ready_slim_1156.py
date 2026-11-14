"""1.156.0: the ready check prints its own ending, one shared walk ending, brief by default."""

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
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
ENDING = SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py"
MAP = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"
BUILD_WALK = SK / "crav1-build-walk/scripts/build_walk.py"
BRANCH_RUN = SK / "crav1-build-walk/scripts/branch_run.py"
SKILLS = ("crav1-tasks-ready-to-build", "crav1-tighten-and-plan-ready-to-build", "crav1-build-walk")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


we = load(ENDING, "walk_ending_t1156")
bm = load(MAP, "build_map_t1156")
bw = load(BUILD_WALK, "build_walk_t1156")
br = load(BRANCH_RUN, "branch_run_t1156")
wp = load(WALK, "walk_progress_t1156")

SPEC = "# Orders\n\nThe receipt lists the order id.\n\n## Open questions\n"
PLAN = """# Plan: orders-api

Reviewed: 2026-11-11, P# open: 0

## Approach

1. Retry the refund on `feat/orders-retry`. (T1, T2)
2. Export the receipt on `feat/orders-export`. (T3)

## Risks
"""
TASKS = """# Tasks

- [ ] T1: Refund to the original card (branch: feat/orders-retry) (after: )
- [ ] T2: Send the refund mail (branch: feat/orders-retry) (after: T1)
- [ ] T3: Export the receipt (branch: feat/orders-export) (after: )
"""


def slice_root(base: Path) -> Path:
    root = base / "docs/specs/orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    return root


def walk(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(WALK), *args],
        capture_output=True, text=True, encoding="utf-8",
    )


def run_block(text: str) -> str:
    """The Run next block: from `Run next:` up to the first part that is not an entry."""
    parts = text.split("\n\n")
    start = parts.index("Run next:")
    out = [parts[start]]
    for part in parts[start + 1:]:
        if not part.startswith("`/crav1-"):
            break
        out.append(part)
    return "\n\n".join(out)


class SharedEnding(unittest.TestCase):
    def test_run_entries_are_one_function(self):
        labels = ["T5 refund to the original card", "T9 send the mail"]
        shared = we.run_entries(labels, "feat/orders-retry", slug="orders-api")
        self.assertEqual(bm.run_entries(labels, "feat/orders-retry", slug="orders-api"), shared)
        self.assertEqual(shared[0], "`/crav1-build-walk orders-api T5`\nbranch feat/orders-retry, T5 refund to the original card")
        self.assertEqual(shared[1].splitlines()[0], "`/crav1-build-walk orders-api feat/orders-retry`")
        one = we.run_entries(labels[:1], "feat/orders-retry", slug="orders-api")
        self.assertEqual(len(one), 1, "a branch with one open task gets no branch entry")

    def test_same_state_gives_the_same_run_next_in_all_three_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp))
            proc = walk("readiness", "--root", str(root), "--skip-sync", "--full")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            full = json.loads(proc.stdout)
            self.assertIn(full["result"], ("ready", "ready-partial"))
            ready = full["ready_branches"]
            self.assertEqual(len(ready), 2, ready)
            readiness_block = run_block(full["ending"])
            # build-walk, started with no branch picked (grouping).
            grouping = bw.next_for({"mode": "grouping", "branches": ready, "root": str(root)})
            self.assertEqual(run_block(grouping["ending"]), readiness_block)
            # branch run: its own entry first, then the other ready branches.
            first = ready[0]["branch"]
            state = {
                "slug": wp.command_slug(root), "branch": "feat/orders-other", "stop": {"kind": "merge"},
                "pr": None, "ready_branches": ready, "built": [],
            }
            text = br.ending(state)["ending"]
            others = run_block(text).split("\n\n")[2:]
            self.assertEqual("\n\n".join(others), "\n\n".join(readiness_block.split("\n\n")[1:]))
            self.assertIn(f"branch {first}", readiness_block)

    def test_compose_order_is_shared(self):
        text = we.compose(
            run=["`/crav1-build-walk T1`\nbranch feat/x, T1 a"],
            held=["- `feat/y` (wave 1): T2 b — held, waits on T1"],
            branch_runs=["- feat/x: running, T1 done, next T3"],
            built=["- T1 a: commit abc1234, tests green"], built_header="Built on feat/x:",
            left=["- Skipped T4: manual step"],
            waiting=["Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2)"],
            alternatives=[we.ALTERNATIVE],
            uncommitted="2 files; commit with /crav1-finalize-commit when ready.",
        )
        heads = [part.splitlines()[0] for part in text.split("\n\n")]
        self.assertEqual(heads[0], "Run next:")
        order = ["Held:", "Branch runs:", "Built on feat/x:", "Left:", "Waiting:", "/crav1-build-tasks", "Uncommitted:"]
        positions = [next(i for i, h in enumerate(heads) if h.startswith(word)) for word in order]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("Next:", text)
        # walk_progress.compose_ending is the same function underneath.
        same = wp.compose_ending("ready", ["`/crav1-build-walk T1`\nbranch feat/x, T1 a"], [], ["Waiting: x"], [we.ALTERNATIVE], None, None, None)
        self.assertEqual(same, we.compose(run=["`/crav1-build-walk T1`\nbranch feat/x, T1 a"], waiting=["Waiting: x"], alternatives=[we.ALTERNATIVE]))

    def test_each_skill_ships_walk_ending(self):
        for skill in SKILLS:
            for tree in (SK, ROOT / "plugins/crav1/skills", ROOT / ".claude/skills"):
                self.assertTrue((tree / skill / "scripts/walk_ending.py").is_file(), f"{tree}/{skill}")
        out = subprocess.run(
            [sys.executable, str(SK / "crav1-build-walk/scripts/walk_ending.py"), "--help"],
            capture_output=True, text=True,
        )
        self.assertEqual(out.returncode, 0, out.stderr)


class BriefByDefault(unittest.TestCase):
    def test_no_flag_is_brief_and_full_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp))
            plain = json.loads(walk("readiness", "--root", str(root), "--skip-sync").stdout)
            brief = json.loads(walk("readiness", "--root", str(root), "--skip-sync", "--brief").stdout)
            full = json.loads(walk("readiness", "--root", str(root), "--skip-sync", "--full").stdout)
            self.assertEqual(plain, brief)
            self.assertNotIn("rows", plain)
            self.assertIn("rows", full)
            self.assertEqual(plain["ending"], full["ending"])
            self.assertEqual(plain["reply"], full["reply"])

    def test_text_prints_the_finished_reply(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = slice_root(Path(tmp))
            proc = walk("readiness", "--root", str(root), "--skip-sync", "--write-map", "--text")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            text = proc.stdout.strip()
            self.assertTrue(text.startswith("Tasks ready to build — orders-api"))
            self.assertIn("| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |", text)
            self.assertIn("Result: ", text)
            self.assertLess(text.index("Result: "), text.index("Run next:"))
            self.assertIn("Build map: docs/specs/orders-api/build-map.md", text)
            self.assertNotRegex(text, r"(?m)^Next:")

    def test_not_ready_next_lines_come_from_the_script(self):
        nothing = {"ready": 0, "waiting": 0, "waits_in_order": 0, "blocked": 0, "needs_verify": 0, "done": 3}
        self.assertEqual(we.not_ready_next("orders-api", nothing, False), "Next: nothing needed now.")
        verify = dict(nothing, needs_verify=2)
        self.assertIn("/crav1-verify-build-against-spec orders-api", we.not_ready_next("orders-api", verify, False))
        held = dict(nothing, waiting=2)
        self.assertIn("/crav1-resolve-open-questions orders-api", we.not_ready_next("orders-api", held, True))


class SkillText(unittest.TestCase):
    CAPS = {
        "crav1-tasks-ready-to-build": 1100,
        "crav1-tighten-and-plan-ready-to-build": 1050,
        "crav1-build-walk": 950,
    }

    def test_word_caps(self):
        for skill, cap in self.CAPS.items():
            n = len((SK / skill / "SKILL.md").read_text(encoding="utf-8").split())
            self.assertLessEqual(n, cap, f"{skill} is {n} words")
        ready = len((SK / "crav1-tasks-ready-to-build/SKILL.md").read_text(encoding="utf-8").split())
        self.assertGreaterEqual(ready, 800, "rules must stay findable")

    def test_agent_instructions_never_write_a_next_line_after_waiting(self):
        bad = re.compile(r"(?<!never )(?<!not )\b(add|write|print)\b[^.]*`Next:` line (after|below) the Waiting", re.I)
        for skill in SKILLS:
            folder = SK / skill
            for path in [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]:
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(bad.search(text), path)
        ready = (SK / "crav1-tasks-ready-to-build/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never add your own `Next:` line", ready)
        self.assertIn("--text", ready)
        for skill in SKILLS[1:]:
            text = (SK / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("shared walk ending", text)

    def test_moved_rules_are_still_findable(self):
        rules = (SK / "crav1-tasks-ready-to-build/references/rules.md").read_text(encoding="utf-8")
        old = (
            "Check each task in this order and stop at the first rule that decides it.",
            "Every task list is in **dependency order**, not task-number order.",
            "plan review unknown (inferred), run /crav1-review-plan",
            "cycle T3 → T7 → T3 (recorded)",
            "held, waits on T3 (recorded)",
            "Order: T5 → T9 → T7 → T8",
        )
        for needle in old:
            self.assertIn(needle, rules)
        shared = (ROOT / "docs/reference/run-ending.md").read_text(encoding="utf-8")
        self.assertIn("## The shared walk ending (1.156.0)", shared)

    def test_full_is_a_choice_word(self):
        ready = (SK / "crav1-tasks-ready-to-build/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Full list: `full` (1.156.0)", ready)


if __name__ == "__main__":
    unittest.main()
