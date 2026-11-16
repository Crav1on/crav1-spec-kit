"""1.175.0: Run next continues only your own branch walk, a built task under
someone else's claim reads built, a reopened step says why above an action
label, a build walk's own files never reopen a step, and the Catch up first
push entry is said once."""

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
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-13T10:00:00+01:00"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wp = load(WALK, "walk_progress_1175")
bm = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "build_map_1175")
we = load(SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py", "walk_ending_1175")


def run(args: list[str]) -> dict:
    proc = subprocess.run([sys.executable, str(WALK), *args], capture_output=True, text=True, check=False)
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    if proc.returncode != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


SPEC = """# Orders CI/CD

The orders-api gets its own pipeline.

## Acceptance criteria

- [ ] The deploy text says how a fix reaches TEST.

## Constraints

- orders-api follows the per-function pipeline pattern.

## Match

- Branch: orders-api feat/orders-cicd

## Open questions

- Which lane prints the label?
  - Blocks: none
"""

TASKS = """# Tasks

- [x] T1: Orders schema (branch: feat/orders-schema) (after: )
- [ ] T9: Orders CI/CD: infra Bicep for dev, test and prod (branch: feat/orders-cicd) (after: T1)
- [ ] T10: Orders CI/CD: deploy pipeline with DEV, TEST and PROD stages (branch: feat/orders-cicd) (after: T9)
- [ ] T11: Orders CI/CD: ci.yml lints and tests orders-api (branch: feat/orders-cicd) (after: T9)
- [ ] T12: Orders CI/CD: README deploy text for a quick fix (branch: feat/orders-cicd) (after: T10, T11)
- [ ] T13: Orders DEV: switch day for the new plan (branch: feat/orders-switch-day) (after: T12)
"""

PLAN = """# Plan: orders

## Approach

1. Schema. (T1)
2. CI/CD. (T9, T10, T11, T12)
3. Switch day. (T13)

## Risks
"""

CLAIMS = """# Claims

In progress: feat/orders-cicd, T9, T10, T11, T12, person B, since 2026-11-16T09:40:00+01:00
"""

# The live shape: no Tasks line, Owner self from person B's own run, every
# task built, PR opened, stopped before the merge.
PROGRESS = """# Build progress

Walk: build-walk
Branch: feat/orders-cicd
Owner: self

## Run

Run: whole branch
Run yes: person B, 2026-11-16T09:40:00+01:00
Task stamps: T9 a1b2c3d4e5f6, T10 b2c3d4e5f6a1, T11 c3d4e5f6a1b2, T12 d4e5f6a1b2c3
Next task: none
- Built: T9, commit 1f2e3d4, tests green
- Built: T10, commit 2e3d4c5, tests none
- Built: T11, commit 3d4c5b6, tests green
- Built: T12, commit 4c5b6a7, tests none

- Step: open-pr
  Done: 2026-11-16T10:30:00+01:00
  Result: PR 82
"""

NOT_BUILT = """# Build progress

Walk: build-walk
Branch: feat/orders-cicd
Owner: self

## Run

Run: whole branch
Run yes: person B, 2026-11-16T09:40:00+01:00
Next task: T9
"""


def make_slice(tmp: str, user: str | None = "person A", progress: str | None = PROGRESS) -> Path:
    repo = Path(tmp) / "specs"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    if user:
        subprocess.run(["git", "-C", str(repo), "config", "user.name", user], check=True)
    root = repo / "orders"
    root.mkdir()
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(TASKS, encoding="utf-8")
    (root / "verify.md").write_text("# Verify\n", encoding="utf-8")
    (root / "claims.md").write_text(CLAIMS, encoding="utf-8")
    if progress:
        (root / "build-progress").mkdir()
        (root / "build-progress" / "feat--orders-cicd.md").write_text(progress, encoding="utf-8")
    return root


def record_walk(root: Path) -> None:
    for step, result in (
        ("review-architecture", "nothing-to-do"),
        ("tighten-spec", "done"),
        ("resolve-open-questions", "done"),
        ("plan-from-spec", "done"),
        ("review-and-tighten-plan", "done"),
        ("tasks-ready-to-build", "ready"),
    ):
        run(["record", "--root", str(root), "--slice", "docs/specs/orders", "--step", step,
             "--result", result, "--when", WHEN, "--yes"])


def stopped_walk(root: Path) -> None:
    wp.set_branch_run(root, "feat/orders-cicd", "stopped before merge", "2026-11-16T10:34:00+01:00")


class WalkOwner(unittest.TestCase):
    def test_someone_elses_walk_is_not_offered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, user="person A")
            stopped_walk(root)
            self.assertEqual(wp.resume_walk_entries(root, "orders"), [])
            self.assertEqual(
                wp.walk_owner_waits(root),
                ["Waiting: T9 to T12 are person B's, built, and wait for PR 82 to merge."],
            )

    def test_your_own_walk_is_offered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, user="person B")
            stopped_walk(root)
            self.assertEqual(
                wp.resume_walk_entries(root, "orders"),
                ["Continue the build walk on feat/orders-cicd:\n`/crav1-build-walk orders feat/orders-cicd`"],
            )
            self.assertEqual(wp.walk_owner_waits(root), [])

    def test_user_flag_wins_and_case_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, user="person A")
            stopped_walk(root)
            self.assertEqual(len(wp.resume_walk_entries(root, "orders", user="Person B")), 1)

    def test_owner_self_alone_is_not_trusted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, user=None)
            stopped_walk(root)
            # No local user: the claim user cannot match, so no offer.
            self.assertEqual(wp.resume_walk_entries(root, "orders"), [])

    def test_unknown_pull_request_is_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, progress=NOT_BUILT)
            stopped_walk(root)
            self.assertEqual(wp.resume_walk_entries(root, "orders"), [])
            self.assertEqual(wp.walk_owner_waits(root), ["Waiting: T9 to T12 are in progress by person B."])

    def test_ids_span(self):
        self.assertEqual(wp._ids_span(["T9", "T10", "T11", "T12"]), "T9 to T12")
        self.assertEqual(wp._ids_span(["T9", "T10"]), "T9 and T10")
        self.assertEqual(wp._ids_span(["T9", "T11", "T12"]), "T9, T11 and T12")


