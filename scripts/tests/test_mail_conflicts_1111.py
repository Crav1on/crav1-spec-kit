"""1.111.0: a mail is written as mail.md; resolve-open-questions settles Conflict lines."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
ATS = SK / "crav1-add-to-spec"
ROQ = SK / "crav1-resolve-open-questions"


class MailAsText(unittest.TestCase):
    def test_mail_is_mail_md(self):
        s = (ATS / "references/sources-mail.md").read_text()
        self.assertIn("Write `mail.md`", s)
        self.assertIn("The original mail file stays outside the repo", s)
        self.assertIn("Do not write a script to edit, split, or re-encode a mail", s)
        self.assertIn("Do not write a local disk path", s)
        self.assertIn("`Message-ID`", s)
        for gone in ("*.eml -text", "CRLF", "image part stays", "untouched original", "image/webp"):
            self.assertNotIn(gone, s, gone)

    def test_no_gitattributes_question_left(self):
        for f in ("references/sources.md", "references/fact.md", "branches/meeting/BRANCH.md"):
            self.assertNotIn(".gitattributes", (ATS / f).read_text(), f)
        self.assertIn("A pasted mail is written as `mail.md`", (ATS / "references/sources.md").read_text())


class Conflicts(unittest.TestCase):
    def test_listed_by_default(self):
        s = (ROQ / "SKILL.md").read_text()
        self.assertIn("Every `**Conflict:**` line in the spec, listed after the questions as `C1`", s)
        self.assertIn("no choice word", s)
        self.assertLessEqual(len(s.split()), 1550)

    def test_reference(self):
        s = (ROQ / "references/conflicts.md").read_text()
        for want in ("(Recommended)", "Nothing is written until the user confirms", "Remove the `**Conflict:**` line",
                     "A headless or bot run lists the conflicts and settles none"):
            self.assertIn(want, s)

    def test_next_names_skill(self):
        self.assertIn("`/crav1-resolve-open-questions <slug>` first", (ATS / "branches/dump/BRANCH.md").read_text())
        self.assertIn("`/crav1-resolve-open-questions <slug>`", (SK / "crav1-finalize-commit/references/pull.md").read_text())


if __name__ == "__main__":
    unittest.main()
