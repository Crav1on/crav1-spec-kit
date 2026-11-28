"""1.211.0: the UI design step, per-screen sign-off, and the plan gate.

Generic fixtures only: orders-dashboard, the product owner, Alex.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
SKILL = SK / "crav1-design-ui"
UI = SKILL / "scripts/ui_screens.py"
APPROVAL = SK / "crav1-record-approval/scripts/approval_needed.py"
TODAY = "2026-11-28"
PERSON = "the product owner"

SPEC = """# Spec: orders dashboard

The orders dashboard screen lists recent orders.

## Acceptance criteria

- [ ] The dashboard lists orders.

## Open questions

- None.
"""

EXPERIENCE = """# UI experience: orders dashboard

## Screens

### Orders list (S1)

Path: /orders

#### States

- Empty: shows "No orders yet" and a New order button.
- Loading: shows a skeleton list.
- Error: says the orders could not load and offers Retry.
- Full of data: shows 50 rows and a pager.

#### Interactions

- Click a row: opens the order detail.
- Keyboard: Tab moves between rows; Enter opens the order.

#### Checks

- [ ] With no orders, the list shows "No orders yet" and a New order button. (S1-C1)
- [ ] When loading fails, the list says so and offers Retry. (S1-C2)
"""

SECOND = """
### Order detail (S2)

Path: /orders/:id

#### States

- Loading: shows a spinner.
- Error: says the order could not load.

#### Checks

- [ ] The detail shows the order total. (S2-C1)
"""

DESIGN = """# UI design: orders dashboard

## Look

Calm and dense.

## Tokens

```yaml
colors:
  primary: "#2457c5"
```

## Screens

### Orders list (S1)

#### Layout

