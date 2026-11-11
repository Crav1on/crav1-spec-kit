"""1.130.0: a question card does not offer an option that only says to type under Other."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_lint():
    path = ROOT / "scripts" / "kit-lint.py"
    spec = importlib.util.spec_from_file_location("kit_lint_1130", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lint = load_lint()


class DeadCard(unittest.TestCase):
    def test_an_edits_option_fails(self):
        text = (
            "- yes (Recommended): Write every recommendation as shown.\n"
            "- **Edits**: Choose this, then type your overrides under Other, e.g. Q12 keep, C1: keep it open.\n"
            "- Other\n"
        )
        why = [w for _, w in lint.dead_card_hits(text)]
        self.assertIn("Edits option", why)
        self.assertIn("choose this, then type", why)
        self.assertIn("type under Other", why)

    def test_reply_with_edits_and_change_some_fail(self):
        text = (
            '> To change something first, reply with your edits, for example "C2: keep it open".\n'
            "3. **Change some.** The user names items to flip.\n"
            "- **Other name**\n"
        )
        why = [w for _, w in lint.dead_card_hits(text)]
        self.assertIn("reply with edits", why)
        self.assertIn("Change some option", why)
        self.assertIn("Other name option", why)

    def test_the_free_text_hint_is_allowed(self):
        text = (
            "- `yes (Recommended)`: write it as shown.\n"
            "- The card's free-text answer. Hint: `Type your changes, e.g. C1: keep it open`.\n"
            "Do not add an `Edits` option. There is no Edits option.\n"
            "Do not offer an option labelled `Other name`.\n"
            "A fifth real choice still goes under Other.\n"
        )
        self.assertEqual(lint.dead_card_hits(text), [])

    def test_the_kit_has_no_dead_card_option(self):
        self.assertEqual(lint.dead_card_problems(ROOT), [])

    def test_the_shared_rule_is_where_cards_live(self):
        page = (ROOT / "docs/reference/question-cards.md").read_text(encoding="utf-8")
        self.assertIn("Never add an option that only tells the user to type somewhere else.", page)
        self.assertIn("free-text answer", page)
        self.assertIn("the hint lives on that option", page)
        rule = (ROOT / ".cursor/rules/crav1.mdc").read_text(encoding="utf-8")
        self.assertIn("question-cards.md", rule)
        self.assertNotIn("reply with your edits", rule)


if __name__ == "__main__":
    unittest.main()
