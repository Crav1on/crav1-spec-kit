"""/crav1-glossary paths (1.105.0): research and term mode never write open questions onto specs; not-found loads on its own path."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-glossary"


def body(path):
    return (SKILL / path).read_text()


class GlossaryPaths(unittest.TestCase):
    def test_never_routes_into_spec_open_questions(self):
        for f in ["SKILL.md", *[f"references/{p.name}" for p in (SKILL / "references").glob("*.md")]]:
            t = body(f)
            self.assertIsNone(re.search(r"Add an open question|under `## Open questions`|Name `/crav1-show-or-ask-open-questions", t), f)
            self.assertIsNone(re.search(r"What does <term> mean here\?", t), f)

    def test_writes_are_glossary_only(self):
        w = re.search(r"## Writes\n\n(.*?)\n\n", body("SKILL.md"), re.S).group(1)
        self.assertNotIn("open question", w)
        self.assertIn("docs/system/glossary.md", w)

    def test_not_found_is_its_own_path(self):
        s = body("SKILL.md")
        self.assertIn("references/not-found.md", s)
        self.assertNotIn("Guesses waiting", s)  # detail lives in the path file
        nf = body("references/not-found.md")
        for needle in ("**Correct**", "**Needs research**", "(inference, not in the docs)", "Guesses waiting", "Nothing is written to a spec"):
            self.assertIn(needle, nf)

    def test_golden_correct_row_shape(self):
        nf = body("references/not-found.md")
        self.assertIn("`<guess> Source: confirmed in chat (<date>)`", nf)

    def test_lean(self):
        self.assertLessEqual(len(body("SKILL.md").split()), 1600)


if __name__ == "__main__":
    unittest.main()
