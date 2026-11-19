"""1.193.0: no Next: lines, one candidates rule, no Synced at before the yes,
commit-now's mention question, and ado_threads.py as the one Azure DevOps way.

Generic fixtures only (contoso, orders-api, person A). Mocked Azure DevOps
responses carry non-ASCII text, which must come through intact.
"""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / ".cursor/skills/crav1"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kl = _load("kit_lint_1193", ROOT / "scripts/kit-lint.py")
pc = _load("pr_common_1193", S / "crav1-open-pr/scripts/pr_common.py")
sp = _load("sweep_progress_1193", S / "crav1-update-specs-from-changes-and-prs/scripts/sweep_progress.py")
pp = _load("pr_points_1193", S / "crav1-add-to-spec/scripts/pr_points.py")
wi = _load("work_item_pick_1193", S / "crav1-finalize-commit/scripts/work_item_pick.py")
ado = _load("ado_threads_1193", S / "crav1-review-pr/scripts/ado_threads.py")

NOTE = """# PR 73

## PR record

- Point: general | agreed | person A | thread 180; to spec; in spec orders-api 2026-11-18 | Slow database delays the response: person B asks
- Point: src/orders/api.py:12 | agreed | person A | thread 181; to spec; in spec orders-api 2026-11-18 | Retry count is three
- Point: src/orders/db.py:40 | agreed | person A | thread 182; to decision | Pick the queue over polling
- Point: src/orders/x.py:1 | open | person A | thread 183 | Not a candidate
"""


def _run(main, argv):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            code = main(argv) or 0
        except SystemExit as exc:
            code = exc.code or 0
    return code, json.loads(buf.getvalue())


class NoNextLines(unittest.TestCase):
    def test_kit_has_no_new_next_lines(self):
        self.assertEqual(kl.next_anywhere_problems(str(ROOT)), [])

    def test_moved_skills_have_no_next_lines(self):
        counts = kl.next_line_counts(str(ROOT))
        for rel in counts:
            self.assertNotIn("crav1-add-to-spec/", rel)
            self.assertNotIn("crav1-update-specs-from-changes-and-prs/", rel)

    def test_new_next_line_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp, ".cursor/skills/crav1/crav1-orders")
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text("End with `Next: /crav1-tighten-spec orders-api`.\n", encoding="utf-8")
            (skill / "scripts/end.py").write_text('print("Next: nothing needed now.")\n', encoding="utf-8")
            (skill / "scripts/check.py").write_text('if line.startswith("Next:"):\n    pass\n', encoding="utf-8")
            problems = kl.next_anywhere_problems(tmp)
            self.assertEqual(len(problems), 2, problems)

    def test_baseline_only_shrinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "scripts").mkdir()
            Path(tmp, kl.NEXT_BASELINE).write_text(".cursor/skills/crav1/crav1-orders/SKILL.md\t1\n", encoding="utf-8")
            Path(tmp, ".cursor/skills/crav1").mkdir(parents=True)
            self.assertIn("lower the baseline", kl.next_anywhere_problems(tmp)[0])

    def _state(self, items=(), proposals=(), flow="manual-flow"):
        return {"items": list(items), "header": {"Flow": flow, "Scope": "all"},
                "proposals": list(proposals), "waiting": []}

    def test_sweep_nothing_pending_files_uncommitted(self):
        out = sp.ending_lines(self._state(), 3)
        self.assertEqual(out["next"], "Run next: nothing needed now.")
        self.assertTrue(out["uncommitted"].startswith("Uncommitted: 3 files"))
        self.assertNotIn("Next:", out["next"].replace("Run next:", ""))

    def test_sweep_pending_is_run_next_block(self):
        item = {"status": "pending", "flags": "-"}
        lines = sp.ending_lines(self._state([item]), 0)["next"].splitlines()
        self.assertEqual(lines[0], "Run next:")
        self.assertEqual(lines[-1], "`/crav1-update-specs-from-changes-and-prs manual-flow`")
        self.assertTrue(lines[-2].endswith(":"))

    def test_add_to_spec_none_left_ending(self):
        text = (S / "crav1-add-to-spec/references/pr-candidates.md").read_text(encoding="utf-8")
        self.assertIn("No spec or decision candidates are open in PR <n>.", text)
        self.assertIn("`/crav1-pr-status pr<n>`", text)


