"""1.177.0: a bare pull request number is resolved from the kit's records
first, only the resolved host's CLI is named, and the PR skills end with
Run next instead of a `Next:` line."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
PR_COMMON = SK / "crav1-open-pr/scripts/pr_common.py"
PR_SKILLS = ("crav1-open-pr", "crav1-pr-status", "crav1-review-pr", "crav1-merge-pr")
sys.dont_write_bytecode = True


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pc = load(PR_COMMON, "pr_common_1177")
lint = load(ROOT / "scripts/kit-lint.py", "kit_lint_1177")

ADO_PR = "https://dev.azure.com/contoso/Orders/_git/orders-api/pullrequest/82"
ADO_PR_OTHER = "https://dev.azure.com/contoso/Orders/_git/orders-web/pullrequest/82"
GH_REMOTE = "https://github.com/contoso/orders-specs.git"
GH_PR = "https://github.com/contoso/orders-specs/pull/82"


def make_specs(root: Path, progress_url: str | None = ADO_PR) -> Path:
    slug = root / "docs/specs/orders-retry"
    (slug / "build-progress").mkdir(parents=True)
    if progress_url:
        (slug / "build-progress/feat-orders-queue.md").write_text(
            "# Build progress\n\nWalk: build-walk\nBranch: feat/orders-queue\nOwner: person B\n"
            f"PR: {progress_url}\nTasks: T9 Queue, T10 Retry\n",
            encoding="utf-8",
        )
    return root


class ResolveRefTest(unittest.TestCase):
    def test_bare_number_forms_parse(self):
        for ref in ("82", "pr82", "PR 82", "#82", "pr #82"):
            self.assertTrue(pc.NUMBER.match(ref), ref)
            self.assertEqual(int(pc.NUMBER.match(ref).group("n")), 82)
        self.assertIsNone(pc.NUMBER.match("feat/orders-queue"))

    def test_record_wins_over_github_remote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp))
            for ref in ("82", "pr82", "PR 82"):
                out = pc.resolve_ref(ref, GH_REMOTE, [root])
                self.assertEqual(out["status"], "ok", out)
                self.assertEqual(out["source"], "records")
                self.assertEqual(out["host"], "azure")
                self.assertEqual(out["tool"], "az")
                self.assertEqual(out["url"], ADO_PR)
                self.assertIn("use az", out["line"])
                self.assertNotIn("gh", out["line"])

    def test_merge_list_and_pr_note_are_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp), progress_url=None)
            (root / "docs/specs/orders-retry/build-map.md").write_text(
                f"Merge these PRs, in this order:\n1. PR 82 (person B): {ADO_PR}\n", encoding="utf-8")
            out = pc.resolve_ref("82", GH_REMOTE, [root])
            self.assertEqual((out["status"], out["url"]), ("ok", ADO_PR))
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp), progress_url=None)
            (root / "docs/system").mkdir(parents=True)
            (root / "docs/system/repos.md").write_text(
                "| Repo | Purpose | URL | Host |\n| --- | --- | --- | --- |\n"
                "| orders-api | code | https://dev.azure.com/contoso/Orders/_git/orders-api | azure |\n",
                encoding="utf-8")
            (root / "docs/notes/2026-11").mkdir(parents=True)
            (root / "docs/notes/2026-11/2026-11-12-pr-orders-api-82.md").write_text("# PR 82\n", encoding="utf-8")
            out = pc.resolve_ref("pr82", GH_REMOTE, [root])
            self.assertEqual(out["status"], "ok", out)
            self.assertEqual(out["url"], ADO_PR)
            self.assertIn("docs/notes/2026-11/2026-11-12-pr-orders-api-82.md", out["sources"])

    def test_same_pr_in_two_records_is_one_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp))
            (root / "docs/specs/orders-retry/walk-progress.md").write_text(f"Waiting: {ADO_PR}\n", encoding="utf-8")
            out = pc.resolve_ref("82", GH_REMOTE, [root])
            self.assertEqual(out["status"], "ok")
            self.assertEqual(len(out["sources"]), 2)

    def test_several_records_ask(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp))
            (root / "docs/specs/orders-retry/build-map.md").write_text(f"PR {ADO_PR_OTHER}\n", encoding="utf-8")
            out = pc.resolve_ref("82", GH_REMOTE, [root])
            self.assertEqual(out["status"], "ask")
            self.assertEqual({c["url"] for c in out["candidates"]}, {ADO_PR, ADO_PR_OTHER})
            self.assertIn("Ask which one", out["line"])

    def test_record_and_known_remote_pr_ask(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp))
            out = pc.resolve_ref("82", GH_REMOTE, [root], remote_has_pr=True)
            self.assertEqual(out["status"], "ask")
            self.assertEqual([c["url"] for c in out["candidates"]], [ADO_PR, GH_PR])

    def test_no_record_falls_back_to_remote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp), progress_url=None)
            out = pc.resolve_ref("82", GH_REMOTE, [root])
            self.assertEqual((out["status"], out["source"], out["tool"]), ("ok", "remote", "gh"))
            self.assertEqual(out["url"], GH_PR)
            out = pc.resolve_ref("82", "", [root])
            self.assertEqual(out["status"], "needs-remote")
            self.assertNotIn("install", out["line"])

    def test_full_url_names_its_host(self):
        out = pc.resolve_ref(ADO_PR, GH_REMOTE, [])
        self.assertEqual(out["source"], "url")
        self.assertEqual(out["tool"], "az")

    def test_cli_is_read_only_json_with_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_specs(Path(tmp))
            before = sorted(p.as_posix() for p in root.rglob("*"))
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", str(PR_COMMON), "resolve", "--ref", "pr82",
                 "--remote-url", GH_REMOTE, "--root", str(root)],
                capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = json.loads(proc.stdout)
            self.assertEqual(out["tool"], "az")
            self.assertTrue(out["line"])
            self.assertEqual(before, sorted(p.as_posix() for p in root.rglob("*")))

    def test_thin_copies_run_resolve(self):
        for skill in ("crav1-pr-status", "crav1-review-pr", "crav1-merge-pr"):
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", str(SK / skill / "scripts/pr_common.py"), "resolve",
                 "--ref", "82", "--remote-url", GH_REMOTE, "--root", str(ROOT / "nonexistent-root")],
                capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(json.loads(proc.stdout)["source"], "remote", skill)


class DocsTest(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_shared_steps_resolve_records_first(self):
        common = self.read("docs/reference/pr-common.md")
        self.assertIn("pr_common.py resolve --ref", common)
        self.assertIn("Never tell the user to install or sign in to `gh` unless", common)
        which = self.read(".cursor/skills/crav1/crav1-review-pr/references/which-pr.md")
        self.assertIn("resolved from the kit's records first", which)
        self.assertNotIn("A bare number needs that remote", which)
        for skill in ("crav1-open-pr", "crav1-pr-status", "crav1-merge-pr"):
            self.assertIn("resolve --ref", (SK / skill / "SKILL.md").read_text(encoding="utf-8"), skill)
        self.assertIn("pr_common.py resolve --ref", which)

    def test_no_next_rule_left(self):
        common = self.read("docs/reference/pr-common.md")
        self.assertNotIn("one `Next:` line", common)
        self.assertIn("never print a `Next:` line", common)
        ending = self.read("docs/reference/run-ending.md")
        self.assertNotIn("`Next:` is exactly one line.", ending)
        self.assertNotIn("Every other skill keeps one `Next:` line.", ending)

    def test_pr_skills_have_no_next_lines(self):
        bad = re.compile(r"^\s*Next:|`Next:\s*[^`]")
        for skill in PR_SKILLS:
            for path in sorted((SK / skill).rglob("*")):
                if path.suffix not in (".md", ".py") or "__pycache__" in path.parts:
                    continue
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertFalse(bad.search(line), f"{path.relative_to(ROOT)}:{i}: {line}")

    def test_no_install_gh_advice(self):
        for skill in PR_SKILLS:
            for path in sorted((SK / skill).rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("winget install GitHub.cli", text, path)


class LintTest(unittest.TestCase):
    def test_prose_next_rule(self):
        self.assertEqual(lint.prose_next_hits("Each ends with one `Next:` line, then Waiting."), [1])
        self.assertEqual(lint.prose_next_hits("Then print a Next: line."), [1])
        self.assertEqual(lint.prose_next_hits("The four never print a `Next:` line."), [])
        self.assertEqual(lint.prose_next_hits("Run next, no `Next:` line."), [])

    def test_kit_is_clean(self):
        self.assertEqual(lint.prose_next_problems(str(ROOT)), [])

    def test_pr_skills_are_run_next_only(self):
        for skill in PR_SKILLS:
            self.assertIn(skill, lint.RUN_NEXT_ONLY_SKILLS)


WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_review_batch_1176b as rb  # noqa: E402

wp = rb.wp
we = wp.ending_mod()
RESUME = wp._run_from_clause(
    "/crav1-tighten-and-plan-ready-to-build orders-api, because the walk resumes when the answers arrive.")


class OwnMergeFirst(unittest.TestCase):
    def test_label_names_yours_and_others(self):
        order = [{"pr": 71, "owner": "yours"}, {"pr": 73, "owner": "yours"}, {"pr": 82, "owner": "person B"}]
        self.assertEqual(wp.own_merge_entry(order),
                         "Merge your PRs 71 and 73 first:\n`/crav1-merge-pr 71`")
        order = [{"pr": 82, "owner": "person B"}, {"pr": 73, "owner": "yours"}]
        self.assertEqual(wp.own_merge_entry(order),
                         "Merge your PR 73 first:\n`/crav1-merge-pr 73`")

    def test_none_of_yours_adds_nothing(self):
        self.assertIsNone(wp.own_merge_entry([{"pr": 82, "owner": "person B"}]))
        self.assertIsNone(wp.own_merge_entry([]))

    def test_ready_check_leads_with_your_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = rb.ending(rb.two_pr_slice(tmp))
            entry = "Merge your PR 71 first:\n`/crav1-merge-pr 71`"
            self.assertIn(entry, text)
            self.assertLess(text.index(entry), text.index("Held:"))
            self.assertLess(text.index("Run next:"), text.index(entry))
            self.assertIn("Waiting: PR 82 is person B's; it unblocks T13.", text)

    def test_resume_stays_below_the_merge_entry(self):
        merge = wp.own_merge_entry([{"pr": 71, "owner": "yours"}, {"pr": 82, "owner": "person B"}])
        text = we.compose(run=[merge, RESUME])
        self.assertLess(text.index("/crav1-merge-pr 71"), text.index("Resume the walk when the answers arrive:"))


class PrOwnerIsWhoOpenedIt(unittest.TestCase):
    def test_pr_note_author_wins_over_the_claimer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = rb.two_pr_slice(tmp)
            notes = Path(tmp) / "specs/docs/notes/2026-11"
            notes.mkdir(parents=True)
            (notes / "2026-11-16-pr-orders-api-71.md").write_text(
                "---\nkind: pr\nauthor: person C\n---\n# PR 71\n", encoding="utf-8")
            self.assertEqual(wp.pr_author(root, 71), "person C")
            prs = wp.open_prs(root)
            self.assertEqual((prs[71]["owner"], prs[71]["added"]), ("person C", ["T5"]))
            text = rb.ending(root)
            self.assertIn("1. PR 71 (person C's, you added T5, feat/orders-readme): ticks T5", text)
            self.assertNotIn("Merge your PR", text)
            self.assertIn("Waiting: PR 71 is person C's; it unblocks T6.", text)

    def test_no_author_recorded_is_not_yours(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = rb.two_pr_slice(tmp)
            log = root / "build-progress/feat--orders-readme.md"
            log.write_text(log.read_text(encoding="utf-8").replace("PR author: person A\n", ""), encoding="utf-8")
            self.assertIsNone(wp.pr_author(root, 71))
            self.assertEqual(wp.open_prs(root)[71]["owner"], "owner not recorded")
            text = rb.ending(root)
            self.assertIn("1. PR 71 (owner not recorded, feat/orders-readme)", text)
            self.assertNotIn("Merge your PR", text)
            self.assertIn("Waiting: PR 71 (owner not recorded); it unblocks T6.", text)

    def test_waiting_groups_one_owner(self):
        order = [{"pr": 71, "owner": "person A", "ticks": ["T5"], "starts": []},
                 {"pr": 73, "owner": "person A", "ticks": ["T43"], "starts": ["T8"]},
                 {"pr": 74, "owner": "yours", "ticks": ["T2"], "starts": []}]
        self.assertEqual(wp.others_merge_waits(order), ["Waiting: PR 71 and PR 73 are person A's; they unblock T8."])


class BlankLineAfterMergeList(unittest.TestCase):
    def test_waiting_after_the_list_gets_a_blank_line(self):
        block = ("Merge these PRs, in this order:\n"
                 "1. PR 71 (yours, feat/orders-readme): ticks T5.\n"
                 "2. PR 82 (person B's, feat/orders-cicd): ticks T9 to T12.")
        text = we.compose(waiting=[block, "Waiting: answers from person C on Q2."])
        self.assertIn("ticks T9 to T12.\n\nWaiting: answers from person C on Q2.", text)

    def test_waiting_lines_stay_together(self):
        text = we.compose(waiting=["Waiting: PR 71 to merge.", "Waiting: answers on Q2."])
        self.assertIn("Waiting: PR 71 to merge.\nWaiting: answers on Q2.", text)


if __name__ == "__main__":
    unittest.main()
