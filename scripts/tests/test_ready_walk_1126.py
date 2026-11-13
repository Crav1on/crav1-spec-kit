"""1.126.0: ready means the first task can start, risks link on a short anchor,
waiting is not a jump back, and records stay one step at a time.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BLOCKS = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/question_blocks.py"
ORDER = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py"
WALK_SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"
WHEN = "2026-11-10T12:00:00+00:00"
WHEN_LATER = "2026-11-10T12:05:00+00:00"

PLAN = """# Plan: the slice

Reviewed: 2026-11-10, P# open: 0

## Risks
"""

CHAIN = """# Tasks

- [ ] T1: first step for the slice
- [ ] T2: second step for the slice
- [ ] T3: third step for the slice
"""

SPEC = """# Spec

## Open questions
"""


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(WALK), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    return proc.returncode, payload


def must(args: list[str]) -> dict:
    code, payload = run(args)
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


def write_slice(root: Path, tasks: str, spec: str = SPEC, plan: str = PLAN) -> None:
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")


class ReadyChain(unittest.TestCase):
    def test_t1_t2_t3_chain_is_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, CHAIN)
            payload = must(["readiness", "--root", str(root)])
        self.assertTrue(payload["ready"])
        self.assertFalse(payload["start_build"])
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["waiting"], [])
        self.assertEqual(payload["assumptions"], [])
        reasons = [row["reason"] for row in payload["rows"] if row.get("reason")]
        self.assertTrue(any(reason.startswith("waits on T1") for reason in reasons))
        self.assertTrue(any(reason.startswith("waits on T2") for reason in reasons))

    def test_cycle_and_missing_after_still_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_slice(root, "- [ ] T1: a\n- [ ] T2: b (after: T3)\n- [ ] T3: c (after: T2)\n")
            cycle = must(["readiness", "--root", str(root)])
            write_slice(root, "- [ ] T1: a (after: T9)\n")
            missing = must(["readiness", "--root", str(root)])
        self.assertFalse(cycle["ready"])
        commands = {row["task"]: row["command"] for row in cycle["blockers"]}
        self.assertEqual(commands["T2"], "/crav1-tighten-plan")
        self.assertEqual(commands["T3"], "/crav1-tighten-plan")
        self.assertNotIn("T1", commands)
        self.assertFalse(missing["ready"])
        self.assertEqual(missing["blockers"][0]["task"], "T1")
        self.assertIn("names no task", missing["rows"][0]["reason"])


class RiskLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location("question_blocks", BLOCKS)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def _spec(self, question: str, blocks: str = "T7") -> str:
        return (
            "# Spec\n\n## Open questions\n\n"
            f"- {question}\n"
            f"  - Blocks: {blocks}\n"
        )

    def test_paraphrased_risk_matches_on_the_question_tag(self):
        spec = self._spec("Which currency for refunds?")
        plan = (
            "## Risks\n\n"
            "- The partner has not picked a currency (question: Which currency). "
            "Do not implement until resolved.\n"
        )
        got = self.mod.analyse(spec, plan)
        self.assertEqual(len(got["risks"]), 1)
        self.assertFalse(got["risks"][0]["blocks_slice"])
        self.assertEqual(got["risks"][0]["question"], "Which currency for refunds?")
        self.assertEqual(got["risks"][0]["because"], "the question has a Blocks line")

    def test_risk_that_names_blocks_t7_links_without_the_question_text(self):
        spec = self._spec("Which currency for refunds?")
        plan = (
            "## Risks\n\n"
            "- Currency stays open. Do not implement until resolved. Blocks T7.\n"
        )
        got = self.mod.analyse(spec, plan)
        self.assertFalse(got["risks"][0]["blocks_slice"])
        self.assertEqual(got["risks"][0]["question"], "Which currency for refunds?")

    def test_blocks_t7_in_the_risk_is_not_a_blocks_line_by_itself(self):
        spec = "# Spec\n\n## Open questions\n\n- Who signs the export?\n"
        plan = (
            "## Risks\n\n"
            "- Currency stays open. Do not implement until resolved. Blocks T7.\n"
        )
        got = self.mod.analyse(spec, plan)
        self.assertTrue(got["risks"][0]["blocks_slice"])
        self.assertIsNone(got["risks"][0]["question"])
        self.assertEqual(got["risks"][0]["because"], "no matching question")

    def test_long_question_matches_on_its_first_sentence(self):
        question = (
            "Which currency for refunds? The partner has not picked one, "
            "and the vendor export depends on it."
        )
        spec = self._spec(question)
        plan = "## Risks\n\n- Which currency for refunds? Do not implement until resolved.\n"
        got = self.mod.analyse(spec, plan)
        self.assertFalse(got["risks"][0]["blocks_slice"])
        self.assertEqual(got["risks"][0]["question"], question)
        self.assertNotIn(question.lower(), plan.lower())


class Waiting(unittest.TestCase):
    ASKED = """# Spec