class Candidates(unittest.TestCase):
    def test_in_spec_without_newer_reply_not_offered(self):
        pts = pc.record_candidates_of(NOTE)
        self.assertFalse(pts[0]["candidate"])
        self.assertFalse(pts[1]["candidate"])
        self.assertTrue(pts[2]["candidate"])
        self.assertFalse(pts[3]["candidate"])

    def test_newer_answer_narrows_and_offers(self):
        line = NOTE.splitlines()[4]
        new = pc.mark_answered(line, "2026-11-19")
        self.assertIn("in spec orders-api (question)", new)
        self.assertIn("answered 2026-11-19", new)
        self.assertTrue(pc.candidate_state(pc.parse_point(new))["candidate"])

    def test_answer_date_after_in_spec_date_is_candidate(self):
        line = "- Point: general | agreed | person A | thread 9; to spec; in spec orders-api 2026-11-18; answered 2026-11-19 | Accept a slow database for now"
        self.assertTrue(pc.candidate_state(pc.parse_point(line))["candidate"])

    def test_cli_answered_then_candidates_accepts_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp, "pr-73.md")
            note.write_text(NOTE, encoding="utf-8")
            code, out = _run(pp.main, ["answered", "--note", str(note), "--thread", "180", "--date", "2026-11-19"])
            self.assertEqual(out["status"], "planned")
            self.assertEqual(note.read_text(encoding="utf-8"), NOTE)
            _run(pp.main, ["answered", "--note", str(note), "--thread", "180", "--date", "2026-11-19", "--yes"])
            code, out = _run(pc.main, ["candidates", "--note", str(note)])
            self.assertEqual([c["number"] for c in out["candidates"]], [1, 3])
            code, out = _run(pc.main, ["candidates", "--note", str(note), "--pick", "1"])
            self.assertEqual([c["number"] for c in out["candidates"]], [1])
            _run(pp.main, ["in-spec", "--note", str(note), "--thread", "180", "--slug", "orders-api", "--date", "2026-11-19", "--yes"])
            code, out = _run(pc.main, ["candidates", "--note", str(note)])
            self.assertEqual([c["number"] for c in out["candidates"]], [3])

    def test_both_skills_name_the_shared_script(self):
        for rel in ("crav1-pr-status/references/classify.md", "crav1-add-to-spec/references/pr-candidates.md"):
            self.assertIn("pr_common.py candidates --note", (S / rel).read_text(encoding="utf-8"))


class SyncedAtWaitsForYes(unittest.TestCase):
    def test_refuses_without_yes_and_writes_with_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp, "spec.md")
            spec.write_text("# orders-api\n\n## Problem\n\nSlow.\n", encoding="utf-8")
            argv = ["synced-at", "--spec", str(spec), "--repo", "orders-api", "--branch", "main",
                    "--sha", "abc1234def", "--date", "2026-11-19"]
            code, out = _run(sp.main, argv)
            self.assertFalse(out["written"])
            self.assertNotIn("Synced at", spec.read_text(encoding="utf-8"))
            code, out = _run(sp.main, argv + ["--yes"])
            self.assertTrue(out["written"])
            self.assertIn("# orders-api\nSynced at: orders-api main@abc1234, 2026-11-19\n", spec.read_text(encoding="utf-8"))

    def test_manual_flow_lists_pre_yes_writes(self):
        text = (S / "crav1-update-specs-from-changes-and-prs/references/manual-flow.md").read_text(encoding="utf-8")
        self.assertIn("only these are written: the note, the PR note", text)
        self.assertNotIn("That part does not need a yes", text)


class CommitNowMention(unittest.TestCase):
    WI = "Work item: 2 — October billing\nWork item: 3 — catalog\nWork item: 4 — exports\nWork item: 5 — Größe\nWork item: 9 — task: T3 Read\n"

    def test_unclear_asks_four_options_and_other(self):
        out = wi.pick(self.WI, [])
        self.assertEqual(out["status"], "ask")
        self.assertLessEqual(len(out["options"]), 4)
        self.assertEqual(out["options"][-1], "No mention")
        self.assertTrue(out["other"])
        self.assertEqual(out["headless"], "copy")

    def test_clear_match_picks_one(self):
        self.assertEqual(wi.pick(self.WI, ["Größe"])["mention"]["id"], "5")

    def test_skill_says_commit_now_may_ask(self):
        text = (S / "crav1-finalize-commit/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`commit-now` may still ask", text)
        self.assertIn("commit-now may still ask", (S / "crav1-finalize-commit/references/choice-words.md").read_text(encoding="utf-8"))


THREADS = {"value": [{"id": 180, "status": 1, "publishedDate": "2026-11-19T08:00:00Z", "lastUpdatedDate": "2026-11-19T10:00:00Z",
                      "comments": [{"id": 1, "parentCommentId": 0, "author": {"displayName": "Åsa Öberg"},
                                    "content": "Är databasen långsam?", "publishedDate": "2026-11-19T08:00:00Z"},
                                   {"id": 2, "parentCommentId": 1, "author": {"displayName": "person A"},
                                    "content": "Accept for now – café", "publishedDate": "2026-11-19T10:00:00Z",
                                    "lastContentUpdatedDate": "2026-11-19T10:05:00Z"}]}]}