class BuiltClaims(unittest.TestCase):
    def test_held_rows_read_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp)
            rows = wp.build_rows(root)
            wp.apply_claims(root, rows)
            by = {row["task"]: row for row in rows if row.get("task")}
            for task in ("T9", "T10", "T11", "T12"):
                self.assertEqual(by[task]["reason"], "built by person B, waits for PR 82 to merge")
                self.assertTrue(by[task]["held"])

    def test_not_built_keeps_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, progress=NOT_BUILT)
            rows = wp.build_rows(root)
            wp.apply_claims(root, rows)
            by = {row["task"]: row for row in rows if row.get("task")}
            self.assertTrue(by["T9"]["reason"].startswith("in progress by person B since 2026-11-16"))

    def test_build_map_reads_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp)
            text, code = bm.run_dir(root)
            self.assertEqual(code, 0, text)
            out = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertNotIn("in progress by person B", out)
            self.assertIn("- Ready now: built, waits for PR 82 to merge", out)

    def test_task_order_claim_phrase_reads_built(self):
        order = bm.task_order
        tasks = order.parse(TASKS)
        res = order.analyse(tasks)
        walks = {"feat/orders-cicd": {"built": {9, 10}, "pr": 82, "merged": False}}
        built = {task_id: walk["pr"] for walk in walks.values() for task_id in walk["built"]}
        order.apply_claim_holds(res, tasks, CLAIMS, built=built)
        reasons = {row["id"]: row["reason"] for row in res["waiting_in_progress"]}
        self.assertEqual(reasons[9], "built by person B, waits for PR 82 to merge")
        self.assertEqual(reasons[10], "built by person B, waits for PR 82 to merge")
        self.assertTrue(reasons[11].startswith("in progress by person B since 2026-11-16"))
        self.assertEqual(reasons[13], "held, waits on T12")

    def test_ready_check_ending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp)
            record_walk(root)
            stopped_walk(root)
            payload = run(["readiness", "--root", str(root), "--skip-sync", "--full"])
            ending = payload["ending"]
            self.assertNotIn("Continue the build walk", ending)
            self.assertNotIn("in progress by person B since", ending)
            self.assertIn("built by person B, waits for PR 82 to merge", ending)
            self.assertIn("1. PR 82 (person B's, feat/orders-cicd): ticks T9 to T12, then T13 can start.", ending)  # 1.176.0
            self.assertNotIn("reopened", ending)


