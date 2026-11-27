"""1.209.0: finding topics, the question itself, waits-on T numbers, the question owner, a dry run onto main.

Generic fixtures only: orders-api, person A, the partner.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
ENDING = SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py"
BLOCKS = SK / "crav1-tasks-ready-to-build/scripts/question_blocks.py"
DRY = ROOT / "scripts/kit_dry_run.py"
WHEN = "2026-11-20T12:00:00+00:00"
FINDING = (
    "the plan requires a named person's yes to stop a prod function app, "
    "but the spec names no approver"
)
OPEN = "../crav1-tighten-spec/SKILL.md"

PLAN = """# Plan

Reviewed: 2026-11-27, P# open: 0

## Approach

1. Record the certificate. (T1)
2. Ship the form. (T2)

## Risks
"""

TASKS = """# Tasks

- [ ] T1: Record the certificate (branch: feat/orders-certificate)
- [ ] T2: Ship the form (branch: feat/orders-export) (after: T1)
"""


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def key_of(text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def jump_block(fid: str, finding: str, topic: str | None = None) -> str:
    lines = [
        f"- Jump-back: {fid}",
        f"  Done: {WHEN}",
        f"  Finding: {finding}",
        "  Result: jumped",
        f"  Open: {OPEN}",
        "  Continue: plan-from-spec",
        f"  Key: {key_of(finding)}",
    ]
    if topic:
        lines.append(f"  Topic: {topic}")
    return "\n".join(lines) + "\n"


def start_slice(progress: str) -> Path:
    root = Path(tempfile.mkdtemp()) / "orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text("# Orders export\n\n## Open questions\n", encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    (root / "walk-progress.md").write_text(
        "# Walk progress\n\n"
        "Walk: tighten-and-plan-ready-to-build\n"
        "Slice: docs/specs/orders-api/\n\n"
        + progress,
        encoding="utf-8",
    )
    return root


def run_walk(root: Path, *args: str) -> tuple[int, dict, str]:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(WALK), *args],
        capture_output=True, text=True, encoding="utf-8", cwd=root,
    )
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw": proc.stdout}
    return proc.returncode, payload, proc.stderr


def readiness(spec: str, tasks: str = TASKS, claims: str | None = None, git_user: str | None = None) -> dict:
    base = Path(tempfile.mkdtemp())
    root = base / "docs/specs/orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    if claims:
        (root / "claims.md").write_text(claims, encoding="utf-8")
    if git_user:
        subprocess.run(["git", "init", "-q"], cwd=base, check=True, capture_output=True)
        subprocess.run(["git", "-C", str(base), "config", "user.name", git_user], check=True)
        subprocess.run(["git", "-C", str(base), "config", "user.email", "a@example.com"], check=True)
    recorded = subprocess.run(
        [sys.executable, str(WALK), "record", "--root", str(root), "--slice", "docs/specs/orders-api",
         "--step", "resolve-open-questions", "--result", "done", "--when", WHEN, "--yes"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if recorded.returncode != 0:
        raise AssertionError(recorded.stderr + recorded.stdout)
    code, payload, err = run_walk(root, "readiness", "--root", str(root), "--full", "--skip-sync")
    if code != 0 or not payload.get("ok", True):
        raise AssertionError(err + json.dumps(payload)[:2000])
    payload["_base"] = str(base)
    return payload


def held_text(payload: dict) -> str:
    parts = list(payload.get("held_lines") or [])
    ending = payload.get("ending") or payload.get("reply") or ""
    return "\n".join(parts) + "\n" + ending


we = load(ENDING, "walk_ending_1209")
qb = load(BLOCKS, "question_blocks_1209")


class FindingTopics(unittest.TestCase):
    def test_empty_topics_are_filled_once(self):
        root = start_slice(jump_block("P9", FINDING) + "\n" + jump_block("P2", "the export omits the tax line on the receipt"))
        code, first, err = run_walk(root, "start", "--root", str(root), "--skip-sync")
        self.assertEqual(code, 0, err or first)
        line = first.get("topics_line") or ""
        self.assertTrue(line.startswith("Filled finding topics: "), line)
        self.assertIn("(P9)", line)
        self.assertIn("(P2)", line)
        self.assertNotIn("topics_line", first.get("resume") or {})
        stored = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertEqual(stored.count("Topic:"), 2)
        self.assertNotIn("Topic: \n", stored)
        code, second, err = run_walk(root, "start", "--root", str(root), "--skip-sync")
        self.assertEqual(code, 0, err or second)
        self.assertNotIn("topics_line", second)
        self.assertEqual((root / "walk-progress.md").read_text(encoding="utf-8"), stored)
        shutil.rmtree(root.parent, ignore_errors=True)

    def test_a_recorded_topic_is_left(self):
        root = start_slice(jump_block("P9", FINDING, topic="approver"))
        code, payload, err = run_walk(root, "start", "--root", str(root), "--skip-sync")
        self.assertEqual(code, 0, err or payload)
        self.assertNotIn("topics_line", payload)
        text = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Topic: approver", text)
        self.assertEqual(text.count("Topic:"), 1)
        shutil.rmtree(root.parent, ignore_errors=True)


class HeldQuestionText(unittest.TestCase):
    def test_statement_gives_way_to_the_question_sentence(self):
        text = "The partner replied that the expiry is January. Which certificate details does the partner still need?"
        self.assertEqual(we.question_text(text), "Which certificate details does the partner still need?")

    def test_held_task_quotes_the_question_field_not_the_statement(self):
        spec = """# Orders export

