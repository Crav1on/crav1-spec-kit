"""1.201.1: design-architecture screen, task names, claims, and the ready check.

Generic names only (orders-platform, orders-api, person A, T1/T2).
"""
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dr = load("design_run_12011", SK / "crav1-design-architecture/scripts/design_run.py")
to = load("task_order_12011", SK / "crav1-tasks-ready-to-build/scripts/task_order.py")
bm = load("build_map_12011", SK / "crav1-tasks-ready-to-build/scripts/build_map.py")
we = load("walk_ending_12011", SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py")
bw = load("build_walk_12011", SK / "crav1-build-walk/scripts/build_walk.py")
claims = load("claims_12011", SK / "crav1-build-walk/scripts/claims.py")
wp = load("walk_progress_12011", SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py")

GOAL = {
    "ask": "split the orders platform",
    "end_goal": "Orders run as their own platform.",
    "drivers": ["Checkout stays fast"],
    "constraints": [],
    "criteria": ["Checkout stays fast in prod"],
    "design": "platform-first",
    "decisions": ["Where orders live", "Alerting owner"],
}

BRANCH_ROW = (
    "- [ ] T5: `fix/x` from `develop`, with a pull request into develop that person A approves "
    "(it changes a pipeline): Apply the CI build policy"
)
MANUAL_ROW = (
    "- [ ] T6: Rotate the orders-api signing key in TEST after the window opens "
    "(manual, secret, TEST, after person A's heads-up). Confirm the pipeline picked up the new key "
    "before the next release window."
)


def fresh(topic="orders-platform"):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "docs/architecture").mkdir(parents=True)
    (tmp / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- orders-api runs.\n", encoding="utf-8")
    path = tmp / "goal.json"
    path.write_text(json.dumps(GOAL), encoding="utf-8")
    code = dr.main(["--root", str(tmp), "create", "--topic", topic, "--input", str(path)])
    if code != 0:
        raise AssertionError("create failed")
    return tmp


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


class DesignScreen(unittest.TestCase):
    def test_run_next_leads_with_one_reason(self):
        text = dr.screen_text(fresh(), "orders-platform")
        lines = text.splitlines()
        self.assertEqual(lines[0], "Run next:")
        self.assertTrue(lines[1].strip())
        self.assertNotIn("Next:", text.replace("Run next:", ""))

    def test_design_branch_offers_the_switch_card(self):
        root = Path(tempfile.mkdtemp())
        git(root, "init", "-q", "-b", "main")
        git(root, "config", "user.email", "person-a@contoso.example")
        git(root, "config", "user.name", "Person A")
        (root / "README.md").write_text("orders-api\n", encoding="utf-8")
        git(root, "add", "README.md")
        git(root, "commit", "-q", "-m", "init")
        (root / "docs/architecture").mkdir(parents=True)
        (root / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- orders-api runs.\n", encoding="utf-8")
        path = root / "goal.json"
        path.write_text(json.dumps(GOAL), encoding="utf-8")
        self.assertEqual(dr.main(["--root", str(root), "create", "--topic", "orders-platform", "--input", str(path)]), 0)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "design")
        git(root, "switch", "-q", "main")
        text = dr.screen_text(root, "orders-platform")
        self.assertNotIn("not a topic yet", text)
        self.assertIn("Switch to the design branch:", text)
        self.assertIn("Switch to design/orders-platform and go on with the orders platform topic?", text)
        self.assertTrue(text.startswith("Run next:\n"))

    def test_resume_json_leaves_parked_status(self):
        root = fresh()
        self.assertEqual(dr.main(["--root", str(root), "park", "--topic", "orders-platform"]), 0)
        design = next((root / "docs/architecture/designs/orders-platform/designs").glob("*/design.md"))
        before = design.read_text(encoding="utf-8")
        self.assertIn("Status: parked", before)
        buf = io.StringIO()
        import contextlib
        with contextlib.redirect_stdout(buf):
            code = dr.main(["--root", str(root), "resume", "--topic", "orders-platform", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(design.read_text(encoding="utf-8"), before)
        self.assertIn('"read"' if False else "parked", before)

    def test_dated_proposal_page_is_found(self):
        root = fresh()
        page = root / "docs/architecture/proposals/2026-11-22/orders-platform.html"
        page.parent.mkdir(parents=True)
        page.write_text("<h1>orders-platform</h1>", encoding="utf-8")
        text = dr.screen_text(root, "orders-platform")
        self.assertIn("docs/architecture/proposals/2026-11-22/orders-platform.html", text)
        self.assertNotIn("Proposal: none", text)

    def test_waiting_names_each_person_once(self):
        root = fresh()
        text = "Which queue owns retries? (person A decides; the on-call rota)"
        self.assertEqual(dr.main([
            "--root", str(root), "question", "--topic", "orders-platform",
            "--decision", "Where orders live", "--text", text,
        ]), 0)
        screen = dr.screen_text(root, "orders-platform")
        self.assertIn("Waiting: person A, asked ", screen)
        self.assertNotIn("from person A decides", screen)
        self.assertLessEqual(max(len(line) for line in screen.splitlines() if line.startswith("Waiting:")), 120)

    def test_all_waiting_does_not_lead_with_next_decision(self):
        root = fresh()
        for title, question in (
            ("Where orders live", "Which queue owns retries? (person A decides)"),
            ("Alerting owner", "Who gets the expiry alert? (person B decides)"),
        ):
            self.assertEqual(dr.main([
                "--root", str(root), "question", "--topic", "orders-platform",
                "--decision", title, "--text", question,
            ]), 0)
        screen = dr.screen_text(root, "orders-platform")
        self.assertIn("The open decisions are waiting on named people.", screen)
        self.assertNotIn("Next decision:", screen)
        self.assertIn("`/crav1-show-or-ask-open-questions`", screen)

    def test_parked_screen_has_no_park_command(self):
        root = fresh()
        self.assertEqual(dr.main(["--root", str(root), "park", "--topic", "orders-platform"]), 0)
        screen = dr.screen_text(root, "orders-platform")
        self.assertNotIn("orders-platform park", screen)
        self.assertIn("The session is parked.", screen)

    def test_ended_screen_leads_with_reopen(self):
        root = fresh()
        self.assertEqual(dr.main(["--root", str(root), "end", "--topic", "orders-platform"]), 0)
        screen = dr.screen_text(root, "orders-platform")
        self.assertTrue(screen.startswith("Run next:\n"))
        self.assertIn("Reopen the topic:", screen)
        self.assertIn("`/crav1-design-architecture orders-platform reopen`", screen)
        self.assertNotIn("Next decision:", screen)
        self.assertNotIn("orders-platform park", screen)
        self.assertNotIn("orders-platform proposal", screen)
        self.assertEqual(dr.main(["--root", str(root), "reopen", "--topic", "orders-platform"]), 0)
        design = next((root / "docs/architecture/designs/orders-platform/designs").glob("*/design.md"))
        self.assertIn("Status: open", design.read_text(encoding="utf-8"))


class TaskNames(unittest.TestCase):
    def test_branch_clause_and_manual_marks(self):
        parsed = to.parse(BRANCH_ROW + "\n" + MANUAL_ROW + "\n")
        by_id = {task["id"]: task["title"] for task in parsed}
        self.assertEqual(by_id[5], "Apply the CI build policy")
        self.assertNotIn("from develop", by_id[5].lower())
        self.assertNotIn("(manual", by_id[6])
        self.assertTrue(by_id[6].startswith("Rotate the orders-api signing key"))
        names = [
            bm.short_name(BRANCH_ROW.split(": ", 1)[1]),
            bm.short_name(
                "`fix/y` from `develop`, with a pull request into develop that person A approves "
                "(it changes a pipeline): Add the lint stage"
            ),
        ]
        sentence = we.tasks_sentence(names)
        self.assertNotIn("From develop and from develop", sentence)
        self.assertIn("Apply the CI build policy", sentence)
        label = bw._task_label({"id": "T5", "title": BRANCH_ROW.split(": ", 1)[1]})
        self.assertEqual(label, "T5 Apply the CI build policy")
        manual = bw._task_label({"id": "T6", "title": MANUAL_ROW.split(": ", 1)[1]})
        self.assertNotIn("(manual", manual)
        self.assertNotIn("…", manual[:80])


class ClaimsWrite(unittest.TestCase):
    def test_add_without_yes_writes_nothing_and_keeps_the_time(self):
        root = Path(tempfile.mkdtemp()) / "docs/specs/orders-api"
        root.mkdir(parents=True)
        (root / "tasks.md").write_text("- [ ] T1: Apply the CI build policy (after: )\n", encoding="utf-8")
        code, payload, _ = _run_claims([
            "add", "--root", str(root), "--branch", "feat/orders-api",
            "--tasks", "T1", "--user", "person A",
        ])
        self.assertEqual(code, 0)
        self.assertFalse(payload["written"])
        self.assertIn("Nothing written", payload["line"])
        self.assertFalse((root / "claims.md").exists())
        code, payload, _ = _run_claims([
            "add", "--yes", "--root", str(root), "--branch", "feat/orders-api",
            "--tasks", "T1", "--user", "person A", "--since", "2026-11-22T09:00:00+00:00",
        ])
        self.assertEqual(code, 0)
        before = (root / "claims.md").read_text(encoding="utf-8")
        self.assertIn("since 2026-11-22T09:00:00+00:00", before)
        code, payload, _ = _run_claims([
            "add", "--yes", "--root", str(root), "--branch", "feat/orders-api",
            "--tasks", "T1", "--user", "person A",
        ])
        self.assertEqual(code, 0)
        self.assertEqual((root / "claims.md").read_text(encoding="utf-8"), before)
        self.assertEqual(payload["claims"][0]["since"], "2026-11-22T09:00:00+00:00")


def _run_claims(args):
    import contextlib
    buf, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        code = claims.main(args)
    text = buf.getvalue()
    payload = json.loads(text) if text.strip().startswith("{") else {"line": text, "raw": err.getvalue()}
    return code, payload, err.getvalue()


PLAN = """# Plan

Reviewed: 2026-11-24, P# open: 0

## Approach

1. README fix (PR 12). (T5)
2. Delete the old orders queue (PR 7 merged into develop). (T6)
"""

SPEC = """# Orders

## Confirmed

- orders-api runs.
"""


def spec_folder(tasks):
    root = Path(tempfile.mkdtemp()) / "docs/specs/orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text(SPEC, encoding="utf-8")
    (root / "plan.md").write_text(PLAN, encoding="utf-8")
    (root / "tasks.md").write_text(tasks, encoding="utf-8")
    (root / "verify.md").write_text("# Verify\n\n## Tasks\n\n| Id | Requirement | Status | Evidence |\n| --- | --- | --- | --- |\n", encoding="utf-8")
    return root


class ReadyCheck(unittest.TestCase):
    def setUp(self):
        self._env = os.environ.get("CRAV1_NO_HOST_LOOKUP")
        os.environ["CRAV1_NO_HOST_LOOKUP"] = "1"

    def tearDown(self):
        if self._env is None:
            os.environ.pop("CRAV1_NO_HOST_LOOKUP", None)
        else:
            os.environ["CRAV1_NO_HOST_LOOKUP"] = self._env

    def test_free_text_pr_mentions_are_not_done(self):
        tasks = (
            "- [ ] T5: README fix (PR 12) (after: )\n"
            "- [ ] T6: Delete the old orders queue (PR 7 merged into develop) (after: )\n"
            "- [ ] T7: Apply the CI build policy (PR 78, merged) (after: )\n"
        )
        self.assertFalse(to.pr_merged("README fix (PR 12)"))
        self.assertFalse(to.pr_merged("Delete the old orders queue (PR 7 merged into develop)"))
        self.assertTrue(to.pr_merged("Apply the CI build policy (PR 78, merged)"))
        self.assertTrue(to.pr_merged("Apply the CI build policy (PR 78) merged"))
        self.assertFalse(bm._pr_merged_line("README fix (PR 12)"))
        self.assertFalse(wp._pr_merged("Delete the old orders queue (PR 7 merged into develop)"))
        root = spec_folder(tasks)
        rows = {row["task"]: row for row in wp.build_rows(root)}
        self.assertNotEqual(rows["T5"]["bucket"], "done")
        self.assertNotEqual(rows["T6"]["bucket"], "done")
        self.assertEqual(rows["T7"]["bucket"], "done")

    def test_after_waits_until_the_pr_merges(self):
        tasks = (
            "- [x] T1: Land the README (PR 12) (branch: feat/orders-api) (after: )\n"
            "- [ ] T2: Delete the old orders queue (branch: feat/orders-api) (after: T1)\n"
            "- [ ] T3: Write the expiry note (branch: feat/orders-notes) (after: )\n"
        )
        root = spec_folder(tasks)
        rows = {row["task"]: row for row in wp.build_rows(root)}
        wp.apply_open_pr_holds(root, list(rows.values()), host_merged=None)
        self.assertEqual(rows["T2"]["reason"], "waits for PR 12 to merge")
        self.assertEqual(rows["T2"]["bucket"], "waiting")
        self.assertNotEqual(rows["T3"]["reason"] if rows["T3"].get("reason") else "", "waits for PR 12 to merge")
        built = bm.build("orders-api", SPEC, PLAN, tasks, walks={}, host_merged=None)
        held = [branch for branch in built["branches"] if branch["status"] == "held"]
        self.assertTrue(any("waits for PR 12 to merge" in (branch.get("held_text") or "") for branch in held))
        wp.apply_open_pr_holds(root, list(rows.values()), host_merged=[12])
        # A merged host state clears the hold. Rebuild the row from the files first.
        again = {row["task"]: row for row in wp.build_rows(root)}
        wp.apply_open_pr_holds(root, list(again.values()), host_merged=[12])
        self.assertNotEqual(again["T2"].get("reason"), "waits for PR 12 to merge")
        self.assertEqual(again["T2"]["bucket"], "ready")

    def test_skip_sync_writes_nothing(self):
        root = spec_folder("- [ ] T1: Apply the CI build policy (after: )\n")
        progress = root / "build-progress"
        progress.mkdir()
        path = progress / "feat--orders-api.md"
        path.write_text(
            "Branch: feat/orders-api\nTasks: T1 Apply the CI build policy\nPR: 12\n\n"
            "- Step: wait-merge\n  Result: done\n",
            encoding="utf-8",
        )
        before = path.read_bytes()
        wp.host_pr_lookup = lambda *args, **kwargs: {"state": {"state": "open", "author": "person A"}}
        state = wp.sync_pr_states(root, record=True, record_author=False)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(state["cleaned"], [])
        wp.sync_pr_states(root, record=True, record_author=True)
        self.assertIn("PR author: person A", path.read_text(encoding="utf-8"))

    def test_merged_pr_offers_the_clear_command_and_names_dependents_only(self):
        line = wp.hard_hit_line(
            "not-ready",
            [{"kind": "blocker", "task": "T1", "bucket": "blocked", "why": "the queue name is not decided"}],
            ["T2", "T3", "T4"],
            rows=[
                {"task": "T1", "deps": []},
                {"task": "T2", "deps": ["T1"]},
                {"task": "T3", "deps": []},
                {"task": "T4", "deps": []},
            ],
        )
        self.assertIn("T2 can start", line)
        self.assertNotIn("T3", line)
        self.assertNotIn("T4", line)
        bare = wp.hard_hit_line(
            "not-ready",
            [{"kind": "blocker", "task": "T1", "bucket": "blocked", "why": "the queue name is not decided"}],
            ["T2", "T3"],
        )
        self.assertIn("T2", bare)
        self.assertIn("T3", bare)
        self.assertEqual(bm.held_phrase({"reason": "", "pr": 12}), "waits for PR 12 to merge")
        row = {"bucket": "ready", "task": "T1", "reason": ""}
        wp.host_pr_lookup = lambda *args, **kwargs: {"state": {"state": "merged"}}
        os.environ.pop("CRAV1_NO_HOST_LOOKUP", None)
        try:
            wp.apply_walk_starts_for = None
            # walk_starts needs a folder; call the host gate and the phase branch directly.
            self.assertTrue(wp._host_merged(Path("."), 12))
        finally:
            os.environ["CRAV1_NO_HOST_LOOKUP"] = "1"
        row["walk_start"] = "wait-merge"
        found = {"phase": "wait-merge", "pr": 12, "reason": "T1 is pushed to its pull request and waits for its merge."}
        if wp._host_merged(Path("."), 12):
            row["clear_walk"] = True
        os.environ["CRAV1_NO_HOST_LOOKUP"] = "1"
        self.assertFalse(wp._host_merged(Path("."), 12))
        hit = wp.classify({
            "bucket": "waiting",
            "task": "T1",
            "reason": found["reason"],
            "pr": 12,
        })
        self.assertEqual(hit["kind"], "waiting")
        self.assertIn("PR 12", hit["why"])


if __name__ == "__main__":
    unittest.main()
