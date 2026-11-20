"""1.199.0: org on pr_common checks, thread replies, answered points, one re-check shape,
lighter pr-status, commit-push, and queued build fixes.

Generic fixtures only (orders-api, contoso, person A).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
PRC = SK / "crav1-open-pr/scripts/pr_common.py"
ADO = SK / "crav1-review-pr/scripts/ado_threads.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ChecksOrganization(unittest.TestCase):
    """Item 1: both az calls carry --organization."""

    def run_checks(self, ref, repo=None):
        mod = load(PRC, "pr_common_t1199")
        calls = []

        def fake(cmd, cwd=None):
            calls.append(cmd)
            if cmd[:4] == ["az", "repos", "pr", "show"]:
                return 0, json.dumps({"status": "active", "isDraft": False}), ""
            return 0, "[]", ""
        mod._run = fake
        mod.emit = lambda out, code=0: out
        args = types.SimpleNamespace(from_json=None, ref=ref, repo=repo)
        mod.cmd_checks(args)
        return calls

    def test_org_from_the_pr_url(self):
        calls = self.run_checks("https://dev.azure.com/contoso/Orders/_git/orders-api/pullrequest/84")
        azure = [c for c in calls if c[0] == "az"]
        self.assertEqual(len(azure), 2)
        for cmd in azure:
            self.assertIn("--organization", cmd)
            self.assertEqual(cmd[cmd.index("--organization") + 1], "https://dev.azure.com/contoso")

    def test_org_from_repos_md_for_a_bare_ref(self):
        mod = load(PRC, "pr_common_t1199b")
        with tempfile.TemporaryDirectory() as tmp:
            system = Path(tmp) / "docs/system"
            system.mkdir(parents=True)
            (system / "repos.md").write_text("| orders-api | https://dev.azure.com/contoso/Orders/_git/orders-api |\n", encoding="utf-8")
            self.assertEqual(mod.azure_org({"host": "azure", "repo": "orders-api"}, tmp), "https://dev.azure.com/contoso")
            self.assertEqual(mod.azure_org({"host": "azure", "org": "fabrikam"}, tmp), "https://dev.azure.com/fabrikam")


class ThreadReply(unittest.TestCase):
    """Item 2: reply inside a thread, set its status, mark the draft posted."""

    def setUp(self):
        self.mod = load(ADO, "ado_threads_t1199")
        self.calls = []
        thread = {"id": 195, "status": 1, "comments": [{"id": 1, "content": "Which setting?"}, {"id": 3, "content": "This one."}]}
        state = {"status": 1}

        def fake(cmd):
            self.calls.append(cmd)
            if "--http-method" in cmd and "PATCH" in cmd:
                state["status"] = 2
                return b"{}"
            if "--http-method" in cmd:
                return json.dumps({"id": 4}).encode()
            return json.dumps(dict(thread, status=state["status"])).encode()
        self.mod.run_az = fake

    def args(self, tmp, **extra):
        draft = Path(tmp) / "reply.md"
        draft.write_text("Thanks, that answers it. I've marked this thread fixed.", encoding="utf-8")
        base = dict(pr=84, thread=195, file=str(draft), status=None, yes=False, note=None, from_file=None,
                    org="https://dev.azure.com/contoso", project="Orders", repo="orders-api")
        base.update(extra)
        return types.SimpleNamespace(**base)

    def test_preview_posts_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.mod.cmd_reply(self.args(tmp, status="fixed"))
        self.assertFalse(out["posted"])
        self.assertEqual(out["body"]["parentCommentId"], 3)
        self.assertTrue(out["link"].endswith("/pullrequest/84?discussionId=195"))
        self.assertFalse(any("--http-method" in c for c in self.calls))

    def test_reply_sets_fixed_and_marks_the_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "pr-84.md"
            note.write_text("# PR 84\n\n## Replies as drafted, 2026-11-20 (not posted)\n\nThread 195: Thanks, that answers it.\n",
                            encoding="utf-8")
            out = self.mod.cmd_reply(self.args(tmp, status="fixed", yes=True, note=str(note)))
            self.assertTrue(out["ok"], out)
            self.assertEqual(out["status"], "fixed")
            self.assertTrue(out["note_marked"])
            self.assertRegex(read(note), r"## Replies as drafted, 2026-11-20 \(thread 195 posted \d{4}-\d{2}-\d{2}\)")
        posts = [c for c in self.calls if "POST" in c]
        self.assertIn("pullRequestThreadComments", posts[0])

    def test_mark_keeps_other_threads_not_posted(self):
        note = "## Replies as drafted, 2026-11-20 (not posted)\n\nThread 195: yes.\nThread 198: no.\n"
        new, changed = self.mod.mark_draft_posted(note, 195, "2026-11-21")
        self.assertTrue(changed)
        self.assertIn("(not posted; thread 195 posted 2026-11-21)", new)

    def test_brief_list_has_thread_keys(self):
        threads = self.mod.summarize([{"id": 195, "status": 1, "threadContext": {"filePath": "/settings.json", "rightFileStart": {"line": 4}},
                                       "comments": [{"id": 1, "author": {"displayName": "person A"}, "content": "Which setting?"}]}])
        self.assertEqual(self.mod.brief_lines(threads), ["thread 195 | active | /settings.json:4 | person A | Which setting?"])

    def test_docs_one_card(self):
        offers = read(SK / "crav1-pr-status/references/offers.md")
        self.assertIn("Card: Post your reply in thread 195 and set it to fixed?", offers)
        self.assertIn("never `I'll resolve this thread`", offers)
        self.assertIn("ado_threads.py reply --pr <n> --thread <id> --file <draft file> --status fixed --note <PR note> --yes", offers)


class AnsweredPoint(unittest.TestCase):
    """Item 4: an answered status, in plain words."""

    def test_set_point_answered(self):
        mod = load(ADO, "ado_threads_t1199c")
        note = "## PR record\n\n- Point: settings.json:4 | waiting on you | you | thread 195; host active | Which setting → this one\n"
        new, line = mod.set_point(note, "195", "answered", None, "2026-11-20")
        self.assertEqual(line, "- Point: settings.json:4 | answered | you | thread 195; host active; answered 2026-11-20 | Which setting → this one")
        self.assertEqual(mod.status_words("answered"), "answered; no code change")
        self.assertIsNone(mod.set_point(note, "999", "answered", None, "2026-11-20")[1])
        self.assertIn("`answered` (1.199.0)", read(SK / "crav1-add-to-spec/references/pr-record.md"))


import subprocess

WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com"]


def git(repo, *args):
    return subprocess.run([*G, "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


class RecheckShapeAndYou(unittest.TestCase):
    """Item 3: one re-check shape, card before the ending, you for the signed-in user."""

    def test_run_ending_shape(self):
        text = read(ROOT / "docs/reference/run-ending.md")
        self.assertIn("Check PR 84 again after person A answers in thread 198:\n`/crav1-pr-status pr84 since-last`", text)
        self.assertIn("never carries a command", text)
        self.assertIn("the ending is printed once", text)

    def test_pr_status_output(self):
        out = read(SK / "crav1-pr-status/references/output.md")
        self.assertIn("A Waiting line never carries a command (1.199.0)", out)
        self.assertIn("`Waiting: you, to accept the settings answer in thread 195.`", out)
        self.assertNotIn("Waiting: /crav1-pr-status", out)
        self.assertIn("Ask it before the run ending (1.199.0)", read(SK / "crav1-pr-status/references/offers.md"))


class LighterRuns(unittest.TestCase):
    """Item 5: one merged-since-sync, brief thread list, open-pr early stop."""

    def test_docs(self):
        offers = read(SK / "crav1-pr-status/references/offers.md")
        self.assertIn("Run it once per run and read its short `line`", offers)
        self.assertIn("runs only when this pull request closes a task", offers)
        self.assertIn("ado_threads.py list --pr <n> --brief", read(SK / "crav1-add-to-spec/references/pr-threads.md"))
        existing = read(SK / "crav1-open-pr/references/existing-pr.md")
        self.assertIn("stop after that one host read", existing)
        self.assertIn("`/crav1-pr-status pr84`", existing)


class CommitPush(unittest.TestCase):
    """Item 6: commit-push takes one yes; the Uncommitted line has a code span."""

    def test_word_and_rules(self):
        skill = read(SK / "crav1-finalize-commit/SKILL.md")
        self.assertIn("`commit-push`", skill)
        self.assertIn("Push only on `commit-push`", skill)
        self.assertIn("5b. **Push on `commit-push` (1.199.0).**", read(SK / "crav1-finalize-commit/references/commit.md"))
        self.assertIn("`commit-push` is `commit-now`, then one plain `git push`", read(SK / "crav1-finalize-commit/references/choice-words.md"))
        self.assertIn("commit with `/crav1-finalize-commit` when ready.", read(ROOT / "docs/reference/run-ending.md"))


class BuildQueue(unittest.TestCase):
    """Item 7: shared plan-step descriptions, pipeline triggers, unlisted-branch drift."""

    def test_a_shared_step_description_is_not_repeated(self):
        bm = load(SK / "crav1-tasks-ready-to-build/scripts/build_map.py", "build_map_t1199")
        plan = "# Plan\n\n## Approach\n\n1. Separate keys. Each store gets its own key. (T1, T2)\n"
        tasks = ("- [ ] T1: Separate keys for orders (branch: feat/orders-keys)\n"
                 "- [ ] T2: Separate keys for billing (branch: feat/billing-keys)\n")
        built = bm.build("orders-api", "# Orders\n", plan, tasks)
        branches = built.get("branches") or []
        self.assertEqual(len(branches), 2)
        # Before 1.199.0 both said "Separate keys. Each store gets its own key."
        self.assertEqual([b.get("about") for b in branches], ["", ""])

    def test_b_pipeline_trigger(self):
        mod = load(SK / "crav1-merge-pr/scripts/pipeline_trigger.py", "pipeline_trigger_t1199")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "azure-pipelines.yml").write_text(
                "trigger:\n  branches:\n    include:\n      - main\n  paths:\n    include:\n      - src/orders\nsteps:\n  - script: echo\n", encoding="utf-8")
            self.assertEqual(mod.check(repo, "develop")["triggered"], [])
            self.assertEqual(len(mod.check(repo, "main", ["src/orders/api.py"])["triggered"]), 1)
            self.assertEqual(mod.check(repo, "main", ["docs/readme.md"])["triggered"], [])
            (repo / "azure-pipelines.yml").write_text("trigger: none\nsteps:\n  - script: echo\n", encoding="utf-8")
            self.assertIsNone(mod.check(repo, "main")["line"])
            wf = repo / ".github/workflows"
            wf.mkdir(parents=True)
            (wf / "deploy.yml").write_text("on:\n  push:\n    branches: [develop]\njobs: {}\n", encoding="utf-8")
            self.assertIn("deploy.yml", mod.check(repo, "develop")["line"])
        self.assertIn("never that a deploy starts", read(SK / "crav1-build-walk/references/common.md"))

    def test_c_unlisted_branch_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "code"
            repo.mkdir()
            subprocess.run([*G, "init", "-q", "-b", "develop", str(repo)], check=True)
            (repo / "src/orders").mkdir(parents=True)
            (repo / "src/orders/api.py").write_text("a = 1\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "start")
            base = git(repo, "rev-parse", "--short", "HEAD")
            git(repo, "checkout", "-qb", "feat/orders-x")
            git(repo, "checkout", "-q", "develop")
            git(repo, "checkout", "-qb", "feat/other")
            (repo / "src/orders/api.py").write_text("a = 2\n")
            git(repo, "commit", "-qam", "other team change")
            git(repo, "checkout", "-q", "develop")
            git(repo, "merge", "-q", "--no-ff", "feat/other", "-m", "Merge branch 'feat/other'")
            git(repo, "checkout", "-q", "feat/orders-x")
            git(repo, "merge", "-q", "--no-ff", "develop", "-m", "Merge develop into feat/orders-x")
            spec_dir = Path(tmp) / "docs/specs/orders-api"
            spec_dir.mkdir(parents=True)
            (spec_dir / "spec.md").write_text(f"# Orders\n\nSynced at: feat/orders-x@{base}\n\n## In the code\n\n- `src/orders/api.py`\n",
                                             encoding="utf-8")
            proc = subprocess.run([sys.executable, str(WALK), "code-drift", "--root", str(spec_dir), "--code-repo", str(repo),
                                   "--base", "develop", "--no-fetch"], capture_output=True, text=True)
            out = json.loads(proc.stdout or proc.stderr)
        self.assertTrue(out.get("behind"), out)
        self.assertTrue(out.get("unlisted"), out)
        self.assertIn("come from a branch the spec does not list", out["background"])
