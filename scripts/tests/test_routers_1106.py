"""1.106.0 routers: each mode lives in one branch file, and SKILL.md routes before it loads."""
import pathlib, re, unittest

C = pathlib.Path(__file__).resolve().parents[2] / ".cursor/skills/crav1"
ROUTERS = {
    "crav1-retire-spec": ["retire", "merge", "park", "convert"],
    "crav1-show-or-ask-open-questions": ["show", "ask"],
    "crav1-explain-this-code": ["what", "why", "teach"],
    "crav1-glossary": ["list", "as-file", "research", "term"],
}


class Routers(unittest.TestCase):
    def test_router_points_at_every_branch_and_branches_exist(self):
        for skill, branches in ROUTERS.items():
            body = (C / skill / "SKILL.md").read_text()
            self.assertIn("Route first, load second", body, skill)
            self.assertEqual(sorted(p.name for p in (C / skill / "branches").iterdir()), sorted(branches), skill)
            for b in branches:
                self.assertIn(f"branches/{b}/BRANCH.md", body, (skill, b))

    def test_mode_sections_are_not_left_inline(self):
        for skill, branches in ROUTERS.items():
            heads = set(re.findall(r"(?m)^## (.+)$", (C / skill / "SKILL.md").read_text()))
            for b in branches:
                moved = set(re.findall(r"(?m)^## (.+)$", (C / skill / "branches" / b / "BRANCH.md").read_text()))
                self.assertFalse(heads & moved, (skill, b, heads & moved))


if __name__ == "__main__":
    unittest.main()
