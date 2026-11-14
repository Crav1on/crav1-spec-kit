"""1.149.0: branch rules stay reachable, and a typical run does not open them.

Word counts are whitespace words, the same count as scripts/check-kit-docs.py.
A file counts when that path's instructions say to read or open it.
Files both the old and new typical path open are left out of the totals.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURSOR = ROOT / ".cursor/skills/crav1"

# (skill folder, reference file, a rule that used to live in SKILL.md)
CASES = (
    ("crav1-tasks-ready-to-build", "work-branches.md", "squash merges are checked"),
    ("crav1-tasks-ready-to-build", "sub-branches.md", "Spec branch and sub-branches"),
    ("crav1-tasks-ready-to-build", "promotion.md", "pipeline runs"),
    ("crav1-tasks-ready-to-build", "work-item-line.md", "crav1-ado-sync"),
    ("crav1-tasks-ready-to-build", "risk-blocks.md", "matches no question still blocks"),
    ("crav1-tasks-ready-to-build", "next-question.md", "crav1-resolve-open-questions"),
    ("crav1-tasks-ready-to-build", "next-verify.md", "crav1-verify-build-against-spec"),
    ("crav1-tasks-ready-to-build", "next-nothing.md", "nothing needed now"),
    ("crav1-verify-build-against-spec", "work-branches.md", "never fetch, never check out"),
    ("crav1-verify-build-against-spec", "sub-branches.md", "left behind"),
    ("crav1-verify-build-against-spec", "promotion.md", "not yet tagged"),
    ("crav1-verify-build-against-spec", "tick-pending.md", "Say yes to tick"),
    ("crav1-verify-build-against-spec", "host-setup-task.md", "Verify never runs `apply`"),
    ("crav1-verify-build-against-spec", "next-fix.md", "crav1-fix-build-gaps"),
    ("crav1-verify-build-against-spec", "next-build.md", "crav1-build-tasks"),
    ("crav1-verify-build-against-spec", "next-plan.md", "crav1-plan-from-spec"),
    ("crav1-verify-build-against-spec", "next-tighten.md", "crav1-tighten-spec"),
    ("crav1-verify-build-against-spec", "next-open-pr.md", "to push to PR <n> and update its description or comment"),
    ("crav1-verify-build-against-spec", "next-done.md", "demoable"),
    ("crav1-verify-build-against-spec", "next-walk.md", "1.142.0"),
    ("crav1-build-features", "dirty-tree.md", "Never stash unless they ask"),
    ("crav1-build-features", "task-branch-cases.md", "does not write `Approved:`"),
    ("crav1-build-features", "status-needs-fix.md", "resume: fix"),
    ("crav1-build-features", "status-needs-ready.md", "resume: ready"),
    ("crav1-build-features", "status-needs-dependency.md", "dependency-start"),
    ("crav1-build-features", "status-blocked.md", "End the board"),
    ("crav1-build-features", "status-skip.md", "skip-slug"),
    ("crav1-build-features", "status-stop.md", "end the board"),
    ("crav1-build-features", "picture-offer.md", "crav1-refresh-system-notes"),
    ("crav1-build-features", "parked.md", "crav1-retire-spec"),
    ("crav1-finalize-commit", "commit.md", "git pull --no-rebase --no-commit"),
    ("crav1-resolve-open-questions", "after-choice.md", "**None** writes `- Blocks: none`"),
    ("crav1-resolve-open-questions", "one-question.md", "1.90.5"),
    ("crav1-resolve-open-questions", "stale-point.md", "research-stale-clear.md"),
    ("crav1-resolve-open-questions", "list-done.md", "crav1-plan-from-spec"),
    ("crav1-what-do-we-know-about-this", "no-slice.md", "crav1-spark-to-spec"),
    ("crav1-what-do-we-know-about-this", "report-writes.md", "docs/playbooks/"),
)

CAPS = {
    "crav1-tasks-ready-to-build": 1100,
    "crav1-verify-build-against-spec": 1500,
    "crav1-build-features": 1600,
    "crav1-finalize-commit": 1300,
    "crav1-resolve-open-questions": 1400,
    "crav1-what-do-we-know-about-this": 1500,
}


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


class LoadPath(unittest.TestCase):
    def test_each_case_file_is_named_with_only_when(self):
        for skill, name, needle in CASES:
            folder = CURSOR / skill
            skill_text = (folder / "SKILL.md").read_text(encoding="utf-8")
            target = folder / "references" / name
            self.assertTrue(target.is_file(), target)
            self.assertIn(name, skill_text, skill)
            self.assertIn("only when", skill_text.lower(), skill)
            # The load-when line that names this file also says only when.
            line = next(l for l in skill_text.splitlines() if name in l)
            self.assertIn("only when", line.lower(), f"{skill} {name}")
            self.assertIn(needle, target.read_text(encoding="utf-8"), f"{skill} {name}")

    def test_skill_files_are_under_the_cap(self):
        for skill, cap in CAPS.items():
            n = words(CURSOR / skill / "SKILL.md")
            self.assertLessEqual(n, cap, f"{skill} is {n} words")

    def test_new_files_use_generic_names(self):
        banned = ("contoso", "fabrikam", "person a", "northwind")
        for skill, name, _needle in CASES:
            text = (CURSOR / skill / "references" / name).read_text(encoding="utf-8").lower()
            for word in banned:
                self.assertNotIn(word, text, f"{skill}/{name}")

    def test_review_pr_stays_a_router(self):
        text = (CURSOR / "crav1-review-pr" / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(words(CURSOR / "crav1-review-pr" / "SKILL.md"), 1600)
        self.assertIn("references/", text)


if __name__ == "__main__":
    unittest.main()
