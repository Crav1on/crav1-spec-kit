"""1.142.0: one Next, other-owner mode, stacking, live yes, and the approval hold."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-build-walk/scripts/build_walk.py"
MAP = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/build_map.py"


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bw = load(SCRIPT, "build_walk")
bm = load(MAP, "build_map_1142")

BRANCH = "feat/orders-host-setup-scripts"
NOTE = "feat/orders-note"
CLEANUP = "feat/orders-one-commit-cleanup-main"
BASE = "develop"


def task(number, title, branch=BRANCH, deps=None, base=BASE):
    return {"id": number, "title": title, "branch": branch, "deps": deps or [], "base": base}


def state(**kwargs):
    base = {
        "mode": "walk",
        "owner": "self",
        "branch": BRANCH,
        "base": BASE,
        "tasks": [task(3, "Apply the CI build policy")],
        "pr": 51,
    }
    base.update(kwargs)
    return base


class SingleNext(unittest.TestCase):
    phases = [
        "confirm-owner",
        "approval",
        "live-dry",
        "live-yes",
        "permission-refused",
        "build",
        "verify",
        "commit",
        "open-pr",
        "merge-base",
        "merge-pr",
        "tick",
        "comment",
        "wait-merge",
        "next-task",
    ]

    def test_each_in_walk_state_has_one_next_and_drops_the_step_skill_line(self):
        for phase in self.phases:
            with self.subTest(phase=phase):
                result = bw.next_for(state(phase=phase, who="person A", approval_asked=False))
                self.assertEqual(result["count"], 1, result)
                self.assertEqual(len(result["next"]), 1)
                line = result["next"][0]
                self.assertEqual(line.count("Next:"), 1)
                commands = [part for part in line.split() if part.startswith("/crav1-")]
                self.assertEqual(len(commands), 1, line)
                for banned in result["suppressed"]:
                    self.assertNotIn(banned, line)

    def test_after_build_the_next_is_verify_not_open_pr(self):
        phase = bw.current_phase({"owner": "self", "built": True, "verified": False, "dirty": False})
        self.assertEqual(phase, "verify")
        result = bw.next_for(state(phase=phase))
        self.assertIn("/crav1-build-walk", result["next"][0])
        self.assertNotIn("/crav1-open-pr", result["next"][0])
        self.assertIn("/crav1-open-pr", result["suppressed"])

    def test_open_pr_phase_names_the_walk_not_review(self):
        result = bw.next_for(state(phase="open-pr"))
        line = result["next"][0]
        self.assertIn("open the pull request", line)
        self.assertIn("/crav1-build-walk", line)
        self.assertNotIn("/crav1-review-pr", line)
        self.assertNotIn("/crav1-open-pr", line)

    def test_grouping_is_one_next_per_branch_with_the_task_name(self):
        result = bw.next_for({
            "mode": "grouping",
            "branches": [
                {"branch": BRANCH, "tasks": [task(3, "Apply the CI build policy")]},
                {"branch": NOTE, "tasks": [task(5, "Note the policy", NOTE)]},
            ],
        })
        self.assertEqual(result["count"], 2)
        self.assertIn("T3 Apply the CI build policy", result["next"][0])
        self.assertIn(BRANCH, result["next"][0])
        self.assertIn("T5 Note the policy", result["next"][1])
        self.assertIn(NOTE, result["next"][1])
        for line in result["next"]:
            self.assertEqual(line.count("Next:"), 1)
            self.assertIn("/crav1-build-walk", line)


class OtherOwner(unittest.TestCase):
    def test_pr_author_or_commit_author_is_someone_else(self):
        pr = bw.detect_other_owner("the owner", pr_author="person A", commit_authors=["the owner"])
        self.assertTrue(pr["other"])
        self.assertIn("person A", pr["why"])
        commit = bw.detect_other_owner("the owner", pr_author="the owner", commit_authors=["person A"])
        self.assertTrue(commit["other"])
        own = bw.detect_other_owner("the owner", pr_author="the owner", commit_authors=["the owner"])
        self.assertFalse(own["other"])
        unnamed = bw.detect_other_owner("", pr_author="person A")
        self.assertFalse(unnamed["other"])
        self.assertFalse(unnamed["known"])

    def test_other_owner_never_opens_or_merges(self):
        allowed = bw.allowed_actions("other")
        self.assertFalse(allowed["open_pr"])
        self.assertFalse(allowed["merge_base"])
        self.assertFalse(allowed["merge_pr"])
        self.assertFalse(allowed["complete_pr"])
        self.assertTrue(allowed["comment_per_push"])
        self.assertFalse(allowed["edit_description"])
        self.assertTrue(bw.allowed_actions("other", description_asked=True)["edit_description"])
        self.assertFalse(bw.allowed_actions("self", description_asked=True)["edit_description"])
        for phase in ("open-pr", "merge-base", "merge-pr"):
            result = bw.next_for(state(owner="other", phase=phase, pushed=True, commented=False))
            self.assertNotIn(result["phase"], bw.OTHER_FORBIDDEN)
            line = result["next"][0]
            self.assertNotIn("open the pull request", line)
            self.assertNotIn("merge develop", line)
            self.assertNotIn("merge pull request", line)
            self.assertFalse(result["allowed"]["open_pr"])
            self.assertFalse(result["allowed"]["merge_pr"])

    def test_ticks_wait_until_that_pull_request_is_merged(self):
        self.assertFalse(bw.may_tick("other", pr_merged=False))
        self.assertTrue(bw.may_tick("other", pr_merged=True))
        waiting = bw.current_phase({"owner": "other", "built": True, "verified": True, "dirty": False, "pr_merged": False, "commented": True, "pushed": True})
        self.assertEqual(waiting, "wait-merge")
        line = bw.next_for(state(owner="other", phase=waiting))["next"][0]
        self.assertIn("wait until", line)
        self.assertIn("merged", line)

    def test_one_comment_per_push_and_the_description_stays(self):
        first = bw.push_comment(BRANCH, 51, "T3 Apply the CI build policy.")
        second = bw.push_comment(BRANCH, 51, "T5 Note the policy.")
        self.assertNotEqual(first["body"], second["body"])
        self.assertIn("Pushed `feat/orders-host-setup-scripts`.", first["body"])
        self.assertIn("T3 Apply the CI build policy.", first["body"])
        self.assertFalse(first["edits_description"])
        self.assertFalse(second["edits_description"])
        self.assertEqual(first["kind"], "comment")


class Stacking(unittest.TestCase):
    def test_a_task_that_needs_an_unmerged_branch_is_cut_from_it(self):
        tasks = [
            task(3, "Apply the CI build policy", BRANCH, []),
            task(7, "Read the policy", NOTE, [3], BASE),
        ]
        plan = bw.stack_from_tasks(tasks, merged=set(), default_base=BASE)
        by_branch = {row["branch"]: row["cut_from"] for row in plan["rows"]}
        self.assertEqual(by_branch[BRANCH], BASE)
        self.assertEqual(by_branch[NOTE], BRANCH)
        self.assertNotEqual(by_branch[NOTE], BASE)

    def test_merge_list_orders_the_child_before_the_parent(self):
        later = "feat/orders-later"
        tasks = [
            task(3, "Apply the CI build policy", BRANCH, []),
            task(7, "Read the policy", NOTE, [3]),
            task(9, "Show the policy", later, [7]),
        ]
        plan = bw.stack_from_tasks(tasks, merged=set())
        pairs = [(row["branch"], row["into"]) for row in plan["merge_list"]]
        self.assertEqual(pairs, [
            (later, NOTE),
            (NOTE, BRANCH),
            (BRANCH, BASE),
        ])
        rendered = "\n".join(bw.render_merge_list(plan["merge_list"]))
        self.assertLess(rendered.index(f"Merge: {later} into {NOTE}"), rendered.index(f"Merge: {NOTE} into {BRANCH}"))
        self.assertLess(rendered.index(f"Merge: {NOTE} into {BRANCH}"), rendered.index(f"Merge: {BRANCH} into {BASE}"))
        text = bw.render_progress(
            "docs/specs/orders-capacity/",
            later,
            "self",
            [task(9, "Show the policy", later)],
            NOTE,
            plan["merge_list"],
            [],
        )
        self.assertIn("Walk: build-walk", text)
        self.assertIn(f"Cut from: {NOTE}", text)
        self.assertIn(f"Merge: {later} into {NOTE}", text)

    def test_a_merged_dependency_is_not_the_cut(self):
        tasks = [
            task(3, "Apply the CI build policy", BRANCH, []),
            task(7, "Read the policy", NOTE, [3]),
        ]
        plan = bw.stack_from_tasks(tasks, merged={BRANCH})
        by_branch = {row["branch"]: row["cut_from"] for row in plan["rows"]}
        self.assertEqual(by_branch[NOTE], BASE)


class NeverRecommendMerged(unittest.TestCase):
    def test_offer_uses_the_140_helper_and_refuses_a_merged_name(self):
        spec = (
            "# Orders\n\n## Match\n\n"
            "- Branch: orders-api feat/orders-one-commit-cleanup-main (PR 42) merged\n"
        )
        plan = "# Plan\n\n## Approach\n\n1. One commit cleanup on main. (T3)\n"
        tasks = "- [ ] T3: Add the host setup scripts on feat/orders-host-setup-scripts from develop (Runs live)\n"
        offer = bw.offer_for("orders", spec, plan, tasks, 3)
        self.assertEqual(offer["name"], BRANCH)
        self.assertNotEqual(offer["name"], CLEANUP)
        self.assertFalse(offer["refused"])
        self.assertIsNone(bw.refuse_unusable(CLEANUP, "merged"))
        self.assertIsNone(bw.refuse_unusable(CLEANUP, "deleted"))
        self.assertEqual(bw.refuse_unusable(BRANCH, "ok"), BRANCH)
        fate = bm.branch_fate(CLEANUP, spec, tasks, None, BASE)
        self.assertEqual(fate, "merged")
        forced = dict(offer)
        forced["fate"] = fate
        self.assertIsNone(bw.refuse_unusable(CLEANUP, forced["fate"]))

    def test_a_recorded_merge_on_the_only_name_is_not_offered(self):
        spec = (
            "# Orders\n\n## Match\n\n"
            "- Branch: orders-api feat/orders-one-commit-cleanup-main (PR 42) merged\n"
        )
        plan = "# Plan\n\n## Approach\n\n1. One commit cleanup on main. (T1)\n"
        tasks = "- [ ] T1: Clean the commit on feat/orders-one-commit-cleanup-main\n"
        offer = bw.offer_for("orders", spec, plan, tasks, 1)
        self.assertNotEqual(offer["name"], CLEANUP)
        self.assertTrue(offer["name"])
        self.assertIn("already merged", offer.get("because") or "")


class RunsLive(unittest.TestCase):
    line = "- [ ] T3: Apply the CI build policy (host setup) (Runs live) (after: )"

    def test_dry_run_then_yes_is_recorded_and_the_box_stays_open_until_then(self):
        dry = bw.live_gate(self.line, dry_ran=False, user_yes=False, approved=True)
        self.assertEqual(dry["phase"], "live-dry")
        self.assertTrue(dry["write_script"])
        self.assertTrue(dry["run_check"])
        self.assertFalse(dry["run_live"])
        self.assertFalse(dry["tick"])
        self.assertFalse(dry["approved_counts_as_yes"])

        waiting = bw.live_gate(self.line, dry_ran=True, user_yes=False, approved=True)
        self.assertEqual(waiting["phase"], "live-yes")
        self.assertTrue(waiting["write_script"])
        self.assertFalse(waiting["run_live"])
        self.assertFalse(waiting["tick"])
        self.assertFalse(waiting["approved_counts_as_yes"])
        self.assertNotIn("live yes:", waiting["line"])
        self.assertIn("[ ]", waiting["line"])

        ran = bw.live_gate(self.line, dry_ran=True, user_yes=True, approved=True, name="person A", date="2026-11-12")
        self.assertEqual(ran["phase"], "run-live")
        self.assertTrue(ran["run_live"])
        self.assertIn("(live yes: person A, 2026-11-12)", ran["line"])
        self.assertIn("[ ]", ran["line"])
        self.assertNotIn("[x]", ran["line"])

    def test_a_live_yes_does_not_change_the_normalized_hash(self):
        before = self.line + "\n"
        after = bw.record_live_yes(self.line, "person A", "2026-11-12") + "\n"
        ticked = before.replace("[ ]", "[x]")
        pr = before.replace("(after: )", "(PR 51) (after: )")
        self.assertTrue(bw.progress_only(before, after))
        self.assertTrue(bw.progress_only(before, ticked))
        self.assertTrue(bw.progress_only(before, pr))
        self.assertTrue(bw.progress_only(before, before.replace("\n", "\r\n")))
        changed = before.replace("Apply the CI build policy", "Apply a different policy")
        self.assertFalse(bw.progress_only(before, changed))

    def test_stamp_conflict_that_is_only_hash_lines_settles(self):
        conflict = textwrap.dedent(
            """\
            # Build progress

            Walk: build-walk
            Branch: feat/orders-host-setup-scripts
            - Step: build
              Done: 2026-11-12T13:00:00+00:00
              Result: done
            <<<<<<< HEAD
              Tasks version: aaaaaaaaaaaa
              Content stamp: normalized
            =======
              Tasks version: bbbbbbbbbbbb
              Content stamp: normalized
            >>>>>>> origin/develop
            """
        )
        self.assertEqual(bw.classify_conflict(conflict), "stamps")
        settled = bw.settle_stamps(conflict, {"Tasks version": "cccccccccccc"})
        self.assertIsNotNone(settled)
        self.assertNotIn("<<<<<<<", settled)
        self.assertIn("Tasks version: cccccccccccc", settled)
        self.assertIn("Result: done", settled)
        mixed = conflict.replace("Result: done", "<<<<<<< HEAD\n  Result: done\n=======\n  Result: skipped\n>>>>>>> origin/develop")
        self.assertEqual(bw.classify_conflict(mixed), "mixed")
        self.assertIsNone(bw.settle_stamps(mixed))


class ApprovalHold(unittest.TestCase):
    line = "- [ ] T4: Apply the CI build policy (Runs live) (after: )"

    def test_an_unapproved_item_holds_and_names_record_or_the_draft(self):
        draft = bw.live_gate(self.line, approval_holding=True, approval_asked=False, approved=False)
        self.assertTrue(draft["held"])
        self.assertEqual(draft["next_command"], "/crav1-show-or-ask-open-questions")
        self.assertFalse(draft["run_live"])
        self.assertFalse(draft["write_script"])
        asked = bw.live_gate(self.line, approval_holding=True, approval_asked=True)
        self.assertEqual(asked["next_command"], "/crav1-record-approval")
        self.assertFalse(asked["run_live"])
        phase = bw.current_phase({"owner": "self", "approval_holding": True, "runs_live": True})
        self.assertEqual(phase, "approval")
        line = bw.next_for(state(phase="approval", approval_asked=False, tasks=[task(4, "Apply the CI build policy")]))["next"][0]
        self.assertIn("/crav1-show-or-ask-open-questions", line)
        self.assertNotIn("/crav1-build-tasks", line)
        self.assertEqual(line.count("Next:"), 1)

    def test_an_approved_line_does_not_replace_the_live_yes(self):
        gate = bw.live_gate(self.line, approval_holding=False, dry_ran=True, user_yes=False, approved=True)
        self.assertEqual(gate["phase"], "live-yes")
        self.assertFalse(gate["run_live"])
        self.assertFalse(gate["approved_counts_as_yes"])
        self.assertTrue(gate["approved_present"])


class Command(unittest.TestCase):
    def test_next_command_prints_one_line(self):
        payload = {"phase": "verify", "owner": "self", "branch": BRANCH, "tasks": [task(3, "Apply the CI build policy")]}
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "state.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(SCRIPT), "next", "--json", str(path)], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        found = json.loads(proc.stdout)
        self.assertEqual(found["count"], 1)
        self.assertNotIn("/crav1-open-pr", found["next"][0])


class Routing(unittest.TestCase):
    def test_skill_routes_before_loading_every_path(self):
        skill = (ROOT / ".cursor/skills/crav1/crav1-build-walk/SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(skill.split()), 1600)
        self.assertIn("Route first", skill)
        for name in ("common.md", "grouping.md", "progress.md", "other-owner.md", "live.md", "stack.md", "steps.md"):
            self.assertIn(f"references/{name}", skill)
            self.assertTrue((ROOT / ".cursor/skills/crav1/crav1-build-walk/references" / name).is_file())
        for word in ("yes", "switch", "own", "edit description", "stop"):
            self.assertIn(f"`{word}`", skill)


if __name__ == "__main__":
    unittest.main()
