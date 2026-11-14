"""1.158.0: open-pr, merge-pr, pr-status and review-pr share pr-common.md and pr_common.py."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
COMMON = ROOT / "docs/reference/pr-common.md"
SKILLS = ("crav1-open-pr", "crav1-merge-pr", "crav1-pr-status", "crav1-review-pr")
CAPS = {"crav1-open-pr": 1150, "crav1-merge-pr": 1150, "crav1-pr-status": 1150, "crav1-review-pr": 1275}
SCRIPT = SK / "crav1-open-pr/scripts/pr_common.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = load(SCRIPT, "pr_common_1158")


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def text(rel: str) -> str:
    return (SK / rel).read_text(encoding="utf-8")


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8")


class SharedPage(unittest.TestCase):
    def test_each_skill_points_at_the_shared_page_and_is_under_its_cap(self):
        for skill in SKILLS:
            body = text(f"{skill}/SKILL.md")
            self.assertIn("../crav1-docs/reference/pr-common.md", body, skill)
            n = words(SK / skill / "SKILL.md")
            self.assertLessEqual(n, CAPS[skill], f"{skill} is {n} words")
            self.assertGreaterEqual(n, 800, f"{skill} is {n} words; too thin to route")

    def test_page_ships_next_to_the_skills(self):
        self.assertTrue(COMMON.is_file())
        for tree in (SK, ROOT / "plugins/crav1/skills", ROOT / ".claude/skills"):
            copy = tree / "crav1-docs/reference/pr-common.md"
            self.assertEqual(copy.read_text(encoding="utf-8"), COMMON.read_text(encoding="utf-8"), str(copy))

    def test_page_keeps_the_shared_rules(self):
        page = COMMON.read_text(encoding="utf-8")
        for needle in (
            "A branch name is not a pull request. Do not pick the newest pull request for the current branch.",
            "Remote: the single `git remote`. If several remotes exist, ask which one.",
            "GitHub `gh`, then Azure DevOps `az`",
            "Try `git`, then `C:\\Program Files\\Git\\cmd\\git.exe`.",
            "Anything else: stop and say the state. Do not reopen it.",
            "Never suggest a rebase, `pull --rebase`, or a force-push.",
            "They never write, clear, commit or push `claims.md`.",
            "Never print, echo, store, or create a token.",
            "When this page and a skill's own rule differ, the skill's rule wins for that skill.",
        ):
            self.assertIn(needle, page)

    def test_each_skill_ships_the_script(self):
        for skill in SKILLS:
            for tree in (SK, ROOT / "plugins/crav1/skills", ROOT / ".claude/skills"):
                self.assertTrue((tree / skill / "scripts/pr_common.py").is_file(), f"{tree}/{skill}")
            out = run(SK / skill / "scripts/pr_common.py", "--help")
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("parse", out.stdout)
        kit = run(ROOT / "scripts/pr-common.py", "host", "--remote-url", "https://github.com/acme/orders-api.git")
        self.assertEqual(json.loads(kit.stdout)["host"], "github")


class Script(unittest.TestCase):
    def test_parse_github_azure_and_a_bare_number(self):
        gh = pc.parse_ref("https://github.com/acme/orders-api/pull/71")
        self.assertEqual((gh["host"], gh["number"], gh["status"]), ("github", 71, "ok"))
        az = pc.parse_ref("https://dev.azure.com/acme/shop/_git/orders-api/pullrequest/12")
        self.assertEqual((az["host"], az["org"], az["repo"], az["number"]), ("azure", "acme", "orders-api", 12))
        vs = pc.parse_ref("https://acme.visualstudio.com/shop/_git/orders-api/pullrequest/12",
                          "https://acme@dev.azure.com/acme/shop/_git/orders-api")
        self.assertEqual(vs["status"], "ok")
        bare = pc.parse_ref("#5", "git@github.com:acme/orders-api.git")
        self.assertEqual((bare["host"], bare["number"]), ("github", 5))
        self.assertEqual(pc.parse_ref("5")["status"], "needs-remote")

    def test_a_branch_is_not_a_pull_request_and_a_mismatch_stops(self):
        self.assertEqual(pc.parse_ref("feat/orders-retry")["status"], "not-a-pr")
        other = pc.parse_ref("https://github.com/acme/billing-api/pull/3", "https://github.com/acme/orders-api.git")
        self.assertEqual(other["status"], "mismatch")
        self.assertIn("do not act across that mismatch", other["line"])

    def test_find_never_picks_the_newest(self):
        one = pc.summarize_find([{"number": 7, "url": "u7", "headRefName": "feat/x", "baseRefName": "develop"}], "feat/x", None)
        self.assertEqual(one["pick"], 7)
        two = pc.summarize_find([
            {"number": 7, "headRefName": "feat/x", "baseRefName": "develop"},
            {"number": 9, "headRefName": "feat/x", "baseRefName": "main"},
        ], "feat/x", None)
        self.assertIsNone(two["pick"])
        self.assertIn("Do not pick the newest", two["line"])
        based = pc.summarize_find([
            {"pullRequestId": 7, "sourceRefName": "refs/heads/feat/x", "targetRefName": "refs/heads/develop"},
            {"pullRequestId": 9, "sourceRefName": "refs/heads/feat/x", "targetRefName": "refs/heads/main"},
        ], "feat/x", "main")
        self.assertEqual(based["pick"], 9)

    def test_find_from_a_saved_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "list.json"
            path.write_text(json.dumps({"value": []}), encoding="utf-8")
            out = run(SCRIPT, "find", "--branch", "feat/x", "--from-json", str(path))
            self.assertEqual(json.loads(out.stdout)["matches"], [])

    def test_checks_summary_and_merge_in_advice(self):
        green = pc.summarize_checks({"state": "OPEN", "statusCheckRollup": [{"name": "lint", "conclusion": "SUCCESS"}]})
        self.assertEqual((green["passing"], green["blocked"]), (["lint"], []))
        red = pc.summarize_checks({
            "state": "OPEN", "isDraft": True, "mergeStateStatus": "BEHIND", "baseRefName": "develop", "headRefName": "feat/x",
            "statusCheckRollup": [{"name": "tests", "conclusion": "FAILURE"}, {"name": "scan", "status": "IN_PROGRESS"}],
        })
        self.assertEqual((red["failing"], red["pending"], red["draft"]), (["tests"], ["scan"], True))
        behind = [b for b in red["blocked"] if b.startswith("behind")][0]
        self.assertIn("Merge develop into feat/x", behind)
        self.assertIn("Never rebase.", behind)
        merged = pc.summarize_checks({"status": "completed", "policies": [{"status": "approved", "configuration": {"type": {"displayName": "Build"}}}]})
        self.assertEqual(merged["state"], "MERGED")
        self.assertIn("state is MERGED", merged["blocked"])

    def test_claim_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            claims = Path(tmp) / "claims.md"
            body = "# Claims\n\nIn progress: feat/orders-cicd, T2, T3, person A, since 2026-11-14T09:00:00+01:00\n"
            claims.write_text(body, encoding="utf-8")
            before = claims.stat().st_mtime_ns
            out = json.loads(run(SCRIPT, "claim", "--root", tmp, "--branch", "feat/orders-cicd").stdout)
            self.assertEqual(out["claims"][0]["tasks"], ["T2", "T3"])
            self.assertEqual(claims.read_text(encoding="utf-8"), body)
            self.assertEqual(claims.stat().st_mtime_ns, before)
            none = json.loads(run(SCRIPT, "claim", "--root", tmp, "--branch", "feat/other").stdout)
            self.assertEqual(none["claims"], [])

    def test_behind_counts_and_advises_a_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@example.com",
                       GIT_COMMITTER_NAME="a", GIT_COMMITTER_EMAIL="a@example.com")
            git = lambda *a: subprocess.run(["git", *a], cwd=tmp, env=env, check=True, capture_output=True)
            git("init", "-q", "-b", "main")
            git("commit", "-q", "--allow-empty", "-m", "one")
            git("checkout", "-q", "-b", "feat/x")
            git("commit", "-q", "--allow-empty", "-m", "mine")
            git("checkout", "-q", "main")
            git("commit", "-q", "--allow-empty", "-m", "two")
            out = json.loads(run(SCRIPT, "behind", "--head", "feat/x", "--base", "main", "--repo", tmp).stdout)
            self.assertEqual((out["behind"], out["ahead"]), (1, 1))
            self.assertIn("git merge main", out["advice"])
            self.assertNotIn("rebase main", out["advice"].lower())

    def test_script_never_writes_or_pushes(self):
        src = SCRIPT.read_text(encoding="utf-8")
        for banned in ('"push"', '"merge",', "write_text", '"complete"', "--status completed", "pr merge", "az login", "--squash"):
            self.assertNotIn(banned, src)


class MergeStaysTheSame(unittest.TestCase):
    """The yes gate, the merge method, the claim rule and the walk ending are word for word."""

    SKILL = SK / "crav1-merge-pr/SKILL.md"

    def body(self) -> str:
        return self.SKILL.read_text(encoding="utf-8")

    def test_yes_gate(self):
        b = self.body()
        for needle in (
            "Run it only when **this turn** explicitly asks to merge a specific pull request, named by number or URL.",
            "`/crav1-open-pr`, a build-tasks loop, `/crav1-review-pr`, or an earlier turn naming a URL is not that ask.",
            "If this turn does not name a pull request, ask which one. That turn is the question only. No merge.",
            "- No merge unless this turn names the pull request and asks to merge it.",
            "A yes on `/crav1-build-walk`'s card that names this pull request is the ask in this turn.",
            "disable-model-invocation: true",
        ):
            self.assertIn(needle, b)

    def test_merge_method(self):
        b = self.body()
        for needle in (
            "Merge **one** named pull request with a **merge commit**, then stop. Never squash. Never rebase.",
            "Strategy: merge commit (GitHub --merge; Azure Repos noFastForward via --squash false). Not squash. Not rebase.",
            "gh pr merge <n-or-url> --merge",
            "Do not pass `--squash`, `--rebase`, `--admin`, `--auto`, or `--delete-branch`.",
            "gh pr view <n-or-url> --json state,mergeCommit --jq .mergeCommit.oid",
            "If merge fails, show the error and the GitHub fallback. Do not retry with another strategy. Do not claim a merge.",
            "- No squash (`--squash true`, squash merge, `mergeStrategy` `squash`). Azure DevOps complete uses `--squash false`, which is the no-fast-forward merge commit.",
            "- No rebase (`--rebase`, rebase and fast-forward, semi-linear / `rebaseMerge`).",
            "- No `--admin`, no `--bypass-policy`, no `bypassPolicy`.",
            "- No second strategy attempt after a refusal or a failed `az repos pr update`.",
            "Do not claim the pull request was merged unless that path returned a merge commit hash.",
            "- Do not claim a no-fast-forward merge unless the parent count was verified as two.",
            "GitHub: `gh pr ready <n-or-url>`. That is the whole ready step. Do not pass extra flags.",
        ):
            self.assertIn(needle, b)
        az = text("crav1-merge-pr/references/azure-devops.md")
        self.assertIn("az repos pr update --org <org-url> --id <n> --draft false --detect false --output json", az)
        self.assertIn("Do not complete while the checks are queued.", az)

    def test_ready_gate_and_anyway(self):
        b = self.body()
        self.assertIn('Read `references/pr-record-gate.md` ("The Ready line") before **Show, then merge**, every run.', b)
        self.assertIn("`anyway` never skips a required check, policy or review.", b)
        self.assertIn("- Not ready: `anyway` (1.97.0; merge although the PR record says `Ready: no`; host checks still apply).", b)
        self.assertIn("Required checks, branch policies, and reviews must pass. If anything blocks, stop and report what. Do not merge.", b)

    def test_claims_are_never_touched(self):
        b = self.body()
        self.assertIn("This skill never writes, clears, commits or pushes `claims.md`.", b)
        self.assertIn("The only file this skill writes is the PR note with its PR record", b)
        self.assertNotIn("claims.py", b)
        for ref in (SK / "crav1-merge-pr/references").glob("*.md"):
            self.assertNotIn("claims.py", ref.read_text(encoding="utf-8"), ref.name)

    def test_walk_ending(self):
        b = self.body()
        self.assertIn("- When `/crav1-build-walk` opened this file, do not print a line of your own for what to run next. The walk prints its one line (1.142.0).", b)
        self.assertIn("End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.", b)

    def test_moved_host_and_read_steps(self):
        gh = text("crav1-merge-pr/references/github.md")
        self.assertIn("Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub", gh)
        self.assertIn("gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,isDraft,baseRefName,headRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup", gh)
        self.assertIn('Read `references/github.md` ("GitHub (Host)")', self.body())


class MovedWordForWord(unittest.TestCase):
    def test_moved_sections(self):
        cases = (
            ("crav1-open-pr/references/checks.md", "| Dirty tree | `git status --porcelain`, ignoring `agent-tools/`. Point them at `/crav1-finalize-commit`. This skill does not commit. |"),
            ("crav1-open-pr/references/checks.md", "Do not treat a missing ref as “zero commits ahead.”"),
            ("crav1-open-pr/references/github.md", "gh pr create --base <base> --head <head> --title <title> --body <body>"),
            ("crav1-open-pr/references/host.md", "Quote every `--query` value (`--query \"value[].pullRequestId\"`)."),
            ("crav1-pr-status/references/classify.md", "| `waiting on <name>` | The last message asks that person or hands them the next step. |"),
            ("crav1-pr-status/references/classify.md", "is flagged `resolved, code unchanged`"),
            ("crav1-pr-status/references/output.md", "11. `PR record: <repo>: <path>`, as a code span."),
            ("crav1-pr-status/references/offers.md", "Never several threads on one yes."),
            ("crav1-review-pr/references/ship.md", "The kit record ends with `Next, after this pull request merges: /crav1-refresh-system-notes"),
        )
        for rel, needle in cases:
            self.assertIn(needle, text(rel), rel)

    def test_every_skill_keeps_its_own_never_rules(self):
        self.assertIn("Never `--force`, `--force-with-lease`, `--force-if-includes`", text("crav1-open-pr/SKILL.md"))
        self.assertIn("- No rebase advice; suggest merging the base into the branch.", text("crav1-pr-status/SKILL.md"))
        self.assertIn("- Suggest merging `<base>` into the branch, never a rebase, `pull --rebase`, or a force-push.", text("crav1-review-pr/SKILL.md"))
        self.assertIn("Never guess `done`: no commit, no `done`.", text("crav1-pr-status/SKILL.md"))


if __name__ == "__main__":
    unittest.main()