Header with the title and a New order button, then filters, then the list.
"""


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ui = load(UI, "ui_screens_1211")
an = load(APPROVAL, "approval_needed_1211")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(UI), *args], capture_output=True, text=True, encoding="utf-8")


def approve(spec_path: Path, item: str) -> None:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(APPROVAL), "write", "--root", str(spec_path.parent),
         "--person", PERSON, "--source-date", "2026-11-27", "--source", "meeting",
         "--quote", "Looks right, go ahead.", "--recorder", "Alex", "--accepted", TODAY,
         "--item", item, "--yes"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


class Slice:
    def __init__(self, experience: str = EXPERIENCE, design: str = DESIGN, spec: str = SPEC):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "docs/specs/orders-dashboard"
        (self.root / "ui").mkdir(parents=True)
        (self.root / "spec.md").write_text(spec, encoding="utf-8")
        if experience is not None:
            (self.root / "ui/experience.md").write_text(experience, encoding="utf-8")
        if design is not None:
            (self.root / "ui/design.md").write_text(design, encoding="utf-8")

    def spec(self) -> str:
        return (self.root / "spec.md").read_text(encoding="utf-8")

    def sync(self) -> dict:
        proc = run("sync", "--root", str(self.root), "--person", PERSON, "--today", TODAY, "--yes")
        return json.loads(proc.stdout)

    def gate(self) -> dict:
        return json.loads(run("gate", "--root", str(self.root)).stdout)

    def edit(self, old: str, new: str, name: str = "ui/experience.md") -> None:
        path = self.root / name
        text = path.read_text(encoding="utf-8")
        self.assert_in(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    @staticmethod
    def assert_in(part: str, whole: str) -> None:
        assert part in whole, part

    def close(self) -> None:
        self.tmp.cleanup()


class ApprovalGateBeforePlan(unittest.TestCase):
    def setUp(self):
        self.s = Slice()

    def tearDown(self):
        self.s.close()

    def test_no_yes_stops_the_plan_and_names_both_commands(self):
        gate = self.s.gate()
        self.assertFalse(gate["ok"])
        self.assertEqual(gate["plan"], "stop")
        self.assertIn("/crav1-design-ui orders-dashboard", gate["run_next"])
        self.assertIn("/crav1-record-approval", gate["run_next"])
        self.assertTrue(gate["run_next"].startswith("Run next:"))

    def test_items_written_but_not_approved_still_stops(self):
        self.s.sync()
        gate = self.s.gate()
        self.assertFalse(gate["ok"])
        self.assertTrue(gate["run_next"].index("/crav1-record-approval") < gate["run_next"].index("/crav1-design-ui"))

    def test_approved_screen_opens_the_plan(self):
        self.s.sync()
        approve(self.s.root / "spec.md", "UI screen Orders list (S1)")
        gate = self.s.gate()
        self.assertTrue(gate["ok"], gate)
        self.assertEqual(gate["approved"], ["Orders list (S1)"])
        self.assertIsNone(gate["run_next"])

    def test_text_mode_prints_lines_and_run_next(self):
        out = run("gate", "--root", str(self.s.root), "--text").stdout
        self.assertIn("No UI screen is signed off yet", out)
        self.assertIn("Run next:", out)

    def test_design_step_never_writes_approved(self):
        self.s.sync()
        self.assertNotIn("Approved:", self.s.spec())

    def test_sync_without_yes_writes_nothing(self):
        before = self.s.spec()
        proc = run("sync", "--root", str(self.s.root), "--person", PERSON, "--today", TODAY)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self.s.spec(), before)
        self.assertEqual(json.loads(proc.stdout)["actions"][0]["do"], "add-item")


class UiPresence(unittest.TestCase):
    def test_ui_none_line_skips_the_gate(self):
        s = Slice(experience=None, design=None, spec=SPEC.replace("# Spec: orders dashboard\n", "# Spec: orders dashboard\n\nUI: none (a nightly export job)\n"))
        try:
            (s.root / "ui").rmdir()
            gate = s.gate()
            self.assertTrue(gate["ok"])
            self.assertEqual(gate["ui"], "no")
            self.assertEqual(gate["plan"], "whole slice")
        finally:
            s.close()

    def test_ui_words_without_files_is_unclear_and_stops(self):
        s = Slice(experience=None, design=None)
        try:
            (s.root / "ui").rmdir()
            gate = s.gate()
            self.assertEqual(gate["ui"], "unclear")
            self.assertFalse(gate["ok"])
            self.assertIn("/crav1-design-ui orders-dashboard", gate["run_next"])
        finally:
            s.close()

    def test_no_ui_words_no_files_is_no_ui(self):
        s = Slice(experience=None, design=None, spec="# Spec: export\n\nA nightly job writes a CSV file.\n")
        try:
            (s.root / "ui").rmdir()
            self.assertEqual(s.gate()["ui"], "no")
        finally:
            s.close()

    def test_template_placeholders_are_not_screens(self):
        template = (ROOT / "docs/specs/_template/ui/experience.md").read_text(encoding="utf-8")
        s = Slice(experience=template, design=(ROOT / "docs/specs/_template/ui/design.md").read_text(encoding="utf-8"))
        try:
            self.assertEqual(ui.screens(s.root), [])
            self.assertEqual(s.gate()["ui"], "unclear")
        finally:
            s.close()


class PerScreenClear(unittest.TestCase):
    def setUp(self):
        self.s = Slice(experience=EXPERIENCE + SECOND)
        self.s.sync()
        approve(self.s.root / "spec.md", "UI screen Orders list (S1)")
        approve(self.s.root / "spec.md", "UI screen Order detail (S2)")
        self.assertEqual(sorted(self.s.gate()["approved"]), ["Order detail (S2)", "Orders list (S1)"])

    def tearDown(self):
        self.s.close()

    def state(self, sid: str) -> dict:
        data = json.loads(run("status", "--root", str(self.s.root)).stdout)
        return next(r for r in data["screens"] if r["id"] == sid)

    def test_typo_keeps_the_yes_and_says_why(self):
        self.s.edit("shows a skeleton list", "shows a skeleten list")
        row = self.state("S1")
        self.assertEqual(row["state"], "approved")
        self.assertEqual(row["change"], "minor")
        self.assertIn("spelling", row["why"])
        result = self.s.sync()
        self.assertIn("not a material change", " ".join(result["wrote"]))
        self.assertNotIn("Cleared:", self.s.spec())
        self.assertEqual(self.state("S1")["change"], "unchanged")

    def test_case_and_punctuation_keep_the_yes(self):
        self.s.edit("opens the order detail.", "Opens the order detail")
        self.assertEqual(self.state("S1")["change"], "minor")

    def test_non_ui_edit_keeps_every_yes(self):
        spec = self.s.root / "spec.md"
        spec.write_text(self.s.spec().replace("lists recent orders", "lists the recent orders"), encoding="utf-8")
        self.s.edit("Calm and dense.", "Calm, dense, and quiet.", name="ui/design.md")
        self.assertEqual(self.state("S1")["state"], "approved")
        self.assertEqual(self.state("S1")["change"], "unchanged")

    def test_new_state_is_material_and_clears_only_that_screen(self):
        self.s.edit("- Full of data:", "- Offline: shows the last list with an Offline banner.\n- Full of data:")
        row = self.state("S1")
        self.assertEqual(row["state"], "changed")
        self.assertIn("the states changed", row["why"])
        gate = self.s.gate()
        self.assertTrue(gate["ok"])
        self.assertEqual(gate["approved"], ["Order detail (S2)"])
        self.assertIn("Orders list (S1)", " ".join(gate["lines"]))
        result = self.s.sync()
        self.assertIn("material change", " ".join(result["wrote"]))
        text = self.s.spec()
        self.assertIn(f"  - Cleared: {TODAY}, material change: the states changed", text)
        self.assertEqual(text.count("Approved:"), 2, "the old Approved line stays in the file")
        self.assertEqual(self.state("S1")["state"], "waiting")
        approve(self.s.root / "spec.md", "UI screen Orders list (S1)")
        self.assertEqual(self.state("S1")["state"], "approved")

    def test_interaction_change_is_material(self):
        self.s.edit("Enter opens the order.", "Enter opens the order in a new window.")
        self.assertEqual(self.state("S1")["change"], "material")
        self.assertIn("interactions", self.state("S1")["why"])

    def test_layout_change_is_material(self):
        self.s.edit("then filters, then the list.", "then the list, with filters in a side panel.", name="ui/design.md")
        row = self.state("S1")
        self.assertEqual(row["state"], "changed")
        self.assertIn("layout", row["why"])

    def test_path_change_is_material(self):
        self.s.edit("Path: /orders\n", "Path: /orders/all\n")
        self.assertIn("path", self.state("S1")["why"])

    def test_rename_is_material_and_renames_the_item(self):
        self.s.edit("### Orders list (S1)", "### Recent orders (S1)")
        self.s.edit("### Orders list (S1)", "### Recent orders (S1)", name="ui/design.md")
        self.assertEqual(self.state("S1")["state"], "changed")
        self.assertIn("name", self.state("S1")["why"])
        self.s.sync()
        self.assertIn("- UI screen Recent orders (S1):", self.s.spec())

    def test_cleared_line_drops_earlier_approved_lines_in_approval_needed(self):
        self.s.edit("- Empty:", "- Archived: shows archived orders greyed out.\n- Empty:")
        self.s.sync()
        rows = {r["text"].split(":")[0]: r for r in an.items(self.s.spec())}
        self.assertFalse(rows["UI screen Orders list (S1)"]["approved"])
        self.assertTrue(rows["UI screen Orders list (S1)"]["cleared"])
        self.assertTrue(rows["UI screen Order detail (S2)"]["approved"])


class NewScreenOwnItem(unittest.TestCase):
    def test_new_screen_adds_an_item_and_earlier_yes_stays(self):
        s = Slice()
        try:
            s.sync()
            approve(s.root / "spec.md", "UI screen Orders list (S1)")
            s.edit("(S1-C2)\n", "(S1-C2)\n" + SECOND)
            result = s.sync()
            self.assertIn("New screen Order detail (S2)", " ".join(result["wrote"]))
            text = s.spec()
            self.assertEqual(text.count("- UI screen "), 2)
            self.assertIn("  - Holds: none (UI screen S2; the plan waits for this yes)", text)
            gate = s.gate()
            self.assertTrue(gate["ok"])
            self.assertEqual(gate["approved"], ["Orders list (S1)"])
            self.assertIn("Not planned until their yes: Order detail (S2).", gate["lines"])
            again = s.sync()
            self.assertEqual(again["wrote"], [])
            self.assertEqual(s.spec().count("- UI screen "), 2)
        finally:
            s.close()

    def test_new_screen_needs_a_person(self):
        s = Slice()
        try:
            proc = run("sync", "--root", str(s.root), "--today", TODAY, "--yes")
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["code"], "person")
        finally:
            s.close()

    def test_item_uses_the_approval_needed_add_item_path(self):
        source = UI.read_text(encoding="utf-8")
        self.assertIn("an.add_item(", source)
        self.assertIn("crav1-record-approval", source)
        self.assertNotIn("Approved: ", re.sub(r'"""[\s\S]*?"""', "", source).replace("Approved: lines", ""))


class NoBinariesUnderUi(unittest.TestCase):
    def test_binary_under_ui_blocks_sync_and_gate(self):
        s = Slice()
        try:
            (s.root / "ui/feedback.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")
            proc = run("sync", "--root", str(s.root), "--person", PERSON, "--today", TODAY, "--yes")
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["code"], "binaries")
            self.assertNotIn("- UI screen ", s.spec())
            gate = s.gate()
            self.assertFalse(gate["ok"])
            self.assertIn("ui/feedback.png", " ".join(gate["lines"]))
        finally:
            s.close()

    def test_html_mock_is_text_and_not_a_screen_source(self):
        s = Slice()
        try:
            (s.root / "ui/mock").mkdir()
            (s.root / "ui/mock/index.html").write_text("<h3>### Hidden (S9)</h3>\n", encoding="utf-8")
            self.assertEqual(ui.binaries(s.root), [])
            self.assertEqual([x["id"] for x in ui.screens(s.root)], ["S1"])
        finally:
            s.close()

    def test_templates_and_skill_ship_no_binaries(self):
        for folder in (SKILL, ROOT / "docs/specs/_template/ui"):
            for path in folder.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    self.assertNotIn(path.suffix.lower(), ui.BINARY_SUFFIXES, path)
                    self.assertNotIn(b"\x00", path.read_bytes(), path)


class TraceAndTouches(unittest.TestCase):
    def test_trace_lists_checks_of_approved_screens_with_no_task(self):
        s = Slice(experience=EXPERIENCE + SECOND)
        try:
            s.sync()
            approve(s.root / "spec.md", "UI screen Orders list (S1)")
            (s.root / "tasks.md").write_text(
                "# Tasks\n\n- [ ] T1: Empty list (verify: ui — no orders shows the message) (spec: ui/experience.md S1-C1)\n"
                "- [ ] T2: Detail total (verify: ui — total shows) (spec: ui/experience.md S2-C1)\n",
                encoding="utf-8",
            )
            out = json.loads(run("trace", "--root", str(s.root)).stdout)
            self.assertEqual(out["ui_tasks"], ["T1", "T2"])
            self.assertEqual(len(out["untraced"]), 1)
            self.assertIn("(S1-C2)", out["untraced"][0])
            self.assertIn("S2-C1 of Order detail (S2)", out["unapproved"][0])
            self.assertFalse(out["ok"])
        finally:
            s.close()

    def test_touches_warns_for_a_signed_off_screen(self):
        s = Slice()
        try:
            s.sync()
            approve(s.root / "spec.md", "UI screen Orders list (S1)")
            out = json.loads(run("touches", "--root", str(s.root), "--text", "The orders list hides cancelled orders.").stdout)
            self.assertEqual(out["touched"], ["Orders list (S1)"])
            self.assertIn("signed-off screen Orders list (S1)", out["lines"][0])
            quiet = json.loads(run("touches", "--root", str(s.root), "--text", "Refunds go to the ledger.").stdout)
            self.assertEqual(quiet["touched"], [])
        finally:
            s.close()


class PlanCheckUiKind(unittest.TestCase):
    def test_ui_is_a_verify_kind(self):
        plan_check = load(SK / "crav1-plan-from-spec/scripts/plan_check.py", "plan_check_1211")
        self.assertIn("ui", plan_check.KINDS)
        line = "- [ ] T1: Empty list (verify: ui — no orders shows the message) (spec: ui/experience.md S1-C1)\n"
        self.assertEqual(plan_check.line_problems(line), [])


class SkillsYamlAndDocs(unittest.TestCase):
    def setUp(self):
        self.data = yaml.safe_load((ROOT / "docs/reference/skills.yaml").read_text(encoding="utf-8"))
        self.entry = next(s for s in self.data["skills"] if s["name"] == "crav1-design-ui")

    def test_entry_and_choice_words(self):
        words = [w["word"] for q in self.entry["choice_words"] for w in q["words"]]
        self.assertEqual(words, ["with-mock", "skip-mock"])
        self.assertEqual(self.entry["lane"], "specify")
        self.assertEqual(self.entry["group"], "Specify")
        self.assertFalse(self.entry["starter"])
        self.assertEqual(self.entry["since"], "1.211.0")
        self.assertEqual(self.entry["walkthrough"], "docs/from-design-ui.md")
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for word in words:
            self.assertIn(f"`{word}`", body)

    def test_entry_sits_next_to_plan_from_spec(self):
        names = [s["name"] for s in self.data["skills"]]
        self.assertEqual(names.index("crav1-design-ui") + 1, names.index("crav1-plan-from-spec"))

    def test_starters_unchanged(self):
        self.assertEqual(self.data["starter_options"], [
            "crav1-spark-to-spec", "crav1-ideas-to-spec", "crav1-bundle-to-specs",
            "crav1-existing-to-specs", "crav1-read-environment", "crav1-fix-bug",
        ])

    def test_skill_md_size_and_description(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        front = text.split("---", 2)[1]
        desc = yaml.safe_load(front)["description"]
        self.assertLessEqual(len(desc.split()), 60)
        self.assertLess(len(text.split()), 2000)
        self.assertIn("disable-model-invocation: true", front)

    def test_route_puts_design_ui_before_plan(self):
        wf = yaml.safe_load((ROOT / "docs/reference/workflow.yaml").read_text(encoding="utf-8"))
        steps = next(r for r in wf["routes"] if r["id"] == "new-slice")["steps"]
        flat = [s["skills"] for s in steps]
        at = flat.index(["crav1-design-ui"])
        self.assertTrue(steps[at].get("optional"))
        self.assertEqual(flat[at + 1], ["crav1-plan-from-spec"])
        self.assertLess(flat.index(["crav1-resolve-open-questions"]), at)

    def test_walkthrough_links_back(self):
        text = (ROOT / "docs/from-design-ui.md").read_text(encoding="utf-8")
        self.assertIn("reference/skills/crav1-design-ui.md", text)
        self.assertIn("from-design-ui.md", (ROOT / "docs/README.md").read_text(encoding="utf-8"))

    def test_plan_and_walk_call_the_gate(self):
        plan = (SK / "crav1-plan-from-spec/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("ui_screens.py gate", plan)
        steps = (SK / "crav1-tighten-and-plan-ready-to-build/references/steps.md").read_text(encoding="utf-8")
        self.assertIn("Open `../crav1-design-ui/SKILL.md`", steps)
        self.assertIn("ui_screens.py", (SK / "crav1-add-to-spec/SKILL.md").read_text(encoding="utf-8"))

    def test_template_copies_listed(self):
        rows = (ROOT / "scripts/template-copies.tsv").read_text(encoding="utf-8")
        self.assertIn("crav1-design-ui/assets/design.md\tdocs/specs/_template/ui/design.md", rows)
        self.assertIn("crav1-design-ui/assets/experience.md\tdocs/specs/_template/ui/experience.md", rows)

    def test_version_stamped(self):
        plugin = json.loads((ROOT / "plugins/crav1/.cursor-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], "1.211.0")
        self.assertTrue((ROOT / "CHANGELOG.md").read_text(encoding="utf-8").split("\n## ", 1)[1].startswith("1.211.0 (2026-11-28)"))


if __name__ == "__main__":
    unittest.main()
