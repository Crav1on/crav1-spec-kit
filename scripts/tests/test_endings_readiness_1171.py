"""1.171.0: wait-merge leaves Run next, readiness reads build-progress, full task
names, branch descriptions, the walk lead, review threads, and the last Next lines."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = Path(__file__).resolve().parent
SK = ROOT / ".cursor/skills/crav1"
sys.path.insert(0, str(TESTS))
import test_claims_sync_1151 as base  # noqa: E402


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bw = load(SK / "crav1-build-walk/scripts/build_walk.py", "build_walk_1171")
we = load(SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py", "walk_ending_1171")
bm = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "build_map_1171")
wp = load(SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py", "walk_progress_1171")


def read(rel: str) -> str:
    return (SK / rel).read_text(encoding="utf-8")


OTHER = [{
    "branch": "feat/orders-cicd",
    "about": "",
    "tasks": [{"id": "T9", "title": "Orders CI/CD: infra Bicep"}],
    "open_tasks": [
        {"id": "T9", "title": "Orders CI/CD: infra Bicep"},
        {"id": "T10", "title": "Orders CI/CD: cd pipeline", "waits": "waits on T9"},
    ],
}]


def wait_state(**extra):
    state = {
        "phase": "wait-merge", "owner": "other", "branch": "feature/orders-incoming", "pr": 71,
        "who": "person A", "slug": "orders-api",
        "tasks": [{"id": "T5", "title": "PR 71: READMEs describe the incoming table"}],
        "ready_branches": OTHER,
    }
    state.update(extra)
    return state


class WaitMergeEnding(unittest.TestCase):
    """1a and 13."""

    def test_wait_merge_has_no_current_branch_entry(self):
        out = bw.next_for(wait_state())
        self.assertNotIn("/crav1-build-walk orders-api T5", out["ending"])
        self.assertTrue(out["ending"].startswith("Run next:"))
        self.assertIn("/crav1-build-walk orders-api T9", out["ending"])
        self.assertIn("Waiting: person A to merge pull request 71", out["ending"])

    def test_wait_merge_alone_is_the_waiting_line(self):
        out = bw.next_for(wait_state(ready_branches=[]))
        self.assertTrue(out["ending"].startswith("Waiting:"))
        self.assertEqual(out["count"], 0)

    def test_other_phases_keep_the_current_entry(self):
        out = bw.next_for(wait_state(phase="comment"))
        self.assertIn("/crav1-build-walk orders-api T5", out["ending"])

    def test_two_tasks_use_the_branch_form_not_a_comma(self):
        out = bw.next_for(wait_state(phase="build", owner="self", ready_branches=[], tasks=[
            {"id": "T43", "title": "Orders incoming: JSON body, tag and content"},
            {"id": "T8", "title": "PR 73: take in develop, resolve conflicts, merge"},
        ]))
        self.assertIn("`/crav1-build-walk orders-api feature/orders-incoming`", out["ending"])
        self.assertNotIn("T43, T8", out["ending"])
        self.assertIn("- T43 Orders incoming: JSON body, tag and content", out["ending"])
        self.assertIn("- T8 PR 73: take in develop, resolve conflicts, merge", out["ending"])


class Lead(unittest.TestCase):
    """4."""

    def test_wait_merge_lead(self):
        out = bw.next_for(wait_state())
        self.assertEqual(out["lead"], "T5 is pushed to PR 71 and waits for its merge.")

    def test_lead_agrees_with_uncommitted(self):
        out = bw.next_for(wait_state(uncommitted="Uncommitted: 1 file (walk-progress.md)."))
        self.assertIn("not committed yet", out["lead"])
        self.assertNotIn("nothing to commit", out["lead"].lower())
        self.assertEqual(out["lead"].count(". "), 0)

    def test_skill_prints_only_the_lead(self):
        self.assertIn("print only the JSON `lead`", read("crav1-build-walk/SKILL.md"))
        self.assertIn("Print only that before `Run next:`", read("crav1-build-walk/references/common.md"))


class FullNames(unittest.TestCase):
    """2."""

    def test_task_label_keeps_an_ellipsis(self):
        label = bw._task_label({"id": "T5", "title": "READMEs describe the table and..."})
        self.assertTrue(label.endswith("..."), label)
        self.assertEqual(bw._task_label({"id": "T3", "title": "Apply the policy."}), "T3 Apply the policy")

    def test_ready_branches_use_the_full_name(self):
        src = read("crav1-tasks-ready-to-build/scripts/build_map.py")
        self.assertIn('"title": task.get("full") or task.get("short") or ""}', src)
        self.assertIn('"title": task.get("full") or task.get("short") or "", "waits"', src)

    def test_an_81_character_title_is_not_cut(self):
        title = "Orders incoming: JSON body with only tag and content, metadata read from the header row"
        self.assertGreater(len(title), 80)
        label = bw._task_label({"id": "T43", "title": title})
        self.assertEqual(label, "T43 " + title)
        block = we.branch_block("feat/orders-incoming", [label], slug="orders-api")
        self.assertIn(title, block)


class Descriptions(unittest.TestCase):
    """3 and 14."""

    def test_cut_from_is_a_planning_note(self):
        names = ["Orders CI/CD: infra Bicep", "Orders CI/CD: cd pipeline"]
        text = we.about_sentence("The orders CI/CD branch, cut from develop after billing-ops: merge main, then build.", names=names)
        self.assertNotIn("cut from", text)
        self.assertEqual(text, "Orders CI/CD: infra Bicep and cd pipeline.")

    def test_a_clean_sentence_still_wins(self):
        self.assertEqual(we.about_sentence("Builds the orders deploy pipeline with three stages."),
                         "Builds the orders deploy pipeline with three stages.")

    def test_planning_note_words(self):
        self.assertTrue(we.planning_note("The orders CI/CD branch, cut from develop after billing-ops."))
        self.assertTrue(we.planning_note("The orders branch."))
        self.assertFalse(we.planning_note("GetReceipts answers 404 for an unknown cursor."))

    def test_done_task_sentence_is_dropped(self):
        done = [{"id": 6, "done": True, "full": "GetReceipts answers 404 for a cursor that matches no receipt", "short": "GetReceipts answers 404"}]
        self.assertTrue(bm._names_done("GetReceipts answers 404 for a cursor that matches no stored receipt.", done))
        self.assertTrue(bm._names_done("T6 fixes the cursor.", done))
        self.assertFalse(bm._names_done("Incoming JSON carries only tag and content.", done))


def write_progress(root: Path, branch: str, owner: str, tasks: str, steps: list[tuple[str, str]]):
    folder = root / "build-progress"
    folder.mkdir(exist_ok=True)
    lines = ["# Build progress", "", "Walk: crav1-build-walk", "Slice: docs/specs/orders-api/",
             f"Branch: {branch}", f"Owner: {owner}", f"Tasks: {tasks}", "Cut from: develop", "Merge list: none", ""]
    for step, result in steps:
        lines += [f"- Step: {step}", "  Done: 2026-11-15 23:30", f"  Result: {result}", ""]
    (folder / (branch.replace("/", "--") + ".md")).write_text("\n".join(lines), encoding="utf-8")


class ReadinessReadsProgress(unittest.TestCase):
    """1b and 12."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = base.write_slice(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def readiness(self, *extra):
        code, payload, err = base.run_py(base.WALK, ["readiness", "--full", "--skip-sync", "--root", str(self.root), *extra])
        self.assertEqual(code, 0, err + json.dumps(payload)[:500])
        return payload

    def test_wait_merge_task_is_not_can_start(self):
        before = self.readiness()
        self.assertIn("T2", before.get("can_start") or [])
        write_progress(self.root, "feat/orders-api-host-setup", "other", "T2 Record the decision",
                       [("build", "built"), ("comment", "pushed to PR 71, commented")])
        after = self.readiness()
        self.assertNotIn("T2", after.get("can_start") or [])
        self.assertIn("Merge these PRs, in this order:\n1. PR 71 (someone else's, feat/orders-api-host-setup): ticks T2.", after["ending"])  # 1.176.0
        self.assertNotIn("/crav1-build-walk T2`", after["ending"])

    def test_progress_mid_build_still_starts(self):
        write_progress(self.root, "feat/orders-api-host-setup", "self", "T2 Record the decision", [("build", "built")])
        self.assertIn("T2", self.readiness().get("can_start") or [])

    def test_progress_merge_waits_parses(self):
        write_progress(self.root, "feat/orders-x", "self", "T5 A, T6 B", [("wait-merge", "PR 12 open")])
        waits = wp.progress_merge_waits(self.root)
        self.assertEqual(waits["T5"]["pr"], 12)
        self.assertEqual(waits["T6"]["branch"], "feat/orders-x")

    def test_ready_branches_drop_the_waiting_task(self):
        write_progress(self.root, "feat/orders-api-host-setup", "self", "T2 Record the decision", [("wait-merge", "PR 71")])
        names = [t["id"] for b in wp.ready_branches(self.root) for t in b.get("tasks") or []]
        self.assertNotIn("T2", names)

    def test_own_claim_line_is_plain(self):
        rows = [{"task": "T5", "own_claim": True, "merge_wait": {"pr": 71, "owner": "self"}, "bucket": "waiting"},
                {"task": "T7", "own_claim": True, "bucket": "ready"}]
        self.assertEqual(wp.own_claim_line(rows), "T7 is yours; the walk resumes it.")
        self.assertIn("`T5 is yours; the walk resumes it.`", read("crav1-tighten-and-plan-ready-to-build/references/readiness.md"))


