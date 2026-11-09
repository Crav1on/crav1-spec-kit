"""Synthetic checks for /crav1-model-data.

These tests run the skill's state script on fixture files. They are not a live
agent replay and they do not claim a modeling method was empirically validated.
A rendered diagram proves the exporter drew pixels, not that a notation is official.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-model-data/scripts/model_run.py"
FIX = ROOT / "scripts/tests/fixtures/data-model"
REPO = FIX / "repo"


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    return proc.returncode, payload


def must(args: list[str]) -> dict:
    code, payload = run(args)
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


def fails(args: list[str], code_name: str) -> dict:
    code, payload = run(args)
    if code == 0:
        raise AssertionError(payload)
    if payload.get("code") != code_name:
        raise AssertionError(payload)
    return payload


class Fixtures(unittest.TestCase):
    def test_discovery_explains_inclusion_and_sets_no_default(self):
        payload = must(["discover", "--root", str(REPO), "--scope", "orders"])
        self.assertFalse(payload["scope_confirmed"])
        self.assertIsNone(payload["default_view"])
        self.assertFalse(payload["area"]["default"])
        self.assertFalse(payload["platform"]["default"])
        area_slugs = [c["slug"] for c in payload["area"]["candidates"]]
        platform_slugs = [c["slug"] for c in payload["platform"]["candidates"]]
        self.assertEqual(area_slugs, ["orders"])
        self.assertEqual(sorted(platform_slugs), ["billing", "orders"])
        self.assertTrue(any("not found" in c["reason"].lower() or "Excluded" in c["reason"] for c in payload["excluded"]))
        self.assertTrue(all(not c["included_as_container"] for c in payload["context"]))
        self.assertTrue(any(c["path"].endswith("landscape.md") for c in payload["context"]))
        bare = must(["discover", "--root", str(REPO)])
        self.assertFalse(bare["scope_confirmed"])
        self.assertEqual(bare["area"]["candidates"], [])
        self.assertEqual(len(bare["platform"]["candidates"]), 2)

    def test_recommendation_fixtures(self):
        home = self._init("manual")
        try:
            kept = must(["recommend", "--home", str(home), "--json", str(FIX / "retain-poor-docs.json")])
            self.assertEqual(kept["recommendation"], "retain")
            self.assertFalse(kept["final"])
            fails(
                ["recommend", "--home", str(home), "--json", str(FIX / "redesign-poor-docs.json")],
                "retain-fit",
            )
            fails(["recommend", "--home", str(home), "--json", str(FIX / "tie.json")], "tie")
            fails(["recommend", "--home", str(home), "--json", str(FIX / "held-gap.json")], "hold")
            short = must(["recommend", "--home", str(home), "--json", str(FIX / "provisional-shortlist.json")])
            self.assertTrue(short["provisional"])
            self.assertFalse(short["final"])
            fails(["recommend", "--home", str(home), "--json", str(FIX / "unknown-not-excluded.json")], "unknown")
            fails(["recommend", "--home", str(home), "--json", str(FIX / "requirement-not-fit.json")], "separate")
            fails(["recommend", "--home", str(home), "--json", str(FIX / "binding.json")], "binding")
        finally:
            shutil.rmtree(home)

    def test_worked_examples_and_views(self):
        fails(["example", "--kind", "history-window", "--json", str(FIX / "history-window.json")], "history-window")
        conditional = must(["example", "--kind", "history-window", "--json", str(FIX / "history-conditional.json")])
        self.assertTrue(conditional["conditional"])
        fails(["example", "--kind", "schema-not-disproof", "--json", str(FIX / "schema-not-disproof.json")], "unknown")
        unknown = must(["example", "--kind", "schema-not-disproof", "--json", str(FIX / "schema-unknown.json")])
        self.assertEqual(unknown["fit"], "unknown")
        self.assertNotEqual(unknown["outcome"], "excluded")
        gap = must(["example", "--kind", "double-count", "--json", str(FIX / "double-count.json")])
        self.assertEqual(gap["result"], "gap")
        same = must(["example", "--kind", "double-count", "--json", str(FIX / "same-grain.json")])
        self.assertEqual(same["total"], 100)
        correction = must(["example", "--kind", "correction", "--json", str(FIX / "correction-gap.json")])
        self.assertTrue(correction["blocks_physical"])
        ok = must(["example", "--kind", "correction", "--json", str(FIX / "correction-ok.json")])
        self.assertFalse(ok["blocks_physical"])
        fails(["example", "--kind", "views", "--json", str(FIX / "views-drop-local.json")], "views")
        fails(["example", "--kind", "views", "--json", str(FIX / "views-promote.json")], "views")
        views = must(["example", "--kind", "views", "--json", str(FIX / "views-ok.json")])
        self.assertIsNone(views["default_view"])
        self.assertTrue(views["local_obligations_preserved"])

    def test_manual_business_checkpoint_and_stage_approval(self):
        home = self._init("manual")
        try:
            fails(["confirm-scope", "--home", str(home)], "scope")
            proposed = must(["propose-scope", "--home", str(home), "--scope", "orders dispatch"])
            self.assertFalse(proposed["scope_confirmed"])
            must(["confirm-scope", "--home", str(home), "--yes"])
            fails(
                ["decide", "--home", str(home), "--json", str(self._decision("physical-shape", "physical-design"))],
                "business-first",
            )
            must(["decide", "--home", str(home), "--json", str(self._decision("order-line-grain", "business-model"))])
            must(["example", "--home", str(home), "--kind", "correction", "--json", str(FIX / "correction-ok.json")])
            must(["diagram", "--home", str(home), "--id", "structure", "--kind", "er", "--caption", "Order and line", "--mermaid", str(FIX / "er.mmd")])
            must(["diagram", "--home", str(home), "--id", "movement", "--kind", "flow", "--caption", "Landing window", "--mermaid", str(FIX / "flow.mmd")])
            current = self._revision(home)
            fails(
                ["approve", "--home", str(home), "--stage", "physical-design", "--revision", current, "--date", "2026-11-08", "--yes"],
                "stage",
            )
            approved = must(["approve", "--home", str(home), "--stage", "business-model", "--revision", current, "--date", "2026-11-08", "--yes"])
            self.assertEqual(approved["approved"], f"Approved: business-model {current}, 2026-11-08")
            confirmed = (home / "confirmed.md").read_text(encoding="utf-8")
            self.assertNotIn("Approved: physical-design", confirmed)
            snapshot = confirmed
            must(["transition", "--home", str(home), "--kind", "concise", "--text", "Consumers keep reading the current grain while a history source is absent. Detailed migration planning is offered, not written."])
            must(["decide", "--home", str(home), "--json", str(self._decision("line-table", "physical-design", grain="one order line"))])
            physical_rev = self._revision(home)
            must(["approve", "--home", str(home), "--stage", "physical-design", "--revision", physical_rev, "--date", "2026-11-08", "--yes"])
            after = (home / "confirmed.md").read_text(encoding="utf-8")
            self.assertTrue(after.startswith(snapshot))
            self.assertIn("Approved: physical-design", after)
            self.assertIn(f"Approved: business-model {current}, 2026-11-08", after)
            self.assertNotIn(f"Approved: business-model {physical_rev}", after)
        finally:
            shutil.rmtree(home)

    def test_auto_keeps_proposals_and_budgets(self):
        home = self._init("auto")
        try:
            fails(
                ["decide", "--home", str(home), "--json", str(self._decision("physical-shape", "physical-design"))],
                "conditional",
            )
            conditional = self._decision("physical-shape", "physical-design")
            body = json.loads(conditional.read_text(encoding="utf-8"))
            body.update({
                "status": "conditional",
                "conditional": True,
                "implementable": False,
                "outcome": "held",
                "fit": "assumed",
                "requirement": "unknown",
                "depends": "business-model",
            })
            path = conditional.with_name("conditional.json")
            path.write_text(json.dumps(body), encoding="utf-8")
            made = must(["decide", "--home", str(home), "--json", str(path)])
            self.assertEqual(made["status"], "conditional")
            text = (home / "proposed.md").read_text(encoding="utf-8")
            self.assertIn("Conditional: yes", text)
            self.assertNotIn("Approved:", (home / "confirmed.md").read_text(encoding="utf-8"))
            choice = {"recommendation": "tie", "tie": True, "best_fit": "star", "user_chose": True, "reason": "pick star"}
            choice_path = home / "choice.json"
            choice_path.write_text(json.dumps(choice), encoding="utf-8")
            fails(["recommend", "--home", str(home), "--json", str(choice_path)], "auto-choice")
            must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--now", "2026-11-08T12:00:00+00:00"])
            fails(
                ["approve", "--home", str(home), "--stage", "business-model", "--revision", self._revision(home), "--date", "2026-11-08", "--yes"],
                "auto-approve",
            )
            fails(["confirm-scope", "--home", str(home), "--yes"], "scope")
            self._budget(home)
        finally:
            shutil.rmtree(home)

    def test_drift_touches_only_affected_decisions_and_dependencies(self):
        home = self._init("manual")
        root = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            must(["decide", "--home", str(home), "--json", str(self._decision("order-grain", "business-model", sources="docs/specs/orders/spec.md"))])
            must(["decide", "--home", str(home), "--json", str(self._decision(
                "line-grain", "business-model", sources="docs/specs/orders/spec.md", depends="order-grain", measure="line amount"
            ))])
            must(["decide", "--home", str(home), "--json", str(self._decision(
                "billing-grain", "business-model", sources="docs/specs/billing/spec.md", measure="invoice amount", scope="area:billing"
            ))])
            must(["pin", "--home", str(home), "--root", str(root), "--source", "docs/specs/orders/spec.md", "--decisions", "order-grain"])
            must(["pin", "--home", str(home), "--root", str(root), "--source", "docs/specs/billing/spec.md", "--decisions", "billing-grain"])
            confirmed_before = (home / "confirmed.md").read_bytes()
            billing_before = self._block(home, "billing-grain")
            (root / "docs/specs/orders/spec.md").write_text(
                "# Orders dispatch\n\nThe weekly total is now defined per shipment, not per order line.\n",
                encoding="utf-8",
            )
            noted = must(["note-drift", "--home", str(home), "--root", str(root)])
            self.assertIn("order-grain", noted["affected"])
            self.assertIn("line-grain", noted["affected"])
            self.assertIn("billing-grain", noted["unaffected"])
            self.assertNotIn("no drift exists", noted["statement"].lower())
            self.assertIn("This is not a claim", noted["statement"])
            self.assertEqual(self._block(home, "billing-grain"), billing_before)
            self.assertEqual((home / "confirmed.md").read_bytes(), confirmed_before)
            self.assertIn("needs-review", self._block(home, "order-grain"))
            quiet = must(["drift", "--home", str(home), "--root", str(root)])
            self.assertTrue(any(item["content_changed"] for item in quiet["checked"]))
        finally:
            shutil.rmtree(home)
            shutil.rmtree(root)

    def test_internal_inconsistency_is_drift_without_a_new_source(self):
        home = self._init("manual")
        root = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            must(["decide", "--home", str(home), "--json", str(self._decision("grain-a", "business-model", grain="one order", measure="ordered amount"))])
            must(["decide", "--home", str(home), "--json", str(self._decision("grain-b", "business-model", grain="one order line", measure="ordered amount"))])
            must(["decide", "--home", str(home), "--json", str(self._decision("other", "business-model", grain="one invoice", measure="invoice amount", scope="area:billing"))])
            must(["pin", "--home", str(home), "--root", str(root), "--source", "docs/specs/orders/spec.md", "--decisions", "grain-a,grain-b"])
            other_before = self._block(home, "other")
            noted = must(["note-drift", "--home", str(home), "--root", str(root)])
            self.assertTrue(noted["internal"])
            self.assertIn("grain-a", noted["affected"])
            self.assertIn("grain-b", noted["affected"])
            self.assertEqual(self._block(home, "other"), other_before)
            self.assertIn("Internal inconsistencies: 1", noted["statement"])
        finally:
            shutil.rmtree(home)
            shutil.rmtree(root)

    def test_report_is_immutable_and_feedback_is_not_approval(self):
        home = self._init("manual")
        try:
            must(["decide", "--home", str(home), "--json", str(self._decision("order-line-grain", "business-model"))])
            must(["example", "--home", str(home), "--kind", "correction", "--json", str(FIX / "correction-ok.json")])
            must(["diagram", "--home", str(home), "--id", "structure", "--kind", "er", "--caption", "Order and line", "--mermaid", str(FIX / "er.mmd")])
            must(["diagram", "--home", str(home), "--id", "movement", "--kind", "flow", "--caption", "Landing window", "--mermaid", str(FIX / "flow.mmd")])
            must(["views", "--home", str(home), "--json", str(FIX / "views-ok.json")])
            rev = self._revision(home)
            must(["approve", "--home", str(home), "--stage", "business-model", "--revision", rev, "--date", "2026-11-08", "--yes"])
            proposed_before = (home / "proposed.md").read_bytes()
            confirmed_before = (home / "confirmed.md").read_bytes()
            exported = must(["report", "--home", str(home), "--now", "2026-11-08T12:00:00+00:00", "--kit", "1.118.0"])
            self.assertEqual((home / "proposed.md").read_bytes(), proposed_before)
            self.assertEqual((home / "confirmed.md").read_bytes(), confirmed_before)
            review = Path(exported["review"])
            md = (review / "report.md").read_text(encoding="utf-8")
            pdf = (review / "report.pdf").read_bytes()
            self.assertIn(f"Revision: {rev}", md)
            self.assertIn(f"Approved: business-model {rev}, 2026-11-08", md)
            self.assertIn("```mermaid", md)
            self.assertIn("erDiagram", md)
            self.assertIn("/Subtype /Image", pdf.decode("latin-1"))
            self.assertNotIn("erDiagram", pdf.split(b"/Subtype /Image", 1)[0].decode("latin-1"))
            self.assertGreater(pdf.count(b"/Subtype /Image"), 0)
            # A second export after a real model change is a new snapshot. The first bytes stay.
            qpath = home / "q.json"
            qpath.write_text(json.dumps({
                "id": "history-window",
                "affects": "docs/specs/orders/spec.md",
                "provider": "dispatch lead",
                "blocks": "order-line-grain",
                "body": "Is a year of as-was history required?",
            }), encoding="utf-8")
            must(["question", "--home", str(home), "--json", str(qpath)])
            second = must(["report", "--home", str(home), "--now", "2026-11-08T13:00:00+00:00", "--kit", "1.118.0"])
            self.assertNotEqual(second["review"], exported["review"])
            self.assertEqual((review / "report.md").read_bytes(), md.encode("utf-8"))
            self.assertEqual((review / "report.pdf").read_bytes(), pdf)
            brought = must(["feedback", "--home", str(home), "--review", str(review), "--comment", "Please show the restatement row.", "--decision", "order-line-grain"])
            self.assertFalse(brought["approved"])
            self.assertTrue(brought["confirmed_unchanged"])
            self.assertEqual((home / "confirmed.md").read_bytes(), confirmed_before)
            self.assertEqual((review / "report.md").read_bytes(), md.encode("utf-8"))
            self.assertIn("not an approval", (home / "proposed.md").read_text(encoding="utf-8"))
            bad = home / "bad.mmd"
            bad.write_text("sequenceDiagram\n    A->>B: no\n", encoding="utf-8")
            fails(["diagram", "--home", str(home), "--id", "seq", "--kind", "flow", "--caption", "no", "--mermaid", str(bad)], "diagram")
        finally:
            shutil.rmtree(home)

    def test_link_line_does_not_write_a_spec(self):
        payload = must(["link-line", "--name", "orders"])
        self.assertEqual(payload["line"], "Data model: docs/data-model/orders/")
        self.assertFalse((ROOT / "docs/data-model").exists())

    def _budget(self, home: Path):
        start = "2026-11-08T12:00:00+00:00"
        # Fresh run for the budget cases. The caller already began one; stop it via the time limit first.
        timed = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--now", "2026-11-08T12:20:00+00:00", "--stage", "business-model"])
        self.assertEqual(timed["stop"], "time")
        self.assertFalse(timed["applied"])
        self.assertTrue((home / "checkpoint.md").is_file())
        self.assertIn("not a live preemption", (home / "checkpoint.md").read_text(encoding="utf-8"))
        fails(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--now", "2026-11-08T12:21:00+00:00"], "resume")
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--now", start])
        first = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "0", "--progress", "yes", "--now", "2026-11-08T12:01:00+00:00", "--stage", "business-model"])
        self.assertEqual(first["stop"], "")
        stable = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "0", "--progress", "yes", "--now", "2026-11-08T12:02:00+00:00"])
        self.assertEqual(stable["stop"], "stable")
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--now", start])
        must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "2", "--progress", "yes", "--now", "2026-11-08T12:01:00+00:00"])
        stall = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "2", "--progress", "no", "--now", "2026-11-08T12:02:00+00:00"])
        self.assertEqual(stall["stop"], "stall")
        self.assertIn("Unfinished: yes", (home / "checkpoint.md").read_text(encoding="utf-8"))
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--now", start])
        must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--now", "2026-11-08T12:01:00+00:00", "--text", "Grain is the order line."])
        must(["auto-pass", "--home", str(home), "--fingerprint", "b", "--unresolved", "1", "--progress", "yes", "--now", "2026-11-08T12:02:00+00:00", "--text", "Use a shipment grain."])
        cycle = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--now", "2026-11-08T12:03:00+00:00", "--text", "Grain is the order line."])
        self.assertEqual(cycle["stop"], "cycle")
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--now", start])
        for n, stage in enumerate(["business-model", "business-model", "physical-design", "physical-design", "physical-design"], start=1):
            step = must([
                "auto-pass", "--home", str(home), "--fingerprint", f"p{n}", "--unresolved", "1",
                "--progress", "yes", "--now", f"2026-11-08T12:0{n}:00+00:00", "--stage", stage,
            ])
            self.assertEqual(step["passes_used"], n)
            self.assertEqual(step["stop"], "")
        capped = must(["auto-pass", "--home", str(home), "--fingerprint", "p6", "--unresolved", "1", "--progress", "yes", "--now", "2026-11-08T12:06:00+00:00", "--stage", "physical-design"])
        self.assertEqual(capped["stop"], "passes")
        self.assertFalse(capped["applied"])
        self.assertEqual(capped["passes_used"], 5)
        self.assertIn("not reset", capped["note"])

    def _init(self, flow: str) -> Path:
        home = Path(tempfile.mkdtemp())
        shutil.rmtree(home)
        must(["init", "--home", str(home), "--name", "orders", "--flow", flow])
        return home

    def _revision(self, home: Path) -> str:
        for line in (home / "index.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("- Revision: "):
                return line.split(": ", 1)[1]
        raise AssertionError("no revision")

    def _block(self, home: Path, decision: str) -> str:
        text = (home / "proposed.md").read_text(encoding="utf-8")
        marker = f"### {decision}\n"
        start = text.find(marker)
        if start < 0:
            raise AssertionError(decision)
        rest = text.find("\n### ", start + 1)
        return text[start:] if rest < 0 else text[start:rest]

    def _decision(self, did: str, stage: str, sources: str = "docs/specs/orders/spec.md", depends: str = "none", measure: str = "ordered amount", grain: str = "one order line", scope: str = "area:orders") -> Path:
        path = Path(tempfile.mkdtemp()) / f"{did}.json"
        path.write_text(json.dumps({
            "id": did,
            "stage": stage,
            "status": "proposed",
            "evidence": "requirement",
            "requirement": "supported",
            "fit": "meets",
            "outcome": "viable-on-evidence",
            "scope": scope,
            "axis": "modeling",
            "sources": sources,
            "depends": depends,
            "conditional": False,
            "implementable": stage == "physical-design",
            "grain": grain,
            "measure": measure,
            "short_source": sources,
            "body": f"{did} is one row at the stated grain.",
        }), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
