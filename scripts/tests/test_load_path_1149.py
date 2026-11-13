"""1.149.0: long skills keep the always-needed path and load a branch file only when it applies.

Word counts use str.split, the same count as scripts/check-kit-docs.py.
Before totals are the 1.145.0 files a typical run opened. After totals are this tree.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"

# Typical-run word totals measured on 1.145.0 (before) and this split (after).
# Whitespace words. A file is counted when that path's instructions say to read it.
BEFORE = {
    "verify": 2468,
    "build-features": 3827,
    "tasks-ready": 1999,
    "what-do-we-know": 3323,
    "finalize-choices": 2694,
    "resolve": 1539,
}


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def skill(name: str) -> Path:
    return SK / name


class LoadPath1149(unittest.TestCase):
    def test_skill_files_stay_under_the_cap(self):
        caps = {
            "crav1-verify-build-against-spec": 1500,
            "crav1-build-features": 1500,
            "crav1-tasks-ready-to-build": 1500,
            "crav1-what-do-we-know-about-this": 1500,
            "crav1-finalize-commit": 1200,
            "crav1-resolve-open-questions": 1300,
        }
        for name, cap in caps.items():
            n = words(skill(name) / "SKILL.md")
            self.assertLessEqual(n, cap, f"{name} is {n} words")

    def test_verify_loads_branches_only_when_they_apply(self):
        s = (skill("crav1-verify-build-against-spec") / "SKILL.md").read_text(encoding="utf-8")
        for name in ("work-branches.md", "sub-branches.md", "promotion.md", "host-setup-tasks.md", "tick-pending.md"):
            self.assertIn(name, s)
        self.assertIn("Do not open", s)
        self.assertIn("1.115.0", s)
        self.assertIn("crav1-host-setup", s)
        self.assertNotIn("Say yes to tick", s)
        self.assertNotIn("left behind:", s)
        ref = skill("crav1-verify-build-against-spec") / "references"
        self.assertIn("never fetch, never check out", (ref / "work-branches.md").read_text(encoding="utf-8"))
        self.assertIn("left behind:", (ref / "sub-branches.md").read_text(encoding="utf-8"))
        self.assertIn("Pipeline runs not checked", (ref / "promotion.md").read_text(encoding="utf-8"))
        self.assertIn("Verify never runs `apply`", (ref / "host-setup-tasks.md").read_text(encoding="utf-8"))
        self.assertIn("Say yes to tick", (ref / "tick-pending.md").read_text(encoding="utf-8"))

    def test_build_features_does_not_open_task_branches_up_front(self):
        s = (skill("crav1-build-features") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/task-branches.md", s)
        self.assertIn("Do not open it when the line is `feat/<slug>`", s)
        self.assertIn("references/worker-status.md", s)
        self.assertIn("references/picture-offer.md", s)
        self.assertIn("ready-partial", s)
        self.assertNotIn("Never stash unless they ask", s)
        self.assertNotIn("un-park", s)
        ref = skill("crav1-build-features") / "references"
        self.assertIn("belongs to <repo>", (ref / "task-branches.md").read_text(encoding="utf-8"))
        self.assertIn("does not write `Approved:`", (ref / "needs-yes.md").read_text(encoding="utf-8"))
        self.assertIn("needs_dependency", (ref / "worker-status.md").read_text(encoding="utf-8"))
        self.assertIn("Never stash unless they ask", (ref / "dirty-tree.md").read_text(encoding="utf-8"))
        self.assertIn("un-park", (ref / "parked.md").read_text(encoding="utf-8"))

    def test_tasks_ready_keeps_the_classifier_and_points_at_the_list(self):
        s = (skill("crav1-tasks-ready-to-build") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/task-list.md", s)
        self.assertIn("references/slice-branches.md", s)
        self.assertIn("references/other-next.md", s)
        self.assertIn("`Blocks: none`", s)
        self.assertIn("Any `Blocks:` line wins", s)
        self.assertIn("question_blocks.py", s)
        self.assertIn("does not write `verify.md`", s)
        self.assertNotIn("squash merges are checked", s)
        self.assertNotIn("cycle T3", s)
        ref = skill("crav1-tasks-ready-to-build") / "references"
        self.assertIn("ready_lines", (ref / "task-list.md").read_text(encoding="utf-8"))
        self.assertIn("squash merges are checked", (ref / "slice-branches.md").read_text(encoding="utf-8"))
        self.assertIn("because that question blocks the first task", (ref / "other-next.md").read_text(encoding="utf-8"))
        self.assertIn("matches no question still blocks", (ref / "plan-risk.md").read_text(encoding="utf-8"))
        self.assertIn("cycle T3", (ref / "cycle.md").read_text(encoding="utf-8"))

    def test_other_splits_keep_the_rules_in_the_branch_file(self):
        know = (skill("crav1-what-do-we-know-about-this") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/startup-options.md", know)
        self.assertIn("references/no-slice.md", know)
        self.assertIn("Do not start `/crav1-help`", know)
        self.assertNotIn("Fill in **Unexplained**", know)
        know_ref = skill("crav1-what-do-we-know-about-this") / "references"
        self.assertIn("name only `/crav1-spark-to-spec`", (know_ref / "startup-options.md").read_text(encoding="utf-8"))
        self.assertIn("Fill in **Unexplained**", (know_ref / "no-slice.md").read_text(encoding="utf-8"))

        commit = (skill("crav1-finalize-commit") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/commit.md", commit)
        self.assertIn("at most two commits", commit.lower())
        self.assertNotIn("git pull --no-rebase", commit)
        body = (skill("crav1-finalize-commit") / "references/commit.md").read_text(encoding="utf-8")
        self.assertIn("git pull --no-rebase --no-commit", body)
        self.assertIn("to push to PR <n> and update its description or comment", body)
        hook = (skill("crav1-finalize-commit") / "references/trailer-hook.md").read_text(encoding="utf-8")
        self.assertIn("never apply the Recommended pick", hook)

        resolve = (skill("crav1-resolve-open-questions") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/catalog.md", resolve)
        self.assertIn("references/stale-point.md", resolve)
        self.assertIn("references/one-question.md", resolve)
        self.assertIn("**None** writes `- Blocks: none`", resolve)
        self.assertIn("Never remove an `Approved:` line", resolve)
        self.assertNotIn("answer-custom", resolve)
        self.assertIn("answer-custom", (skill("crav1-resolve-open-questions") / "references/catalog.md").read_text(encoding="utf-8"))

    def test_typical_runs_load_fewer_words_than_1_145(self):
        after = {
            "verify": words(skill("crav1-verify-build-against-spec") / "SKILL.md")
            + words(skill("crav1-verify-build-against-spec") / "references/test-dependencies.md")
            + words(skill("crav1-verify-build-against-spec") / "references/work-branches.md"),
            "build-features": words(skill("crav1-build-features") / "SKILL.md")
            + words(skill("crav1-build-features") / "references/picture-offer.md"),
            "tasks-ready": words(skill("crav1-tasks-ready-to-build") / "SKILL.md")
            + words(skill("crav1-tasks-ready-to-build") / "references/task-list.md")
            + words(skill("crav1-tasks-ready-to-build") / "references/slice-branches.md"),
            "what-do-we-know": words(skill("crav1-what-do-we-know-about-this") / "SKILL.md")
            + words(skill("crav1-what-do-we-know-about-this") / "references/live-reads.md")
            + words(skill("crav1-what-do-we-know-about-this") / "references/answer.md"),
            "finalize-choices": words(skill("crav1-finalize-commit") / "SKILL.md")
            + words(skill("crav1-finalize-commit") / "branches/message-only/BRANCH.md"),
            "resolve": words(skill("crav1-resolve-open-questions") / "SKILL.md")
            + words(skill("crav1-resolve-open-questions") / "references/catalog.md"),
        }
        for name, before in BEFORE.items():
            self.assertLess(after[name], before, f"{name}: {after[name]} is not under {before}")


if __name__ == "__main__":
    unittest.main()