## Open questions

- The partner replied that the expiry is January.
  - Q: Which certificate details does the partner still need?
  - Statement: The partner replied that the expiry is January.
  - Answer: The expiry is January.
  - Blocks: T1
"""
        payload = readiness(spec, tasks="- [ ] T1: Record the certificate (branch: feat/orders-certificate)\n")
        text = held_text(payload)
        self.assertIn('open question "Which certificate details does the partner still need?"', text)
        self.assertNotIn('open question "The partner replied', text)
        self.assertNotIn('open question "The expiry is January."', text)
        shutil.rmtree(payload["_base"], ignore_errors=True)


class WaitsOnNumbers(unittest.TestCase):
    def test_a_waits_on_list_stays_t_numbers(self):
        names = {"T3": "Record the decision", "T5": "Take in develop", "T12": "Ship the form"}
        self.assertEqual(we._named_reason("waits on T3, T5", names), "waits on T3, T5")
        nested = "waits on Record the decision (T3), Take in develop (T5)"
        self.assertEqual(we._named_reason(nested, names), "waits on T3, T5")
        block = we.branch_block(
            "feat/orders-export",
            ["Ship the form (T12)", "Record the decision (T3)", "Take in develop (T5)"],
            first="Ship the form (T12)",
            waits={"T12": "waits on T3, T5"},
        )
        self.assertIn("- Ship the form (T12) (waits on T3, T5)", block)
        wait = block.split("waits on", 1)[1].split(")", 1)[0]
        self.assertEqual(wait, " T3, T5")
        pr = "held, waits on PR 21 to merge (T47, recorded)"
        self.assertEqual(we._named_reason(pr, {"T47": "Ship the form"}), pr)

    def test_other_names_stay_readable(self):
        self.assertEqual(
            we._named_reason("after T3", {"T3": "Record the decision"}),
            "after Record the decision (T3)",
        )


class QuestionOwner(unittest.TestCase):
    SPEC_OWNER = """# Orders export

## Open questions

- Which certificate details does the partner still need?
  - Ask: the partner
  - Asked: 2026-11-01, mail to person A. Question 1.
  - Blocks: T1
"""
    SPEC_RUNNER = """# Orders export

## Open questions

- Which certificate details does the partner still need?
  - Asked: 2026-11-01, mail to person A. Question 1.
  - Blocks: T1
"""
    SPEC_CLAIM = """# Orders export

## Open questions

- Which certificate details does the partner still need?
  - Blocks: T1
"""
    CLAIM = "In progress: feat/orders-certificate, T1, person A, since 2026-11-13T15:50:00+01:00\n"
    TASK = "- [ ] T1: Record the certificate (branch: feat/orders-certificate)\n"

    def test_ask_field_wins_over_the_runner(self):
        payload = readiness(self.SPEC_OWNER, tasks=self.TASK, claims=self.CLAIM, git_user="person A")
        text = held_text(payload)
        self.assertIn("Waiting for the partner.", text)
        self.assertNotIn("Waiting for person A.", text)
        shutil.rmtree(payload["_base"], ignore_errors=True)

    def test_runner_when_no_owner_is_recorded(self):
        asked = readiness(self.SPEC_RUNNER, tasks=self.TASK)
        self.assertIn("Waiting for person A.", held_text(asked))
        shutil.rmtree(asked["_base"], ignore_errors=True)
        claimed = readiness(self.SPEC_CLAIM, tasks=self.TASK, claims=self.CLAIM, git_user="person A")
        self.assertIn("Waiting for person A.", held_text(claimed))
        shutil.rmtree(claimed["_base"], ignore_errors=True)

    def test_owner_mark_is_read(self):
        text = """# Orders

## Open questions

- Which certificate details does the partner still need?
  - owner: the platform team
  - Asked: 2026-11-01, mail to person A.
  - Blocks: T1
