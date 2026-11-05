"""1.115.1: K, N and C items are bullet blocks with the fill-in line under each; apply reads both layouts."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
REP = ROOT / ".cursor/skills/crav1/crav1-what-do-we-know-about-this/reports"
APPLY = ROOT / ".cursor/skills/crav1/crav1-resolve-open-questions/references/apply.md"


class PlaybookBullets(unittest.TestCase):
    def test_item_blocks_no_tables(self):
        for d in ("short", "full"):
            t = (REP / f"playbook-{d}.md").read_text()
            for s in ("Items (1.115.1)", "never tables", "> - **N1:**", ">   - From:", ">   - Where:",
                      ">   - Change:", ">   - Answer:", "`**K<n>:**", "`**C<n>:**", "No separate list of fill-in lines"):
                self.assertIn(s, t, f"{d}: {s}")
            self.assertNotRegex(t, r"\| [KN] \|", d)
            self.assertNotIn("Under the Kept table", t)
            self.assertNotIn("Under the Needs your answer table", t)
            self.assertNotIn("<K<n> Change: lines>", t)
            self.assertIn("**Run these steps in order, one at a time. You can stop and come back later.**", t)

    def test_apply_reads_both_layouts(self):
        a = APPLY.read_text()
        for s in ("**Item blocks (1.115.1):**", "**Older files (1.110.0 to 1.115.0):**", "`N<n> Answer:`",
                  "`C<n> Answer:`", "`K<n> Change:`", "C answers:"):
            self.assertIn(s, a)


if __name__ == "__main__":
    unittest.main()
