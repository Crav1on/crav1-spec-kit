"""1.195.0: per-branch base, unrecorded-only drift, docx import, later_for, batch caps.

Generic fixtures only (orders-api, contoso, person A).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
MSS = SK / "crav1-add-to-spec/scripts/merged_since_sync.py"
DOCX = SK / "crav1-add-to-spec/scripts/docx_to_md.py"
NOTES = SK / "crav1-add-to-spec/scripts/notes_index.py"
PLAN = SK / "crav1-tighten-plan/scripts/plan_check.py"
GIT = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com"]


def py(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False)


def js(script: Path, *args: str) -> dict:
    proc = py(script, *args)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc


def read(rel: str) -> str:
    return (SK / rel).read_text(encoding="utf-8")


class Repo:
    def __init__(self, base: str):
        self.path = Path(tempfile.mkdtemp()) / "orders-api"
        self.path.mkdir()
        subprocess.run(["git", "init", "-q", "-b", base, str(self.path)], check=True)

    def git(self, *args: str) -> str:
        return subprocess.run(GIT + ["-C", str(self.path), *args], capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, name: str) -> str:
        (self.path / f"{name}.py").write_text(name + "\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", name)
        return self.git("rev-parse", "--short=7", "HEAD")


class PerBranchBase(unittest.TestCase):
    """M1: a repo whose work branches merge into develop, with main also present."""

    def setUp(self):
        self.repo = Repo("main")
        self.repo.commit("base")
        self.repo.git("checkout", "-q", "-b", "develop")
        self.dev_before = self.repo.commit("dev1")
        self.repo.git("checkout", "-q", "-b", "feat/orders-retry")
        self.recorded = self.repo.commit("retry1")
        self.repo.commit("retry2")
        self.repo.git("checkout", "-q", "develop")
        self.repo.git("merge", "-q", "--no-ff", "feat/orders-retry", "-m", "Merge pull request #74 from contoso/feat/orders-retry")
        self.merge = self.repo.git("rev-parse", "--short=7", "HEAD")
        self.repo.git("checkout", "-q", "main")
        self.tmp = Path(tempfile.mkdtemp())
        self.spec = self.tmp / "spec.md"

    def write(self, *lines: str) -> None:
        self.spec.write_text("# Orders API\n" + "".join(l + "\n" for l in lines) + "\n## Problem\n", encoding="utf-8")

    def test_repos_md_merges_into_develop(self):
        repos = self.tmp / "repos.md"
        repos.write_text("| Repo | Merges into |\n| --- | --- |\n| orders-api | develop |\n", encoding="utf-8")
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        out = js(MSS, "check", "--spec", str(self.spec), "--code-repo", str(self.repo.path), "--repos", str(repos))
        self.assertEqual(out["offer"], "take-in", out)
        self.assertEqual(out["branches"][0]["base"], "develop")
        self.assertEqual(out["branches"][0]["base_from"], "repos.md Merges into")
        self.assertIn(f"PR 74 merged at {self.merge} with 1 commit", out["question"])

    def test_synced_at_base_line_names_develop(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18",
                   f"Synced at: orders-api develop@{self.dev_before}, 2026-11-18")
        out = js(MSS, "check", "--spec", str(self.spec), "--code-repo", str(self.repo.path),
                 "--repos", str(self.tmp / "none.md"))
        self.assertEqual(out["offer"], "take-in", out)
        self.assertEqual(out["branches"][0]["base_from"], "Synced at")

    def test_base_flag_wins(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        out = js(MSS, "check", "--spec", str(self.spec), "--code-repo", str(self.repo.path), "--base", "develop")
        self.assertEqual(out["branches"][0]["base_from"], "--base")
        self.assertEqual(out["offer"], "take-in")

    def test_main_as_base_sees_not_merged(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        out = js(MSS, "check", "--spec", str(self.spec), "--code-repo", str(self.repo.path), "--base", "main")
        self.assertEqual(out["status"], "not-merged")

    def test_callers_pass_base(self):
        for rel in ("crav1-tighten-and-plan-ready-to-build/references/steps.md", "crav1-pr-status/references/offers.md",
                    "crav1-update-specs-from-changes-and-prs/references/manual-flow.md",
                    "crav1-update-specs-from-changes-and-prs/references/auto-flow.md",
                    "crav1-merge-pr/references/after-merge.md", "crav1-build-walk/references/sync.md"):
            text = read(rel)
            self.assertIn("--base <Merges into>", text, rel)
            self.assertIn("found per branch", text, rel)
            self.assertNotIn("as `design_run.py` finds it, or `--base`", text, rel)


class UnrecordedDrift(unittest.TestCase):
    """M3: only commits the spec and notes have not recorded count; base merge-ins are left out."""

    def test_counts_only_new_commits(self):
        repo = Repo("develop")
        repo.commit("base")
        repo.git("checkout", "-q", "-b", "feat/orders-retry")
        first = repo.commit("retry1")
        noted = repo.commit("retry2")
        repo.git("checkout", "-q", "develop")
        repo.commit("dev-other")
        repo.git("checkout", "-q", "feat/orders-retry")
        repo.git("merge", "-q", "--no-ff", "develop", "-m", "Merge develop")
        new = repo.commit("retry3")
        docs = Path(tempfile.mkdtemp()) / "docs"
        root = docs / "specs" / "orders-api"
        root.mkdir(parents=True)
        (root / "spec.md").write_text(f"# Orders API\nSynced at: orders-api feat/orders-retry@{first}, 2026-11-18\n\n## Problem\n",
                                      encoding="utf-8")
        (root / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (root / "tasks.md").write_text("# Tasks\n\n- [ ] T1 Record the lane (after: )\n", encoding="utf-8")
        (docs / "notes" / "2026-11").mkdir(parents=True)
        (docs / "notes" / "2026-11" / "2026-11-18-retry.md").write_text(
            f"---\ntitle: Retry\nkind: code change\ncommits: [{noted}]\nused_by: [orders-api]\n---\n# Retry\n", encoding="utf-8")
        out = js(WALK, "code-drift", "--root", str(root), "--code-repo", str(repo.path), "--base", "develop")
        self.assertTrue(out["behind"], out)
        b = out["drift"][0]
        self.assertEqual(b["count"], 1)
        self.assertEqual(b["already_recorded"], 1)
        self.assertGreaterEqual(b["base_merge_ins"], 1)
        self.assertGreater(b["total"], b["count"])
        self.assertTrue(any(c.startswith(new) or new.startswith(c[:7]) for c in json.dumps(b["commits"]).split('"') if c), b)


class StaleSeen(unittest.TestCase):
    """M2: code drift runs at the walk start; a stale walk recommends rerun on reopen cards."""

    def test_card_recommends_rerun_when_stale(self):
        sys.path.insert(0, str(WALK.parent))
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("walk_progress_t1195", WALK)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            sys.path.pop(0)
        calm = mod.reopen_card("review-and-tighten-plan", ["tasks"], False)
        self.assertIn("(Recommended)", calm["options"][0]["label"])
        self.assertEqual(calm["options"][0]["id"], "nothing new")
        stale = mod.reopen_card("review-and-tighten-plan", ["tasks"], False, True)
        self.assertEqual(stale["options"][0]["id"], "rerun")
        self.assertIn("(Recommended)", stale["options"][0]["label"])
        self.assertNotIn("(Recommended)", stale["options"][1]["label"])

    def test_steps_run_drift_at_the_start(self):
        text = read("crav1-tighten-and-plan-ready-to-build/references/steps.md")
        start = text.index("**Code drift at the start (1.195.0).**")
        self.assertLess(start, text.index("**Spec behind the code first (1.194.0).**"))
        self.assertIn("--stale-seen", text)
        self.assertIn("again as a recheck", text)
        self.assertIn("--stale-seen", read("crav1-tighten-and-plan-ready-to-build/references/progress.md"))


def make_docx(path: Path) -> None:
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    body = (
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Orders sync</w:t></w:r></w:p>'
        '<w:p><w:r><w:t xml:space="preserve">Person A said the </w:t></w:r>'
        '<w:r><w:rPr><w:b/></w:rPr><w:t>retry limit</w:t></w:r><w:r><w:t xml:space="preserve"> is three.</w:t></w:r></w:p>'
        '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t>Move DEV first</w:t></w:r></w:p>'
        '<w:p><w:pPr><w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t>then TEST</w:t></w:r></w:p>'
    )
    core = ('<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dcterms="http://purl.org/dc/terms/"><dcterms:created>2026-11-19T09:00:00Z</dcterms:created></cp:coreProperties>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", f'<?xml version="1.0"?><w:document {w}><w:body>{body}</w:body></w:document>')
        z.writestr("docProps/core.xml", core)


class DocxToMd(unittest.TestCase):
    """A6: docx to Markdown, word for word, no network."""

    def test_convert_and_check(self):
        tmp = Path(tempfile.mkdtemp())
        doc = tmp / "minutes.docx"
        make_docx(doc)
        out = js(DOCX, "convert", "--docx", str(doc))
        md = out["markdown"]
        self.assertEqual(out["created"], "2026-11-19T09:00:00Z")
        self.assertIn("# Orders sync", md)
        self.assertIn("Person A said the **retry limit** is three.", md)
        self.assertIn("\n- Move DEV first", md)
        self.assertIn("\n  - then TEST", md)
        target = tmp / "transcript.md"
        js(DOCX, "convert", "--docx", str(doc), "--out", str(target))
        self.assertEqual(target.read_text(encoding="utf-8"), md)
        same = js(DOCX, "check", "--docx", str(doc), "--md", str(target))
        self.assertTrue(same["same"])
        target.write_text(md.replace("three", "four"), encoding="utf-8")
        proc = py(DOCX, "check", "--docx", str(doc), "--md", str(target))
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(json.loads(proc.stdout)["same"])

    def test_bad_file_is_reported(self):
        bad = Path(tempfile.mkdtemp()) / "x.docx"
        bad.write_text("not a zip", encoding="utf-8")
        proc = py(DOCX, "convert", "--docx", str(bad))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Not a readable .docx", proc.stdout)

    def test_named_in_sources_binary_and_meeting_branch(self):
        self.assertIn("scripts/docx_to_md.py", read("crav1-add-to-spec/references/sources-binary.md"))
        self.assertIn("scripts/docx_to_md.py", read("crav1-add-to-spec/branches/meeting/BRANCH.md"))
        self.assertNotIn("urllib", (DOCX).read_text(encoding="utf-8"))


class SaveForLater(unittest.TestCase):
    """A2-A4: save for later writes later_for; waiting_for stays for parked specs; one batch rule."""

    def test_later_lists_notes(self):
        root = Path(tempfile.mkdtemp())
        month = root / "docs" / "notes" / "2026-11"
        month.mkdir(parents=True)
        (month / "2026-11-19-team-call.md").write_text(
            "---\ntitle: Team call\nkind: meeting\nsource_date: 2026-11-19\nused_by: []\nlater_for: [orders-api, general]\n---\n# Team call\n",
            encoding="utf-8")
        out = py(NOTES, "later", "--slug", "orders-api", "--root", str(root)).stdout
        self.assertIn("Saved for later on orders-api: 1", out)
        self.assertIn("Team call", out)
        self.assertIn("Saved for later on general: 1", py(NOTES, "later", "--slug", "general", "--root", str(root)).stdout)
        self.assertIn("Saved for later on orders-export: 0", py(NOTES, "later", "--slug", "orders-export", "--root", str(root)).stdout)

    def test_one_batch_rule_and_options(self):
        text = read("crav1-add-to-spec/branches/meeting/references/one-batch.md")
        self.assertIn("**One to four items:** one questions call, one question per item.", text)
        self.assertIn("**More than four items:** always the batch card", text)
        self.assertIn("### Save for later", text)
        self.assertIn("later_for: [general]", text)
        self.assertIn("Never put it in `waiting_for`", text)
        self.assertNotIn("Ask about every item in one questions call, one question per item;", text)

    def test_recap_counts_saved_not_noted(self):
        text = read("crav1-add-to-spec/branches/meeting/references/after-the-list.md")
        self.assertNotIn("Noted: <n>", text)
        self.assertIn("Saved for later: <n>", text)
        self.assertIn("There is no Noted count", text)

    def test_readers_show_later_for(self):
        for rel in ("crav1-help/references/modes.md", "crav1-retire-spec/branches/park/BRANCH.md",
                    "crav1-show-or-ask-open-questions/references/asked.md", "crav1-tighten-spec/SKILL.md",
                    "crav1-add-to-spec/references/notes.md"):
            self.assertIn("later_for", read(rel), rel)
        self.assertIn("note-later-for", (ROOT / "docs/reference/marks.yaml").read_text(encoding="utf-8"))


class Endings(unittest.TestCase):
    """A1 and A5: Run next lists every changed spec; finalize-commit examples carry a reason line."""

    def test_meeting_ending_names_every_spec_and_the_walk(self):
        text = read("crav1-add-to-spec/branches/meeting/references/after-the-list.md")
        self.assertIn("The new information reopened the walk.", text)
        self.assertIn("Resume the spec walk:", text)
        self.assertIn("`/crav1-tighten-and-plan-ready-to-build orders-api`", text)
        self.assertIn("Also changed, not tightened: orders-export.", text)
        self.assertIn("Every changed spec is named", text)
        stop = read("crav1-add-to-spec/references/stop.md")
        self.assertIn("Resume the spec walk:", stop)
        self.assertIn("tighten-and-plan-ready-to-build", read("crav1-add-to-spec/references/fact.md"))

    def test_commit_examples_have_reasons(self):
        text = read("crav1-finalize-commit/references/commit.md")
        for reason, label in (("The commit is only local.", "Push the specs repo:"),
                              ("The build walk on this branch is not finished.", "Continue the build walk"),
                              ("The commit is only local and no pull request is open.", "Push and open the pull request:"),
                              ("PR <n> does not have this commit yet.", "Push to PR <n> and comment:")):
            self.assertIn(f"Run next:\n   {reason}\n\n   {label}", text)


class TightenRules(unittest.TestCase):
    """M4, M5, M6."""

    def test_whether_findings_recommend_ask_or_keep(self):
        skill = read("crav1-tighten-spec/SKILL.md")
        cat = read("crav1-tighten-spec/references/catalog.md")
        self.assertIn("the recommended option is `ask`", skill)
        self.assertIn("that patch is never the recommended option", skill)
        self.assertIn("always lists `ask` or `keep`", skill)
        self.assertIn("is never the recommended option", cat)

    def test_one_owner_for_acceptance_ticks(self):
        self.assertIn("`tick-from-verify`", read("crav1-tighten-spec/references/catalog.md"))
        self.assertIn("Never tick a spec acceptance box", read("crav1-tighten-spec/SKILL.md"))
        self.assertIn("never ticks an acceptance box", read("crav1-verify-build-against-spec/references/tick-pending.md"))

    def items(self, n: int, task_ids=()):
        rows = [{"id": f"P{i}", "issue": f"issue {i}", "tag": "plan", "status": "open",
                 "options": "A fix; keep", "recommendation": "A fix"} for i in range(1, n + 1)]
        for r in rows:
            if r["id"] in task_ids:
                r["changes_tasks"] = True
        path = Path(tempfile.mkdtemp()) / "items.json"
        path.write_text(json.dumps(rows), encoding="utf-8")
        return str(path)

    def test_batch_caps_at_eight_and_keeps_task_changes_out(self):
        out = py(PLAN, "batch", "--items", self.items(12, {"P5"})).stdout
        card = [l for l in out.splitlines() if l.startswith("Card:")][0]
        self.assertNotIn("P5 ", card)
        self.assertIn("P9 ", card)
        self.assertNotIn("P10 ", card)
        self.assertIn("each gets its own card (adds, removes or reorders tasks): P5.", out)
        self.assertIn("in the next card: P10, P11, P12.", out)

    def test_only_task_changes_get_no_card(self):
        out = py(PLAN, "batch", "--items", self.items(2, {"P1", "P2"})).stdout
        self.assertNotIn("Card:", out)
        self.assertIn("P1, P2", out)

    def test_skill_points_at_the_cap(self):
        self.assertIn("Batch cap: 8", read("crav1-tighten-plan/SKILL.md"))
        self.assertIn("never goes in a yes-to-all card", read("crav1-tighten-plan/references/issues.md"))


if __name__ == "__main__":
    unittest.main()
