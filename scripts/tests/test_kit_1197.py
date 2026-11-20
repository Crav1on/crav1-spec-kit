"""1.197.0: whole-label maps, prod lint per item, release gates, quiet tickable, small fixes, reviewer packet.

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
WALK = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
PLAN = SK / "crav1-plan-from-spec/scripts/plan_check.py"
BATCH = SK / "crav1-tighten-plan/scripts/batch_offer.py"


def py(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, check=False)


def js(script: Path, *args: str) -> dict:
    proc = py(script, *args)
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


class WholeLabels(unittest.TestCase):
    """Item 1: the label map replaces a whole option label only."""

    def setUp(self):
        self.bo = load(BATCH, "batch_offer_t1197")

    def test_words_inside_text_are_kept(self):
        self.assertEqual(self.bo.plain("keep it open until its verify row passes; ask person A whether the job may restart"),
                         "keep it open until its verify row passes; ask person A whether the job may restart")
        self.assertEqual(self.bo.plain("A keep as written, so the plan decides"), "keep as written, so the plan decides")

    def test_whole_ids_still_map(self):
        self.assertEqual(self.bo.plain("A tick-from-verify; B keep"), "tick it from the passing verify row; keep as written")
        self.assertEqual(self.bo.plain("ask"), "ask the owner")
        self.assertEqual(self.bo.plain("keep: the plan decides"), "keep as written: the plan decides")

    def test_card_text_not_garbled(self):
        text = self.bo.offer("Tighten-spec batch", [{"id": "I1", "issue": "retry limit unclear",
                                                     "options": "keep it open; ask person A", "recommendation": "keep it open",
                                                     "why": "no source decides it"}])
        self.assertNotIn("as written it open", text)
        self.assertNotIn("the owner person A", text)


class ProdLintPerItem(unittest.TestCase):
    """Item 2: judge each verify item and its target; scan manual prod task text."""

    def lint(self, tasks: str, risks: str = "- none\n") -> str:
        root = spec_folder(tasks, "# Plan\n\n## Risks\n\n" + risks)
        return py(PLAN, "lint", "--root", str(root)).stdout

    def test_harmless_items_are_not_flagged(self):
        out = self.lint(
            "- [ ] T4: Params (verify: manual, prod; az bicep build-params for infra/main.prod.bicepparam compiles locally)\n"
            "- [ ] T24: Retry (verify: unit — retries with PROD-like settings pass)\n"
            "- [ ] T27: Check (verify: manual, prod; read the function app state shows Stopped)\n"
            "- [ ] T36: Setting (verify: manual, prod; the setting name exists on fn-orders-prod)\n"
            "- [ ] T42: Compile (verify: bicep build passes for the prod template)\n"
            "- [ ] T30: Dev (verify: manual, prod health; delete the test row on DEV)\n")
        self.assertEqual(out.strip(), "Lint: 0 problems.")

    def test_real_prod_write_item_is_flagged(self):
        out = self.lint("- [ ] T51: Load (verify: unit — parser; manual, post one message on prod and check it lands)\n")
        self.assertIn("Prod verify: T51", out)
        self.assertNotIn("parser", out.split("(", 1)[1].split(")")[0])

    def test_manual_prod_task_text_is_scanned(self):
        task = "- [ ] T52 (manual, prod, one yes) Drop the old orders tables after the release's PROD stage (after: T8)\n"
        out = self.lint(task)
        self.assertIn("Prod write: T52 is a manual prod task that writes to prod without an owner: and a Risks line", out)
        ok = self.lint(task.replace("one yes", "owner: person A, one yes"),
                       "- T52 drops the old orders tables only with the first release to main.\n")
        self.assertEqual(ok.strip(), "Lint: 0 problems.")


class ReleaseGate(unittest.TestCase):
    """Item 2: a manual prod task waits for its release and is never the first task."""

    def test_gate_holds_task(self):
        root = spec_folder(
            "- [ ] T1 Add the export endpoint (branch: feat/orders-export)\n"
            "- [ ] T2 (manual, prod, owner: person A, one yes) Drop the old orders tables after the PROD stage (after: T1)\n"
            "- [ ] T3 (manual, prod, owner: person A) Drop the audit table (after-release: main)\n",
            "# Plan\n\n## Risks\n\n- T2 runs only with the first develop to main release.\n")
        mod = load(WALK, "walk_progress_t1197a")
        gates = mod.release_gates(root)
        self.assertEqual(gates["T3"], "waits for the first release to main and a prod yes")
        self.assertIn("T2", gates)
        text = py(WALK, "readiness", "--root", str(root), "--text").stdout
        self.assertIn("T3 (manual, prod, owner: person A) Drop the audit table — waits for the first release to main", text)
        self.assertNotIn("Run only T2", text)
        self.assertNotIn("Run only T3", text)
        self.assertNotIn("orders-api T3`", text)

    def test_no_risk_line_no_gate(self):
        root = spec_folder("- [ ] T2 (manual, prod, owner: person A) Read the version page\n")
        self.assertEqual(load(WALK, "walk_progress_t1197b").release_gates(root), {})


class QuietTickable(unittest.TestCase):
    """Item 3: only failing or no-evidence rows are questions."""

    def test_untested_rows_wait(self):
        root = spec_folder("- [ ] T16: Export (verify: unit)\n")
        (root / "spec.md").write_text("# Orders API\n\n## Acceptance criteria\n\n- [ ] Retries stop after three tries\n"
                                      "- [ ] The export writes one file per day\n- [ ] A bad row is skipped\n", encoding="utf-8")
        (root / "verify.md").write_text(
            "# Verify\n\n## Acceptance — details\n\n| Id | Acceptance | Evidence | Result | Task |\n| --- | --- | --- | --- | --- |\n"
            "| A1 | Retries stop after three tries | — | pass on develop | T1 |\n"
            "| A2 | The export writes one file per day | — | untested | T16 |\n"
            "| A3 | A bad row is skipped | src/export.py:20 | fail | T16 |\n", encoding="utf-8")
        out = js(WALK, "tickable", "--root", str(root))
        self.assertEqual({c["row"]: c["why"] for c in out["cards"]}, {"A1": "passes with no evidence", "A3": "failing"})
        self.assertEqual(out["waiting"], [2])
        self.assertEqual(out["waiting_line"], "1 acceptance item waits on its tasks.")


class SmallFixes(unittest.TestCase):
    """Item 4: resolved playbook, no Kept line, ADO PR number, housekeeping count and wording."""

    def test_ado_merge_subject_gives_pr(self):
        mod = load(SK / "crav1-add-to-spec/scripts/start_check.py", "start_check_t1197")
        for subject, pr in (("Merge pull request 82 from feat/orders-cicd into develop", "82"),
                            ("Merge pull request #71 from contoso/feat/orders-retry", "71"),
                            ("Merged PR 90: orders export", "90"), ("Add retry (#12)", "12")):
            m = mod.PR_SUBJECT.search(subject)
            self.assertEqual(next(g for g in m.groups() if g), pr, subject)

    def test_preserve_says_nothing_when_unchanged(self):
        claims = SK / "crav1-build-walk/scripts/claims.py"
        tmp = Path(tempfile.mkdtemp())
        text = "# Tasks\n\n- [ ] T2: Record the decision (branch: feat/orders-api-record)\n"
        (tmp / "b.md").write_text(text, encoding="utf-8")
        (tmp / "a.md").write_text(text, encoding="utf-8")
        out = js(claims, "preserve", "--before", str(tmp / "b.md"), "--after", str(tmp / "a.md"), "--tasks", "T2")
        self.assertFalse(out["changed"])
        self.assertIsNone(out["line"])

    def test_housekeeping_count_and_wording(self):
        root = spec_folder("- [ ] T1: Retry (verify: unit)\n", "# Plan\n\nReviewed: 2026-11-20, P# open: 3\n")
        items = root / "items.json"
        items.write_text(json.dumps([
            {"id": "P3", "issue": "stale read line", "tag": "plan", "status": "open", "housekeeping": True,
             "options": "update it", "recommendation": "update it"},
            {"id": "P4", "issue": "no 400 test", "tag": "plan", "status": "open", "options": "add-regression; keep",
             "recommendation": "add-regression", "why": "the spec names a 400 reply"}]), encoding="utf-8")
        out = py(PLAN, "batch", "--items", str(items)).stdout
        self.assertTrue(out.startswith("Applying with no card (housekeeping): P3 stale read line."))
        rev = py(PLAN, "reviewed", "--root", str(root), "--items", str(items)).stdout
        self.assertIn("P# open 3 would be 1", rev)

    def test_start_uses_resolved_playbook(self):
        docs = Path(tempfile.mkdtemp()) / "docs"
        root = docs / "specs" / "orders-api"
        root.mkdir(parents=True)
        (docs / "playbooks").mkdir()
        (docs / "playbooks" / "orders-process-1-0.md").write_text("# Orders process 1.0\n\n1. Ship it.\n", encoding="utf-8")
        (root / "spec.md").write_text("# Orders API\n\nPlaybook: `docs/playbooks/orders-process-1-0.md`\n\n## Problem\n", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(WALK), "start", "--root", "orders process 1 0", "--skip-sync"],
                              capture_output=True, text=True, cwd=docs.parent)
        out = json.loads(proc.stdout)
        if out.get("how") and "playbook" in out["how"]:
            self.assertEqual(out["playbook"], "docs/playbooks/orders-process-1-0.md")
            self.assertIsNotNone(out["playbook_status"])
        else:
            self.fail(proc.stdout + proc.stderr)


class RuleDocs(unittest.TestCase):
    """Item 5: short batch question; proposed, not done."""

    def test_question_cards_short_question(self):
        page = (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("The question is short (1.197.0)", page)
        self.assertIn("Never put the items in the question.", page)
        self.assertNotIn("The question text still names every item.", page)

    def test_proposed_not_done(self):
        common = read("crav1-tighten-and-plan-ready-to-build/references/common.md")
        self.assertIn("**Proposed, not done (1.197.0).**", common)
        self.assertIn("Never write `I've updated`", common)
        self.assertIn("do not run `repo_sync.py status` yourself", common)
