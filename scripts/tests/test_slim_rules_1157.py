"""1.157.0: a short always-loaded rule, its full text in standing-rules.md, and walk endings that are Run next only."""

from __future__ import annotations

import importlib.util
import inspect
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE = ROOT / ".cursor/rules/crav1.mdc"
FULL = ROOT / "docs/reference/standing-rules.md"
SK = ROOT / ".cursor/skills/crav1"
WORD_CAP = 700


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bw = load(SK / "crav1-build-walk/scripts/build_walk.py", "build_walk_1157")
br = load(SK / "crav1-build-walk/scripts/branch_run.py", "branch_run_1157")
we = load(SK / "crav1-tasks-ready-to-build/scripts/walk_ending.py", "walk_ending_1157")
lint = load(ROOT / "scripts/kit-lint.py", "kit_lint_1157")

# Sentences the rule held before 1.157.0. Each must still be found word for word.
MOVED = (
    "The landscape, glossary, picture and `Synced at` rules live in the skills that write them",
    "`/crav1-existing-to-specs` still runs only when the user names repos.",
    "`/crav1-read-environment` still runs only when the user names the host. Naming production, prod, or live stops.",
    "While `/crav1-what-do-we-know-about-this` is the running skill, do not start `/crav1-help`",
    "Never ask what the conversation, the files, or an earlier answer already settles; use it and say so in one line.",
    "Gather the questions that remain into one batch, not one per turn.",
    "Confirm all writes once at the end with a single yes, listing what will be written.",
    "A question has at most 4 options; a fifth goes under Other.",
    "the question text does not also say `Recommendation: X`.",
    "A prompt for a value the user left out is outside the budget; every other prompt, including one at a stop, counts (1.95.0).",
    "offer a work branch first, never Stay there. Specs and docs, and the specs repo, are exempt.",
    "never an inline `python -`, `node -e` or heredoc script that edits files.",
    "Set `PYTHONUTF8=1` and pass `-X utf8`.",
    "Never as a Markdown link, `file://`, `vscode://` or an absolute path.",
    "A quoted note in `docs/notes/` gets `Used by <slug>`. `Absorbed by <slug>` only after the user says yes.",
    "Full install paths: `docs/install.md` in the kit repo.",
)

# Rules every session needs: they stay in the always-loaded rule.
CORE = (
    "Specs, not chat history, are the source of truth.",
    "name only these six",
    "call `/crav1-help` and quote its answer with its source. Never give an order from memory.",
    "A run ends with one `Next:` line",
    "`Run next:` block first",
    "Never rebase.",
    "merging its base in",
    "never `--flags`",
    "single yes",
    " (Recommended)",
    "Implementation code is never written or committed on a base branch",
    "code-branch.md",
    "running-scripts.md",
    "question-cards.md",
    "standing-rules.md",
    "Production data is never read.",
    "Do not scaffold an application unless the user asked for one.",
)


def words(text: str) -> int:
    return len(text.split())


class ShortRule(unittest.TestCase):
    def test_rule_is_under_the_cap(self):
        self.assertLessEqual(words(RULE.read_text(encoding="utf-8")), WORD_CAP)

    def test_copies_match(self):
        text = RULE.read_text(encoding="utf-8")
        self.assertEqual((ROOT / "plugins/crav1/rules/crav1.mdc").read_text(encoding="utf-8"), text)
        self.assertLessEqual(words((ROOT / ".claude/CLAUDE.md").read_text(encoding="utf-8")), WORD_CAP + 50)

    def test_core_rules_stay(self):
        text = RULE.read_text(encoding="utf-8")
        for rule in CORE:
            self.assertIn(rule, text)

    def test_moved_rules_are_still_found_word_for_word(self):
        full = FULL.read_text(encoding="utf-8")
        for sentence in MOVED:
            self.assertIn(sentence, full)
        self.assertNotIn("Asking (1.70.0, 1.93.0)", RULE.read_text(encoding="utf-8"))

    def test_full_page_ships_next_to_the_skills(self):
        full = FULL.read_text(encoding="utf-8")
        for copy in (SK / "crav1-docs/reference/standing-rules.md",
                     ROOT / "plugins/crav1/skills/crav1-docs/reference/standing-rules.md",
                     ROOT / ".claude/skills/crav1-docs/reference/standing-rules.md"):
            self.assertTrue(copy.is_file(), copy)

    def test_order_line_has_no_stale_next(self):
        self.assertNotIn("keeps one Next", RULE.read_text(encoding="utf-8"))


