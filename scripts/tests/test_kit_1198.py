"""1.198.0: phase-aware build-walk endings, checked behind state, release gates in the build walk,
kit update line, fewer cards, container detection and small fixes.

Generic fixtures only (orders-api, contoso, person A).
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
BW = SK / "crav1-build-walk/scripts/build_walk.py"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com"]


def py(script: Path, *args: str, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False, cwd=cwd)


def js(script: Path, *args: str, cwd=None) -> dict:
    proc = py(script, *args, cwd=cwd)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(rel: str) -> str:
    return (SK / rel).read_text(encoding="utf-8")


def spec_folder(tasks: str, plan: str = "# Plan\n") -> Path:
    root = Path(tempfile.mkdtemp()) / "docs" / "specs" / "orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text("# Orders API\n\n## Problem\n\nx\n", encoding="utf-8")
    (root / "plan.md").write_text(plan, encoding="utf-8")
    (root / "tasks.md").write_text("# Tasks\n\n" + tasks, encoding="utf-8")
    return root


LONG = ("Idempotent incoming. The code is on develop since PR 73 merged; T30 checks it there, and adds three tests "
        "for a repeated message, a replayed batch and a duplicate id, each with its own fixture and a short note "
        "on why the store keeps the first copy and drops the rest, so the replay never writes twice.")


class PhaseLabels(unittest.TestCase):
    """Item 1: Run next labels follow the step; short titles."""

    def setUp(self):
        self.bw = load(BW, "build_walk_t1198a")

    def ending(self, phase, **extra):
        state = {"mode": "walk", "phase": phase, "branch": "feat/orders-retry", "slug": "orders-api",
                 "tasks": [{"id": "T30", "title": LONG}], "pr": 85, **extra}
        return self.bw.next_for(self.bw.prepare_state(state))

    def test_merge_pr_label(self):
        out = self.ending("merge-pr")
        self.assertIn("Merge PR 85 for T30:\n`/crav1-build-walk orders-api T30`", out["ending"])
        self.assertNotIn("Build T30", out["ending"])

    def test_tick_and_verify_labels(self):
        self.assertIn("Tick T30, now that PR 85 is merged:", self.ending("tick")["ending"])
        self.assertIn("Verify Idempotent incoming (T30) on feat/orders-retry:", self.ending("verify")["ending"])

    def test_short_title(self):
        label = self.bw._task_label({"id": "T30", "title": LONG})
        self.assertEqual(label, "Idempotent incoming (T30)")
        long_one = "Add " + " ".join(["retry"] * 40)
        cut = self.bw.short_title(long_one)
        self.assertLessEqual(len(cut), 121)
        self.assertTrue(cut.endswith("…"))

    def test_lead_never_capitalizes_branch_and_states_only_checked_facts(self):
        out = self.ending("merge-base", behind_count=2)
        self.assertTrue(out["lead"].startswith("feat/orders-retry is 2 commits behind develop"))
        unknown = self.ending("merge-base")
        self.assertNotIn("is behind", unknown["lead"])


class BehindCheckAndRecord(unittest.TestCase):
    """Item 1: real behind check, nothing-to-do advances, --pr and several steps in one record."""

    def setUp(self):
        self.bw = load(BW, "build_walk_t1198b")

    def test_nothing_to_do_advances(self):
        info = {"owner": "self", "steps": [{"step": "merge-base", "result": "nothing-to-do (0 behind)"}]}
        self.assertEqual(self.bw.phase_from_progress(info), "merge-pr")

    def test_behind_count_zero_skips_merge_base(self):
        tmp = Path(tempfile.mkdtemp())
        origin, work = tmp / "origin.git", tmp / "orders-api"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "develop", str(origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(origin), str(work)], check=True, capture_output=True)
        subprocess.run(G + ["-C", str(work), "checkout", "-q", "-b", "develop"], check=True)
        (work / "a.txt").write_text("a", encoding="utf-8")
        subprocess.run(G + ["-C", str(work), "add", "-A"], check=True)
        subprocess.run(G + ["-C", str(work), "commit", "-qm", "a"], check=True)
        subprocess.run(G + ["-C", str(work), "push", "-q", "-u", "origin", "develop"], check=True, capture_output=True)
        subprocess.run(G + ["-C", str(work), "checkout", "-q", "-b", "feat/orders-retry"], check=True)
        (work / "b.txt").write_text("b", encoding="utf-8")
        subprocess.run(G + ["-C", str(work), "add", "-A"], check=True)
        subprocess.run(G + ["-C", str(work), "commit", "-qm", "b"], check=True)
        self.assertEqual(self.bw.behind_count(work, "feat/orders-retry", "develop"), 0)
        self.assertIsNone(self.bw.behind_count(tmp / "missing", "feat/orders-retry", "develop"))

    def test_record_pr_and_several_steps(self):
        root = spec_folder("- [ ] T30: Idempotent incoming (branch: feat/orders-retry)\n")
        init = js(BW, "progress", "init", "--root", str(root), "--branch", "feat/orders-retry", "--tasks", "T30", "--yes")
        self.assertTrue(init["ok"], init)
        out = js(BW, "progress", "record", "--root", str(root), "--branch", "feat/orders-retry",
                 "--step", "build,verify,commit", "--result", "done", "--yes")
        self.assertEqual(out["line"], "Recorded build, verify, commit in the build progress file.")
        self.assertNotIn("text", out)
        js(BW, "progress", "record", "--root", str(root), "--branch", "feat/orders-retry",
           "--step", "open-pr", "--result", "done", "--pr", "85", "--yes")
        text = Path(out["path"]).read_text(encoding="utf-8")
        self.assertIn("done (PR 85)", text)
        self.assertEqual(self.bw.read_progress(text)["pr"], 85)
        self.assertEqual(text.count("- Step: verify"), 1)


class BuildWalkGate(unittest.TestCase):
    """Item 2: release gate and unbranched manual tasks in the build-walk ending."""

    def test_gated_task_is_never_first(self):
        root = spec_folder(
            "- [x] T1: Export endpoint (branch: feat/orders-export)\n"
            "- [ ] T52 (manual, prod, owner: person A) Drop the old orders tables (after-release: main)\n"
            "- [ ] T53 (manual, DEV, owner: person A) Check the DEV export page\n"
            "- [ ] T4: Retry on 503 (branch: feat/orders-retry)\n")
        bw = load(BW, "build_walk_t1198c")
        ready = [{"branch": "feat/orders-api-separate-keys", "tasks": [{"id": "T52", "title": "(manual, prod) Drop the old orders tables"},
                                                                         {"id": "T53", "title": "(manual, DEV) Check the DEV export page"}]},
                 {"branch": "feat/orders-retry", "tasks": [{"id": "T4", "title": "Retry on 503"}]}]
        state = {"mode": "walk", "phase": "next-task", "branch": "feat/orders-export", "slug": "orders-api",
                 "tasks": [{"id": "T1", "title": "Export endpoint"}], "root": str(root), "ready_branches": ready}
        out = bw.next_for(bw.prepare_state(state))
        self.assertNotIn("T52", out["ending"])
        self.assertNotIn("feat/orders-api-separate-keys", out["ending"])
        self.assertIn("Run the manual task (manual, DEV) Check the DEV export page (T53) (no branch):", out["ending"])
        self.assertIn("`/crav1-build-walk T4`", out["ending"])


class KitUpdateLine(unittest.TestCase):
    """Item 3: one read-only Kit update available line at the start and in the ending."""

    def setUp(self):
        import os
        self.mod = load(SK / "crav1-update-kit/scripts/update_kit.py", "update_kit_t1198")
        self.mod.detect = lambda root, home=None: {"version": "1.197.0", "mode": "drop-in"}
        self.old = os.environ.get("CRAV1_KIT_LATEST")

    def tearDown(self):
        import os
        if self.old is None:
            os.environ.pop("CRAV1_KIT_LATEST", None)
        else:
            os.environ["CRAV1_KIT_LATEST"] = self.old

    def test_newer_release_gives_one_line(self):
        import os
        os.environ["CRAV1_KIT_LATEST"] = "1.198.0"
        found = self.mod.update_available(Path("."))
        self.assertEqual(found["line"], "Kit update available: 1.197.0 -> 1.198.0")
        self.assertIn("`/crav1-update-kit`", found["run"])

    def test_silent_when_current_or_offline(self):
        import os
        os.environ["CRAV1_KIT_LATEST"] = "1.197.0"
        self.assertIsNone(self.mod.update_available(Path(".")))
        os.environ["CRAV1_KIT_LATEST"] = "off"
        self.assertIsNone(self.mod.update_available(Path(".")))

    def test_build_walk_ending_carries_it(self):
        bw = load(BW, "build_walk_t1198d")
        state = {"mode": "walk", "phase": "build", "branch": "feat/orders-retry", "tasks": [{"id": "T4", "title": "Retry"}],
                 "kit_update": {"line": "Kit update available: 1.197.0 -> 1.198.0",
                                "run": "Update the kit first (1.198.0 is out):\n`/crav1-update-kit`"}}
        out = bw.next_for(bw.prepare_state(state))
        self.assertEqual(out["kit_update"], "Kit update available: 1.197.0 -> 1.198.0")
        self.assertIn("Update the kit first (1.198.0 is out):\n`/crav1-update-kit`", out["ending"])


class DependencyContainers(unittest.TestCase):
    """Item 5: find stopped containers and a stopped podman machine before offering an install."""

    def setUp(self):
        self.mod = load(SK / "crav1-verify-build-against-spec/scripts/dep_check.py", "dep_check_t1198")

    def test_no_runtime_offers_install(self):
        out = self.mod.check(["orders-storage"], which=lambda tool: None, run=lambda cmd: (1, ""))
        self.assertEqual(out["state"], "no-runtime")
        self.assertTrue(out["install"])

    def test_stopped_podman_machine_and_container(self):
        def run(cmd):
            if cmd[:2] == ["podman", "ps"]:
                return 125, ""
            if cmd[:3] == ["podman", "machine", "list"]:
                return 0, "podman-machine-default\tfalse\n"
            return 1, ""
        out = self.mod.check(["orders-storage"], which=lambda tool: "/usr/bin/podman" if tool == "podman" else None, run=run)
        self.assertEqual(out["state"], "stopped")
        self.assertEqual(out["start"][0], "podman machine start")
        self.assertFalse(out["install"])

    def test_stopped_container_recommends_start(self):
        def run(cmd):
            if cmd[:2] == ["docker", "ps"]:
                return 0, "orders-storage\tcontoso/storage-emulator\texited\n"
            return 1, ""
        out = self.mod.check(["orders-storage"], which=lambda tool: "/usr/bin/docker" if tool == "docker" else None, run=run)
        self.assertEqual(out["state"], "stopped")
        self.assertEqual(out["start"], ["docker start orders-storage"])
        self.assertIn("No install needed", out["line"])

    def test_running_container(self):
        run = lambda cmd: (0, "orders-storage\tcontoso/storage-emulator:latest\trunning\n") if cmd[1] == "ps" else (1, "")
        out = self.mod.check(["orders-storage"], which=lambda tool: "/x" if tool == "podman" else None, run=run)
        self.assertEqual(out["state"], "running")

    def test_doc_runs_only_dependency_free_tests(self):
        text = read(SK / "crav1-verify-build-against-spec/references/test-dependencies.md")
        self.assertIn("runs only the tests that do not need it", text)
        self.assertIn("dep_check.py containers --service", text)


class FewerCards(unittest.TestCase):
    """Item 4: one yes opens the PR; Not yet folds the specs push."""

    def test_open_pr_one_yes_and_no_open_only_when_unpushed(self):
        draft = read(SK / "crav1-open-pr/references/draft.md")
        self.assertIn("the walk's yes already chose `push`", draft)
        self.assertIn("Leave this choice out when the head is not pushed", draft)
        self.assertIn("with no second card", read(SK / "crav1-build-walk/references/steps.md"))

    def test_not_yet_covers_specs_push(self):
        self.assertIn("commit and push the walk's specs files", read(SK / "crav1-build-walk/references/common.md"))
        self.assertIn("`Not yet`, that answer already covers this commit and push", read(SK / "crav1-build-walk/references/sync.md"))


class SmallFixes(unittest.TestCase):
    """Item 6: org from repos.md, fetch before the PR-note gate, quoted --query, no Next: in prose."""

    def test_org_from_repos_md(self):
        mod = load(SK / "crav1-review-pr/scripts/ado_threads.py", "ado_threads_t1198")
        with tempfile.TemporaryDirectory() as tmp:
            system = Path(tmp) / "docs/system"
            system.mkdir(parents=True)
            (system / "repos.md").write_text(
                "| Repo | URL |\n| --- | --- |\n| orders-api | https://dev.azure.com/contoso/Orders/_git/orders-api |\n"
                "| orders-web | https://dev.azure.com/contoso/Orders/_git/orders-web |\n", encoding="utf-8")
            self.assertEqual(mod.repos_md_route(Path(tmp), "orders-web")["repo"], "orders-web")
            self.assertEqual(mod.repos_md_route(Path(tmp))["org"], "https://dev.azure.com/contoso")
            self.assertEqual(mod.repos_md_route(Path(tmp) / "docs"), mod.repos_md_route(Path(tmp)))

    def test_docs(self):
        self.assertIn("git -C <specs repo> fetch --quiet", read(SK / "crav1-merge-pr/references/pr-record-gate.md"))
        self.assertIn('--query "user.name"', read(SK / "crav1-pr-status/references/modes.md"))
        self.assertIn("Quote every `--query` value", read(ROOT / "docs/reference/pr-common.md"))
        self.assertIn("Your own prose has no `Next:` line", read(SK / "crav1-build-walk/references/common.md"))
        self.assertIn("--code-repo <code checkout>", read(SK / "crav1-pr-status/references/since-last.md"))


WP = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
BM = SK / "crav1-tasks-ready-to-build/scripts/build_map.py"
WE = SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py"


class ReadyCheckEnding(unittest.TestCase):
    """Item 8: ready-check ending fixes."""

    @classmethod
    def setUpClass(cls):
        cls.wp = load(WP, "walk_progress_t1198")

    def test_a_hard_hit_is_named_with_the_ready_tasks(self):
        hits = [{"task": "T12", "bucket": "blocked", "kind": "blocked",
                 "why": "The queue name is not decided. The walk does not invent a step for this."},
                {"task": "T20", "bucket": "waiting", "kind": "waiting", "why": "x"}]
        line = self.wp.hard_hit_line("not-ready", hits, ["T3", "T4", "T5", "T6"])
        self.assertEqual(line, "Not ready: T12 is blocked (the queue name is not decided). "
                               "T3, T4, T5 and T6 can start once that is cleared.")
        self.assertIsNone(self.wp.hard_hit_line("not-ready", hits, []))
        self.assertIsNone(self.wp.hard_hit_line("ready-partial", hits, ["T3"]))

    def test_b_own_pushed_task_waits_for_its_merge(self):
        rows = [{"task": "T30", "own_claim": True, "own_pr_open": 85, "bucket": "ready"}]
        self.assertEqual(self.wp.own_claim_line(rows), "T30 is yours and waits for PR 85's merge.")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "build-progress"
            folder.mkdir()
            (folder / "feat--orders-retry.md").write_text(
                "# Build progress\n\nBranch: feat/orders-retry\nOwner: self\nTasks: T30\n\n"
                "- Step: build T30\n  Done: 2026-11-20\n  Result: done\n"
                "- Step: open-pr\n  Done: 2026-11-20\n  Result: done (PR 85)\n", encoding="utf-8")
            self.assertEqual(self.wp.progress_open_prs(Path(tmp)), {"T30": 85})
            (folder / "feat--orders-retry.md").write_text(
                (folder / "feat--orders-retry.md").read_text() + "- Step: merge-pr\n  Done: 2026-11-21\n  Result: done\n")
            self.assertEqual(self.wp.progress_open_prs(Path(tmp)), {})

    def test_c_resume_names_who_and_needs_questions(self):
        questions = [{"task": "T26", "reason": 'open question "Which queue?"', "who": "person A", "asked": True},
                     {"task": "T33", "reason": 'open question "Which region?"', "who": "the project team (owners)", "asked": True}]
        _line, nxt = self.wp._waiting_lines(questions, "orders-api")
        entry = self.wp._run_from_clause(nxt)
        self.assertTrue(entry.startswith("Resume the walk when the answers from person A and the project team arrive:"), entry)
        approvals = [{"task": "T5", "reason": "approval needed \"go live\"", "approval": True, "asked": True}]
        _line, nxt = self.wp._waiting_lines(approvals, "orders-api")
        self.assertNotIn("answers", nxt or "")

    def test_d_record_without_card_when_only_waits(self):
        wp = load(WP, "walk_progress_t1198d")
        wp.load = lambda root: {"steps": {"tasks-ready-to-build": {"result": "ready-partial"}}}
        with tempfile.TemporaryDirectory() as tmp:
            waits = [{"kind": "waiting", "task": "T26"}, {"kind": "blocker", "merge": True, "task": "T30"}]
            self.assertEqual(wp.record_quiet(Path(tmp), "not-ready", waits), "Recorded: not-ready (was ready-partial).")
            self.assertIsNone(wp.record_quiet(Path(tmp), "not-ready", waits + [{"kind": "blocked", "task": "T12"}]))
            self.assertIsNone(wp.record_quiet(Path(tmp), "ready-partial", waits))

    def test_e_repeated_question_once_and_cut(self):
        bm = load(BM, "build_map_t1198")
        question = ("Which storage account holds the retry queue for orders-api, given that the shared one is "
                    "being retired next quarter, and who approves the move to the new one?")
        built = {"branches": [{"name": "feat/orders-retry", "section": "wave", "wave": 1,
                               "tasks": [{"id": 26, "title": "Retry queue"}, {"id": 33, "title": "Retry alerts"}]}]}
        rows = [{"task": "T26", "bucket": "waiting", "held": True, "who": "person A", "reason": f'open question "{question}"'},
                {"task": "T33", "bucket": "waiting", "held": True, "who": "person A", "reason": f'open question "{question}"'}]
        report = bm.report_by_branch(built, rows)
        text = "\n".join(report["held_lines"])
        self.assertEqual(text.count("Which storage account"), 1, text)
        self.assertIn("same question as T26", text)
        first = next(line for line in text.splitlines() if "T26" in line)
        self.assertLess(len(first.split('"')[1]), 125)

    def test_f_build_map_only_change_label(self):
        we = load(WE, "walk_ending_t1198")
        block = we.catch_up_block("orders-api", uncommitted=["docs/specs/orders-api/build-map.md"])
        self.assertIn("Commit the updated build map:", block)
        self.assertNotIn("changed spec file", block)
        block = we.catch_up_block("orders-api", uncommitted=["docs/specs/orders-api/build-map.md", "docs/specs/orders-api/tasks.md"])
        self.assertIn("Commit the 2 changed spec files:", block)


class PlainCardLabels(unittest.TestCase):
    """Item 7: plain labels on build-walk cards."""

    def test_rule(self):
        text = read(SK / "crav1-build-walk/references/common.md")
        self.assertIn("never a `yes:` or `stop:` prefix on the label", text)
        self.assertIn("On yes:", text)


class NextTaskFallback(unittest.TestCase):
    """Item 6: next --task falls back to the recommended branch."""

    def test_recommended_branch_for_exists(self):
        bw = load(BW, "build_walk_t1198n")
        self.assertTrue(callable(bw.recommended_branch_for))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(bw.recommended_branch_for(Path(tmp), "T4"))
        import importlib
        tbm = load(ROOT / "scripts/tests/test_build_map.py", "test_build_map_t1198")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "cancel-booking"
            folder.mkdir()
            (folder / "tasks.md").write_text(tbm.TASKS, encoding="utf-8")
            (folder / "plan.md").write_text(tbm.PLAN, encoding="utf-8")
            (folder / "spec.md").write_text(tbm.SPEC, encoding="utf-8")
            self.assertEqual(bw.recommended_branch_for(folder, "T3"), "feat/cancel-booking-send-receipt")
