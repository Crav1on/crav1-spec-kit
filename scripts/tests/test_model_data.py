"""Synthetic checks for /crav1-model-data.

These tests run the skill's state script on fixture files. They are not a live
agent replay and they do not claim a modeling method was empirically validated.
A rendered diagram proves the exporter drew pixels, not that a notation is official.
"""

from __future__ import annotations

import json
import re
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
            must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", "2026-11-08T12:00:00+00:00"])
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
            exported = must(["report", "--home", str(home), "--test-clock", "--now", "2026-11-08T12:00:00+00:00", "--kit", "1.118.0"])
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
            second = must(["report", "--home", str(home), "--test-clock", "--now", "2026-11-08T13:00:00+00:00", "--kit", "1.118.0"])
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

    def test_revise_keeps_history_and_refuses_a_hand_edit(self):
        home = self._init("auto")
        try:
            made = must(["decide", "--home", str(home), "--json", str(self._decision("order-line-grain", "business-model"))])
            original = (home / "proposed.md").read_text(encoding="utf-8")
            (home / "proposed.md").write_text(original.replace("one row", "HAND EDIT"), encoding="utf-8")
            refused = fails(["drift", "--home", str(home), "--root", str(REPO)], "hand-edit")
            self.assertIn("proposed.md", refused["error"])
            self.assertIn("revise --id", refused["error"])
            self.assertIn("history.md", refused["error"])
            (home / "proposed.md").write_text(original, encoding="utf-8")
            must(["drift", "--home", str(home), "--root", str(REPO)])
            body = json.loads(self._decision("order-line-grain", "business-model").read_text(encoding="utf-8"))
            body["status"] = "confirmed"
            body["sources"] = "docs/specs/orders/spec.md, docs/specs/billing/spec.md"
            body["body"] = "The grain stays one order line, and billing is now a source."
            path = home / "revise-decision.json"
            path.write_text(json.dumps(body), encoding="utf-8")
            must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", "2026-11-09T12:00:00+00:00"])
            base = must([
                "auto-baseline", "--home", str(home), "--fingerprint", "base",
                "--test-clock", "--now", "2026-11-09T12:01:00+00:00",
            ])
            self.assertEqual(base["passes_used"], 0)
            revised = must([
                "revise", "--home", str(home), "--id", "order-line-grain",
                "--reason", "add the billing source", "--input", str(path),
            ])
            self.assertEqual(revised["status"], "proposed")
            self.assertEqual(revised["kind"], "decision")
            self.assertNotEqual(revised["revision"], made["revision"])
            self.assertFalse(revised["counted_as_pass"])
            self.assertEqual(revised["passes_used"], 0)
            self.assertEqual(revised["pass_effect"], "inside-current-pass")
            text = (home / "proposed.md").read_text(encoding="utf-8")
            self.assertIn("billing is now a source", text)
            self.assertIn("docs/specs/billing/spec.md", text)
            self.assertNotIn("- Status: confirmed", text)
            history = (home / "history.md").read_text(encoding="utf-8")
            self.assertIn(made["revision"], history)
            self.assertIn("add the billing source", history)
            self.assertIn("one row at the stated grain", history)
            step = must([
                "auto-pass", "--home", str(home), "--fingerprint", "fixed", "--unresolved", "1",
                "--progress", "yes", "--test-clock", "--now", "2026-11-09T12:02:00+00:00",
            ])
            self.assertEqual(step["passes_used"], 1)
            again = dict(body)
            again["body"] = "The grain stays one order line after the correction pass."
            path.write_text(json.dumps(again), encoding="utf-8")
            second = must([
                "revise", "--home", str(home), "--id", "order-line-grain",
                "--reason", "wording after the pass", "--input", str(path),
            ])
            self.assertEqual(second["passes_used"], 1)
            self.assertFalse(second["counted_as_pass"])
            must(["example", "--home", str(home), "--kind", "correction", "--json", str(FIX / "correction-ok.json")])
            example = json.loads((FIX / "correction-ok.json").read_text(encoding="utf-8"))
            example["kind"] = "correction"
            example["narrative"] = "Corrected narrative for the restatement."
            epath = home / "revise-example.json"
            epath.write_text(json.dumps(example), encoding="utf-8")
            ex = must([
                "revise", "--home", str(home), "--id", "correction",
                "--reason", "fix the worked example", "--input", str(epath),
            ])
            self.assertEqual(ex["kind"], "example")
            self.assertEqual(ex["status"], "proposed")
            self.assertIn("Corrected narrative", (home / "proposed.md").read_text(encoding="utf-8"))
            self.assertIn("fix the worked example", (home / "history.md").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(home)

    def test_content_goes_through_files_and_the_baseline_is_free(self):
        home = self._init("auto")
        try:
            fails(
                ["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "2", "--now", "2026-11-09T12:00:00+00:00"],
                "clock",
            )
            must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "2", "--test-clock", "--now", "2026-11-09T12:00:00+00:00"])
            big = home / "proposal.txt"
            big.write_text("Grain is the order line.\n" * 2000, encoding="utf-8")
            self.assertGreater(big.stat().st_size, 32767)
            argv = [
                "auto-pass", "--home", str(home), "--fingerprint", "base", "--unresolved", "1",
                "--progress", "yes", "--text-file", str(big),
                "--test-clock", "--now", "2026-11-09T12:01:00+00:00",
            ]
            joined = " ".join([sys.executable, str(SCRIPT), *argv])
            self.assertLess(len(joined), 32767)
            first = must(argv)
            self.assertTrue(first["baseline"])
            self.assertEqual(first["passes_used"], 0)
            self.assertFalse(first["counted_as_pass"])
            fails(
                ["auto-baseline", "--home", str(home), "--fingerprint", "again", "--test-clock", "--now", "2026-11-09T12:01:30+00:00"],
                "baseline",
            )
            must(["recommend", "--home", str(home), "--input", str(FIX / "retain-poor-docs.json")])
            for n in (1, 2):
                step = must([
                    "auto-pass", "--home", str(home), "--fingerprint", f"c{n}", "--unresolved", "1",
                    "--progress", "yes", "--test-clock", "--now", f"2026-11-09T12:0{n + 1}:00+00:00",
                ])
                self.assertEqual(step["passes_used"], n)
                self.assertFalse(step["baseline"])
            capped = must([
                "auto-pass", "--home", str(home), "--fingerprint", "c3", "--unresolved", "1",
                "--progress", "yes", "--test-clock", "--now", "2026-11-09T12:04:00+00:00",
            ])
            self.assertEqual(capped["stop"], "passes")
            self.assertEqual(capped["passes_used"], 2)
            self.assertFalse(capped["applied"])
        finally:
            shutil.rmtree(home)

    def test_report_is_built_from_saved_records(self):
        home = self._init("auto")
        try:
            must(["decide", "--home", str(home), "--json", str(self._decision("order-line-grain", "business-model"))])
            must(["recommend", "--home", str(home), "--json", str(FIX / "retain-poor-docs.json")])
            qpath = home / "q.json"
            qpath.write_text(json.dumps({
                "id": "history-window",
                "affects": "docs/specs/orders/spec.md",
                "provider": "dispatch lead",
                "blocks": "order-line-grain",
                "body": "Is a year of as-was history required?",
            }), encoding="utf-8")
            must(["question", "--home", str(home), "--json", str(qpath)])
            views = {
                "area_obligations": ["keep the local rule"],
                "platform_obligations": ["keep the local rule", "platform only rule"],
                "promoted_to_platform_rule": False,
                "default_view": None,
            }
            vpath = home / "views.json"
            vpath.write_text(json.dumps(views), encoding="utf-8")
            must(["views", "--home", str(home), "--input", str(vpath)])
            must(["diagram", "--home", str(home), "--id", "structure", "--kind", "er", "--caption", "Order and line", "--mermaid", str(FIX / "er.mmd")])
            must(["diagram", "--home", str(home), "--id", "movement", "--kind", "flow", "--caption", "Landing window", "--mermaid", str(FIX / "flow.mmd")])
            must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", "2026-11-09T10:25:00+00:00"])
            must(["auto-pass", "--home", str(home), "--fingerprint", "base", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-09T10:26:00+00:00"])
            stall = must(["auto-pass", "--home", str(home), "--fingerprint", "base", "--unresolved", "1", "--progress", "no", "--test-clock", "--now", "2026-11-09T10:31:00+00:00"])
            self.assertEqual(stall["stop"], "stall")
            exported = must(["report", "--home", str(home), "--test-clock", "--now", "2026-11-09T10:52:00+00:00", "--kit", "1.121.0"])
            md = (Path(exported["review"]) / "report.md").read_text(encoding="utf-8")
            pdf = (Path(exported["review"]) / "report.pdf").read_bytes()
            h1 = [line for line in md.splitlines() if line.startswith("# ") and not line.startswith("##")]
            self.assertEqual(h1, ["# Data model review: orders"])
            self.assertEqual(sum(line.strip() == "## Diagrams" for line in md.splitlines()), 1)
            self.assertEqual(sum(line.strip() == "## Transition" for line in md.splitlines()), 1)
            self.assertFalse(any(line.startswith("# Proposed") or line.startswith("# Confirmed") or line.startswith("# Questions") or line.startswith("# Comparisons") for line in md.splitlines()))
            self.assertNotIn("Current No stage is approved.", md)
            self.assertIn("Nothing confirmed yet.", md)
            self.assertIn("None yet.", md)
            self.assertIn("Nothing recorded yet.", md)
            self.assertRegex(md, r"Report: report-data-model-full · 2026-11-09 · kit 1.121.0")
            self.assertLess(md.index("Run: flow auto, stop stall, passes 1 of 5, minutes 6 of 20, checkpoint written."), md.index("## Summary"))
            self.assertLess(md.index("## Worked examples"), md.index("## Questions"))
            self.assertEqual(md.count("keep the local rule"), 1)
            self.assertEqual(md.count("platform only rule"), 1)
            self.assertIn("Is a year of as-was history required?", md)
            self.assertIn("current orders grain", md)
            prose = self._pdf_text(pdf)
            self.assertIn("Run: flow auto, stop stall", prose)
            self.assertIn("current orders grain", prose)
            self.assertIn("one row at the stated grain", prose)
            self.assertIn("Is a year of as-was history required?", prose)
            self.assertIn("structure", prose)
            self.assertIn("movement", prose)
            self.assertNotIn("Diagram 1", prose)
            self.assertNotIn("Current No stage is approved.", prose)
            # An older model with no integrity section is still readable.
            index = (home / "index.md").read_text(encoding="utf-8")
            (home / "index.md").write_text(index.split("\n## Integrity\n", 1)[0], encoding="utf-8")
            must(["example", "--home", str(home), "--kind", "correction", "--json", str(FIX / "correction-ok.json")])
            second = must(["report", "--home", str(home), "--test-clock", "--now", "2026-11-09T11:00:00+00:00", "--kit", "1.121.0"])
            self.assertNotEqual(second["review"], exported["review"])
            self.assertEqual((Path(exported["review"]) / "report.md").read_text(encoding="utf-8"), md)
            later = (Path(second["review"]) / "report.md").read_text(encoding="utf-8")
            self.assertIn("The correction keeps the prior amount", later)
            self.assertIn("The correction keeps the prior amount", self._pdf_text((Path(second["review"]) / "report.pdf").read_bytes()))
            self.assertNotIn("Nothing recorded yet.", later)
        finally:
            shutil.rmtree(home)

    def test_pdf_diagrams_wrap_use_landscape_and_split(self):
        home = self._init("manual")
        try:
            must(["decide", "--home", str(home), "--json", str(self._decision("order-line-grain", "business-model"))])
            wide = home / "wide.mmd"
            lines = ["erDiagram"]
            for i in range(8):
                lines.append(f"E{i} {{")
                for attr in range(4):
                    lines.append(f"string field{attr}")
                lines.append("}")
                if i:
                    lines.append(f"E{i - 1} ||--o{{ E{i} : link")
            wide.write_text("\n".join(lines) + "\n", encoding="utf-8")
            flow = home / "flow.mmd"
            nodes = ["flowchart LR"]
            for i in range(9):
                nodes.append(f"N{i}[Node {i}] --> N{i + 1}[Node {i + 1}]")
            flow.write_text("\n".join(nodes) + "\n", encoding="utf-8")
            must(["diagram", "--home", str(home), "--id", "platform-structure", "--kind", "er", "--caption", "Wide structure", "--mermaid", str(wide)])
            must(["diagram", "--home", str(home), "--id", "platform-movement", "--kind", "flow", "--caption", "Wide movement", "--mermaid", str(flow)])
            exported = must(["report", "--home", str(home), "--test-clock", "--now", "2026-11-09T12:00:00+00:00", "--kit", "1.121.0"])
            pdf = (Path(exported["review"]) / "report.pdf").read_bytes()
            prose = self._pdf_text(pdf)
            self.assertIn("platform-structure (part 1 of 2)", prose)
            self.assertIn("platform-structure (part 2 of 2)", prose)
            self.assertIn("split into numbered parts", prose)
            self.assertNotIn("Diagram 1", prose)
            self.assertIn(b"/MediaBox [0 0 792 612]", pdf)
            sizes = [(int(w), int(h)) for w, h in re.findall(rb"/Width (\d+) /Height (\d+)", pdf)]
            draws = [(float(w), float(h)) for w, h in re.findall(rb"q ([0-9.]+) 0 0 ([0-9.]+) ", pdf)]
            self.assertGreaterEqual(len(sizes), 2)
            self.assertTrue(all(w <= 720 for w, _h in sizes))
            self.assertLess(max(w for w, _h in sizes), 8 * 180)
            self.assertGreater(max(h for _w, h in sizes), 150)
            for (dw, dh), (w, h) in zip(draws, sizes):
                self.assertGreaterEqual(dw / w, 0.57)
                self.assertGreaterEqual((dh / h) * 14, 8)
        finally:
            shutil.rmtree(home)

    def test_unknown_history_coverage_and_a_lean_on_a_tie(self):
        unknown = {
            "retained_days": 405,
            "needed_days": 2230,
            "other_source": True,
            "claim": "can-reconstruct",
        }
        path = Path(tempfile.mkdtemp()) / "unknown.json"
        path.write_text(json.dumps(unknown), encoding="utf-8")
        result = must(["example", "--kind", "history-window", "--json", str(path)])
        self.assertEqual(result["result"], "question")
        self.assertTrue(result["open_question"])
        dated = dict(unknown)
        dated["other_source_from"] = "2020-10-01"
        path.write_text(json.dumps(dated), encoding="utf-8")
        dated_result = must(["example", "--kind", "history-window", "--json", str(path)])
        self.assertEqual(dated_result["result"], "question")
        covered = dict(unknown)
        covered["other_source_days"] = 2000
        path.write_text(json.dumps(covered), encoding="utf-8")
        self.assertEqual(must(["example", "--kind", "history-window", "--json", str(path)])["result"], "ok")
        short = dict(unknown)
        short["other_source_days"] = 10
        path.write_text(json.dumps(short), encoding="utf-8")
        self.assertEqual(must(["example", "--kind", "history-window", "--json", str(path)])["result"], "gap")
        home = self._init("manual")
        root = Path(tempfile.mkdtemp())
        try:
            unknown_path = home / "unknown.json"
            unknown_path.write_text(json.dumps(unknown), encoding="utf-8")
            stored = must(["example", "--home", str(home), "--kind", "history-window", "--json", str(unknown_path)])
            self.assertEqual(stored["result"], "question")
            self.assertIn("history-window-coverage", (home / "questions.md").read_text(encoding="utf-8"))
            body = json.loads(self._decision("storage-layout", "business-model").read_text(encoding="utf-8"))
            body["outcome"] = "tie"
            body["axis"] = "storage"
            (home / "tie.json").write_text(json.dumps(body), encoding="utf-8")
            must(["decide", "--home", str(home), "--json", str(home / "tie.json")])
            rec = {
                "recommendation": "targeted",
                "existing_meets_need": True,
                "documentation": "poor",
                "provisional": True,
                "decision_changing_gaps": ["storage"],
                "best_fit": "shared database",
                "axis": "storage",
                "reason": "Keep the shared database for operational feeds.",
            }
            (home / "rec.json").write_text(json.dumps(rec), encoding="utf-8")
            must(["recommend", "--home", str(home), "--input", str(home / "rec.json")])
            shutil.copytree(REPO, root, dirs_exist_ok=True)
            flagged = must(["drift", "--home", str(home), "--root", str(root)])
            self.assertTrue(any("storage-layout" in item and "tie" in item for item in flagged["internal"]))
            rec["reason"] = "tie on axis storage excluded from best fit"
            (home / "rec.json").write_text(json.dumps(rec), encoding="utf-8")
            must(["recommend", "--home", str(home), "--input", str(home / "rec.json")])
            clear = must(["drift", "--home", str(home), "--root", str(root)])
            self.assertFalse(any("storage-layout" in item for item in clear["internal"]))
        finally:
            shutil.rmtree(home)
            shutil.rmtree(root, ignore_errors=True)

    def test_link_line_does_not_write_a_spec(self):
        payload = must(["link-line", "--name", "orders"])
        self.assertEqual(payload["line"], "Data model: docs/data-model/orders/")
        self.assertFalse((ROOT / "docs/data-model").exists())

    def _pdf_text(self, pdf: bytes) -> str:
        raw = pdf.split(b"/Subtype /Image", 1)[0]
        parts = []
        for match in re.findall(br"\((?:\\.|[^\\)])*\) Tj", raw):
            inner = match[1:-4].replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
            parts.append(inner.decode("latin-1"))
        return "\n".join(parts)

    def _budget(self, home: Path):
        start = "2026-11-08T12:00:00+00:00"
        # Fresh run for the budget cases. The caller already began one; stop it via the time limit first.
        timed = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:20:00+00:00", "--stage", "business-model"])
        self.assertEqual(timed["stop"], "time")
        self.assertFalse(timed["applied"])
        self.assertTrue((home / "checkpoint.md").is_file())
        self.assertIn("not a live preemption", (home / "checkpoint.md").read_text(encoding="utf-8"))
        fails(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:21:00+00:00"], "resume")
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", start])
        first = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "0", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:01:00+00:00", "--stage", "business-model"])
        self.assertEqual(first["stop"], "")
        stable = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "0", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:02:00+00:00"])
        self.assertEqual(stable["stop"], "stable")
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", start])
        must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "2", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:01:00+00:00"])
        stall = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "2", "--progress", "no", "--test-clock", "--now", "2026-11-08T12:02:00+00:00"])
        self.assertEqual(stall["stop"], "stall")
        self.assertIn("Unfinished: yes", (home / "checkpoint.md").read_text(encoding="utf-8"))
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", start])
        must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:01:00+00:00", "--text", "Grain is the order line."])
        must(["auto-pass", "--home", str(home), "--fingerprint", "b", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:02:00+00:00", "--text", "Use a shipment grain."])
        cycle = must(["auto-pass", "--home", str(home), "--fingerprint", "a", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:03:00+00:00", "--text", "Grain is the order line."])
        self.assertEqual(cycle["stop"], "cycle")
        must(["auto-begin", "--home", str(home), "--minutes", "20", "--passes", "5", "--test-clock", "--now", start])
        baseline = must([
            "auto-pass", "--home", str(home), "--fingerprint", "base", "--unresolved", "1",
            "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:00:30+00:00", "--stage", "business-model",
        ])
        self.assertTrue(baseline["baseline"])
        self.assertEqual(baseline["passes_used"], 0)
        self.assertFalse(baseline["counted_as_pass"])
        for n, stage in enumerate(["business-model", "business-model", "physical-design", "physical-design", "physical-design"], start=1):
            step = must([
                "auto-pass", "--home", str(home), "--fingerprint", f"p{n}", "--unresolved", "1",
                "--progress", "yes", "--test-clock", "--now", f"2026-11-08T12:0{n}:00+00:00", "--stage", stage,
            ])
            self.assertFalse(step["baseline"])
            self.assertEqual(step["passes_used"], n)
            self.assertEqual(step["stop"], "")
        capped = must(["auto-pass", "--home", str(home), "--fingerprint", "p6", "--unresolved", "1", "--progress", "yes", "--test-clock", "--now", "2026-11-08T12:06:00+00:00", "--stage", "physical-design"])
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
