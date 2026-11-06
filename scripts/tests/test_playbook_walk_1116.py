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


class WalkChat1117(unittest.TestCase):
    """1.117.0: words in chat, intent before a write, no help or pr-status, apply boundary."""

    def test_chat_hides_ids_and_jump_still_works(self):
        w = (SK / "references/walk.md").read_text()
        self.assertIn("Do not use K, N or C item ids in the walk conversation, not even in parentheses", w)
        self.assertIn("`go to N9`", w)
        self.assertIn("does not repeat the id", w)
        self.assertNotIn("Picking up at Step 4, N9", w)

    def test_intent_before_write(self):
        w = (SK / "references/walk.md").read_text()
        for n in ("intended", "one focused follow-up", "explicit yes",
                  "does not win by default", "missing note is not proof",
                  "Do not force a choice between the docs and the memory"):
            self.assertIn(n, w, n)
        self.assertIn("do not count against the prompt budget", w)

    def test_no_help_no_pr_status_apply_boundary(self):
        w = (SK / "references/walk.md").read_text()
        s = (SK / "SKILL.md").read_text()
        self.assertIn("Do not start `/crav1-help`", w)
        self.assertIn("Do not start `/crav1-help`", s)
        self.assertIn("Do not run `/crav1-pr-status`", w)
        self.assertIn("filled, confirmed lines only", w)
        self.assertIn("does not run plan, build, or merge", w)
        self.assertIn("While `/crav1-what-do-we-know-about-this` is the running skill, do not start `/crav1-help`",
                      (ROOT / ".cursor/rules/crav1.mdc").read_text())

    def test_reads_trials_and_gaps(self):
        w = (SK / "references/walk.md").read_text()
        common = (SK / "reports/common.md").read_text()
        full = (SK / "reports/playbook-full.md").read_text()
        self.assertIn("One pass applies only while matching", w)
        self.assertIn("outside the work tree", common)
        self.assertIn("Never checkout, commit, or push for a trial", common)
        self.assertIn("does not run `/crav1-pr-status`", common)
        self.assertIn("No guessed range", full)
        self.assertIn("it never takes answers in chat", (SK / "reports/playbook-short.md").read_text())
        self.assertIn("Headless: never walk", (SK / "SKILL.md").read_text())

    def test_generated_prompt_note(self):
        page = (ROOT / "docs/reference/skills/crav1-what-do-we-know-about-this.md").read_text()
        self.assertIn("Follow-ups to understand what the user means do not count", page)
        self.assertNotIn("Prompt budget: 0 (asks nothing)", page)
        self.assertIn("crav1-help", page)
        self.assertIn("crav1-pr-status", page)
        self.assertIn("Does not start", page)


if __name__ == "__main__":
    unittest.main()
