"""1.207.0: write decisions back, stale wording without a jump back, readable names.

Generic fixtures only: static-IP option, week 40 to week 50, person A, orders-api.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
STALE = SK / "crav1-add-to-spec/scripts/stale_state_lines.py"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
ENDING = SK / "crav1-finalize-commit/scripts/ending.py"
LINT = ROOT / "scripts/kit-lint.py"
WHEN = "2026-11-20T12:00:00+00:00"

SPEC = """# Orders API

## Constraints

- Static IP. The service uses the static-IP option.
  - Possible answer to the Conflict line above, not a settlement.
  - The earlier date stands until person A and person B answer.
  - Waiting for person A's pick.

## Milestones

The cutover is still week 40 because the earlier note said so.

## Open questions

- Which week does the milestone use? The plan still reasons from week 40.

> The mail quoted "week 40" and this quote stays.

Answered: 2026-11-01, person A, mail: "week 40 stays" Source: docs/sources/2026-11-01-orders/
"""


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(script, *args):
    proc = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw": proc.stdout}
    return proc.returncode, payload, proc.stderr


class StaleStateLines(unittest.TestCase):
    def test_lists_notes_and_old_values_and_skips_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.md"
            path.write_text(SPEC, encoding="utf-8")
            code, payload, err = run(
                STALE, "--spec", str(path), "--changed", "C1", "--old", "week 40",
                "--new", "week 50", "--decision", "the static-IP option", "--date", "2026-11-27",
            )
            self.assertEqual(code, 0, err or payload)
            self.assertGreaterEqual(payload["n_notes"], 3)
            self.assertGreaterEqual(payload["n_lines"], 1)
            self.assertTrue(payload["excluded"])
            self.assertIn("week 40", " ".join(row["text"] for row in payload["excluded"]))
            self.assertEqual(payload["question"], f"Mark {payload['n_notes']} notes superseded and update {payload['n_lines']} lines?")
            self.assertFalse(load(LINT, "lint_1207_card").bare_code(payload["header"]))
            self.assertFalse(load(LINT, "lint_1207_q").bare_code(payload["question"]))
            self.assertIsNone(payload["wrote"])
            self.assertIn("Possible answer", path.read_text(encoding="utf-8"))
            code, wrote, err = run(
                STALE, "--spec", str(path), "--changed", "C1", "--old", "week 40",
                "--new", "week 50", "--decision", "the static-IP option", "--date", "2026-11-27", "--yes",
            )
            self.assertEqual(code, 0, err or wrote)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Superseded 2026-11-27 by the static-IP option.", text)
            self.assertIn("week 50", text)
            self.assertIn('> The mail quoted "week 40"', text)
            self.assertIn('Answered: 2026-11-01, person A, mail: "week 40 stays"', text)
            self.assertNotIn("result", json.dumps(wrote.get("card")))


class StaleWording(unittest.TestCase):
    def folder(self):
        root = Path(tempfile.mkdtemp())
        (root / "spec.md").write_text("# Orders API\n\n## Open questions\n\n- Which week?\n", encoding="utf-8")
        return root

    def test_offer_names_the_finding_and_does_not_jump(self):
        root = self.folder()
        code, out, err = run(
            WALK, "spec-finding", "--root", str(root), "--id", "P9", "--topic", "static-IP notes",
            "--text", "the static-IP notes still say week 40 and restate the old option",
        )
        self.assertEqual(code, 0, err or out)
        self.assertEqual(out["offer"], "stale-wording")
        self.assertEqual(out["header"], "Static-IP notes (P9)")
        self.assertEqual(out["question"], "Update the old static-IP notes (P9) now?")
        self.assertNotIn("result", out)
        self.assertEqual(out["options"][0]["label"], "Update the wording now (Recommended)")
        self.assertEqual(out["options"][1]["label"], "Keep it as an open point")
        self.assertTrue(out["patch_only"])
        self.assertFalse(out["full_skill"])
        lint = load(LINT, "lint_1207_walk")
        self.assertFalse(lint.bare_code(out["header"]))
        self.assertFalse(lint.bare_code(out["question"]))

    def test_question_wording_goes_to_resolve_and_update_covers_the_plan(self):
        root = self.folder()
        code, out, err = run(
            WALK, "spec-finding", "--root", str(root), "--id", "P10",
            "--text", "the open question still says week 40",
        )
        self.assertEqual(code, 0, err or out)
        self.assertEqual(out["offer"], "stale-wording")
        self.assertEqual(out["owner"], "resolve-open-questions")
        code, recorded, err = run(
            WALK, "spec-finding", "--root", str(root), "--id", "P10", "--choice", "update",
            "--notes-only", "--no-scope-drift", "--yes",
            "--text", "the open question still says week 40",
        )
        self.assertEqual(code, 0, err or recorded)
        self.assertEqual(recorded["recorded"], "patched")
        self.assertEqual(recorded["cover"], ["plan-from-spec", "review-and-tighten-plan"])
        self.assertIn("- Patched: P10", (root / "walk-progress.md").read_text(encoding="utf-8"))
        code, again, _err = run(
            WALK, "spec-finding", "--root", str(root), "--id", "P10",
            "--text", "the open question still says week 40",
        )
        self.assertEqual(code, 0)
        self.assertIsNone(again["offer"])
        self.assertTrue(again["open_point"])

    def test_still_says_on_a_merge_stays_a_kind_conflict(self):
        root = self.folder()
        (root / "spec.md").write_text(
            "# Orders API\nSynced at: orders-api develop@4ef3776, 2026-11-18\n", encoding="utf-8")
        code, out, err = run(
            WALK, "spec-finding", "--root", str(root), "--id", "P15", "--kind", "spec-text",
            "--text", "PR 82 merged into develop at f6aad4d; Synced at still says 4ef3776",
        )
        self.assertEqual(code, 0, err or out)
        self.assertEqual(out["offer"], "kind-conflict")

    def test_a_real_spec_defect_still_jumps_back(self):
        root = self.folder()
        code, out, err = run(
            WALK, "spec-finding", "--root", str(root), "--id", "P2", "--topic", "approver",
            "--text", "the plan requires a named person's yes, but the spec names no approver",
        )
        self.assertEqual(code, 0, err or out)
        self.assertEqual(out["offer"], "jump-back")
        self.assertEqual(out["header"], "Approver (P2)")
        self.assertIn("Fix Approver (P2)", out["question"])
        self.assertEqual(out["options"][0]["label"], "Fix it in the spec first (Recommended)")


class ReopenCard(unittest.TestCase):
    def test_clear_without_the_card_token_is_refused(self):
        root = Path(tempfile.mkdtemp())
        (root / "spec.md").write_text("# Orders API\n\n## Problem\nThe first draft.\n", encoding="utf-8")
        (root / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (root / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        code, recorded, err = run(
            WALK, "record", "--root", str(root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN, "--yes",
        )
        self.assertEqual(code, 0, err or recorded)
        (root / "spec.md").write_text("# Orders API\n\n## Problem\nA later edit.\n", encoding="utf-8")
        code, refused, _err = run(WALK, "clear", "--root", str(root), "--step", "tighten-spec", "--yes")
        self.assertEqual(code, 1)
        self.assertEqual(refused["code"], "needs-card")
        self.assertEqual(refused["message"], "ask the reopen card first")
        ready_code, ready, err = run(WALK, "readiness", "--root", str(root))
        self.assertEqual(ready_code, 0, err or ready)
        token = ready["reopen_cards"][0]["card"]
        self.assertNotEqual(token, "tighten-spec")
        code, cleared, err = run(
            WALK, "clear", "--root", str(root), "--step", "tighten-spec", "--card", token, "--yes",
        )
        self.assertEqual(code, 0, err or cleared)
        self.assertEqual(cleared["cleared"], "tighten-spec")

    def test_a_stale_mark_since_the_last_record_counts(self):
        root = Path(tempfile.mkdtemp())
        (root / "spec.md").write_text(
            "# Orders API\n\n## Problem\nThe first draft.\n\n## Research findings\n\nStale since 2026-11-20: the static-IP note.\n",
            encoding="utf-8",
        )
        (root / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (root / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        code, recorded, err = run(
            WALK, "record", "--root", str(root), "--step", "tighten-spec",
            "--result", "done", "--when", WHEN, "--yes",
        )
        self.assertEqual(code, 0, err or recorded)
        (root / "spec.md").write_text(
            "# Orders API\n\n## Problem\nA later edit.\n\n## Research findings\n\nStale since 2026-11-20: the static-IP note.\n",
            encoding="utf-8",
        )
        code, ready, err = run(WALK, "readiness", "--root", str(root))
        self.assertEqual(code, 0, err or ready)
        self.assertTrue(ready["stale_seen"])
        self.assertEqual(ready["reopen_cards"][0]["options"][0]["id"], "rerun")


class CommitEnding(unittest.TestCase):
    def test_an_unfinished_spec_walk_comes_before_the_build_walk(self):
        root = Path(tempfile.mkdtemp())
        (root / "spec.md").write_text("# Orders API\n", encoding="utf-8")
        (root / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (root / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        code, recorded, err = run(
            WALK, "record", "--root", str(root), "--step", "review-architecture",
            "--result", "done", "--when", WHEN, "--yes",
        )
        self.assertEqual(code, 0, err or recorded)
        ending = load(ENDING, "ending_1207")
        out = ending.build({"root": str(root), "slug": "orders-api", "branch": "master", "walk": True})
        self.assertIn("Resume the spec walk:", out["ending"])
        self.assertIn("`/crav1-tighten-and-plan-ready-to-build orders-api`", out["ending"])
        self.assertNotIn("master", out["ending"])
        self.assertNotIn("Continue the build walk", out["ending"])
        self.assertTrue(out["ending"].startswith("Run next:"))

    def test_a_finished_spec_walk_uses_the_feature_branch(self):
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", "-b", "feat/orders-api", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "person-a@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "person A"], check=True)
        (root / "README").write_text("orders\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "README"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "start"], check=True)
        (root / "spec.md").write_text("# Orders API\n", encoding="utf-8")
        ending = load(ENDING, "ending_1207b")
        out = ending.build({"root": str(root), "slug": "orders-api", "branch": "master", "walk": True})
        self.assertIn("Continue the build walk on feat/orders-api:", out["ending"])
        self.assertIn("`/crav1-build-walk orders-api feat/orders-api`", out["ending"])
        self.assertNotIn("master", out["ending"])


class ReadableNames(unittest.TestCase):
    def test_task_labels_and_done_marks_keep_both_shapes(self):
        build_map = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "map_1207")
        self.assertEqual(build_map.task_label(3, "Add login page"), "Add login page (T3)")
        marks = build_map.map_marks(
            "~~Persist the decision (T1)~~ ✓ done (PR 12)\n"
            "~~T4 Orders README~~ ✓ done (PR 13)\n"
        )
        self.assertEqual(marks[1], "PR 12")
        self.assertEqual(marks[4], "PR 13")

    def test_script_questions_are_never_a_bare_code(self):
        lint = load(LINT, "lint_1207_bare")
        self.assertTrue(lint.bare_code("P9"))
        self.assertTrue(lint.bare_code("P9?"))
        self.assertFalse(lint.bare_code("Static-IP notes (P9)"))
        self.assertFalse(lint.bare_code("Update the old static-IP notes (P9) now?"))
        walk = load(WALK, "walk_1207_names")
        offer = walk._stale_offer("P9", "tighten-spec", "static-IP notes")
        self.assertEqual(lint.card_hits(offer["question"], [(o["label"], o["text"]) for o in offer["options"]]), [])


if __name__ == "__main__":
    unittest.main()
