"""1.178.0: build-map colours and legend, stale style rules written and
committed by the kit, the update-kit Run next ending, the ready check asking
for the code repo first and reading owner and merge state in one host lookup,
re-running after an answer, and owner choices from names the kit knows."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import test_review_batch_1176b as rb  # noqa: E402
import test_pr_state_11772 as ps  # noqa: E402

wp = rb.wp
pc = wp.pr_common_mod()
bm = wp.map_mod()
UK = rb.UK
SK = rb.SK
ROOT = rb.ROOT
SHA = ps.SHA


def branch(name, status="ready", **extra):
    base = {"name": name, "status": status, "waits": [], "section": "wave", "wave": 1,
            "tasks": [{"id": 1, "done": status == "done"}]}
    base.update(extra)
    return base


class MapColours(unittest.TestCase):
    def test_states(self):
        self.assertEqual(bm.map_state(branch("a", "done")), "done")
        self.assertEqual(bm.map_state(branch("a", "waiting on a question")), "waiting")
        self.assertEqual(bm.map_state(branch("a", "held", held_text="built, waits for PR 82 to merge")), "waiting")
        self.assertEqual(bm.map_state(branch("a", "held", held_on=["feat/x"])), "waiting")
        self.assertEqual(bm.map_state(branch("a", "held", held_text="in progress")), "todo")
        self.assertEqual(bm.map_state(branch("a", "ready")), "todo")
        self.assertEqual(bm.map_state(branch("a", "waits in order")), "todo")
        self.assertEqual(bm.map_state(branch("a", "blocked", section="blocked")), "blocked")
        self.assertEqual(bm.map_state(branch("a", "ready", loop=True)), "blocked")
        self.assertEqual(bm.map_state(branch("a", "held", held_text="built, waits for PR 1 to merge", failed=True)),
                         "blocked", "a failed check or reopened step is red")

    def test_diagram_has_classes_edges_and_legend(self):
        done = branch("feat/orders-a", "done")
        wait = branch("feat/orders-b", "held", held_text="built, waits for PR 82 to merge", wave=2,
                      waits=["feat/orders-a"], tasks=[{"id": 2, "done": False}])
        red = branch("feat/orders-c", "ready", failed=True, wave=3, waits=["feat/orders-b"],
                     tasks=[{"id": 3, "done": False}])
        todo = branch("feat/orders-d", "ready", wave=4, waits=["feat/orders-c"], tasks=[{"id": 4, "done": False}])
        branches = [done, wait, red, todo]
        text = bm._mermaid(branches, {b["name"]: b for b in branches})
        self.assertIn("  b1 --> b2", text, "out of a done box: solid")
        self.assertIn("  b2 -.-> b3", text, "out of a waiting box: dashed")
        self.assertIn("  b3 ==> b4", text, "out of a blocked box: thick")
        self.assertIn("class b1,key1 done", text)
        self.assertIn("class b2,key2 waiting", text)
        self.assertIn("class b3,key3 blocked", text)
        self.assertIn("class b4,key4 todo", text)
        self.assertIn('subgraph legend["Legend"]', text)
        for label in ("Done", "Waits on a PR or question", "Blocked", "Ready or not started"):
            self.assertIn(f'["{label}"]', text)
        self.assertIn("linkStyle 0 stroke:#4ade80", text)
        self.assertIn("linkStyle 1 stroke:#fbbf24", text)
        self.assertIn("linkStyle 2 stroke:#f87171,stroke-width:4px", text)
        self.assertIn("linkStyle default stroke:#60a5fa", text)

    def test_bright_on_dark(self):
        def lum(hex_colour):
            r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        for colour in bm.MAP_EDGE_COLOURS.values():
            self.assertGreater(lum(colour), 0.35, colour)
        for style in bm.MAP_CLASSES.values():
            text = re.search(r"color:(#[0-9a-f]{6})", style).group(1)
            stroke = re.search(r"stroke:(#[0-9a-f]{6})", style).group(1)
            self.assertGreater(lum(text), 0.8)
            self.assertGreater(lum(stroke), 0.35)
        self.assertIn("color:#cbd5e1", bm.MAP_GROUP_STYLE)

    def test_failed_or_reopened_step_marks_the_walk(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "build-progress"
            folder.mkdir()
            (folder / "feat--orders-a.md").write_text(
                "Branch: feat/orders-a\nTasks: T1\n\n- Step: build T1\n  Result: done\n"
                "- Step: verify\n  Result: failed (check orders-lint)\n", encoding="utf-8")
            (folder / "feat--orders-b.md").write_text(
                "Branch: feat/orders-b\nTasks: T2\n\n- Step: verify\n  Result: failed\n"
                "- Step: verify\n  Result: done\n", encoding="utf-8")
            (folder / "feat--orders-c.md").write_text(
                "Branch: feat/orders-c\nTasks: T3\n\n- Step: build T3\n  Result: reopened\n", encoding="utf-8")
            state = bm.progress_state(tmp)
            self.assertTrue(state["feat/orders-a"]["failed"])
            self.assertFalse(state["feat/orders-b"]["failed"], "a later done clears it")
            self.assertTrue(state["feat/orders-c"]["failed"])

    def test_written_map_colours_a_waiting_pr_amber(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            with mock.patch.dict(os.environ, {"CRAV1_NO_HOST_LOOKUP": "1"}):
                ps.ready(root, "--write-map")
            text = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertIn("classDef waiting", text)
            self.assertRegex(text, r"class [b0-9,]*b\d[b0-9,key]* waiting")
            self.assertIn('subgraph legend["Legend"]', text)

    def test_reference_documents_colours(self):
        text = (SK / "crav1-tasks-ready-to-build/references/build-map.md").read_text(encoding="utf-8")
        self.assertIn("Colours (1.178.0)", text)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class StyleRules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        b = Path(self.tmp.name)
        self.root, self.old, self.new = b / "repo", b / "old", b / "new"
        for tree, text in ((self.old, "style v1\n"), (self.new, "style v2\n")):
            path = tree / rb.ASSETS / "draft-commit-style.mdc"
            path.parent.mkdir(parents=True)
            path.write_text(text, encoding="utf-8")
        self.root.mkdir()
        git(self.root, "init", "-q", "-b", "main")
        for key, value in (("user.email", "person-a@example.com"), ("user.name", "person A"),
                           ("commit.gpgsign", "false")):
            git(self.root, "config", key, value)
        (self.root / ".cursor/rules").mkdir(parents=True)
        (self.root / ".claude/rules").mkdir(parents=True)
        (self.root / ".cursor/rules/draft-commit-style.mdc").write_text(
            "Read crav1-draft-commit-message/references/style.md\n", encoding="utf-8")
        (self.root / ".claude/rules/draft-commit-style.md").write_text(
            "Read crav1-draft-commit-message/references/style.md\n", encoding="utf-8")
        (self.root / "app.txt").write_text("project\n", encoding="utf-8")
        installed = self.root / rb.ASSETS / "draft-commit-style.mdc"
        installed.parent.mkdir(parents=True)
        installed.write_text("style v1\n", encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "start")

    def tearDown(self):
        self.tmp.cleanup()

    def test_write_accepts_style_rules_only(self):
        UK._write(self.root, ".cursor/rules/draft-commit-style.mdc", b"style v2\n")
        self.assertEqual((self.root / ".cursor/rules/draft-commit-style.mdc").read_text(), "style v2\n")
        with self.assertRaises(UK.Refuse):
            UK._write(self.root, "app.txt", b"x")

    def test_apply_and_commit_take_the_stale_rules(self):
        out = UK.apply_overlay(self.root, self.old, self.new, {"cursor", "claude"}, True, set(), set())
        self.assertIn(".cursor/rules/draft-commit-style.mdc", out["touched"])
        self.assertIn(".claude/rules/draft-commit-style.md", out["touched"])
        # The new asset is now installed on this branch, so the rewrite is the kit's own.
        self.assertEqual((self.root / rb.ASSETS / "draft-commit-style.mdc").read_text(), "style v2\n")
        (self.root / "app.txt").write_text("project edit\n", encoding="utf-8")
        done = UK.commit_kit(self.root, "1.177.2", "1.178.0", True, old_root=self.old, new_root=self.new)
        self.assertIn(".cursor/rules/draft-commit-style.mdc", done["committed"])
        self.assertIn(".claude/rules/draft-commit-style.md", done["committed"])
        self.assertIn("app.txt", done["left_uncommitted"])

    def test_a_hand_edited_rule_is_not_committed(self):
        (self.root / ".cursor/rules/draft-commit-style.mdc").write_text("my words\n", encoding="utf-8")
        self.assertFalse(UK.style_rule_kit_owned(self.root, ".cursor/rules/draft-commit-style.mdc"))
        self.assertFalse(UK.style_rule_kit_owned(self.root, "app.txt"))

    def test_rule_with_no_new_asset_is_removed(self):
        (self.new / rb.ASSETS / "draft-commit-style.mdc").unlink()
        actions = UK.build_actions(self.root, self.old, self.new, {"cursor", "claude"})
        self.assertIn(".cursor/rules/draft-commit-style.mdc", actions["files"]["delete"])
        UK.apply_overlay(self.root, self.old, self.new, {"cursor", "claude"}, True, set(), set())
        self.assertFalse((self.root / ".cursor/rules/draft-commit-style.mdc").exists())
        self.assertTrue(UK.style_rule_kit_owned(self.root, ".cursor/rules/draft-commit-style.mdc"))
        done = UK.commit_kit(self.root, "1.177.2", "1.178.0", True, old_root=self.old, new_root=self.new)
        self.assertIn(".cursor/rules/draft-commit-style.mdc", done["committed"])


class UpdateKitEnding(unittest.TestCase):
    def test_run_next_and_no_next_line(self):
        for path in (SK / "crav1-update-kit/SKILL.md", ROOT / "docs/from-update-kit.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("Run next: nothing needed now.", text, path)
            self.assertNotRegex(text, r"(?m)^Next:", path)
        overlay = (SK / "crav1-update-kit/references/overlay.md").read_text(encoding="utf-8")
        for word in ("delete it", "remove it by hand", "edit it by hand", "hand-edit"):
            self.assertNotIn(word, overlay)


class OneHostLookup(unittest.TestCase):
    def test_host_state_reads_the_author_too(self):
        run = ps.HostState()
        out, cmd = run.run_with("github", {"state": "OPEN", "author": {"login": "person-b", "name": "person B"}})
        self.assertEqual(out["author"], "person B")
        self.assertIn("state,mergeCommit,mergedAt,closedAt,author", cmd)
        out, cmd = run.run_with("azure", {"status": "active", "author": "person B"})
        self.assertEqual(out["author"], "person B")
        self.assertIn("createdBy.displayName", " ".join(cmd))

    def test_owner_recorded_from_the_same_lookup_and_no_second_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            log = root / "build-progress/feat--orders-cicd.md"
            log.write_text(re.sub(r"(?m)^(PR author|Opened by):.*\n", "", log.read_text(encoding="utf-8")),
                           encoding="utf-8")
            states = {71: {"state": "open", "sha": None, "date": None, "author": "person A"},
                      82: {"state": "open", "sha": None, "date": None, "author": "person B"}}
            _stack, ref, state = ps.host(states)
            env = {k: v for k, v in os.environ.items() if k != "CRAV1_NO_HOST_LOOKUP"}
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(wp, "host_pr_ref", side_effect=ref), \
                    mock.patch.object(pc, "host_lookup", side_effect=ps.lookup_of(state)) as calls, \
                    mock.patch.object(pc, "host_author", return_value=None) as author:
                out = ps.ready_json(root)
            self.assertEqual(author.call_count, 0, "no second lookup for the owner")
            self.assertEqual(calls.call_count, 2)
            self.assertIn("PR author: person B", log.read_text(encoding="utf-8"))
            self.assertEqual(out["owner_unknown"], [])
            self.assertIsNone(out["ask_first"])

    def test_repo_is_asked_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            env = {k: v for k, v in os.environ.items() if k != "CRAV1_NO_HOST_LOOKUP"}
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(pc, "host_author", return_value=None):
                out = ps.ready_json(root)
            self.assertEqual(out["ask_first"], "code-repo")
            self.assertEqual(out["owner_unknown"], [], "an unhosted PR's owner is not asked yet")

    def test_owner_asked_only_when_the_host_names_no_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            log = root / "build-progress/feat--orders-readme.md"
            log.write_text(re.sub(r"(?m)^(PR author|Opened by):.*\n", "", log.read_text(encoding="utf-8")),
                           encoding="utf-8")
            with ps.fake_host({71: {"state": "open", "sha": None, "date": None},
                               82: {"state": "open", "sha": None, "date": None}}):
                out = ps.ready_json(root)
            self.assertEqual([item["pr"] for item in out["owner_unknown"]], [71])
            self.assertEqual(out["ask_first"], "pr-author")
            self.assertEqual(out["owner_choices"][-1], "Don't know")
            self.assertIn("person B", out["owner_choices"])

    def test_docs_say_repo_first(self):
        text = (SK / "crav1-tasks-ready-to-build/references/pr-owner.md").read_text(encoding="utf-8")
        self.assertLess(text.index("## Repo first"), text.index("## Owner"))
        self.assertIn("20-second timeout", text)


class RerunAfterAnswer(unittest.TestCase):
    def test_code_repo_and_pr_author_return_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
            proc = subprocess.run([sys.executable, str(rb.WALK), "code-repo", "--root", str(root), "--pr", "71",
                                   "--repo", "orders-api"], capture_output=True, text=True, check=False, env=env)
            data = json.loads(proc.stdout)
            self.assertIn("readiness --root", data["rerun"])
            self.assertIn("in this same run", data["line"])
            proc = subprocess.run([sys.executable, str(rb.WALK), "pr-author", "--root", str(root), "--pr", "82",
                                   "--name", "person B"], capture_output=True, text=True, check=False, env=env)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "recorded", proc.stderr)
            self.assertIn("readiness --root", data["rerun"])

    def test_docs_rerun_and_never_still_stand(self):
        ref = (SK / "crav1-tasks-ready-to-build/references/pr-owner.md").read_text(encoding="utf-8")
        self.assertIn("run the ready check again in this same run", ref)
        self.assertIn("never say the earlier steps still stand", ref)
        skill = (SK / "crav1-tasks-ready-to-build/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("repo first, rerun", skill)


class OwnerChoices(unittest.TestCase):
    def test_known_names_are_offered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            (root / "build-progress/feat--orders-extra.md").write_text(
                "Branch: feat/orders-extra\nOwner: self\nOpened by: person C\nPR 90\n", encoding="utf-8")
            notes = Path(tmp) / "docs/notes"
            notes.mkdir()
            (notes / "2026-11-10-pr-orders-api-91.md").write_text("---\nauthor: person D\n---\nbody\n",
                                                                  encoding="utf-8")
            names = wp.known_people(root)
            for who in ("person B", "person C", "person D"):
                self.assertIn(who, names)
            self.assertNotIn("self", names)
            self.assertEqual(len(names), len({n.lower() for n in names}))
            self.assertEqual(wp.owner_choices(root)[-1], "Don't know")

    def test_pr_author_lists_choices_when_host_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ps.specs_repo(tmp)
            env = dict(os.environ, CRAV1_NO_HOST_LOOKUP="1")
            proc = subprocess.run([sys.executable, str(rb.WALK), "pr-author", "--root", str(root), "--pr", "71"],
                                  capture_output=True, text=True, check=False, env=env)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "not-found")
            self.assertIn("person B", data["choices"])
            self.assertEqual(data["choices"][-1], "Don't know")


if __name__ == "__main__":
    unittest.main()
