"""1.146.0: stable finding identity, walk map write, and one start command.

A close reword of a recorded finding is that finding, with a this-is-new
escape. Old progress files that store only Key still match. The walk's ready
check writes build-map.md. start returns resume and playbook-status together.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BLOCKS = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/question_blocks.py"
MAP = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/build_map.py"
SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"
WHEN = "2026-11-13T09:00:00+00:00"
FINDING = (
    "the plan requires a named person's yes to stop a prod function app, "
    "but the spec names no approver"
)
REWORD = (
    "the plan requires a named person's yes before stopping a prod function app, "
    "but the spec names no approver"
)
SAME = "same recorded finding (Recommended)"
NEW = "this is new"
NEW_REC = "this is new (Recommended)"


def run(script: Path, args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )
    return proc.returncode, proc.stdout, proc.stderr


def must_json(args: list[str], cwd: Path | None = None) -> dict:
    code, out, err = run(WALK, args, cwd)
    try:
        payload = json.loads(out or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(err + out) from exc
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload or err or out)
    return payload


def key_of(text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def slice_dir(parent: Path | None = None) -> Path:
    base = parent or Path(tempfile.mkdtemp())
    root = base / "orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text("# Orders export\n\n## Open questions\n", encoding="utf-8")
    (root / "plan.md").write_text(
        "# Plan\n\nReviewed: 2026-11-11, P# open: 0\n\n## Approach\n\n1. Record the order.\n\n## Risks\n",
        encoding="utf-8",
    )
    (root / "tasks.md").write_text(
        "# Tasks\n\n- [ ] T1: record the order (branch: feat/orders-record) (spec: A1)\n",
        encoding="utf-8",
    )
    return root


def record_jump(root: Path, finding: str, fid: str = "P2", topic: str | None = None, force_new: bool = False) -> dict:
    args = [
        "spec-finding", "--root", str(root), "--id", fid, "--text", finding,
        "--choice", "tighten-spec", "--yes",
    ]
    if topic:
        args.extend(["--topic", topic])
    if force_new:
        args.append("--new")
    return must_json(args)


class StableFinding(unittest.TestCase):
    def test_exact_words_are_not_asked_again(self):
        root = slice_dir()
        record_jump(root, FINDING, topic="approver")
        again = must_json(["spec-finding", "--root", str(root), "--id", "P2", "--text", FINDING])
        self.assertIsNone(again["offer"])
        self.assertTrue(again["already_jumped"])
        self.assertNotIn("options", again)

    def test_close_reword_offers_same_or_new_and_alias_keeps_the_first_key(self):
        root = slice_dir()
        first = record_jump(root, FINDING, topic="approver")
        offered = must_json([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", REWORD, "--topic", "approver",
        ])
        self.assertEqual(offered["offer"], "same-or-new")
        self.assertIsNone(offered["wrote"])
        labels = [item["label"] for item in offered["options"]]
        self.assertEqual(labels, [SAME, NEW])
        self.assertTrue(offered["options"][0]["recommended"])
        self.assertFalse(offered["options"][1]["recommended"])
        skipped = must_json([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", REWORD,
            "--choice", "tighten-spec", "--yes",
        ])
        self.assertEqual(skipped["offer"], "same-or-new")
        self.assertIsNone(skipped["wrote"])
        self.assertFalse((root / "walk-progress.md").read_text(encoding="utf-8").count("- Jump-back:") > 1)
        accepted = must_json([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", REWORD,
            "--topic", "approver", "--choice", "same", "--yes",
        ])
        self.assertTrue(accepted["aliased"])
        self.assertEqual(accepted["key"], first["key"])
        self.assertEqual(accepted["recorded"], "open-point")
        progress = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn(f"Key: {first['key']}", progress)
        self.assertIn("Topic: approver", progress)
        self.assertIn("Alias:", progress)
        self.assertEqual(progress.count("- Jump-back:"), 1)

    def test_this_is_new_records_a_separate_finding(self):
        root = slice_dir()
        first = record_jump(root, FINDING, topic="approver")
        offered = must_json([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", REWORD, "--new",
        ])
        self.assertEqual(offered["offer"], "jump-back")
        recorded = must_json([
            "spec-finding", "--root", str(root), "--id", "P4", "--text", REWORD,
            "--topic", "currency", "--new", "--choice", "tighten-spec", "--yes",
        ])
        self.assertEqual(recorded["recorded"], "jump-back")
        self.assertNotEqual(recorded["key"], first["key"])
        progress = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertEqual(progress.count("- Jump-back:"), 2)
        self.assertNotIn("Alias:", progress)

    def test_a_different_topic_is_not_the_same_finding(self):
        root = slice_dir()
        record_jump(root, FINDING, topic="approver")
        offered = must_json([
            "spec-finding", "--root", str(root), "--id", "P2", "--text", REWORD, "--topic", "currency",
        ])
        self.assertEqual(offered["offer"], "jump-back")

    def test_two_close_findings_recommend_this_is_new(self):
        root = slice_dir()
        receipt = "the export omits the tax line on the printed receipt for the order"
        invoice = "the export omits the tax line on the printed invoice for the order"
        both = "the export omits the tax line on the printed receipt and the invoice for the order"
        record_jump(root, receipt, fid="P2")
        record_jump(root, invoice, fid="P4", force_new=True)
        offered = must_json(["spec-finding", "--root", str(root), "--id", "P6", "--text", both])
        self.assertEqual(offered["offer"], "same-or-new")
        self.assertEqual(offered["options"][0]["label"], NEW_REC)
        self.assertTrue(offered["options"][0]["recommended"])
        self.assertGreaterEqual(len(offered["matches"]), 2)

    def test_old_progress_file_still_matches_exact_words(self):
        root = slice_dir()
        stored = key_of(FINDING)
        (root / "walk-progress.md").write_text(
            "# Walk progress\n\n"
            "Walk: tighten-and-plan-ready-to-build\n"
            "Slice: docs/specs/orders-api/\n\n"
            "- Jump-back: P2\n"
            f"  Done: {WHEN}\n"
            f"  Finding: {FINDING}\n"
            "  Result: jumped\n"
            "  Open: ../crav1-tighten-spec/SKILL.md\n"
            "  Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build\n"
            f"  Key: {stored}\n",
            encoding="utf-8",
        )
        exact = must_json(["spec-finding", "--root", str(root), "--id", "P2", "--text", FINDING])
        self.assertTrue(exact["already_jumped"])
        self.assertIsNone(exact["offer"])
        reword = must_json(["spec-finding", "--root", str(root), "--id", "P2", "--text", REWORD])
        self.assertEqual(reword["offer"], "same-or-new")
        self.assertIn(NEW, [item["label"] for item in reword["options"]])


class StableQuestion(unittest.TestCase):
    def test_exact_key_stays_and_stable_key_ignores_a_commit_list(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("question_blocks_1146", BLOCKS)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        text = "Which currency for refunds?"
        norm = re.sub(r"\s+", " ", text).strip().lower()
        expect = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]
        self.assertEqual(mod.question_key(text), expect)
        left = "Which currency for refunds? See commit abc1234."
        right = "Which currency for refunds? See commit ffeedd11."
        self.assertNotEqual(mod.question_key(left), mod.question_key(right))
        self.assertEqual(mod.question_stable_key(left), mod.question_stable_key(right))
        self.assertEqual(mod.question_similarity(left, right), 1.0)
        self.assertLess(
            mod.question_similarity(
                "Which currency for refunds on the card?",
                "Which lane prints the shipping label?",
            ),
            0.86,
        )

    def test_one_reword_stays_and_two_close_questions_do_not_merge(self):
        root = slice_dir()
        (root / "spec.md").write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Which currency for refunds?\n"
            "  - Blocks: T1\n",
            encoding="utf-8",
        )
        must_json([
            "record", "--root", str(root), "--step", "resolve-open-questions",
            "--result", "done", "--yes", "--when", WHEN,
        ])
        progress = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Question:", progress)
        (root / "spec.md").write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Which currency should refunds use?\n"
            "  - Blocks: T1\n",
            encoding="utf-8",
        )
        held = must_json(["readiness", "--root", str(root)])
        self.assertEqual(len(held["question_aliases"]), 1)
        self.assertEqual(held["question_aliases"][0]["how"], "similar")
        self.assertEqual(held["question_aliases"][0]["matched"], "Which currency for refunds?")
        rows = {row["task"]: row for row in held["rows"]}
        self.assertEqual(rows["T1"]["bucket"], "waiting")
        self.assertTrue(rows["T1"]["kept"])
        escaped = must_json([
            "readiness", "--root", str(root),
            "--new-question", held["question_aliases"][0]["key"],
        ])
        self.assertEqual(escaped["question_aliases"], [])
        self.assertEqual({row["task"]: row["bucket"] for row in escaped["rows"]}["T1"], "waiting")

        (root / "spec.md").write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Which currency for refunds on the printed receipt?\n"
            "  - Blocks: T1\n"
            "- Which currency for refunds on the printed invoice?\n"
            "  - Blocks: none\n",
            encoding="utf-8",
        )
        must_json([
            "record", "--root", str(root), "--step", "resolve-open-questions",
            "--result", "done", "--yes", "--when", WHEN,
        ])
        (root / "spec.md").write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Which currency for refunds on the printed receipt and the invoice?\n"
            "  - Blocks: T1\n",
            encoding="utf-8",
        )
        mixed = must_json(["readiness", "--root", str(root)])
        self.assertEqual(mixed["question_aliases"], [])

    def test_a_refreshed_commit_list_uses_the_stable_key(self):
        root = slice_dir()
        (root / "spec.md").write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Which currency for refunds? See commit abc1234.\n"
            "  - Blocks: T1\n",
            encoding="utf-8",
        )
        must_json([
            "record", "--root", str(root), "--step", "resolve-open-questions",
            "--result", "done", "--yes", "--when", WHEN,
        ])
        (root / "spec.md").write_text(
            "# Orders export\n\n## Open questions\n\n"
            "- Which currency for refunds? See commit ffeedd11.\n"
            "  - Blocks: T1\n",
            encoding="utf-8",
        )
        payload = must_json(["readiness", "--root", str(root)])
        self.assertEqual(payload["question_aliases"][0]["how"], "stable")
        self.assertEqual(payload["question_aliases"][0]["similarity"], 1.0)


class WalkMapAndStart(unittest.TestCase):
    def test_write_map_matches_the_standalone_file_and_is_opt_in(self):
        root = slice_dir()
        code, out, err = run(MAP, [str(root)])
        self.assertEqual(code, 0, err or out)
        standalone = (root / "build-map.md").read_bytes()
        (root / "build-map.md").unlink()
        plain = must_json(["readiness", "--root", str(root)])
        self.assertNotIn("build_map", plain)
        self.assertFalse((root / "build-map.md").exists())
        wrote = must_json(["readiness", "--root", str(root), "--write-map"])
        self.assertEqual((root / "build-map.md").read_bytes(), standalone)
        self.assertTrue(wrote["build_map"].startswith("Build map:"))
        self.assertTrue(str(wrote["build_map_wrote"]).endswith("build-map.md"))
        self.assertEqual((root / "verify.md").exists(), False)

    def test_start_returns_resume_and_playbook_status(self):
        repo = Path(tempfile.mkdtemp())
        specs = repo / "docs" / "specs"
        root = slice_dir(specs)
        (root / "spec.md").write_text(
            "# Orders export\n\nPlaybook: docs/playbooks/orders-export.md\n\n## Open questions\n",
            encoding="utf-8",
        )
        other = specs / "orders-archive"
        other.mkdir()
        (other / "spec.md").write_text("# Orders archive\n", encoding="utf-8")
        book = repo / "docs" / "playbooks" / "orders-export.md"
        book.parent.mkdir(parents=True)
        book.write_text(
            "# Orders export\n\nDocs path: docs/playbooks/orders-export.md\n",
            encoding="utf-8",
        )
        started = must_json(["start", "--root", str(root)], cwd=repo)
        resumed = must_json(["resume", "--root", str(root), "--no-playbook"])
        self.assertEqual(started["slug"], "orders-api")
        self.assertEqual(started["how"], "folder")
        self.assertIsNone(started["playbook_status"])
        self.assertEqual(started["resume"], resumed)
        by_slug = must_json(
            ["start", "--root", "orders-api", "--playbook", str(book)],
            cwd=repo,
        )
        status = must_json(["playbook-status", "--root", str(root), "--playbook", str(book)])
        bare = must_json(["resume", "--root", str(root)])
        self.assertEqual(by_slug["slug"], "orders-api")
        self.assertEqual(by_slug["playbook_status"], status)
        self.assertEqual(by_slug["resume"], bare)
        code, out, _err = run(WALK, ["start", "--root", "orders"], cwd=repo)
        self.assertEqual(code, 2)
        payload = json.loads(out)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["code"], "several")
        self.assertEqual(
            sorted(item["slug"] for item in payload["matches"]),
            ["orders-api", "orders-archive"],
        )
        titled = must_json(["start", "--root", "orders export"], cwd=repo)
        self.assertEqual(titled["slug"], "orders-api")

    def test_walk_docs_do_not_open_the_ready_skill(self):
        for name in ("SKILL.md", "references/readiness.md", "references/common.md"):
            text = (SKILL / name).read_text(encoding="utf-8")
            self.assertNotIn("Open `../crav1-tasks-ready-to-build/SKILL.md`", text)
        readiness = (SKILL / "references/readiness.md").read_text(encoding="utf-8")
        self.assertIn("readiness --root <spec-folder> --write-map", readiness)
        self.assertIn("this is new", readiness)
        common = (SKILL / "references/common.md").read_text(encoding="utf-8")
        self.assertIn("walk_progress.py start --root <folder-or-slug>", common)
        steps = (SKILL / "references/steps.md").read_text(encoding="utf-8")
        self.assertIn(SAME, steps)
        self.assertIn(NEW, steps)


if __name__ == "__main__":
    unittest.main()
