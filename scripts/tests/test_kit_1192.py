"""1.192.0: /crav1-explain-tech explains one technology tied to where the specs use it.

find (mentions with links, owners, the spec to save to), the not-in-spec path,
the answer check (fixed shape, word counts, links), deeper, the save step (only
with --yes, to the right notes file), the Run next, routing and registration.
Generic fixture only (orders-api, person A).
"""
import contextlib
import importlib.util
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-explain-tech"
_spec = importlib.util.spec_from_file_location("explain_tech_1192", SKILL / "scripts/explain_tech.py")
et = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(et)
_lspec = importlib.util.spec_from_file_location("kit_lint_1192", ROOT / "scripts/kit-lint.py")
kl = importlib.util.module_from_spec(_lspec)
_lspec.loader.exec_module(kl)

SPEC = """# orders-api

## Problem

Checkout is slow when payment fails.

## Payment retry

A failed payment goes on the Service Bus retry queue and is tried again later.

## Approval needed

- person A (orders platform owner)
"""
PLAN = "# Plan: orders-api\n\n## Decisions\n\n- One service-bus queue per environment, five tries.\n"
ADR = "# ADR: retry queue\n\nStatus: accepted\nDeciders: person A, person B\n\nWe use ServiceBus for retries.\n"


def run(root, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = et.main(["--root", str(root)] + list(args))
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / "docs/specs/orders-api"
        (d / "adr").mkdir(parents=True)
        (d / "spec.md").write_text(SPEC, encoding="utf-8")
        (d / "plan.md").write_text(PLAN, encoding="utf-8")
        (d / "adr/0001-retry-queue.md").write_text(ADR, encoding="utf-8")
        (self.tmp / "docs/specs/_template").mkdir()
        (self.tmp / "docs/specs/_template/spec.md").write_text("Service Bus template line\n", encoding="utf-8")
        (self.tmp / "docs/architecture/designs/orders-platform").mkdir(parents=True)
        (self.tmp / "docs/architecture/spec.md").write_text("# Architecture\n\n## Confirmed\n\n- orders-api runs.\n", encoding="utf-8")
        (self.tmp / "docs/architecture/designs/orders-platform/goal.md").write_text("# Goal\n\n## Drivers\n\n- Keep Service Bus\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def snapshot(self):
        return {p.relative_to(self.tmp).as_posix(): p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()}


class TestFind(Base):
    def test_mentions_found_with_links(self):
        res = et.find(self.tmp, "Service Bus")
        self.assertTrue(res["in_spec"])
        links = [m["link"] for m in res["mentions"]]
        self.assertIn("docs/specs/orders-api/spec.md#payment-retry", links)
        self.assertIn("docs/specs/orders-api/plan.md#decisions", links)       # service-bus
        self.assertIn("docs/specs/orders-api/adr/0001-retry-queue.md", links)  # ServiceBus, under the title
        self.assertIn("docs/architecture/designs/orders-platform/goal.md#drivers", links)
        self.assertFalse(any("_template" in l for l in links))
        design = [m for m in res["mentions"] if m["kind"] == "design topic"]
        self.assertTrue(design and not any(m["decided"] for m in design))  # under discussion, not decided
        self.assertEqual(res["save_to"], "orders-api")
        self.assertEqual(res["notes_file"], "docs/specs/orders-api/notes.md")
        who = [o["who"] for o in res["owners"]]
        self.assertIn("person A, person B", who)
        self.assertIn("person A (orders platform owner)", who)

    def test_every_link_points_at_a_real_section(self):
        for m in et.find(self.tmp, "Service Bus")["mentions"]:
            path, _, frag = m["link"].partition("#")
            self.assertTrue((self.tmp / path).is_file())
            if frag:
                heads = {et.anchor(h) for _, h in et.headings((self.tmp / path).read_text().splitlines())}
                self.assertIn(frag, heads)

    def test_not_in_spec(self):
        res = et.find(self.tmp, "Private Link")
        self.assertFalse(res["in_spec"])
        self.assertEqual(res["mentions"], [])
        self.assertEqual(res["save_to"], "")
        end = et.ending("Private Link", not_in_spec=True)
        self.assertIn("not in the specs", end)
        self.assertIn("`/crav1-show-or-ask-open-questions ask research private-link`", end)
        self.assertNotIn("docs/specs", end)

    def test_scope_and_unknown_scope(self):
        self.assertTrue(all(m["path"].startswith("docs/architecture/designs/orders-platform") for m in et.find(self.tmp, "Service Bus", "orders-platform")["mentions"]))
        code, _, err = run(self.tmp, "find", "--tech", "Service Bus", "--scope", "billing")
        self.assertEqual(code, 2)
        self.assertIn("orders-api", err)

    def test_find_writes_nothing(self):
        before = self.snapshot()
        run(self.tmp, "find", "--tech", "Service Bus")
        run(self.tmp, "find", "--tech", "Private Link")
        self.assertEqual(self.snapshot(), before)


class TestCheck(Base):
    def sample(self, name):
        return (SKILL / "assets" / name).read_text(encoding="utf-8")

    def test_samples_pass(self):
        self.assertTrue(et.check(self.sample("sample-short.md"))["ok"])
        self.assertTrue(et.check(self.sample("sample-not-in-spec.md"))["ok"])
        self.assertTrue(et.check(self.sample("sample-deeper.md"), deeper=True)["ok"])
        self.assertEqual(kl.explain_tech_problems(str(ROOT)), [])

    def test_deeper_flag_changes_the_shape(self):
        res = et.check(self.sample("sample-short.md"), deeper=True)
        self.assertFalse(res["ok"])
        self.assertTrue(any("How it fits with the rest of the spec" in p for p in res["problems"]))
        self.assertTrue(any("deeper answer is 300 to 900" in p for p in res["problems"]))
        self.assertFalse(et.check(self.sample("sample-deeper.md"))["ok"])  # too long for short

    def test_word_count_and_order(self):
        short = "**What it is.** x\n**How it works.** y\n**Where it shows up.** z\n**Why it is used.** a\n**Main tradeoff.** b\n**One alternative.** c\n\nRun next:\n"
        res = et.check(short)
        self.assertTrue(any("words; a short answer is 150 to 250" in p for p in res["problems"]))
        swapped = short.replace("**Main tradeoff.**", "**TMP**").replace("**One alternative.**", "**Main tradeoff.**").replace("**TMP**", "**One alternative.**")
        self.assertTrue(any("out of order" in p for p in et.check(swapped)["problems"]))
        self.assertTrue(any("Next: line" in p for p in et.check(short + "Next: do it\n")["problems"]))

    def test_invented_link_is_caught(self):
        text = self.sample("sample-short.md")
        self.assertEqual(et.check(text, root=self.tmp)["problems"], [])  # the fixture has both sections
        bad = text.replace("plan.md#decisions", "plan.md#queues").replace("](docs/specs/orders-api/spec.md#payment-retry)", "](docs/specs/billing/spec.md)")
        problems = et.check(bad, root=self.tmp)["problems"]
        self.assertTrue(any("section that does not exist: docs/specs/orders-api/plan.md#queues" in p for p in problems))
        self.assertTrue(any("file that does not exist: docs/specs/billing/spec.md" in p for p in problems))

    def test_deeper_route_and_ending(self):
        r = et.parse_route("deeper Private Link in orders-api")
        self.assertEqual(r, {"tech": "Private Link", "scope": "orders-api", "deeper": True, "save": False})
        self.assertNotIn("deeper Service Bus", et.ending("Service Bus", deeper=True))
        self.assertIn("`/crav1-explain-tech deeper Service Bus`", et.ending("Service Bus"))


class TestSave(Base):
    def entry(self, **kw):
        fd, name = tempfile.mkstemp(suffix=".json")
        import os
        os.close(fd)
        f = Path(name)
        f.write_text(json.dumps(dict({"summary": "Service Bus holds payment retries.", "links": ["docs/specs/orders-api/spec.md#payment-retry"]}, **kw)), encoding="utf-8")
        self.addCleanup(f.unlink)
        return str(f)

    def test_nothing_written_without_yes(self):
        before = self.snapshot()
        code, out, _ = run(self.tmp, "save", "--tech", "Service Bus", "--spec", "orders-api", "--input", self.entry())
        self.assertEqual(code, 0)
        res = json.loads(out)
        self.assertEqual(res["written"], [])
        self.assertEqual(res["path"], "docs/specs/orders-api/notes.md")
        self.assertEqual(res["card"]["words"], ["yes", "not-now"])
        self.assertEqual(self.snapshot(), before)

    def test_save_writes_the_right_notes_file(self):
        code, out, err = run(self.tmp, "save", "--tech", "Service Bus", "--spec", "orders-api", "--input", self.entry(), "--yes")
        self.assertEqual(code, 0, err)
        notes = (self.tmp / "docs/specs/orders-api/notes.md").read_text(encoding="utf-8")
        self.assertTrue(notes.startswith("# Notes: orders-api\n\n## Technology notes\n\n### Service Bus ("))
        self.assertRegex(notes, r"### Service Bus \(\d{4}-\d{2}-\d{2}\)\n\nService Bus holds payment retries.\n\n- \[docs/specs/orders-api/spec.md#payment-retry\]\(spec.md#payment-retry\)")
        self.assertEqual(json.loads(out)["written"], ["docs/specs/orders-api/notes.md"])
        code, _, err = run(self.tmp, "save", "--tech", "Service Bus", "--spec", "orders-api", "--input", self.entry(), "--yes")
        self.assertEqual(code, 2)
        self.assertIn("already has a note", err)

    def test_existing_notes_get_the_section_once(self):
        n = self.tmp / "docs/specs/orders-api/notes.md"
        n.write_text("# Notes: orders-api\n\n## Ideas\n\n- keep it small\n", encoding="utf-8")
        run(self.tmp, "save", "--tech", "Service Bus", "--spec", "orders-api", "--input", self.entry(), "--yes")
        run(self.tmp, "save", "--tech", "Private Link", "--spec", "orders-api", "--input", self.entry(links=[]), "--yes")
        text = n.read_text(encoding="utf-8")
        self.assertIn("## Ideas\n\n- keep it small", text)
        self.assertEqual(text.count("## Technology notes"), 1)
        self.assertLess(text.index("### Service Bus"), text.index("### Private Link"))

    def test_architecture_and_refusals(self):
        code, _, err = run(self.tmp, "save", "--tech", "Service Bus", "--spec", "architecture", "--input", self.entry(links=["docs/architecture/spec.md#confirmed"]), "--yes")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.tmp / "docs/architecture/notes.md").is_file())
        for args, why in ((["--spec", "orders-api", "--input", self.entry(links=["docs/specs/orders-api/spec.md#no-such"])], "not in"),
                          (["--spec", "orders-api", "--input", self.entry(links=["docs/specs/billing/spec.md"])], "not a file"),
                          (["--spec", "orders-platform", "--input", self.entry()], "design topic"),
                          (["--spec", "billing", "--input", self.entry()], "no spec named")):
            code, _, err = run(self.tmp, "save", "--tech", "Kafka", *args, "--yes")
            self.assertEqual(code, 2, args)
            self.assertIn(why, err)
        self.assertFalse((self.tmp / "docs/specs/billing").exists())

    def test_saved_ending(self):
        end = et.ending("Service Bus", saved="docs/specs/orders-api/notes.md")
        self.assertIn("Commit the note:\n`/crav1-finalize-commit`", end)
        self.assertIn("Uncommitted: 1 file.", end)


