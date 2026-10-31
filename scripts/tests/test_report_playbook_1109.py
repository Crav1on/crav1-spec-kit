"""1.109.0: report-playbook-short / report-playbook-full (preview)."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1/crav1-what-do-we-know-about-this"
DEPTHS = ("short", "full")


class Playbook(unittest.TestCase):
    def test_router_names_playbook_and_loads_one_file(self):
        s = (SK / "SKILL.md").read_text()
        self.assertIn("`playbook` (1.109.0, preview", s)
        self.assertIn("Read only `reports/common.md` and `reports/<type>-<depth>.md`", s)
        self.assertIn("**No report word:** the free-form answer below, unchanged", s)

    def test_templates_exist_with_buckets(self):
        for d in DEPTHS:
            t = (SK / "reports" / f"playbook-{d}.md").read_text()
            self.assertLess(len(t.split()), 600, d)
            for h in ("## Kept", "## Needs your answer", "## Compose", "## Steps", "## Order"):
                self.assertIn(h, t, f"{d}: {h}")
            self.assertIn("recommended answer and why", t)
            self.assertIn("Write nothing in the project", t)
            self.assertIn("Preview (1.109.0)", t)
            self.assertNotIn("road" + "map", t.lower())

    def test_no_hand_off_phrasing(self):
        for d in DEPTHS:
            t = (SK / "reports" / f"playbook-{d}.md").read_text()
            # The only allowed mention is the ban itself.
            for m in re.finditer(r"for [<A-Za-z][^ ]* to decide", t):
                line = t[t.rfind("\n", 0, m.start()) + 1 : t.find("\n", m.end())]
                self.assertIn("Never write a hand-off", line)
            self.assertNotIn("for Arvid", t)

    def test_short_caps_steps_full_does_not(self):
        self.assertIn("at most 8 numbered kit commands", (SK / "reports/playbook-short.md").read_text())
        self.assertIn("no cap", (SK / "reports/playbook-full.md").read_text())

    def test_diagram_order_not_c4_first(self):
        self.assertIn("No C4.", (SK / "reports/playbook-short.md").read_text())
        self.assertIn("never as the first diagram", (SK / "reports/playbook-full.md").read_text())


if __name__ == "__main__":
    unittest.main()
