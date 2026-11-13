"""1.114.0: open-pr existing pull request path; next-step lines name the PR."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
OP = SK / "crav1-open-pr"


class OpenPrExisting(unittest.TestCase):
    def test_skill_points_at_reference(self):
        s = (OP / "SKILL.md").read_text()
        self.assertIn("## Existing pull request", s)
        self.assertIn("Read `references/existing-pr.md`", s)
        self.assertIn("existing one", s.split("---")[1])
        self.assertNotIn("If the list is non-empty, print the URL.", s)
        self.assertLess(len(s.split()), 2000)

    def test_reference_choices_and_confirm(self):
        r = (OP / "references/existing-pr.md").read_text()
        for t in ("`update` Update description | `comment` Add as comment",
                  "`comment` Add as comment | `update` Update description",
                  "`push-only` Push only", "`stop` Stop",
                  "`yes (Recommended)`: post it as shown.",
                  "Nothing is posted until that yes.",
                  "Do not add an `Edits` option.",
                  "kit-neutral", "gh pr comment", "az repos pr update"):
            self.assertIn(t, r)

    def test_next_step_lines_name_pr(self):
        for p in ("crav1-finalize-commit/references/commit.md", "crav1-build-features/SKILL.md",
                  "crav1-build-tasks/branches/one-task/BRANCH.md",
                  "crav1-build-tasks/branches/several-tasks/BRANCH.md",
                  "crav1-verify-build-against-spec/SKILL.md",
                  "crav1-help/references/status.md"):
            self.assertIn("to push to PR <n> and update its description or comment",
                          (SK / p).read_text(), p)

    def test_copies_in_sync(self):
        a = (OP / "references/existing-pr.md").read_text()
        for c in (ROOT / ".claude/skills/crav1-open-pr/references/existing-pr.md",
                  ROOT / "plugins/crav1/skills/crav1-open-pr/references/existing-pr.md"):
            self.assertEqual(a, c.read_text())


if __name__ == "__main__":
    unittest.main()