def state(**kwargs):
    base = {
        "mode": "walk",
        "owner": "self",
        "branch": "feat/orders-host-setup-scripts",
        "base": "develop",
        "tasks": [{"id": 3, "title": "Apply the CI build policy"}],
        "pr": 51,
    }
    base.update(kwargs)
    return base


def no_next(text: str) -> bool:
    return "Next:" not in text.replace("Run next:", "")


class WalkEndingRunNextOnly(unittest.TestCase):
    phases = ("confirm-owner", "approval", "live-dry", "live-yes", "build", "verify",
              "commit", "open-pr", "merge-base", "merge-pr", "tick", "wait-merge")

    def test_no_phase_prints_a_next_line(self):
        for phase in self.phases:
            out = bw.next_for(state(phase=phase))
            self.assertTrue(out["ending"].startswith("Run next:"), phase)
            self.assertTrue(no_next(out["ending"]), (phase, out["ending"]))

    def test_next_data_stays_one_per_entry(self):
        out = bw.next_for(state(phase="tick", ready_branches=[
            {"branch": "feat/orders-note", "tasks": [{"id": 5, "title": "Note the policy"}]}]))
        commands = [line for line in out["ending"].splitlines() if line.startswith("`")]
        self.assertEqual(len(out["next"]), len(commands))
        for line, command in zip(out["next"], commands):
            self.assertTrue(line.startswith("Next: " + command.strip("`") + ","), (line, command))

    def test_grouping_prints_run_next_only(self):
        out = bw.next_for({"mode": "grouping", "branches": [
            {"branch": "feat/orders-note", "tasks": [{"id": 5, "title": "Note the policy"}]}]})
        self.assertTrue(no_next(out["ending"]))
        self.assertIn("`/crav1-build-walk T5`", out["ending"])

    def test_held_step_says_why_on_waiting(self):
        out = bw.next_for(state(phase="approval"))
        self.assertIn("`/crav1-show-or-ask-open-questions`", out["ending"])
        self.assertIn("Waiting: T3 Apply the CI build policy is held and that Approval needed item is unanswered.",
                      out["ending"])
        merge = bw.next_for(state(phase="wait-merge", owner="other"))
        self.assertIn("Waiting: Ticks on feat/orders-host-setup-scripts wait until pull request 51 is merged.",
                      merge["ending"])
        given = bw.next_for(state(phase="approval", waiting="Waiting: the partner's yes."))
        self.assertEqual(given["ending"].count("Waiting:"), 1)

    def test_no_branch_left_runs_verify(self):
        out = bw.next_for(state(phase="next-task", slug="orders-capacity", spec_count=2, ready_branches=[]))
        self.assertIn("`/crav1-verify-build-against-spec orders-capacity`", out["ending"])
        self.assertTrue(no_next(out["ending"]))

    def test_branch_run_ending_has_no_next(self):
        out = br.ending({"slug": "orders-api", "branch": "feat/orders-cicd", "pr": 12,
                         "built": [{"task": "T2", "commit": "a1b2c3d4e5f6", "tests": "green"}]})
        self.assertTrue(no_next(out["ending"]))

    def test_compose_has_no_next_lines(self):
        self.assertNotIn("next_lines", inspect.signature(we.compose).parameters)


class NoWalkNextExamples(unittest.TestCase):
    def test_lint_flags_a_walk_next_in_any_skill(self):
        self.assertEqual(lint.stray_next_problems(str(ROOT)), [])
        for path in [*(SK / "crav1-build-walk").rglob("*.md"), *(SK / "crav1-finalize-commit").rglob("*.md")]:
            self.assertNotIn("Next: /crav1-build-walk", path.read_text(encoding="utf-8"), path)

    def test_finalize_commit_resume_is_a_run_next_entry(self):
        text = (SK / "crav1-finalize-commit/references/commit.md").read_text(encoding="utf-8")
        self.assertIn("`/crav1-build-walk orders-api feat/orders-cicd`", text)
        ending = (ROOT / "docs/reference/run-ending.md").read_text(encoding="utf-8")
        self.assertIn("never has a `Next:` line (1.157.0)", ending)
        self.assertNotIn("then one full `Next:` line for that branch", ending)


if __name__ == "__main__":
    unittest.main()