PR = {"pullRequestId": 73, "title": "Orders: retry ñ", "status": "active", "creationDate": "2026-11-17T09:00:00Z",
      "description": "Adds retry — für orders-api.", "reviewers": [{"displayName": "Åsa Öberg", "vote": 10}, {"displayName": "person B", "vote": -5}]}
ITS = {"value": [{"id": 1, "createdDate": "2026-11-17T09:00:00Z", "sourceRefCommit": {"commitId": "aaaaaaa1"}},
                 {"id": 2, "createdDate": "2026-11-19T09:00:00Z", "sourceRefCommit": {"commitId": "bbbbbbb2"}}]}


class AdoThreads(unittest.TestCase):
    def test_list_has_dates_and_keeps_accents(self):
        rows = ado.summarize(THREADS["value"])
        self.assertEqual(rows[0]["comments"][1]["updated"], "2026-11-19T10:05:00Z")
        self.assertEqual(rows[0]["comments"][0]["author"], "Åsa Öberg")
        self.assertEqual(rows[0]["published"], "2026-11-19T08:00:00Z")

    def test_pr_votes_and_description(self):
        view = ado.pr_view(PR)
        self.assertEqual(view["description"], "Adds retry — für orders-api.")
        self.assertEqual([v["vote_text"] for v in view["votes"]], ["approved", "waiting for author"])

    def test_iterations(self):
        rows = ado.iterations_view(ITS)
        self.assertEqual(rows[-1]["head"], "bbbbbbb2")

    def test_cli_output_is_utf8_with_accents(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp, "threads.json")
            raw.write_bytes(json.dumps(THREADS, ensure_ascii=False).encode("utf-8"))
            env = dict(os.environ, PYTHONIOENCODING="cp1252")
            done = subprocess.run([sys.executable, str(S / "crav1-review-pr/scripts/ado_threads.py"), "list", "--pr", "73",
                                   "--from-file", str(raw)], capture_output=True, env=env)
            self.assertEqual(done.returncode, 0, done.stderr)
            text = done.stdout.decode("utf-8")
            self.assertIn("Åsa Öberg", text)
            self.assertIn("café", text)

    def test_set_status_previews_then_reads_back(self):
        calls = []

        def fake(args):
            calls.append(args)
            return json.dumps({"id": 180, "status": 2}).encode("utf-8")
        old = ado.run_az
        ado.run_az = fake
        try:
            base = ["set-status", "--pr", "73", "--thread", "180", "--status", "fixed",
                    "--org", "https://dev.azure.com/contoso", "--project", "orders", "--repo", "orders-api"]
            code, out = _run(ado.main, base)
            self.assertFalse(out["changed"])
            self.assertEqual(calls, [])
            code, out = _run(ado.main, base + ["--yes"])
            self.assertTrue(out["ok"])
            self.assertEqual(out["status"], "fixed")
            self.assertIn("PATCH", calls[0])
            self.assertNotIn("PATCH", calls[1])
        finally:
            ado.run_az = old

    def test_since_last_uses_the_recorded_state(self):
        note = ("# PR 73\n\n## PR record\n\n- Read: person A | aaaaaaa1, push 1, newest comment 2026-11-19T08:00Z | 2026-11-19\n\n"
                "## Description as of 2026-11-18\n\nAdds retry — für orders-api.\n\n## PR updates as of 2026-11-18\n\nnone\n")
        threads = ado.summarize(THREADS["value"])
        out = ado.since_last(note, "person A", threads, ado.iterations_view(ITS), ado.pr_view(PR))
        self.assertTrue(out["new_push"])
        self.assertEqual([c["comment"] for c in out["new_comments"]], [2])
        self.assertFalse(out["description_changed"])
        changed = dict(PR, description="Adds retry — and exports.")
        self.assertTrue(ado.since_last(note, "person A", threads, ado.iterations_view(ITS), ado.pr_view(changed))["description_changed"])
        self.assertFalse(ado.since_last(note, "person B", threads, [], ado.pr_view(PR))["earlier"])

    def test_docs_have_no_az_rest_for_pr_threads(self):
        for rel in ("crav1-add-to-spec/references/pr-threads.md", "crav1-add-to-spec/references/pr-comments.md",
                    "crav1-review-pr/references/comment-as-posted.md", "crav1-review-pr/references/re-review.md",
                    "crav1-pr-status/references/since-last.md"):
            text = (S / rel).read_text(encoding="utf-8")
            self.assertNotIn("az rest --", text, rel)
            self.assertNotRegex(text, r"az devops invoke --org <org-url> --area git", rel)


if __name__ == "__main__":
    unittest.main()
