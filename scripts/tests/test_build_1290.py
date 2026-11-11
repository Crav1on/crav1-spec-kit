"""1.129.0: separate question cards, a yes is waiting, the map names the branch, shell line endings."""
import importlib.util
import pathlib
import sys
import unittest

sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ask = load(SK / "crav1-build-tasks/scripts/ask_order.py", "ask_order")
eol = load(SK / "crav1-build-tasks/scripts/sh_eol.py", "sh_eol")


class AskOrder(unittest.TestCase):
    def test_a_branch_name_in_the_permissions_slot_is_reasked(self):
        self.assertTrue(ask.reask("permissions", "feat/orders-retry"))
        self.assertTrue(ask.reask("permissions", ""))
        self.assertTrue(ask.reask("permissions", "click please"))
        self.assertFalse(ask.reask("permissions", "click"))
        self.assertFalse(ask.reask("permissions", " Continue "))

    def test_a_permissions_word_on_the_branch_card_is_reasked(self):
        self.assertTrue(ask.reask("branch", "click"))
        self.assertTrue(ask.reask("branch", ""))
        self.assertTrue(ask.reask("branch", "Other name"))
        self.assertFalse(ask.reask("branch", "feat/orders-host-setup"))
        self.assertFalse(ask.reask("branch", "Create feat/orders-retry from develop"))


class ShellLineEndings(unittest.TestCase):
    def test_the_offer_is_conditional_and_never_says_it_was_added(self):
        line = eol.note(True, "", "true", False)
        self.assertIn("`*.sh text eol=lf`", line)
        self.assertNotIn("added", line.lower())
        self.assertIsNone(eol.note(False, "", "true", True))
        self.assertIsNone(eol.note(True, "", "false", False))
        self.assertIsNone(eol.note(True, "", "input", False))
        self.assertIsNotNone(eol.note(True, "", "false", True))
        self.assertIsNone(eol.note(True, "*.sh text eol=lf\n", "true", True))
        self.assertIsNone(eol.note(True, "* text=auto\n*.sh eol=lf\n", True, False))
        self.assertIsNotNone(eol.note(True, "* text=auto\n", "true", False))


class SkillText(unittest.TestCase):
    def test_the_branch_card_and_the_yes_are_written_down(self):
        one = (SK / "crav1-build-tasks/branches/one-task/BRANCH.md").read_text(encoding="utf-8")
        run = (SK / "crav1-build-tasks/branches/one-task/references/run.md").read_text(encoding="utf-8")
        approvals = (SK / "crav1-build-tasks/branches/one-task/references/tool-approvals.md").read_text(encoding="utf-8")
        task = (SK / "crav1-create-feature-branch/references/task-branch.md").read_text(encoding="utf-8")
        skill = (SK / "crav1-create-feature-branch/SKILL.md").read_text(encoding="utf-8")
        guard = (SK / "crav1-create-feature-branch/references/code-branch.md").read_text(encoding="utf-8")
        for text, phrase in (
            (one, "needs_yes"),
            (one, "the partner's yes to turn off pipelines 7 and 24"),
            (one, "scripts/ask_order.py"),
            (one, "references/task-branch.md"),
            (one, "resume: eol"),
            (run, "STATUS: needs_yes"),
            (run, "scripts/sh_eol.py"),
            (run, "Do not return `blocked` for this."),
            (approvals, "Its own card"),
            (approvals, "Do not guess `click`."),
            (task, "--recommend T1"),
            (task, "committed later on"),
            (task, "the script will live on this branch"),
            (task, "cut later"),
            (task, "(map: <picked>)"),
            (skill, "No Stay on a base"),
            (skill, "references/task-branch.md"),
            (guard, "Other name"),
            (guard, "not a second card"),
        ):
            self.assertIn(phrase, text)

    def test_the_map_reference_matches_the_script(self):
        text = (SK / "crav1-tasks-ready-to-build/references/build-map.md").read_text(encoding="utf-8")
        self.assertIn("1 branch, 1 can start now", text)
        self.assertIn("3 branches, 3 can start now", text)
        self.assertIn("Task text names feat/orders-cicd; built on feat/orders-retry", text)
        self.assertIn("work-item.md", text)
        self.assertIn("--recommend T1", text)
        self.assertNotIn("can run in parallel", text)


if __name__ == "__main__":
    unittest.main()
