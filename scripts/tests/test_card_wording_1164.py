"""Card wording rule and its kit-lint check (1.164.0)."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".cursor/skills/crav1"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LINT = _load("kit_lint_1164", ROOT / "scripts/kit-lint.py")


class CardLint(unittest.TestCase):
    def hits(self, text):
        return [why for _, why in LINT.card_text_hits(text)]

    def test_good_card_passes(self):
        text = (
            "Card: Merge PR 71 into develop?\n"
            "- **Merge PR 71 (Recommended)** (`yes`): merge PR 71 now. Why: checks are green.\n"
            "- **Not yet** (`stop`): leave PR 71 open and pause the walk.\n"
        )
        self.assertEqual(self.hits(text), [])

    def test_brackets_in_question(self):
        text = "Card: Merge (PR 71) now?\n- **Merge it (Recommended)**: merge PR 71 into develop.\n"
        self.assertIn("the question has brackets", self.hits(text))

    def test_option_without_what_happens(self):
        text = "Card: Merge PR 71 now?\n- **yes (Recommended)**\n- **stop**: leave it open for now.\n"
        self.assertTrue(any("does not say what happens" in h for h in self.hits(text)))

    def test_recommended_not_first(self):
        text = "Card: Merge PR 71 now?\n- **Not yet**: leave PR 71 open.\n- **Merge (Recommended)**: merge PR 71 now.\n"
        self.assertTrue(any("not first" in h for h in self.hits(text)))

    def test_jargon(self):
        text = "Card: Switch to other-owner mode?\n- **Switch (Recommended)**: add my work to PR 71.\n"
        self.assertTrue(any("other-owner mode" in h for h in self.hits(text)))
        text = "Card: Approve T7?\n- **Approve (Recommended)**: clear needs_yes on T7 now.\n"
        self.assertTrue(any("needs_yes" in h for h in self.hits(text)))

    def test_inline_options_flagged(self):
        self.assertTrue(self.hits("The card is `switch` (Recommended), `own`, or `stop`.\n"))
        self.assertTrue(self.hits("Options: `skip` (Recommended), `reapply`.\n"))
        self.assertTrue(self.hits("Set it? **Leave it (Recommended)** / **Set to active**\n"))

    def test_prose_and_fences_not_flagged(self):
        text = (
            "The recommended option is first and marked Recommended (see the rule).\n"
            "A card asks one plain question. Say `yes` to merge.\n"
            "```\nCard: Bad (question)?\n- **x**\n```\n"
        )
        self.assertEqual(self.hits(text), [])

    def test_script_numbered_options(self):
        text = "Card: How should I fix it?\n1. Move T14 (Recommended) (`fix-loop`): Build T14 on feat/x instead.\n2. Leave it (`stop`): Change nothing at all.\n"
        self.assertEqual(self.hits(text), [])

    def test_scope_is_the_reworded_skills(self):
        self.assertEqual(
            set(LINT.CARD_LINT_SKILLS),
            {
                "crav1-tasks-ready-to-build", "crav1-build-walk",
                "crav1-tighten-and-plan-ready-to-build", "crav1-open-pr",
                "crav1-merge-pr", "crav1-pr-status", "crav1-review-pr",
            },
        )
        self.assertEqual(LINT.card_wording_problems(str(ROOT)), [])

    def test_reworded_files_have_card_blocks(self):
        for rel in (
            "crav1-build-walk/references/other-owner.md",
            "crav1-build-walk/references/common.md",
            "crav1-build-walk/references/sync.md",
            "crav1-pr-status/references/offers.md",
            "crav1-tighten-and-plan-ready-to-build/references/playbook.md",
        ):
            text = (SKILLS / rel).read_text(encoding="utf-8")
            self.assertTrue(LINT.card_blocks(text), rel)
        common = (SKILLS / "crav1-build-walk/references/common.md").read_text(encoding="utf-8")
        self.assertIn("Card: Merge PR 71 into develop?", common)
        self.assertIn("There is no Edits option.", common)
        self.assertIn("A missing word is asked again.", common)


class ScriptCards(unittest.TestCase):
    def check(self, offer):
        options = [(o["label"], o.get("text", "")) for o in offer["options"]]
        self.assertEqual(LINT.card_hits(offer["question"], options), [], offer)

    def test_walk_progress_offers(self):
        walk = _load("walk_progress_1164", SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py")
        jump = walk._jump_back_offer("P2")
        self.check(jump)
        self.assertEqual(jump["background"], "P2 is about the spec, not the plan.")
        one = walk._same_or_new_offer("P3", [{"key": "a", "finding": "needs an approver", "id": "P1"}])
        self.check(one)
        many = walk._same_or_new_offer("P3", [
            {"key": "a", "finding": "needs an approver", "id": "P1"},
            {"key": "b", "finding": "needs a named approver", "id": "P2"},
        ])
        self.check(many)

    def test_loop_card(self):
        build_map = _load("build_map_1164", SKILLS / "crav1-tasks-ready-to-build/scripts/build_map.py")
        card = build_map.loop_card([
            {"label": "Move T14 to feat/orders-dev-switch", "detail": "Build T14 on feat/orders-dev-switch instead.", "why": "its plan step describes it."},
            {"label": "Start T15 without T13", "detail": "T15 no longer waits for T13.", "why": "it changes the build order."},
        ])
        options = [(o["label"], o["text"]) for o in card["options"]]
        self.assertEqual(LINT.card_hits("How should I fix it?", options), [])


class RuleAndPointer(unittest.TestCase):
    def test_rule_section(self):
        page = (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("## Card wording (1.164.0)", page)
        self.assertIn("Waiting for person A to approve T7", page)
        self.assertIn("There is no", (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8"))

    def test_always_loaded_rule_stays_small(self):
        rule = (ROOT / ".cursor/rules/crav1.mdc").read_text(encoding="utf-8")
        self.assertIn("options saying what happens", rule)
        self.assertLessEqual(len(rule.split()), 660)


class PlainWaitingLines(unittest.TestCase):
    def test_build_walk_waiting_lines(self):
        bw = _load("build_walk_1164", SKILLS / "crav1-build-walk/scripts/build_walk.py")
        base = {"slug": "orders-api", "branch": "feat/orders-cicd", "tasks": [{"id": 5, "title": "Deploy"}], "pr": 71}
        seen = {}
        for phase in ("confirm-owner", "approval", "live-yes", "wait-merge"):
            state = dict(base, phase=phase, who="person A")
            if phase in ("confirm-owner", "wait-merge"):
                state["owner"] = "other"
            ending = bw.next_for(state)["ending"]
            line = next(l for l in ending.splitlines() if l.startswith("Waiting:"))
            seen[phase] = line
            for word in LINT.CARD_JARGON + ("Approval needed item", "other-owner"):
                self.assertNotIn(word.lower(), line.lower(), line)
        self.assertIn("person A to merge pull request 71", seen["wait-merge"])
        self.assertIn("your yes to run T5", seen["live-yes"])


class LiveRunCards(unittest.TestCase):
    def setUp(self):
        self.walk = _load("walk_progress_live_1164", SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py")

    def test_reopen_card_is_plain(self):
        for rerun in (False, True):
            card = self.walk.reopen_card("review-and-tighten-plan", ["tasks"], rerun)
            options = [(o["label"], o["text"]) for o in card["options"]]
            self.assertEqual(LINT.card_hits(card["question"], options), [])
            text = " ".join([card["background"], card["question"]] + [o["text"] + o["label"] for o in card["options"]])
            for bad in ("review-and-tighten-plan", "stamp", "Done", "Result", "--step", "clear --"):
                self.assertNotIn(bad, text)
            self.assertEqual(card["question"], "Skip redoing the plan review?")
            self.assertEqual(card["background"], "The plan review reopened because the tasks changed.")
            self.assertTrue(card["options"][0]["label"].startswith("Redo" if rerun else "Skip"))

    def test_claim_line_agrees_in_number(self):
        src = (SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py").read_text(encoding="utf-8")
        self.assertIn('pronoun = "it" if len(own) == 1 else "them"', src)

    def test_record_and_playbook_guidance(self):
        steps = (SKILLS / "crav1-tighten-and-plan-ready-to-build/references/steps.md").read_text(encoding="utf-8")
        self.assertIn("Card: Save the ready check as done?", steps)
        progress = (SKILLS / "crav1-tighten-and-plan-ready-to-build/references/progress.md").read_text(encoding="utf-8")
        self.assertIn("Card: Skip redoing the plan review?", progress)
        playbook = (SKILLS / "crav1-tighten-and-plan-ready-to-build/references/playbook.md").read_text(encoding="utf-8")
        self.assertIn("Do not name step ids", playbook)


class HeldLines(unittest.TestCase):
    def test_short_question(self):
        bm = _load("build_map_held_1164", SKILLS / "crav1-tasks-ready-to-build/scripts/build_map.py")
        self.assertEqual(bm.short_question("**New:** Which currency for refunds? It matters for EU."), "Which currency for refunds?")
        long = "Which " + "very " * 40 + "long question is this?"
        out = bm.short_question(long)
        self.assertLessEqual(len(out), 160)  # more room in 1.165.0
        self.assertTrue(out.endswith("…"))


class FewerReadsAndScripts(unittest.TestCase):
    def test_read_field(self):
        walk = _load("walk_progress_read_1164", SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py")
        self.assertEqual(walk.read_for("playbook"), "references/playbook.md")
        self.assertEqual(walk.read_for("plan-from-spec"), "references/steps.md")
        self.assertEqual(walk.read_for("tasks-ready-to-build"), "references/readiness.md")
        self.assertEqual(walk.read_for(None), "references/readiness.md")
        src = (SKILLS / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py").read_text(encoding="utf-8")
        self.assertIn('"read": read_for(continue_from)', src)
        for rel in set(walk.READ_FOR.values()):
            self.assertTrue((SKILLS / "crav1-tighten-and-plan-ready-to-build" / rel).is_file(), rel)

    def test_lead_sentence_and_powershell(self):
        ending = (ROOT / "docs/reference/run-ending.md").read_text(encoding="utf-8")
        self.assertIn("at most one short lead sentence of recap", ending)
        readiness = (SKILLS / "crav1-tighten-and-plan-ready-to-build/references/readiness.md").read_text(encoding="utf-8")
        self.assertIn("at most one short lead sentence of recap", readiness)
        scripts = (ROOT / "docs/reference/running-scripts.md").read_text(encoding="utf-8")
        self.assertIn("do not redirect a script's output with `>`", scripts)
        self.assertIn("BOM", scripts)


class RunNextLayout(unittest.TestCase):
    def setUp(self):
        self.we = _load("walk_ending_layout_1164", SKILLS / "crav1-tasks-ready-to-build/scripts/walk_ending.py")

    def test_two_tasks_with_plan_sentence(self):
        block = self.we.branch_block(
            "feat/orders-cicd", ["T9 Add the pipeline", "T10 Add the test stage"], first="T9 Add the pipeline",
            slug="orders-api", about="Build and test **orders-api** on every push. Then deploy to dev.")
        self.assertEqual(block, "\n".join([
            "**feat/orders-cicd**",
            "Build and test orders-api on every push. Then deploy to dev.",
            "2 open tasks:",
            "- T9 Add the pipeline",
            "- T10 Add the test stage",
            "",
            "Run the whole branch:",
            "`/crav1-build-walk orders-api feat/orders-cicd`",
            "Run only T9, the first task:",
            "`/crav1-build-walk orders-api T9`",
        ]))

    def test_one_task_no_sentence_no_slug(self):
        block = self.we.branch_block("feat/orders-note", ["T5 Note the export"], first="T5 Note the export")
        # No plan step: the description comes from the task name (1.166.0).
        self.assertEqual(block, "**feat/orders-note**\nNote the export.\n1 open task:\n- T5 Note the export\n\nRun T5:\n`/crav1-build-walk T5`")

    def test_open_map_line_under_build_map(self):
        reply = self.we.ready_reply("orders-api", "ready", None, "Run next:", build_map="docs/specs/orders-api/build-map.md")
        lines = reply.splitlines()
        at = lines.index("Build map: docs/specs/orders-api/build-map.md")
        self.assertEqual(lines[at + 1], "Zoom the map in your browser:")
        self.assertEqual(lines[at + 2], "`/crav1-tasks-ready-to-build orders-api open-map`")
        self.assertNotIn("export-map", reply)


if __name__ == "__main__":
    unittest.main()
