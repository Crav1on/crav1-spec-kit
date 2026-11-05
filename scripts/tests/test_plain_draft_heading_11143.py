"""1.114.3: the review-pr drafted heading is always plain, on a re-review too."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
COPIES = [".cursor/skills/crav1/crav1-review-pr", ".claude/skills/crav1-review-pr", "plugins/crav1/skills/crav1-review-pr"]


class PlainDraftHeading(unittest.TestCase):
    def test_every_copy(self):
        for c in COPIES:
            t = (ROOT / c / "references/notes.md").read_text()
            self.assertIn("The drafted heading is always plain `## Comment as drafted, <YYYY-MM-DD>`, on a re-review too", t, c)


if __name__ == "__main__":
    unittest.main()
