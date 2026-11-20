"""1.196.0: shared start checks, claims prune, prod verify, fewer cards, plain card labels, ticking.

Generic fixtures only (orders-api, contoso, person A).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
MSS = SK / "crav1-add-to-spec/scripts/merged_since_sync.py"
START = SK / "crav1-add-to-spec/scripts/start_check.py"
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


def g(repo: Path, *args: str) -> str:
    return subprocess.run(GIT + ["-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def commit(repo: Path, name: str) -> str:
    (repo / f"{name}.py").write_text(name + "\n", encoding="utf-8")
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", name)
    return g(repo, "rev-parse", "--short=7", "HEAD")


def spec_folder(spec_text: str) -> Path:
    docs = Path(tempfile.mkdtemp()) / "docs"
    root = docs / "specs" / "orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text(spec_text, encoding="utf-8")
    (root / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (root / "tasks.md").write_text("# Tasks\n\n- [ ] T1 Record the lane (after: )\n", encoding="utf-8")
    return root


class StaleLocalBase(unittest.TestCase):
    """Item 1: origin/develop has the PR merge; the local develop in the checkout is behind."""

    def setUp(self):
        top = Path(tempfile.mkdtemp())
        self.origin = top / "origin"
        self.origin.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "develop", str(self.origin)], check=True)
        commit(self.origin, "base")
        self.work = top / "orders-api"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.work)], check=True)
        g(self.origin, "checkout", "-q", "-b", "feat/orders-retry")
        self.first = commit(self.origin, "retry1")
        commit(self.origin, "retry2")
        g(self.work, "fetch", "-q", "origin")
        g(self.origin, "checkout", "-q", "develop")
        g(self.origin, "merge", "-q", "--no-ff", "feat/orders-retry", "-m", "Merge pull request #82 from contoso/feat/orders-retry")
        self.merge = g(self.origin, "rev-parse", "--short=7", "HEAD")
        self.spec = f"# Orders API\nSynced at: orders-api feat/orders-retry@{self.first}, 2026-11-18\n\n## Problem\n"

    def test_helper_prefers_origin_after_fetch(self):
        out = js(START, "state", "--code-repo", str(self.work), "--branch", "feat/orders-retry", "--base", "develop")
        self.assertEqual(out["fetch"], "fetched")
        self.assertEqual(out["base"], "origin/develop")
        self.assertEqual(out["merged"]["pr"], "82")
        self.assertEqual(out["merged"]["merge_short"], self.merge)

    def test_merged_since_sync_sees_the_merge(self):
        root = spec_folder(self.spec)
        out = js(MSS, "check", "--spec", str(root / "spec.md"), "--code-repo", str(self.work), "--base", "develop")
        self.assertEqual(out["offer"], "take-in", out)
        self.assertEqual(out["branches"][0]["base"], "develop")
        self.assertIn(f"PR 82 merged at {self.merge}", out["question"])

    def test_code_drift_sees_the_merged_tip(self):
        root = spec_folder(self.spec)
        g(self.work, "fetch", "-q", "origin")
        g(self.work, "branch", "-q", "feat/orders-retry", "origin/feat/orders-retry")
        out = js(WALK, "code-drift", "--root", str(root), "--code-repo", str(self.work), "--base", "develop")
        self.assertTrue(out["behind"], out)
        self.assertEqual(out["merged"]["sha"], self.merge)
        self.assertTrue(out["merged"]["tip_merged"])
        self.assertEqual(out["command"], "/crav1-add-to-spec pr82")

    def test_recorded_merge_is_current(self):
        root = spec_folder(self.spec.replace("\n\n## Problem", f"\nSynced at: orders-api develop@{self.merge}, 2026-11-20\n\n## Problem"))
        out = js(WALK, "code-drift", "--root", str(root), "--code-repo", str(self.work), "--base", "develop")
        self.assertIsNone(out.get("merged"), out)


class TipMergedFastForward(unittest.TestCase):
    """Item 1: a branch whose tip is already in the base with no new commits after Synced at is merged."""

    def test_tip_merged_without_new_commits(self):
        repo = Path(tempfile.mkdtemp()) / "orders-api"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "develop", str(repo)], check=True)
        commit(repo, "base")
        g(repo, "checkout", "-q", "-b", "feat/orders-export")
        tip = commit(repo, "export1")
        g(repo, "checkout", "-q", "develop")
        commit(repo, "dev-other")
        g(repo, "merge", "-q", "--no-ff", "feat/orders-export", "-m", "Merge pull request #83 from contoso/feat/orders-export")
        root = spec_folder(f"# Orders API\nSynced at: orders-api feat/orders-export@{tip}, 2026-11-18\n\n## Problem\n")
        out = js(WALK, "code-drift", "--root", str(root), "--code-repo", str(repo), "--base", "develop")
        self.assertTrue(out["behind"], out)
        self.assertEqual(out["merged"]["pr"], "83")
        self.assertEqual(out["drift"], [])


CLAIMS = SK / "crav1-build-walk/scripts/claims.py"


class ClaimsPrune(unittest.TestCase):
    """Item 2: finished claims clear with no card; unfinished ones stay, with or without age."""

    def setUp(self):
        top = Path(tempfile.mkdtemp())
        self.repo = top / "orders-api"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "develop", str(self.repo)], check=True)
        commit(self.repo, "base")
        for name in ("feat/orders-retry", "feat/orders-export"):
            g(self.repo, "checkout", "-q", "-b", name, "develop")
            commit(self.repo, name.split("/")[1])
        g(self.repo, "checkout", "-q", "develop")
        g(self.repo, "merge", "-q", "--no-ff", "feat/orders-retry", "-m", "Merge pull request #71 from contoso/feat/orders-retry")
        self.root = top / "docs" / "specs" / "orders-api"
        self.root.mkdir(parents=True)
        (self.root / "tasks.md").write_text(
            "# Tasks\n\n- [x] T5 Retry (after: )\n- [x] T8 Docs (after: )\n- [ ] T9 Export (after: )\n- [ ] T10 Later (after: )\n",
            encoding="utf-8")
        (self.root / "claims.md").write_text(
            "# Claims\n\n"
            "In progress: feat/orders-retry, T5, person A, since 2026-11-10T09:00:00+01:00\n"
            "In progress: feat/orders-docs, T8, person B, since 2026-11-10T09:00:00+01:00\n"
            "In progress: feat/orders-export, T9, person B, since 2026-11-10T09:00:00+01:00\n"
            "In progress: feat/orders-later, T10, person A, since 2026-11-19T09:00:00+01:00\n",
            encoding="utf-8")

    def test_prune_clears_only_finished(self):
        out = js(CLAIMS, "prune", "--root", str(self.root), "--code-repo", str(self.repo), "--base", "develop")
        self.assertEqual(out["line"], "Cleared 2 finished claims: T5 (ticked), T8 (ticked).")
        text = (self.root / "claims.md").read_text(encoding="utf-8")
        self.assertNotIn("T5", text)
        self.assertNotIn("T8", text)
        self.assertIn("feat/orders-export, T9, person B", text)
        self.assertIn("feat/orders-later, T10, person A", text)

    def test_merged_branch_clears_with_its_pr(self):
        (self.root / "tasks.md").write_text("# Tasks\n\n- [ ] T5 Retry (after: )\n- [ ] T9 Export (after: )\n", encoding="utf-8")
        out = js(CLAIMS, "prune", "--root", str(self.root), "--code-repo", str(self.repo), "--base", "develop", "--dry-run")
        self.assertEqual(out["line"], "Cleared 1 finished claim: T5 (PR 71).")
        self.assertIsNone(out["wrote"])

    def test_no_finished_claims_says_nothing(self):
        (self.root / "claims.md").write_text(
            "# Claims\n\nIn progress: feat/orders-export, T9, person B, since 2026-11-10T09:00:00+01:00\n", encoding="utf-8")
        before = (self.root / "claims.md").read_text(encoding="utf-8")
        out = js(CLAIMS, "prune", "--root", str(self.root), "--code-repo", str(self.repo))
        self.assertIsNone(out["line"])
        self.assertEqual((self.root / "claims.md").read_text(encoding="utf-8"), before)

    def test_finished_claims_never_warn(self):
        out = js(CLAIMS, "list", "--root", str(self.root), "--now", "2026-11-20T09:00:00+01:00")
        joined = " ".join(out["warnings"])
        self.assertNotIn("T5 has been", joined)
        self.assertIn("T9 has been", joined)

    def test_docs_run_prune_and_merge_pr_clears(self):
        self.assertIn("claims.py prune", read("crav1-merge-pr/SKILL.md"))
        self.assertNotIn("This skill never writes, clears", read("crav1-merge-pr/SKILL.md"))
        self.assertIn("claims.py prune", read("crav1-tighten-and-plan-ready-to-build/references/steps.md"))
        self.assertIn("Never write a line saying claims or claimed tasks were kept", read("crav1-tighten-and-plan-ready-to-build/references/steps.md"))


PLAN = SK / "crav1-tighten-plan/scripts/plan_check.py"


class ProdVerify(unittest.TestCase):
    """Item 3: prod verifies are read-only; prod writes are their own task with owner, yes and Risks line."""

    def lint(self, tasks: str, risks: str = "- none\n") -> str:
        root = Path(tempfile.mkdtemp())
        (root / "tasks.md").write_text("# Tasks\n\n" + tasks, encoding="utf-8")
        (root / "plan.md").write_text("# Plan\n\n## Risks\n\n" + risks, encoding="utf-8")
        return py(PLAN, "lint", "--root", str(root)).stdout

    def test_read_only_prod_passes(self):
        out = self.lint("- [ ] T50: Health (verify: manual, prod health and version)\n- [ ] T53: Unit (verify: unit, DEV)\n")
        self.assertEqual(out.strip(), "Lint: 0 problems.")

    def test_prod_write_in_verify_is_flagged(self):
        out = self.lint("- [ ] T51: Load (verify: manual, prod, post one message and check it lands)\n")
        self.assertIn("Prod verify: T51", out)
        self.assertIn("verify on DEV/TEST", out)

    def test_prod_write_task_needs_owner_and_risk(self):
        out = self.lint("- [ ] T52: Push (verify: manual, prod-write, one yes)\n")
        self.assertIn("without an owner: and a Risks line", out)
        ok = self.lint("- [ ] T52: Push (verify: manual, prod-write, owner: person A, one yes)\n",
                       "- T52 writes one test message to prod; person A says yes first.\n")
        self.assertEqual(ok.strip(), "Lint: 0 problems.")

    def test_rule_in_docs(self):
        self.assertIn("## Prod verify (1.196.0)", read("crav1-plan-from-spec/references/checks.md"))
        self.assertIn("## Prod verify (1.196.0)", read("crav1-tighten-plan/references/issues.md"))


class FewerCards(unittest.TestCase):
    """Item 4: housekeeping auto-applies, covered reopens clear, the save rides on the last yes."""

    def items(self, rows):
        path = Path(tempfile.mkdtemp()) / "items.json"
        path.write_text(json.dumps(rows), encoding="utf-8")
        return str(path)

    def row(self, i, **extra):
        r = {"id": f"P{i}", "issue": f"issue {i}", "tag": "plan", "status": "open", "options": "fix; keep", "recommendation": "fix"}
        r.update(extra)
        return r

    def test_housekeeping_has_no_card(self):
        out = py(PLAN, "batch", "--items", self.items([self.row(1), self.row(7, issue="Trace row for the retry constraint", housekeeping=True),
                                                      self.row(14, issue="missing mark", housekeeping="mark")])).stdout
        self.assertIn("Applied with no card (housekeeping): P7 Trace row for the retry constraint; P14 missing mark.", out)
        card = [l for l in out.splitlines() if l.startswith("On yes:")][0]
        self.assertNotIn("P7", card)
        self.assertIn("P1", card)

    def test_only_housekeeping_prints_only_the_line(self):
        out = py(PLAN, "batch", "--items", self.items([self.row(7, housekeeping=True)])).stdout
        self.assertNotIn("Card:", out)
        self.assertTrue(out.startswith("Applied with no card"))

    def test_auto_clear_line(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("walk_progress_t1196", WALK)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        line = mod.auto_clear_line(["review-and-tighten-plan"])
        self.assertIn("reopened only because of a fact this walk just recorded", line)
        self.assertIn("with no card", line)

    def test_docs(self):
        self.assertIn("--covered <step>", read("crav1-tighten-and-plan-ready-to-build/references/progress.md"))
        self.assertIn("The save rides on the step's last yes", read("crav1-tighten-and-plan-ready-to-build/references/steps.md"))
        self.assertIn("## Housekeeping with no card (1.196.0)", read("crav1-tighten-plan/references/issues.md"))


class CardRules(unittest.TestCase):
    """Item 5: plain labels, bullets above batch cards, a short question and a result-on-yes line."""

    def test_batch_offer_maps_letters_and_ids(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("batch_offer_t1196", SK / "crav1-tighten-plan/scripts/batch_offer.py")
        bo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bo)
        self.assertEqual(bo.plain("A tick-from-verify; B keep"), "tick it from the passing verify row; keep as written")
        self.assertEqual(bo.plain("A park-risk, B add-regression"), "note it as a risk, add a regression test")
        text = bo.offer("Tighten-plan batch", [{"id": "P1", "issue": "no 400 test", "options": "A add-regression; keep",
                                                "recommendation": "A add-regression", "why": "the spec names a 400 reply"}])
        self.assertIn("- P1 no 400 test. Why: the spec names a 400 reply. Yes: add a regression test.", text)
        self.assertIn("Card: Tighten-plan batch: apply the recommendation?\nOn yes: P1 no 400 test: add a regression test.", text)
        for bad in ("tick-from-verify", "park-risk", "add-regression", "| A ", " A add"):
            self.assertNotIn(bad, text)

    def test_walk_cards_have_plain_labels_and_results(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("walk_progress_t1196b", WALK)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        card = mod.reopen_card("review-and-tighten-plan", ["tasks"], True)
        self.assertTrue(card["result"].startswith("On yes:"))
        jump = mod._jump_back_offer("P9", "add-to-spec", "/crav1-add-to-spec pr73")
        self.assertEqual(jump["options"][0]["label"], "Record the code in the spec first (Recommended)")
        self.assertTrue(jump["result"].startswith("On yes: /crav1-add-to-spec pr73"))
        for label in mod.PLAIN_LABELS.values():
            self.assertNotIn("/crav1-", label)

    def test_question_cards_rules(self):
        page = (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("## Walk card rules (1.196.0)", page)
        self.assertIn("On yes:", page)
        self.assertIn("`suggest` only for wording findings", page)
        self.assertIn("the meeting batch's fixed choice set", page)
        self.assertIn("Offer **`suggest`** only for a wording finding", read("crav1-tighten-spec/SKILL.md"))


class Tickable(unittest.TestCase):
    """Item 6: tick clear acceptance items with no card; soon-stale items get a recheck note."""

    def setUp(self):
        self.root = spec_folder("# Orders API\n\n## Acceptance criteria\n\n"
                                "- [ ] Retries stop after three tries\n"
                                "- [ ] The export writes one file per day\n"
                                "- [ ] Unit tests for the retry\n"
                                "- [ ] Failure case: a bad row is skipped\n\n## Open questions\n")
        (self.root / "verify.md").write_text(
            "# Verify\n\n## Acceptance — details\n\n| Id | Acceptance | Evidence | Result | Task |\n| --- | --- | --- | --- | --- |\n"
            "| A1 | Retries stop after three tries | src/retry.py:40, tests/test_retry.py:12 | pass on develop | T1 |\n"
            "| A2 | The export writes one file per day | src/export.py:9 | pass on develop | T2 |\n"
            "| A3 | item 3 | tests/test_retry.py:30 | pass on feat/orders-retry | T1 |\n"
            "| A4 | Failure case: a bad row is skipped | src/export.py:20 | fail | T2 |\n", encoding="utf-8")
        (self.root / "tasks.md").write_text(
            "# Tasks\n\n- [x] T1: Retry (verify: unit)\n- [x] T2: Export (verify: unit)\n"
            "- [ ] T3: Export by region, touches src/export.py (verify: unit — one file per region)\n", encoding="utf-8")

    def test_report_without_write(self):
        out = js(WALK, "tickable", "--root", str(self.root))
        acts = {i["row"]: i["action"] for i in out["items"]}
        self.assertEqual(acts, {"A1": "tick", "A2": "tick-recheck"})
        self.assertEqual({c["row"] for c in out["cards"]}, {"A3", "A4"})
        self.assertIsNone(out["wrote"])
        self.assertIn("- [ ] Retries stop", (self.root / "spec.md").read_text(encoding="utf-8"))

    def test_write_ticks_and_adds_recheck(self):
        out = js(WALK, "tickable", "--root", str(self.root), "--write")
        self.assertEqual(out["line"], "Ticked 2 acceptance items from verify: item 1 (A1), item 2 (A2, recheck on T3).")
        spec = (self.root / "spec.md").read_text(encoding="utf-8")
        self.assertIn("- [x] Retries stop after three tries", spec)
        self.assertIn("- [x] The export writes one file per day", spec)
        self.assertIn("- [ ] Unit tests for the retry", spec)
        tasks = (self.root / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("(verify: unit — one file per region; recheck item 2 (verify A2))", tasks)
        again = js(WALK, "tickable", "--root", str(self.root), "--write")
        self.assertEqual(again["items"], [])

    def test_docs(self):
        self.assertIn("tickable --root <spec-folder> --write", read("crav1-tighten-spec/SKILL.md"))
        self.assertIn("**Tickable at the start (1.196.0).**", read("crav1-tighten-and-plan-ready-to-build/references/steps.md"))


if __name__ == "__main__":
    unittest.main()
