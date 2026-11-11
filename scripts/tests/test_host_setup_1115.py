"""1.115.0: host setup skill, shared reference, plan/build/verify/pr-status/fix-bug pointers."""
import pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
HS = SK / "crav1-host-setup"


class HostSetup(unittest.TestCase):
    def test_skill(self):
        s = (HS / "SKILL.md").read_text()
        self.assertIn("references/host-setup.md", s)
        self.assertIn("code-branch.md", s)
        self.assertIn("Host setup not applied. Run it after a yes.", s)
        self.assertLess(len(s.split()), 2000)

    def test_reference(self):
        r = (HS / "references/host-setup.md").read_text()
        for t in ("`yes (Recommended)`: run it as shown.",
                  "Type your changes, e.g. make it optional",
                  "Do not add an `Edits` option.",
                  "Nothing runs until that yes.",
                  "`apply`", "`check`", "kit-neutral", "## Secrets",
                  "infra/ado/<name>.sh", "generated from these comments"):
            self.assertIn(t, r)

    def test_pointers(self):
        for p in ("crav1-plan-from-spec/SKILL.md",
                  "crav1-build-tasks/branches/implement/BRANCH.md",
                  "crav1-verify-build-against-spec/SKILL.md",
                  "crav1-pr-status/SKILL.md"):
            t = (SK / p).read_text()
            self.assertIn("1.115.0", t, p)
            self.assertTrue("crav1-host-setup" in t, p)
        self.assertIn("`/crav1-host-setup`", (SK / "crav1-fix-bug/SKILL.md").read_text())
        self.assertIn("done host", (SK / "crav1-pr-status/SKILL.md").read_text())

    def test_copies_in_sync(self):
        for f in ("SKILL.md", "references/host-setup.md"):
            a = (HS / f).read_text()
            for c in (ROOT / ".claude/skills/crav1-host-setup" / f,
                      ROOT / "plugins/crav1/skills/crav1-host-setup" / f):
                self.assertEqual(a, c.read_text(), c)


if __name__ == "__main__":
    unittest.main()