"""
        found = qb.kept_open(text, task_ids=["T1"])
        self.assertEqual(found[0]["who"], "the platform team")
        self.assertTrue(found[0]["owner_recorded"])
        self.assertEqual(found[0]["prompt"], "")


class DryRunOntoMain(unittest.TestCase):
    def test_placeholder_and_unknown_spec_stop(self):
        base = Path(tempfile.mkdtemp())
        proj = base / "project"
        spec = proj / "docs/specs/orders-api"
        spec.mkdir(parents=True)
        (spec / "spec.md").write_text("# Orders API\n", encoding="utf-8")
        retired = proj / "docs/specs/retired/old-slice"
        retired.mkdir(parents=True)
        (retired / "spec.md").write_text("# Old\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(proj)], check=True)
        subprocess.run(["git", "-C", str(proj), "add", "-A"], check=True)
        env = dict(os.environ, GIT_AUTHOR_NAME="person A", GIT_AUTHOR_EMAIL="a@example.com",
                   GIT_COMMITTER_NAME="person A", GIT_COMMITTER_EMAIL="a@example.com")
        subprocess.run(["git", "-C", str(proj), "commit", "-qm", "start"], check=True, env=env)
        for spec_arg, needle in (
            ("<your spec>", "is a placeholder"),
            ("<orders>", "is a placeholder"),
            ("missing-slice", "No spec named 'missing-slice'"),
        ):
            proc = subprocess.run(
                [sys.executable, str(DRY), "--branch", "feat/kit-test", "--spec", spec_arg, "--repo", str(proj)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn(needle, proc.stdout)
            self.assertIn("Available specs: orders-api", proc.stdout)
            self.assertNotIn("readiness skipped", proc.stdout)
            self.assertNotIn("retired", proc.stdout)
        shutil.rmtree(base, ignore_errors=True)

    def test_merge_onto_main_and_conflict_hides_main_only_deletes(self):
        from test_kit_dry_run_1199 import git, kit_fixture, project_fixture, restamp

        base = Path(tempfile.mkdtemp())
        try:
            kit = kit_fixture(base)
            only = kit / ".cursor/skills/crav1/crav1-docs/reference/only-on-main.md"
            only.write_text("# Only on main\n", encoding="utf-8")
            git(kit, "add", "-A")
            git(kit, "commit", "-qm", "main adds a file")
            ahead = project_fixture(base, kit)
            clean = _dry(ahead, kit)
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            self.assertNotIn("branch is behind main", clean.stdout)
            self.assertNotIn("could not compare this branch with main", clean.stdout, clean.stdout)
            update = clean.stdout.split("--- Update ---", 1)[1].split("--- Checks ---", 1)[0]
            self.assertIn("only-on-main.md", update, clean.stdout)

            git(kit, "checkout", "-q", "main")
            restamp(kit, "1.0.2")
            git(kit, "add", "-A")
            git(kit, "commit", "-qm", "main restamps")
            git(kit, "tag", "v1.0.2")
            conflict_proj = _project_at(base / "conflict", kit, "v1.0.2")
            blocked = _dry(conflict_proj, kit)
            self.assertEqual(blocked.returncode, 0, blocked.stdout + blocked.stderr)
            self.assertRegex(
                blocked.stdout,
                r"branch is behind main by \d+ commits?; these files come only from main: .*\.cursor/skills/crav1/crav1-docs/reference/only-on-main\.md",
            )
            update = blocked.stdout.split("--- Update ---", 1)[1].split("--- Checks ---", 1)[0]
            self.assertNotIn("only-on-main.md", update)
        finally:
            shutil.rmtree(base, ignore_errors=True)


def _dry(proj: Path, kit: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, CRAV1_DRY_RUN_NO_CLIPBOARD="1")
    return subprocess.run(
        [sys.executable, str(DRY), "--branch", "feat/kit-test", "--spec", "orders-api",
         "--kit-source", str(kit), "--repo", str(proj)],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=600,
    )


def _project_at(base: Path, kit: Path, rev: str) -> Path:
    from test_kit_dry_run_1199 import git

    base.mkdir(parents=True, exist_ok=True)
    proj = base / "project"
    proj.mkdir()
    subprocess.run(["git", "init", "-q", str(proj)], check=True)
    old = base / "kit-old"
    git(kit, "worktree", "add", "-q", "--detach", str(old), rev)
    shutil.copytree(old / ".cursor", proj / ".cursor")
    git(kit, "worktree", "remove", "--force", str(old))
    spec = proj / "docs/specs/orders-api"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("# Orders API\n\n## Problem\n\nOrders need an export.\n", encoding="utf-8")
    (spec / "plan.md").write_text("# Plan\n\nReviewed: 2026-11-19, P# open: 0\n", encoding="utf-8")
    (spec / "tasks.md").write_text("# Tasks\n\n- [ ] T1 Add the export endpoint (branch: feat/orders-export)\n", encoding="utf-8")
    git(proj, "add", "-A")
    git(proj, "commit", "-qm", "start")
    return proj


if __name__ == "__main__":
    unittest.main()
