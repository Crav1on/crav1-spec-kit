"""1.114.2: a record-only review-pr run never drafts, and drafted comments use a four-backtick fence."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
COPIES = [".cursor/skills/crav1/crav1-review-pr", ".claude/skills/crav1-review-pr", "plugins/crav1/skills/crav1-review-pr"]


class RecordOnlyDraft(unittest.TestCase):
    def test_every_copy(self):
        for c in COPIES:
            t = (ROOT / c / "references/comment-as-posted.md").read_text()
            self.assertIn("It never writes a `## Comment as drafted` section", t, c)
            self.assertIn("always inside a fence of four backticks tagged markdown, never three", t, c)
            self.assertIn("A record-only run never adds a drafted section", (ROOT / c / "references/notes.md").read_text(), c)


if __name__ == "__main__":
    unittest.main()
