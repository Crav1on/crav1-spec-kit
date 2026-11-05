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
            self.assertLess(len(t.split()), 1500, d)
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

    def test_no_step_cap(self):
        for d in DEPTHS:
            t = (SK / "reports" / f"playbook-{d}.md").read_text()
            self.assertNotIn("At most 8 steps", t)
            self.assertIn("No cap on steps", t)

    def test_diagram_order_not_c4_first(self):
        self.assertIn("No C4.", (SK / "reports/playbook-short.md").read_text())
        self.assertIn("never as the first diagram", (SK / "reports/playbook-full.md").read_text())


class Polish1091(unittest.TestCase):
    """1.109.1: plain wording, Kept can change, Out of scope last, merge order suggested, fool-proof steps."""

    def test_polish_rules(self):
        for d in DEPTHS:
            t = (SK / "reports" / f"playbook-{d}.md").read_text()
            for s in ("never a file name ending in `.md` in prose", "**Kept** is not frozen", "**Out of scope**",
                      "suggested, can change", "Never offer rebase as the kit's way", "their suggestion only",
                      "DEV Bicep", "**Type:**", "**You should see:**", "**Done when:**",
                      "**Run these steps in order, one at a time. You can stop and come back later.**",
                      "one fact among the others"):
                self.assertIn(s, t, f"{d}: {s}")
            self.assertIsNone(re.search(r"\b(spec|plan|tasks)\.md\b", t), d)
            self.assertNotIn("road" + "map", t.lower())


class Polish1092(unittest.TestCase):
    """1.109.2: clear change/answer blocks with examples, short From/To, one block per step, no cap in full."""

    def test_answer_blocks(self):
        for d in DEPTHS:
            t = (SK / "reports" / f"playbook-{d}.md").read_text()
            for s in ("**To change a decision under Kept**", "These are decisions already made. You can still change any of them",
                      "**To answer the questions under Needs your answer**",
                      "Nothing needs to run first", "Example:",
                      "never squeeze them into one line", "### Step <n>: <short title>"):
                self.assertIn(s, t, f"{d}: {s}")
        full = (SK / "reports/playbook-full.md").read_text()
        self.assertIn("No cap on steps: as many as the work needs.", full)
        self.assertNotIn("| K | Decision |", full)
        self.assertNotIn("| N | Question |", full)


class Apply1110(unittest.TestCase):
    """1.110.0: report only lists, blocks above tables, Recorded in Step, Answer: lines, Compose bullets, safe diagrams, apply."""

    def test_templates(self):
        for d in DEPTHS:
            t = (SK / "reports" / f"playbook-{d}.md").read_text()
            for s in ("Print each block word for word ABOVE its items", "Recorded in Step <n>", "/crav1-resolve-open-questions apply <this file>", "written-out bullets, never a table",
                      "Diagram syntax (1.110.0)", "no double quotes", "`-->|plain words|`"):
                self.assertIn(s, t, f"{d}: {s}")
            # 1.116.0: full offers a walk in chat after writing; short still only lists
            self.assertIn("Walk through it now?" if d == "full" else "it never takes answers in chat", t, d)
            self.assertNotIn("To change it |", t)
            self.assertNotIn("Written by, after your yes", t)
            self.assertNotIn("`change: K<n>", t)
            self.assertNotIn("| From (short) |", t)
            self.assertLess(t.index("<change block>"), t.index("<K1, K2, … as item blocks"))
            self.assertIn("The answer step comes first", t)

    def test_apply_on_resolve(self):
        d = ROOT / ".cursor/skills/crav1/crav1-resolve-open-questions"
        s = (d / "SKILL.md").read_text()
        self.assertIn("`apply` (1.110.0), as `apply <file>`", s)
        self.assertLess(len(s.split()), 2000)
        a = (d / "references/apply.md").read_text()
        for w in ("Staleness first", "**New:**", "**Already settled the same way:**", "**Conflicting:**",
                  "One question per conflict", "who decided each", "Nothing is written until the user confirms",
                  "/crav1-add-to-spec", "Never edit the filled file"):
            self.assertIn(w, a)

    def test_golden_diagrams_safe(self):
        g = (ROOT / "scripts/tests/goldens/playbook-order.md").read_text()
        blocks = re.findall(r"^```mermaid\n(.*?)^```", g, re.M | re.S)
        self.assertEqual(len(blocks), 2)
        for b in blocks:
            self.assertNotIn('"', b)
            self.assertTrue(b.isascii())
            self.assertNotRegex(b, r"\[[^\]]*[():#&`][^\]]*\]")


if __name__ == "__main__":
    unittest.main()
