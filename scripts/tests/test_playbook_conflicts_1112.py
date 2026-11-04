"""1.112.0: playbook reports list Conflict lines as C items under Needs your answer."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
REP = ROOT / ".cursor/skills/crav1/crav1-what-do-we-know-about-this/reports"


class PlaybookConflicts(unittest.TestCase):
    def test_c_items_and_answer_step(self):
        for d in ("short", "full"):
            t = (REP / f"playbook-{d}.md").read_text()
            self.assertIn("numbered C1, C2, …", t, d)
            self.assertIn("`C<n> Answer:`", t, d)
            self.assertIn("C1 Answer: take the newer quote", t, d)
            self.assertIn("names every N and every C it covers", t, d)
            self.assertIn("settles the C items too", t, d)


if __name__ == "__main__":
    unittest.main()
