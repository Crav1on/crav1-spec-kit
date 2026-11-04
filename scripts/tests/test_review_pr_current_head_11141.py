"""1.114.1: review-pr re-review computes line links from the current head commit."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
REL = "crav1-review-pr/references/re-review.md"


class ReReviewCurrentHead(unittest.TestCase):
    def test_rule(self):
        r = (ROOT / ".cursor/skills/crav1" / REL).read_text()
        for t in ("**Lines from the current head (1.114.1).**",
                  "never from the PR record, the kit record, an earlier draft",
                  "When the code moved, link the new lines."):
            self.assertIn(t, r)
        c = (ROOT / ".cursor/skills/crav1/crav1-review-pr/references/comment-layout.md").read_text()
        self.assertIn("read again from the current head commit", c)

    def test_copies(self):
        a = (ROOT / ".cursor/skills/crav1" / REL).read_text()
        for p in (ROOT / ".claude/skills" / REL, ROOT / "plugins/crav1/skills" / REL):
            self.assertEqual(a, p.read_text())


if __name__ == "__main__":
    unittest.main()
