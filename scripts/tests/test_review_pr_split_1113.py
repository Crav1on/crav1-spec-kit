"""1.113.0: review-pr chat shows only the postable review; kit record and context go to files."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1/crav1-review-pr"


class ReviewPrSplit(unittest.TestCase):
    def test_skill_points_at_output(self):
        s = (SK / "SKILL.md").read_text()
        self.assertIn("## Output (1.113.0)", s)
        self.assertIn("Read `references/output.md`", s)
        self.assertIn("Posting takes only the review block.", s)
        self.assertNotIn("```text\nNext, after this pull request merges", s)
        self.assertLess(len(s.split()), 2000)

    def test_output_reference(self):
        o = (SK / "references/output.md").read_text()
        for t in ("## Plain run", "## With outside context", "## Posting",
                  "`Kit record: <PR note path>`",
                  "Read-only: kit record and context (not for posting)",
                  "`<date>-pr-<repo>-<n>-context`", "`Context: <path>`",
                  "never mentions the context, the kit or the specs"):
            self.assertIn(t, o)

    def test_notes_keep_kit_record(self):
        n = (SK / "references/notes.md").read_text()
        self.assertIn("## Kit record, <YYYY-MM-DD>", n)
        self.assertNotIn("The chat review still shows them", n)


if __name__ == "__main__":
    unittest.main()
