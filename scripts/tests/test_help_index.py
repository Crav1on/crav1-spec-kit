"""1.106.0 load path: /crav1-help reads reference/index.yaml and one skill page, not skills.yaml or CHANGELOG whole."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HELP = ROOT / ".cursor/skills/crav1/crav1-help"


class HelpIndex(unittest.TestCase):
    def test_index_lists_every_skill_with_a_page(self):
        text = (ROOT / "docs/reference/index.yaml").read_text()
        idx = dict(re.findall(r"^  (crav1-[\w-]+):\n(?:    .*\n)*?    page: (\S+)", text, re.M))
        skills = {p.parent.name for p in (ROOT / ".cursor/skills/crav1").glob("*/SKILL.md")} - {"crav1-docs"}
        self.assertEqual(set(idx), skills)
        for name, e in idx.items():
            self.assertTrue((ROOT / "docs" / e).is_file(), name)

    def test_help_reads_index_first_and_changelog_only_on_ask(self):
        body = (HELP / "SKILL.md").read_text()
        self.assertIn("reference/index.yaml", body)
        self.assertIn("Do not read `reference/skills.yaml`", body)
        self.assertRegex(body, r"CHANGELOG\.md.*Read it only for what's new")

    def test_modes_do_not_load_skills_yaml(self):
        self.assertNotIn("skills.yaml", (HELP / "references/modes.md").read_text())


class DescriptionCap(unittest.TestCase):
    def test_every_description_is_at_most_60_words(self):
        for p in (ROOT / ".cursor/skills/crav1").glob("*/SKILL.md"):
            fm = p.read_text().split("---", 2)[1]
            d = re.search(r"^description: >-\n((?:  .*\n)+)", fm, re.M).group(1)
            self.assertLessEqual(len(d.split()), 60, p.parent.name)


if __name__ == "__main__":
    unittest.main()