## Open questions

- Which currency for refunds?
  - Asked: 2026-10-10, mail to the partner. Question 1.
  - Blocks: T1
"""

    PENDING = """# Spec

## Open questions

- Which currency for refunds?
  - Pending: drafted 2026-10-10 for the partner, mail. Not marked as sent yet.
  - Blocks: T1
"""

    def _ready(self, spec: str, recorded: bool) -> dict:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        write_slice(root, CHAIN, spec=spec)
        if recorded:
            must([
                "record", "--root", str(root), "--slice", "docs/specs/the-slice",
                "--step", "resolve-open-questions", "--result", "done",
                "--when", WHEN, "--yes",
            ])
        return must(["readiness", "--root", str(root)])

    def test_kept_resolve_is_waiting_not_a_jump_back(self):
        payload = self._ready(self.ASKED, recorded=True)
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["jump_back"], [])
        self.assertFalse(payload["recommend_jump"])
        self.assertGreaterEqual(len(payload["waiting"]), 1)
        row = payload["waiting"][0]
        self.assertEqual(row["task"], "T1")
        self.assertEqual(row["who"], "the partner")
        self.assertTrue(row["asked"])
        self.assertFalse(row["can_jump_back"])
        self.assertEqual(
            payload["waiting_line"],
            "Waiting: 1 tasks wait on open questions (the partner).",
        )
        by_task = {item["task"]: item for item in payload["waiting"]}
        self.assertIn("held, waits on T1", by_task["T2"]["reason"])
        self.assertIn("held, waits on T2", by_task["T3"]["reason"])
        self.assertIn("/crav1-tighten-and-plan-ready-to-build the-slice", payload["waiting_next"])
        self.assertIn("answers arrive", payload["waiting_next"])

    def test_not_yet_asked_names_show_or_ask(self):
        payload = self._ready(self.PENDING, recorded=True)
        self.assertEqual(payload["waiting"][0]["who"], "the partner")
        self.assertFalse(payload["waiting"][0]["asked"])
        self.assertFalse(payload["recommend_jump"])
        self.assertIn("/crav1-show-or-ask-open-questions the-slice", payload["waiting_next"])
        self.assertIn("not asked yet", payload["waiting_next"])

    def test_unrecorded_resolve_is_still_a_jump_back(self):
        payload = self._ready(self.ASKED, recorded=False)
        self.assertEqual(payload["waiting"], [])
        self.assertTrue(payload["recommend_jump"])
        self.assertEqual(payload["blockers"][0]["command"], "/crav1-resolve-open-questions")
        self.assertTrue(payload["blockers"][0]["can_jump_back"])


class Records(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_slice(self.root, CHAIN)

    def tearDown(self):
        self.tmp.cleanup()

    def test_record_refuses_more_than_one_step(self):
        code, payload = run([
            "record", "--root", str(self.root), "--yes",
            "--step", "tighten-spec", "--step", "resolve-open-questions",
            "--result", "done",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "one-step")
        self.assertFalse((self.root / "walk-progress.md").exists())
        code, payload = run([
            "record", "--root", str(self.root), "--yes",
            "--step", "tighten-spec, resolve-open-questions",
            "--result", "done",
        ])
        self.assertEqual(payload["code"], "one-step")

    def test_nothing_to_do_keeps_an_earlier_done(self):
        must([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN, "--yes",
        ])
        kept = must([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "nothing-to-do", "--when", WHEN_LATER, "--yes",
        ])
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertTrue(kept["kept_done"])
        self.assertEqual(kept["result"], "done")
        self.assertIn("Result: done", text)
        self.assertNotIn("Result: nothing-to-do", text)

    def test_reopened_nothing_to_do_says_use_clear(self):
        must([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN, "--yes",
        ])
        text = (self.root / "spec.md").read_text(encoding="utf-8")
        (self.root / "spec.md").write_text(text.replace("# Spec", "# Spec edited", 1), encoding="utf-8")
        code, payload = run([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "nothing-to-do", "--yes",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "use-clear")
        text = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Result: done", text)
        self.assertIn(f"Done: {WHEN}", text)

    def test_resume_warns_when_done_stamps_match(self):
        must([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN, "--yes",
        ])
        must([
            "record", "--root", str(self.root), "--step", "resolve-open-questions",
            "--result", "done", "--when", WHEN, "--yes",
        ])
        warned = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIn("tighten-spec", warned["done_stamp_warning"])
        self.assertIn("resolve-open-questions", warned["done_stamp_warning"])
        self.assertIn(WHEN, warned["done_stamp_warning"])
        must([
            "record", "--root", str(self.root), "--step", "plan-from-spec",
            "--result", "done", "--when", WHEN_LATER, "--yes",
        ])
        # The first two still share a stamp, so the warning stays.
        still = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIn(WHEN, still["done_stamp_warning"])
        self.assertNotIn(WHEN_LATER, still["done_stamp_warning"])

    def test_distinct_stamps_have_no_warning(self):
        must([
            "record", "--root", str(self.root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN, "--yes",
        ])
        must([
            "record", "--root", str(self.root), "--step", "resolve-open-questions",
            "--result", "done", "--when", WHEN_LATER, "--yes",
        ])
        payload = must(["resume", "--root", str(self.root), "--no-playbook"])
        self.assertIsNone(payload["done_stamp_warning"])


class JsonIds(unittest.TestCase):
    def test_task_order_json_uses_t_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.md"
            path.write_text(CHAIN, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ORDER), str(path), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["order"], ["T1", "T2", "T3"])
        self.assertEqual(payload["ready"], ["T1"])
        self.assertEqual(payload["next"], "T1")
        self.assertEqual(payload["blocked"], [])
        self.assertEqual(payload["waits_in_order"][0]["id"], "T2")
        self.assertTrue(payload["waits_in_order"][0]["reason"].startswith("waits on T1"))


class WindowsEncoding(unittest.TestCase):
    def test_scripts_print_under_cp1252(self):
        scripts = sorted((ROOT / ".cursor/skills/crav1").glob("**/scripts/*.py"))
        scripts.append(ROOT / "scripts/task-order.py")
        self.assertGreaterEqual(len(scripts), 8)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        for script in scripts:
            text = script.read_text(encoding="utf-8")
            self.assertIn('reconfigure(encoding="utf-8")', text, script.name)
            proc = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                env=env,
                check=False,
            )
            stderr = proc.stderr.decode("utf-8", "replace")
            self.assertNotIn("UnicodeEncodeError", stderr, script.name)
            self.assertEqual(proc.returncode, 0, script.name + "\n" + stderr)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.md"
            path.write_text(CHAIN, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ORDER), str(path)],
                capture_output=True,
                env=env,
                check=False,
            )
        stderr = proc.stderr.decode("utf-8", "replace")
        self.assertEqual(proc.returncode, 0, stderr)
        self.assertNotIn("UnicodeEncodeError", stderr)
        out = proc.stdout.decode("utf-8", "replace")
        self.assertTrue("→" in out or "->" in out)


class WalkWording(unittest.TestCase):
    def test_docs_say_jump_back_reruns_the_skill_and_readiness_builds_rows(self):
        readiness = (WALK_SKILL / "references/readiness.md").read_text(encoding="utf-8")
        steps = (WALK_SKILL / "references/steps.md").read_text(encoding="utf-8")
        common = (WALK_SKILL / "references/common.md").read_text(encoding="utf-8")
        progress = (WALK_SKILL / "references/progress.md").read_text(encoding="utf-8")
        write = (
            ROOT / ".cursor/skills/crav1/crav1-plan-from-spec/references/write.md"
        ).read_text(encoding="utf-8")
        self.assertIn("readiness --root", readiness)
        self.assertIn("Do not hand-build a rows JSON file", readiness)
        self.assertIn("the first task can start", readiness)
        self.assertIn("waits on T#", readiness)
        self.assertIn("not a jump back", readiness)
        self.assertIn("recommend_jump", readiness)
        self.assertIn("Waiting: <n> tasks wait on open questions (<who>).", readiness)
        self.assertIn("/crav1-show-or-ask-open-questions <slug>", readiness)
        self.assertIn("does not write `Reviewed:`", readiness)
        self.assertIn("even for a small patch", steps)
        self.assertIn("clear --step <id> --yes", steps)
        self.assertIn("keeps an earlier `done` Result", steps)
        self.assertIn("One `record` call per step", steps)
        self.assertIn("refuses more than one step", common)
        self.assertIn("done_stamp_warning", progress)
        self.assertIn("kept open; blocks T2, T4 until resolved.", write)
        self.assertIn("(question: <first words>)", write)
        self.assertIn('Only a question with no `Blocks:` line keeps "do not implement until resolved"', write)


if __name__ == "__main__":
    unittest.main()
