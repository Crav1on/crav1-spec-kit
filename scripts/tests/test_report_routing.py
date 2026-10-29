"""Routing and progressive-loading checks for /crav1-what-do-we-know-about-this report words (1.104.0)."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-what-do-we-know-about-this"
WORDS = [f"{t}-{d}" for t in ("feature", "change", "build") for d in ("short", "full")]


class ReportRouting(unittest.TestCase):
    def setUp(self):
        self.skill = (SKILL / "SKILL.md").read_text()

    def test_one_file_per_report_word(self):
        found = sorted(p.stem for p in (SKILL / "reports").glob("*.md") if p.stem != "common")
        self.assertEqual(found, sorted(WORDS))

    def test_skill_routes_before_loading(self):
        self.assertIn("Route first, load second", self.skill)
        self.assertIn("Do not open `reports/`", self.skill)
        self.assertIn("Read only `reports/common.md` and `reports/<type>-<depth>.md`", self.skill)

    def test_skill_stays_lean(self):
        self.assertLessEqual(len(self.skill.split()), 1600)
        for heading in ("## At a glance", "## Unblock order", "C4 level 1", "## The 30-second version"):
            self.assertNotIn(heading, self.skill, "template content belongs in reports/")

    def test_report_files_do_not_load_each_other(self):
        for w in WORDS:
            text = (SKILL / "reports" / f"{w}.md").read_text()
            others = [o for o in WORDS if o != w and f"reports/{o}.md" in text]
            self.assertEqual(others, [], w)
            self.assertIn("reports/common.md", text)

    def test_c4_only_where_locked(self):
        r = lambda w: (SKILL / "reports" / f"{w}.md").read_text()
        self.assertIn("C4 always", r("feature-full"))
        self.assertIn("C4 only when the change alters architecture or pipelines", r("change-full"))
        for w in ("feature-short", "change-short", "build-short", "build-full"):
            self.assertIn("No C4", r(w), w)

    def test_build_uses_dependency_order(self):
        for w in ("build-short", "build-full"):
            self.assertIn("Dependency order", (SKILL / "reports" / f"{w}.md").read_text())

    def test_common_rules(self):
        c = (SKILL / "reports/common.md").read_text()
        for needle in ("Live read.", "(inference, not in the docs)", "Downloads", "ask first", "Allow", "Skip", "Mermaid", "Never inside the project"):
            self.assertIn(needle, c)
        self.assertIsNone(re.search(r"vault|bot", c, re.I))


if __name__ == "__main__":
    unittest.main()
