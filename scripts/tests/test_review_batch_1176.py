"""1.176.0 review batch (part 1).

N1: a step recorded again after a spec edit uses its own fresh stamps, so
the reopen clears, clear really clears, and the ready check no longer
blocks on it. Plus the plan-check, readiness-ending, question and task-title
fixes listed in the CHANGELOG.
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
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-15T10:00:00+00:00"
LATER = "2026-11-16T12:45:00+00:00"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(WALK), *args], capture_output=True, text=True, check=False)
    try:
        return proc.returncode, json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc


def must(args: list[str]) -> dict:
    code, payload = run(args)
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


SPEC = """# Orders export

The receipt lists the order id.

## What the dump says

- The export runs nightly. MARK-dump

## Constraints

- No export during a test session. MARK-constraints

## Trace

- From meeting 2026-11-10. MARK-trace

## Open questions

- Which lane prints the label?
  - Blocks: none
"""


def write_slice(root: Path) -> None:
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text("# Plan\n\n## Risks\n", encoding="utf-8")
    (root / "tasks.md").write_text("# Tasks\n\n- [ ] T1 Record the lane (after: )\n", encoding="utf-8")
    (root / "verify.md").write_text("# Verify\n", encoding="utf-8")


def record(root: Path, step: str, result: str = "done", when: str = WHEN) -> None:
    must([
        "record", "--root", str(root), "--slice", "docs/specs/orders-export",
        "--step", step, "--result", result, "--when", when, "--yes",
    ])


def record_walk(root: Path) -> None:
    for step, result in (
        ("review-architecture", "nothing-to-do"),
        ("tighten-spec", "done"),
        ("resolve-open-questions", "done"),
        ("plan-from-spec", "done"),
        ("review-and-tighten-plan", "done"),
        ("tasks-ready-to-build", "ready"),
    ):
        record(root, step, result)


def statuses(root: Path) -> tuple[dict, dict]:
    payload = must(["resume", "--root", str(root), "--no-playbook"])
    return {row["id"]: row["status"] for row in payload["steps"]}, payload


def outside_edit(root: Path) -> None:
    text = (root / "spec.md").read_text(encoding="utf-8")
    text = text.replace("MARK-dump", "MARK-dump\n- From meeting 2026-11-12: access is not offered first.")
    text = text.replace("MARK-trace", "MARK-trace\n- From meeting 2026-11-12.")
    (root / "spec.md").write_text(text, encoding="utf-8")


class N1StaleBaseline(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()) / "orders-export"
        self.root.mkdir()
        write_slice(self.root)
        record_walk(self.root)
        outside_edit(self.root)

    def test_edit_reopens_tighten_spec_first(self):
        by_id, payload = statuses(self.root)
        self.assertEqual(by_id["tighten-spec"], "reopen")
        self.assertEqual(payload["continue_from"], "tighten-spec")

    def test_recording_again_clears_the_reopen_step_by_step(self):
        record(self.root, "tighten-spec", when=LATER)
        by_id, payload = statuses(self.root)
        self.assertEqual(by_id["tighten-spec"], "keep")
        self.assertEqual(payload["continue_from"], "plan-from-spec")
        record(self.root, "plan-from-spec", when=LATER)
        record(self.root, "review-and-tighten-plan", when=LATER)
        by_id, payload = statuses(self.root)
        for step in ("tighten-spec", "plan-from-spec", "review-and-tighten-plan"):
            self.assertEqual(by_id[step], "keep", step)
        self.assertNotEqual(payload["continue_from"], "tighten-spec")

    def test_ready_check_does_not_block_on_a_re_recorded_step(self):
        for step in ("tighten-spec", "plan-from-spec", "review-and-tighten-plan"):
            record(self.root, step, when=LATER)
        wp = load(WALK, "walk_progress_1176_ready")
        hits = wp.reopened_hits(self.root)
        others, _replaced = wp._without_self_reopen(hits)
        self.assertEqual([h["step"] for h in others], [])

    def test_clear_really_clears(self):
        payload = must(["clear", "--root", str(self.root), "--step", "tighten-spec", "--yes"])
        self.assertEqual(payload["cleared"], "tighten-spec")
        by_id, _ = statuses(self.root)
        self.assertEqual(by_id["tighten-spec"], "keep")

    def test_reopen_reason_names_the_step_own_sections(self):
        wp = load(WALK, "walk_progress_1176_reason")
        hits = {h["step"]: h for h in wp.reopened_hits(self.root)}
        self.assertIn("What the dump says", hits["tighten-spec"]["reason"])
        self.assertIn("Trace", hits["tighten-spec"]["reason"])
        self.assertNotIn("Constraints", hits["tighten-spec"]["reason"])



PLAN_CHECK = SK / "crav1-plan-from-spec/scripts/plan_check.py"
QB = SK / "crav1-tasks-ready-to-build/scripts/question_blocks.py"
WE = SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py"
TO = SK / "crav1-tasks-ready-to-build/scripts/task_order.py"
BM = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"
BW = SK / "crav1-build-walk/scripts/build_walk.py"
BR = SK / "crav1-build-walk/scripts/branch_run.py"


class N2SettledSpecFinding(unittest.TestCase):
    def setUp(self):
        self.pc = load(PLAN_CHECK, "plan_check_1176")

    def test_patched_spec_finding_does_not_send_back(self):
        items = [{"id": "P1", "issue": "x", "tag": "spec", "kind": "defect", "status": "patched"}]
        out = self.pc.empty_queue_next(items, True, False, "orders-api")
        self.assertNotIn("tighten-spec", out)
        self.assertIn("`/crav1-tasks-ready-to-build orders-api`", out)

    def test_open_spec_finding_uses_label_above_command(self):
        items = [{"id": "P1", "issue": "x", "tag": "spec", "kind": "defect", "status": "open"}]
        out = self.pc.empty_queue_next(items, True, False, "orders-api")
        self.assertEqual(out, "Run next:\n\nFix the spec finding, which is a spec defect:\n`/crav1-tighten-spec orders-api`")
        self.assertNotIn("Next:", out.replace("Run next:", ""))


class N3PartialNoLinter(unittest.TestCase):
    def setUp(self):
        self.pc = load(PLAN_CHECK, "plan_check_1176_lint")

    def plan(self, *lines):
        return "# Plan\n\n## Linter\n\n" + "\n".join(f"- {line}" for line in lines) + "\n\n## Risks\n"

    def test_named_tool_beside_a_partial_no_linter_line(self):
        plan = self.plan("flake8 covers the Python code.", "No linter or checker in this repo for the host setup shell scripts.")
        self.assertTrue(self.pc.linter_line(plan)[1])

    def test_recorded_go_on_without_one(self):
        plan = self.plan("No linter for the shell scripts. Go on without one for those shell scripts, chosen 2026-11-11 by person A.")
        self.assertTrue(self.pc.linter_line(plan)[1])

    def test_only_no_linter_is_not_named(self):
        plan = self.plan("This repo has no linter or checker for the code these tasks touch.")
        self.assertFalse(self.pc.linter_line(plan)[1])


class N4AskedFromProse(unittest.TestCase):
    def setUp(self):
        self.qb = load(QB, "question_blocks_1176")

    def test_raised_with_or_waiting_for_a_person_counts_as_asked(self):
        for text in ("Which CA issues the certificate? Raised with Person A.",
                     "Which lane prints the label? Waiting for Contoso.",
                     "Who signs? Waiting for Person B to reply."):
            self.assertTrue(self.qb._said_asked(text, []), text)

    def test_waiting_for_a_thing_is_not_asked(self):
        self.assertFalse(self.qb._said_asked("Which lane? We are waiting for the export to finish.", []))
        self.assertFalse(self.qb._said_asked("Which lane prints the label?", []))

    def test_marks_count_too(self):
        self.assertTrue(self.qb._said_asked("Which lane?", ["Raised with Person A on 2026-11-06."]))


class N5CommitBeforePush(unittest.TestCase):
    def test_uncommitted_files_come_before_the_push(self):
        we = load(WE, "walk_ending_1176_n5")
        text = we.catch_up_block("orders-api", [], [], 3, uncommitted=["spec.md", "plan.md", "tasks.md", "walk-progress.md", "build-map.md"])
        self.assertIn("Commit the 5 changed spec files:\n`/crav1-finalize-commit`\nThen push the specs repo:\n`git push`", text)
        self.assertLess(text.index("/crav1-finalize-commit"), text.index("git push"))

    def test_slice_uncommitted_reads_git(self):
        wp = load(WALK, "walk_progress_1176_n5")
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "spec.md").write_text("x\n", encoding="utf-8")
        self.assertEqual(wp.slice_uncommitted(root), ["spec.md"])
        self.assertEqual(wp.slice_uncommitted(Path(tempfile.mkdtemp())), [])


class N6WaitSaidOnce(unittest.TestCase):
    def test_own_claim_line_skips_a_merge_wait(self):
        wp = load(WALK, "walk_progress_1176_n6")
        rows = [{"task": "T5", "own_claim": True, "merge_wait": {"pr": 71, "owner": "self"}}]
        self.assertIsNone(wp.own_claim_line(rows))


class N7ReplyKeepsTail(unittest.TestCase):
    def test_readiness_reference_prints_reply(self):
        ref = (SK / "crav1-tighten-and-plan-ready-to-build/references/readiness.md").read_text(encoding="utf-8")
        self.assertIn("Print the script's `reply` as the reply, word for word (1.176.0)", ref)
        self.assertIn("never drop those closing lines", ref)

    def test_reply_has_the_tail(self):
        we = load(WE, "walk_ending_1176_n7")
        text = we.ready_reply("orders-api", "not-ready", None, "Run next:\n\nX:\n`git push`",
                              sources=["spec.md"], build_map="docs/specs/orders-api/build-map.md")
        self.assertTrue(text.endswith("Zoom the map in your browser:\n`/crav1-tasks-ready-to-build orders-api open-map`"))


class N8WholeQuestion(unittest.TestCase):
    def test_held_question_is_not_cut(self):
        bm = load(BM, "build_map_1176_n8")
        question = ("Which CA issues the orders-api client certificate (the internal one or the partner one), "
                    "what are the subject and thumbprint, and who renews it before it runs out next year?")
        row = {"reason": f'open question "{question}" (recorded)', "who": "Person A", "quote": None}
        text = bm.held_phrase(row)
        # 1.198.0: a long question is cut at a clause end near 120 characters.
        quoted = text.split('"')[1]
        self.assertLessEqual(len(quoted), 125)
        self.assertTrue(question.startswith(quoted.rstrip("…").rstrip()), quoted)
        self.assertIn("Waiting for Person A.", text)


class TaskTitles(unittest.TestCase):
    def test_code_spans_keep_text_and_no_stray_space(self):
        to = load(TO, "task_order_1176")
        rest = ("Separate keys on PROD `orders-api`, as T18, once PROD has `infra-orders` "
                "(verify: keys (two) differ) and stays stopped (`T27`) (after: T17)")
        out = to.first_words(rest)
        self.assertEqual(out, "Separate keys on PROD orders-api, as T18, once PROD has infra-orders and stays stopped (T27)")
        self.assertNotIn(" ,", out)
        self.assertNotIn(" )", out)

    def test_build_map_readable_has_no_stray_space(self):
        bm = load(BM, "build_map_1176_titles")
        out = bm._readable("`azuredevops/cd-orders.yml`, from PR 74's `cd-orders-prod.yml`, triggers on main")
        self.assertEqual(out, "azuredevops/cd-orders.yml, from PR 74's cd-orders-prod.yml, triggers on main")


class LabelAboveCommand(unittest.TestCase):
    def test_build_walk_endings(self):
        bw = load(BW, "build_walk_1176")
        for phase in ("build", "verify", "commit", "next-task"):
            state = {"slug": "orders-api", "phase": phase, "branch": "feat/orders-api",
                     "tasks": [{"id": 3, "title": "Record the decision"}], "spec_count": 2, "ready_branches": [],
                     "next_tasks": [{"id": 3, "title": "Record the decision"}], "next_branch": "feat/orders-api"}
            ending = bw.next_for(state)["ending"]
            # 1.198.0: the label follows the step the branch is on.
            verb = {"verify": "Verify", "commit": "Commit"}.get(phase, "Build")
            self.assertIn(f"{verb} T3 Record the decision on feat/orders-api:\n`/crav1-build-walk orders-api T3`", ending, phase)
            self.assertNotIn("\nbranch feat/", ending)

    def test_branch_run_endings(self):
        br = load(BR, "branch_run_1176")
        no_pr = br.ending({"slug": "orders-api", "branch": "feat/orders-cicd", "stop": "merge"})["ending"]
        self.assertIn("Open the pull request for feat/orders-cicd:\n`/crav1-open-pr`", no_pr)
        with_pr = br.ending({"slug": "orders-api", "branch": "feat/orders-cicd", "pr": 82, "stop": {"kind": "merge"}})["ending"]
        self.assertIn("Merge PR 82 into develop, after your yes:\n`/crav1-build-walk orders-api feat/orders-cicd`", with_pr)

    def test_not_ready_next_has_no_next_line(self):
        we = load(WE, "walk_ending_1176_next")
        self.assertEqual(we.not_ready_next("orders-api", {}, False), "Nothing needed now.")
        verify = we.not_ready_next("orders-api", {"needs_verify": 1}, False)
        self.assertIn("Verify the built tasks, which aren't verified yet:\n`/crav1-verify-build-against-spec orders-api`", verify)

    def test_kit_lint_catches_both(self):
        lint = load(ROOT / "scripts/kit-lint.py", "kit_lint_1176")
        self.assertEqual([why for _n, why in lint.layout_hits("Next: /crav1-open-pr, because.")], ["a Next: line"])
        old = "Run next:\n\n`/crav1-build-walk orders-api T3`\nbranch feat/orders-api, T3 Record the decision"
        self.assertEqual([why for _n, why in lint.layout_hits(old)], ["a lowercase line under a command"])
        self.assertEqual(lint.layout_hits("Run next:\n\nBuild T3:\n`/crav1-build-walk T3`\n"), [])
        self.assertEqual(lint.ending_layout_problems(str(ROOT)), [])
        self.assertIn("crav1-plan-from-spec", lint.RUN_NEXT_ONLY_SKILLS)



class SmallPersonBFixes(unittest.TestCase):
    def test_repo_sync_names_a_code_repo_by_folder(self):
        rs = load(SK / "crav1-build-walk/scripts/repo_sync.py", "repo_sync_1176")
        code = Path(tempfile.mkdtemp()) / "orders-api"
        code.mkdir()
        self.assertEqual(rs.repo_name(code), "The repo at orders-api")
        (code / "docs" / "specs").mkdir(parents=True)
        self.assertEqual(rs.repo_name(code), "The specs repo")

    def test_status_without_upstream_says_which_repo(self):
        rs = load(SK / "crav1-build-walk/scripts/repo_sync.py", "repo_sync_1176_status")
        code = Path(tempfile.mkdtemp()) / "orders-api"
        code.mkdir()
        subprocess.run(["git", "init", "-q", str(code)], check=True)
        payload = rs._status_payload(code, True, None)
        self.assertEqual(payload["state"], "no-upstream")
        self.assertTrue(payload["message"].startswith("The repo at orders-api has no upstream"))

    def test_docs_agree_on_whole_branch_commits(self):
        claims = (SK / "crav1-build-walk/references/claims.md").read_text(encoding="utf-8")
        steps = (SK / "crav1-build-walk/references/steps.md").read_text(encoding="utf-8")
        self.assertIn("A whole-branch start is different: it also commits `walk-progress.md` and its progress file", claims)
        self.assertIn("A whole-branch run follows [branch-run.md](branch-run.md) for its commits and pushes instead.", steps)

    def test_style_rule_names_its_real_path(self):
        asset = SK / "crav1-finalize-commit/branches/message-only/assets/draft-commit-style.mdc"
        self.assertIn("crav1-finalize-commit/branches/message-only/references/style.md", asset.read_text(encoding="utf-8").splitlines()[1])
        self.assertTrue((SK / "crav1-finalize-commit/branches/message-only/references/style.md").is_file())


if __name__ == "__main__":
    unittest.main()