class RecordUnchanged(unittest.TestCase):
    """16."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = base.write_slice(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def record(self, result):
        return base.run_py(base.WALK, ["record", "--root", str(self.root), "--slice", "docs/specs/orders-api",
                                       "--step", "tasks-ready-to-build", "--result", result, "--yes"])

    def test_same_result_does_not_restamp(self):
        code, first, err = self.record("ready-partial")
        self.assertEqual(code, 0, err)
        self.assertTrue(first.get("wrote"))
        before = (self.root / "walk-progress.md").read_text(encoding="utf-8")
        code, second, err = self.record("ready-partial")
        self.assertEqual(code, 0, err)
        self.assertTrue(second.get("unchanged"), second)
        self.assertEqual((self.root / "walk-progress.md").read_text(encoding="utf-8"), before)
        self.assertTrue(wp.record_unchanged(self.root, "tasks-ready-to-build", "ready-partial"))
        self.assertFalse(wp.record_unchanged(self.root, "tasks-ready-to-build", "ready"))

    def test_readiness_says_record_unchanged(self):
        code, payload, err = base.run_py(base.WALK, ["readiness", "--full", "--skip-sync", "--root", str(self.root)])
        self.assertIn("record_unchanged", payload)


class VerifyReplyBlocks(unittest.TestCase):
    """11."""

    def test_branch_blocks_come_from_readiness(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            root = base.write_slice(tmp)
            blocks = we.ready_branch_blocks(root)
            self.assertTrue(blocks)
            self.assertTrue(all(block.startswith("**") for block in blocks))
            self.assertIn("/crav1-build-walk", blocks[0])
            self.assertIn("open task", blocks[0])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_reply_doc_says_so(self):
        self.assertIn("ready_branch_blocks", read("crav1-tasks-ready-to-build/scripts/walk_ending.py"))


class NoNextLines(unittest.TestCase):
    """5, 6, 7, 8, 9, 10, 17."""

    def test_review_posts_a_new_thread(self):
        posting = read("crav1-review-pr/references/posting.md")
        self.assertIn("new top-level thread", posting)
        self.assertIn("`parentCommentId` 0", posting)
        self.assertNotIn("as a reply in the earlier comment's thread", posting)

    def test_review_ends_with_run_next(self):
        skill = read("crav1-review-pr/SKILL.md")
        self.assertNotIn("`Next: nothing needed now.`", skill)
        self.assertIn("Commit the PR note:", skill)

    def test_ready_check_asks_record_before_ending(self):
        text = read("crav1-tighten-and-plan-ready-to-build/references/readiness.md")
        self.assertIn("Ask the record card first, then print `reply`", text)

    def test_fix_finalize_open_pr_have_no_next_line(self):
        for rel in ("crav1-fix-build-gaps/branches/verify-gaps/BRANCH.md",
                    "crav1-finalize-commit/references/commit.md",
                    "crav1-open-pr/references/after.md"):
            text = read(rel)
            for line in text.splitlines():
                self.assertFalse(line.strip().startswith("Next:"), (rel, line))
                self.assertNotIn("`Next: /crav1", line, rel)
                self.assertNotIn("`Next: git push", line, rel)
        self.assertIn("Push to PR <n> and comment:", read("crav1-finalize-commit/references/commit.md"))
        self.assertIn("Review PR <n>:", read("crav1-open-pr/references/after.md"))
        self.assertIn("**Catch up first**", read("crav1-fix-build-gaps/branches/verify-gaps/BRANCH.md"))

    def test_other_owner_status_word(self):
        self.assertIn("Implemented, verified, tick pending", read("crav1-build-walk/references/other-owner.md"))


if __name__ == "__main__":
    unittest.main()