class NoFalseReopen(unittest.TestCase):
    def test_a_build_walks_own_files_never_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, progress=None)
            record_walk(root)
            self.assertEqual(wp.reopened_hits(root), [])
            # Everything a whole-branch walk writes in the specs repo.
            (root / "claims.md").write_text(CLAIMS, encoding="utf-8")
            (root / "build-progress").mkdir()
            (root / "build-progress" / "feat--orders-cicd.md").write_text(PROGRESS, encoding="utf-8")
            stopped_walk(root)
            (root / "verify.md").write_text(
                "# Verify\n\n| T9 | Orders CI/CD | Not implemented | pass locally at 1f2e3d4 |\n", encoding="utf-8",
            )
            # A tick after the merge is a progress mark too.
            ticked = TASKS.replace("- [ ] T9:", "- [x] T9:")
            (root / "tasks.md").write_text(ticked.replace("\n", "\r\n"), encoding="utf-8")
            self.assertEqual(wp.reopened_hits(root), [])


class ReopenReason(unittest.TestCase):
    def test_a_real_spec_change_says_which_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_slice(tmp, progress=None)
            record_walk(root)
            (root / "spec.md").write_text(
                SPEC.replace("pipeline pattern.", "pipeline pattern, with its own infra folder."), encoding="utf-8",
            )
            hits = wp.reopened_hits(root)
            tighten = next(hit for hit in hits if hit["step"] == "tighten-spec")
            self.assertEqual(
                tighten["reason"],
                "The spec's Constraints section changed after /crav1-tighten-spec was last recorded in walk-progress.md.",
            )
            entry = wp.not_ready_run("not-ready", "orders", hits, ["T9"], None, {}, None, None, {}, None, False)
            lines = entry[0].split("\n")
            self.assertEqual(lines[0], "The spec's Constraints section changed after /crav1-tighten-spec was last recorded in walk-progress.md, so T9 waits.")
            self.assertEqual(lines[1], "Finish the reopened /crav1-tighten-spec step:")
            self.assertEqual(lines[2], "`/crav1-tighten-spec orders`")
            self.assertNotIn("by hand", entry[0])

    def test_no_tasks_and_no_sections(self):
        why = wp.reopen_reason("review-and-tighten-plan", ["plan"], [])
        self.assertEqual(why, "Plan.md changed after /crav1-review-plan was last recorded in walk-progress.md.")
        entry = wp.not_ready_run("not-ready", "", [{"bucket": "reopened", "step": "plan-from-spec", "reason": "The spec changed after /crav1-plan-from-spec was last recorded in walk-progress.md."}],
                                 [], None, {}, None, None, {}, None, False)
        self.assertEqual(entry, ["The spec changed after /crav1-plan-from-spec was last recorded in walk-progress.md.\nFinish the reopened /crav1-plan-from-spec step:\n`/crav1-plan-from-spec`"])


class PushOnce(unittest.TestCase):
    def test_push_only_block_says_it_once(self):
        block = we.catch_up_block("orders", ahead=2)
        self.assertEqual(block, "**Catch up first**\n\nPush the specs repo, which is 2 commits ahead of origin:\n`git push`")
        self.assertEqual(block.count("ahead"), 1)

    def test_other_sentences_stay(self):
        block = we.catch_up_block("orders", behind=["T4"], ahead=1)
        self.assertIn("verify.md is behind for T4.", block)
        self.assertNotIn("The specs repo is", block)
        self.assertTrue(block.endswith("Push the specs repo, which is 1 commit ahead of origin:\n`git push`"))


if __name__ == "__main__":
    unittest.main()
