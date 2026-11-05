"""1.116.0: guided playbook walk in chat (report-playbook-full asks; report-playbook-walk resumes)."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1/crav1-what-do-we-know-about-this"


class PlaybookWalk(unittest.TestCase):
    def test_skill_routes_walk_to_reference(self):
        s = (SK / "SKILL.md").read_text()
        for n in ("report-playbook-walk", "`Walk through it now?`", "references/walk.md", "Headless: never walk"):
            self.assertIn(n, s)
        self.assertLessEqual(len(s.split()), 1600)

    def test_full_asks_short_does_not(self):
        self.assertIn("Walk through it now?", (SK / "reports/playbook-full.md").read_text())
        self.assertNotIn("walk.md", (SK / "reports/playbook-short.md").read_text())

    def test_walk_reference(self):
        w = (SK / "references/walk.md").read_text()
        for n in ("first item whose `Answer:`", "Blocking answers first", "`skip`", "Steps order", "`go to N9`",
                  "**Why this matters**", "`more`", "`yes`", "Never edit a spec", "Free flow",
                  "Compose, Merge order, Steps", "**Reply yes** (or \"confirm\")",
                  "To change something first, reply with your edits", "Headless or bot run", "never walk",
                  "Out of scope"):
            self.assertIn(n, w, n)
        self.assertNotRegex(w, r"(?i)vault|thomas|nyx")


if __name__ == "__main__":
    unittest.main()
