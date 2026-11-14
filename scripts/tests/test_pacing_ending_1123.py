"""1.123.0: large-batch pacing, the pause ending, and the commit Next line."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PacingAndEnding(unittest.TestCase):
    def test_large_batch_counts_and_always_offers_one_by_one(self):
        pacing = (ROOT / ".cursor/skills/crav1/crav1-tighten-spec/references/pacing.md").read_text(encoding="utf-8")
        skill = (ROOT / ".cursor/skills/crav1/crav1-tighten-spec/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("More than 8 issues", skill)
        self.assertIn("references/pacing.md", skill)
        self.assertIn("12 issues to fix, 3 open questions, 4 small wording.", pacing)
        self.assertIn("One by one is always offered", pacing)
        self.assertIn("Do not print findings", pacing)
        self.assertIn("Left for /crav1-resolve-open-questions: I3, I10, I11.", pacing)
        self.assertIn("no menu", skill.lower())

    def test_pause_is_one_line_then_the_shared_ending(self):
        progress = (
            ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/references/progress.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Paused at resolve-open-questions.", progress)
        # 1.154.0: the pause names the command in a Run next block, not a Next: line.
        self.assertIn(
            "Run next:\n\n`/crav1-tighten-and-plan-ready-to-build docs/playbooks/orders-retry.md`\ncontinues from plan-from-spec",
            progress,
        )
        self.assertNotIn("Next: /crav1-tighten-and-plan-ready-to-build", progress)
        self.assertIn("Waiting:", progress)
        self.assertIn("Uncommitted:", progress)
        self.assertIn("- Extra: review-security", progress)
        self.assertIn("cover --yes", progress)
        self.assertIn("outside this walk", progress)
        self.assertIn("nothing new", progress)

    def test_commit_next_line_follows_run_ending(self):
        ending = (ROOT / "docs/reference/run-ending.md").read_text(encoding="utf-8")
        self.assertIn("walk-progress.md", ending)
        self.assertIn("continue_from", ending)
        self.assertIn(
            "Next: /crav1-tighten-and-plan-ready-to-build docs/playbooks/orders-retry.md, because the walk paused before plan-from-spec.",
            ending,
        )
        self.assertIn("Next: push main, because a pull request cannot open from main into itself.", ending)
        self.assertIn("/crav1-open-pr", ending)
        skill = (ROOT / ".cursor/skills/crav1/crav1-finalize-commit/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("at most two commits", skill.lower())
        self.assertIn("run-ending.md", skill)


if __name__ == "__main__":
    unittest.main()
