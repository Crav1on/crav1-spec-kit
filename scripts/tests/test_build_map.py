"""Build map: one branch per plan step, waves, who, and the build-map word (1.128.0)."""
import importlib.util
import pathlib
import re
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_map_wrapper", ROOT / "scripts/build-map.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
bm = wrapper.load()

TASK_ID = re.compile(r"\bT\d+\b")

PLAN = """# Plan: Cancel a booking

## Approach

1. Record the refund decision. (T1, T2)
2. Send the receipt. (T3)

## Risks

- None for this slice.
"""

TASKS = """# Tasks

- [ ] T1: Persist the decision (verify: unit — saved) (spec: refund)
- [ ] T2: Reject an unknown booking (verify: unit — unknown) (spec: refund) (after: T1)
- [ ] T3: Email the receipt (verify: unit — sent) (spec: receipt) (after: T2)
"""

SPEC = """# Cancel a booking

## Open questions

- Which channel is used for the receipt?
  - Blocks: none
"""


def render(spec=SPEC, plan=PLAN, tasks=TASKS, slug="cancel-booking"):
    return bm.build(slug, spec, plan, tasks)


def mermaid(text):
    match = re.search(r"```mermaid\n(.*?)```", text, re.S)
    return match.group(1).strip() if match else ""


class BuildMap(unittest.TestCase):
    def test_default_groups_one_branch_per_step(self):
        result = render()
        text = result["markdown"]
        self.assertIn(bm.BY_STEP, text)
        self.assertNotIn(bm.NO_STEPS, text)
        self.assertIn("### feat/cancel-booking-record-refund-decision", text)
        self.assertIn("### feat/cancel-booking-send-receipt", text)
        self.assertNotIn("feat/cancel-extra", text)
        record = text.split("### feat/cancel-booking-record-refund-decision", 1)[1].split("###", 1)[0]
        self.assertIn("Persist the decision", record)
        self.assertIn("Reject an unknown booking", record)
        self.assertNotIn("Email the receipt", record)
        self.assertIsNone(TASK_ID.search(text))

    def test_override_moves_one_task_off_the_step_branch(self):
        tasks = TASKS.replace(
            "- [ ] T2: Reject an unknown booking (verify: unit — unknown) (spec: refund) (after: T1)",
            "- [ ] T2: Reject an unknown booking (verify: unit — unknown) (spec: refund) (after: T1) (map: feat/cancel-extra)",
        )
        text = render(tasks=tasks)["markdown"]
        self.assertIn("### feat/cancel-extra", text)
        record = text.split("### feat/cancel-booking-record-refund-decision", 1)[1].split("###", 1)[0]
        extra = text.split("### feat/cancel-extra", 1)[1].split("###", 1)[0]
        self.assertIn("Persist the decision", record)
        self.assertNotIn("Reject an unknown booking", record)
        self.assertIn("Reject an unknown booking", extra)
        self.assertIn("- Delivers: Reject an unknown booking", extra)
        receipt = text.split("### feat/cancel-booking-send-receipt", 1)[1]
        self.assertIn("Waits for: feat/cancel-extra", receipt)
        self.assertIsNone(TASK_ID.search(text))

    def test_waves_follow_branch_dependencies(self):
        text = render()["markdown"]
        wave1 = text.split("## Wave 1", 1)[1].split("## Wave 2", 1)[0]
        wave2 = text.split("## Wave 2", 1)[1]
        self.assertIn("feat/cancel-booking-record-refund-decision", wave1)
        self.assertNotIn("feat/cancel-booking-send-receipt", wave1)
        self.assertIn("feat/cancel-booking-send-receipt", wave2)
        self.assertIn("Waits for: feat/cancel-booking-record-refund-decision", wave2)
        self.assertIn("Ready now: ready", wave1)
        self.assertIn("Ready now: waits in order", wave2)
        diagram = mermaid(text)
        self.assertIn("flowchart LR", diagram)
        self.assertIn('subgraph w1["Wave 1"]', diagram)
        self.assertIn('subgraph w2["Wave 2"]', diagram)
        self.assertIn("direction TB", diagram)
        self.assertIn('b1["feat/cancel-booking-record-refund-decision"]', diagram)
        self.assertIn('b2["feat/cancel-booking-send-receipt"]', diagram)
        self.assertIn("b1 --> b2", diagram)
        self.assertIn("## Wave 1: 1 branch", text)
        self.assertIn("## Wave 2: 1 branch", text)

    def test_who_uses_waiting_for_then_latest_mark_then_unnamed(self):
        spec = """# Cancel a booking

## Open questions

- Waiting for the partner to confirm the currency?
  - Pending: 2026-10-01, for a colleague, mail.
  - Asked: 2026-10-02, mail to someone else.
  - Blocks: T1
- Which inbox receives the receipt?
  - Pending: 2026-10-03, for a colleague, mail.
  - Asked: 2026-10-04, mail to a colleague.
  - Blocks: T3
- Which locale is on the receipt?
  - Blocks: T2
"""
        text = render(spec=spec)["markdown"]
        record = text.split("### feat/cancel-booking-record-refund-decision", 1)[1].split("###", 1)[0]
        receipt = text.split("### feat/cancel-booking-send-receipt", 1)[1]
        self.assertIn("Waiting for the partner to confirm the currency? — the partner", record)
        self.assertIn("Which locale is on the receipt? — not named yet", record)
        self.assertIn("Which inbox receives the receipt? — a colleague", receipt)
        self.assertIn("Ready now: waiting on a question", record)
        self.assertIsNone(TASK_ID.search(text))

    def test_readiness_states(self):
        waiting = render(spec="""# Cancel a booking

## Open questions

- Which currency for refunds?
  - Pending: 2026-10-10, for the partner, mail.
  - Blocks: T1
""")
        self.assertIn("Ready now: waiting on a question", waiting["markdown"])
        self.assertIn("— the partner", waiting["markdown"])

        ordered = render()
        self.assertIn("Ready now: ready", ordered["markdown"])
        self.assertIn("Ready now: waits in order", ordered["markdown"])

        cycle = bm.build("cancel-booking", SPEC, """# Plan

## Approach

1. Store the decision. (T1)
2. Notify the guest. (T2)
""", """# Tasks

- [ ] T1: Store the decision (after: T2)
- [ ] T2: Notify the guest (after: T1)
""")
        blocked = cycle["markdown"].split("## Blocked", 1)[1]
        self.assertNotIn("## Wave", cycle["markdown"])
        self.assertIn("Ready now: blocked", blocked)
        self.assertIn("Waits for: feat/cancel-booking-notify-guest", blocked)
        self.assertIn("Waits for: feat/cancel-booking-store-decision", blocked)
        self.assertIsNone(TASK_ID.search(cycle["markdown"]))

        missing = bm.build("cancel-booking", SPEC, """# Plan

## Approach

1. Store the decision. (T1)
""", """# Tasks

- [ ] T1: Store the decision (after: T9)
""")
        self.assertIn("## Blocked", missing["markdown"])
        self.assertIn(f"Waits for: {bm.UNKNOWN_DEP}", missing["markdown"])
        self.assertIn("Ready now: blocked", missing["markdown"])
        self.assertIsNone(TASK_ID.search(missing["markdown"]))
        self.assertIn("Wave 1: none", missing["summary"])

        risk = bm.build(
            "cancel-booking",
            "# Cancel a booking\n\n## Open questions\n",
            "# Plan\n\n## Approach\n\n1. Store the decision. (T1)\n\n## Risks\n\n- The currency is unknown. Do not implement until resolved.\n",
            "- [ ] T1: Store the decision\n",
        )
        self.assertIn("Held: a plan risk blocks the whole slice", risk["markdown"])
        self.assertIn("Ready now: blocked", risk["markdown"])
        self.assertIsNone(TASK_ID.search(risk["markdown"]))

        missing_plan = bm.build("cancel-booking", "", None, "- [ ] T1: Store the decision\n")
        self.assertIn("Held: no plan.md.", missing_plan["markdown"])
        self.assertIn(bm.NO_STEPS, missing_plan["markdown"])
        self.assertIn("Ready now: blocked", missing_plan["markdown"])

    def test_default_matches_golden(self):
        golden = (ROOT / "scripts/tests/goldens/build-map.md").read_text(encoding="utf-8")
        self.assertEqual(render()["markdown"], golden)

    def test_rendered_map_has_no_task_ids_and_has_mermaid(self):
        text = render()["markdown"]
        self.assertIsNone(TASK_ID.search(text))
        self.assertIn("```mermaid", text)
        self.assertIn("flowchart LR", text)
        self.assertNotIn("## Files", text)
        for field in ("- Delivers:", "- Tasks:", "- Waits for:", "- Question:", "- Ready now:"):
            self.assertIn(field, text)

    def test_build_map_word_keeps_scope(self):
        parsed = bm.parse_invocation("build-map cc 1.0")
        self.assertEqual(parsed["mode"], "map")
        self.assertEqual(parsed["scope"], "cc 1.0")
        self.assertEqual(bm.parse_invocation("cc 1.0")["mode"], "report")
        self.assertEqual(bm.parse_invocation("cc 1.0")["scope"], "cc 1.0")
        self.assertEqual(bm.parse_invocation("/crav1-tasks-ready-to-build build-map")["scope"], "")
        both = bm.parse_invocation("pipeline runs build-map cancel-booking")
        self.assertEqual(both["mode"], "map")
        self.assertTrue(both["pipeline_runs"])
        self.assertEqual(both["scope"], "cancel-booking")
        names = bm.scope_folder_names("cc 1.0")
        self.assertIn("cc-1-0", names)
        self.assertIn("cc-1.0", names)
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            folder = root / "cc-1-0"
            folder.mkdir()
            (folder / "tasks.md").write_text("- [ ] T1: Name the slice\n", encoding="utf-8")
            (folder / "plan.md").write_text("# Plan\n\n## Approach\n\n1. Name the slice. (T1)\n", encoding="utf-8")
            (folder / "spec.md").write_text("# CC\n\n## Open questions\n", encoding="utf-8")
            found = bm.slice_dirs(root, "cc 1.0")
            self.assertEqual(found, [folder])
            text, code = bm.run_dir(folder, chat=True, stdout=True)
            self.assertEqual(code, 0)
            self.assertIn("Build map — cc-1-0", text)
            self.assertIn("docs/specs/cc-1-0/build-map.md", text)
            self.assertNotIn("Ready (dependency order)", text)
            self.assertFalse((folder / "build-map.md").exists())
            pointer, code = bm.run_dir(folder, chat=False, stdout=False)
            self.assertEqual(code, 0)
            self.assertEqual(pointer, "Build map: docs/specs/cc-1-0/build-map.md")
            self.assertTrue((folder / "build-map.md").is_file())
            written = (folder / "build-map.md").read_text(encoding="utf-8")
            self.assertIsNone(TASK_ID.search(written))
            self.assertIn("```mermaid", written)

    def test_no_steps_falls_back_to_one_branch_per_task(self):
        plan = "# Plan: Cancel a booking\n\n## Approach\n\n1. \n"
        result = render(plan=plan)
        text = result["markdown"]
        self.assertIn(bm.NO_STEPS, text)
        self.assertNotIn(bm.BY_STEP, text)
        self.assertIn("### feat/cancel-booking-persist-decision", text)
        self.assertIn("### feat/cancel-booking-reject-unknown-booking", text)
        self.assertIn("### feat/cancel-booking-email-receipt", text)
        self.assertIsNone(TASK_ID.search(text))

        unnamed = render(plan="# Plan\n\n## Approach\n\n1. Record the refund decision.\n2. Send the receipt.\n")
        self.assertIn(bm.UNNAMED, unnamed["markdown"])
        self.assertIn("### feat/cancel-booking-persist-decision", unnamed["markdown"])
        self.assertNotIn("### feat/cancel-booking-record-refund-decision", unnamed["markdown"])

    def test_step_mark_links_a_task_and_titles_drop_the_marks(self):
        plan = """# Plan

## Approach

1. Record the refund decision.
2. Send the receipt.
"""
        tasks = """# Tasks

- [ ] T1: Persist the decision (step: 1)
- [ ] T2: Reject an unknown booking (after: T1) (step: 1)
- [ ] T3: Email the receipt (after: T2) (step: 2)
"""
        text = render(plan=plan, tasks=tasks)["markdown"]
        self.assertIn(bm.BY_STEP, text)
        self.assertNotIn(bm.UNNAMED, text)
        self.assertIn("### feat/cancel-booking-record-refund-decision", text)
        self.assertIn("### feat/cancel-booking-send-receipt", text)
        self.assertNotIn("(step:", text)
        self.assertNotIn("(map:", text)

    def test_parallel_count_names_question_holds(self):
        spec = """# Cancel a booking

## Open questions

- Which currency for refunds?
  - Pending: 2026-10-10, for the partner, mail.
  - Blocks: T3
"""
        plan = """# Plan

## Approach

1. Record the decision. (T1)
2. Store the card. (T2)
3. Send the receipt. (T3)
"""
        tasks = """# Tasks

- [ ] T1: Record the decision (after: ) (spec: decision)
- [ ] T2: Store the card (after: ) (spec: card)
- [ ] T3: Send the receipt (after: ) (spec: receipt)
"""
        result = bm.build("cancel-booking", spec, plan, tasks)
        text = result["markdown"]
        self.assertIn("## Wave 1: 3 branches, 2 can start now", text)
        self.assertIn("Wave 1: 3 branches, 2 can start now —", result["summary"])
        self.assertIn("Ready now: waiting on a question", text)
        self.assertEqual(text.count("Ready now: ready"), 2)
        diagram = mermaid(text)
        self.assertIn('subgraph w1["Wave 1"]', diagram)
        self.assertIn("direction TB", diagram)
        self.assertIn("flowchart LR", diagram)

    def test_overlap_is_a_note_and_does_not_change_readiness(self):
        plan = """# Plan

## Approach

1. Record the decision. (T1)
2. Store the card. (T2)
3. Send the receipt. (T3)
"""
        shared = """# Tasks

- [ ] T1: Record the decision in `src/refund.py` (after: ) (spec: refund)
- [ ] T2: Store the card in `src/refund.py` (after: ) (spec: refund)
- [ ] T3: Send the receipt (after: ) (spec: receipt)
"""
        separate = """# Tasks

- [ ] T1: Record the decision (after: ) (spec: decision)
- [ ] T2: Store the card (after: ) (spec: card)
- [ ] T3: Send the receipt (after: ) (spec: receipt)
"""
        hit = bm.build("cancel-booking", SPEC, plan, shared)
        quiet = bm.build("cancel-booking", SPEC, plan, separate)
        self.assertIn(
            "Overlap: feat/cancel-booking-record-decision and feat/cancel-booking-store-card both cover refund; both name `src/refund.py`.",
            hit["markdown"],
        )
        self.assertNotIn("Overlap:", quiet["markdown"])
        note = "Overlap: feat/cancel-booking-record-decision and feat/cancel-booking-store-card both cover refund; both name `src/refund.py`."
        self.assertIn(note, hit["summary"])
        wave_at = hit["summary"].index("Wave 1:")
        self.assertGreater(hit["summary"].index(note), wave_at)
        self.assertNotIn("Overlap:", quiet["summary"])
        self.assertEqual(hit["pointer"], "Build map: docs/specs/cancel-booking/build-map.md")
        self.assertNotIn("Overlap", hit["pointer"])
        for result in (hit, quiet):
            self.assertIn("## Wave 1: 3 branches, can run in parallel", result["markdown"])
            self.assertEqual(result["markdown"].count("Ready now: ready"), 3)
            self.assertNotIn("## Blocked", result["markdown"])
            self.assertIsNone(TASK_ID.search(result["markdown"]))
            self.assertIn("Wave 1: 3 branches, can run in parallel —", result["summary"])

    def test_same_branch_internal_wait_stays_ready(self):
        text = render()["markdown"]
        record = text.split("## Wave 1", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Ready now: ready", record)
        self.assertIn("Waits for: none", record)

    def test_skill_routes_the_word_and_points_at_the_script(self):
        skill = (ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("build-map", skill)
        self.assertIn("references/build-map.md", skill)
        self.assertIn("running-scripts.md", skill)
        self.assertIn("Build map: docs/specs/<slug>/build-map.md", skill)
        self.assertLessEqual(len(skill.split()), 2000)


if __name__ == "__main__":
    unittest.main()