class TestEndingsAndRegistration(unittest.TestCase):
    def test_run_next_shape_and_routes(self):
        for kw in ({}, {"deeper": True, "spec": "orders-api"}, {"not_in_spec": True}, {"saved": "x.md"}):
            text = et.ending("Service Bus", **kw)
            self.assertTrue(text.startswith("Run next:"))
            self.assertNotRegex(text, r"(?m)^Next:")
            for cmd in re.findall(r"(?m)^`([^`]+)`$", text):
                skill = re.match(r"^/(crav1-[a-z0-9-]+)", cmd).group(1)
                self.assertTrue((ROOT / ".cursor/skills/crav1" / skill).is_dir(), cmd)
                if skill == "crav1-explain-tech":
                    self.assertEqual(et.parse_route(cmd.split(" ", 1)[1])["tech"], "Service Bus")

    def test_choice_words_hyphen_only_and_registered(self):
        self.assertTrue(all(re.fullmatch(r"[a-z]+(-[a-z]+)*", w) for w in et.CHOICE_WORDS))
        for f in ("docs/reference/skills.yaml", "docs/reference/index.yaml", "docs/guild-routing.md", "docs/reference/skills/crav1-explain-tech.md",
                  "plugins/crav1/skills/crav1-explain-tech/SKILL.md", ".claude/skills/crav1-explain-tech/SKILL.md"):
            self.assertIn("crav1-explain-tech", (ROOT / f).read_text(encoding="utf-8") if not f.endswith("SKILL.md") else (ROOT / f).read_text(encoding="utf-8") + "crav1-explain-tech", f)

    def test_skill_never_tells_users_to_hand_edit(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never tell the user to edit a spec file by hand", text)
        self.assertIn("Links in the answer come only from `find`", text)


if __name__ == "__main__":
    unittest.main()
