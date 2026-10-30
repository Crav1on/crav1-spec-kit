"""1.108.0: /crav1-existing-to-specs recheck (repos vs specs)."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1/crav1-existing-to-specs"
BR = SK / "branches/recheck"


class Recheck(unittest.TestCase):
    def test_router_points_at_branch_only(self):
        s = (SK / "SKILL.md").read_text()
        self.assertIn("(branches/recheck/BRANCH.md)", s)
        self.assertIn("`recheck` / `repos vs specs`", s)
        self.assertIn("do not read the other branches", s)

    def test_branch_size_and_references(self):
        b = (BR / "BRANCH.md").read_text()
        self.assertLess(len(b.split()), 1500)
        for ref in ("units.md", "handoff.md"):
            self.assertIn(f"branches/recheck/references/{ref}", b)
            self.assertTrue((BR / "references" / ref).is_file())

    def test_no_spec_writes_and_no_open_questions(self):
        b = (BR / "BRANCH.md").read_text()
        self.assertIn("Write nothing into any `spec.md`", b)
        self.assertIn("Never add an open question to a spec", b)
        self.assertIn("Do not create a spec folder", b)
        self.assertIn("Never add an open question to a spec", (BR / "references/handoff.md").read_text())

    def test_reports_gaps_and_stale_claims(self):
        b = (BR / "BRANCH.md").read_text()
        self.assertIn("**Code with no spec:**", b)
        self.assertIn("**Stale claims:**", b)
        self.assertIn("`## Code with no slice`", b)
        self.assertIn("`since`", b)

    def test_choice_words_in_data(self):
        y = (ROOT / "docs/reference/skills.yaml").read_text()
        self.assertRegex(y, r'word: "recheck"')
        self.assertRegex(y, r'word: "repos vs specs"')

    def test_pointers_from_add_to_spec_and_route(self):
        self.assertIn("/crav1-existing-to-specs recheck", (ROOT / ".cursor/skills/crav1/crav1-add-to-spec/SKILL.md").read_text())
        self.assertIn("id: repo-gaps", (ROOT / "docs/reference/workflow.yaml").read_text())


if __name__ == "__main__":
    unittest.main()
