"""1.122.0: every skill ends with one Next line.

kit-lint checks the same rules. This test pins the shared reference and a
couple of endings that used to list several steps.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def kit_lint():
    spec = importlib.util.spec_from_file_location("kit_lint", ROOT / "scripts/kit-lint.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunEndingTest(unittest.TestCase):
    def test_shared_reference_states_the_shape(self):
        text = (ROOT / "docs/reference/run-ending.md").read_text(encoding="utf-8")
        self.assertIn("Next:", text)
        self.assertIn("Waiting:", text)
        self.assertIn("Uncommitted:", text)
        self.assertIn("nothing needed now", text)
        self.assertIn("`Next:` is exactly one line.", text)
        self.assertIn("does not run it", text)

    def test_every_skill_points_at_the_rule_and_next_names_one_step(self):
        problems = kit_lint().run_ending_problems(str(ROOT))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_standing_rule_points_at_the_reference(self):
        rule = (ROOT / ".cursor/rules/crav1.mdc").read_text(encoding="utf-8")
        self.assertIn("crav1-docs/reference/run-ending.md", rule)
        self.assertEqual(rule.count("A run ends with one `Next:` line"), 1)

    def test_add_to_spec_stop_does_not_list_the_later_route(self):
        text = (ROOT / ".cursor/skills/crav1/crav1-add-to-spec/references/stop.md").read_text(encoding="utf-8")
        self.assertIn("Next: /crav1-tighten-spec <slug>, because the new information is not tightened yet.", text)
        self.assertNotIn("/crav1-help next", text)
        self.assertIn("Do not run `/crav1-finalize-commit`", text)


if __name__ == "__main__":
    unittest.main()
