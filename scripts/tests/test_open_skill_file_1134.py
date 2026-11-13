"""1.134.0: a skill that runs another kit skill opens that file.

Command-only frontmatter stays. The open-the-file rule lives in one page.
Call sites name a sibling path and point at that page.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURSOR = ROOT / ".cursor" / "skills" / "crav1"
TREES = (
    CURSOR,
    ROOT / ".claude" / "skills",
    ROOT / "plugins" / "crav1" / "skills",
)
RULE = "open-skill-file.md"
OPEN = re.compile(
    r"Open `(\.\./crav1-[a-z0-9-]+/"
    r"(?:SKILL\.md|(?:references|branches)/[A-Za-z0-9_./-]+\.md))`"
)
PHRASES = (
    "file-read tool",
    "slash command",
    "skill tool",
    "command-only",
    "open the file instead and continue",
    "never a reason to stop",
    ".claude/skills/crav1-<name>/SKILL.md",
    ".cursor/skills/crav1/crav1-<name>/SKILL.md",
    "skills/crav1-<name>/SKILL.md",
)
STEP_SKILLS = (
    "crav1-review-architecture",
    "crav1-tighten-spec",
    "crav1-resolve-open-questions",
    "crav1-plan-from-spec",
    "crav1-review-plan",
    "crav1-tighten-plan",
    "crav1-tasks-ready-to-build",
    "crav1-review-security",
    "crav1-model-data",
    "crav1-show-or-ask-open-questions",
    "crav1-suggest-tests-for-code",
    "crav1-tighten-and-plan-ready-to-build",
    "crav1-build-features",
    "crav1-fix-bug",
    "crav1-update-specs-from-changes-and-prs",
    "crav1-add-to-spec",
    "crav1-read-environment",
)
NOT_COMMAND_ONLY = ("crav1-help", "crav1-update-kit")

WALK = "crav1-tighten-and-plan-ready-to-build"
LOCKED = [
    "../crav1-review-architecture/SKILL.md",
    "../crav1-tighten-spec/SKILL.md",
    "../crav1-resolve-open-questions/SKILL.md",
    "../crav1-plan-from-spec/SKILL.md",
    "../crav1-review-plan/SKILL.md",
    "../crav1-tighten-plan/SKILL.md",
]
# The ready check writes the map itself (1.146.0). It does not open that skill.
EXTRAS = [
    "../crav1-review-security/SKILL.md",
    "../crav1-model-data/SKILL.md",
    "../crav1-show-or-ask-open-questions/SKILL.md",
    "../crav1-suggest-tests-for-code/SKILL.md",
]


def skill_file(*parts: str) -> Path:
    return CURSOR.joinpath(*parts)


REQUIRED = {
    skill_file(WALK, "SKILL.md"): LOCKED,
    skill_file(WALK, "references", "steps.md"): LOCKED + EXTRAS,
    skill_file(WALK, "references", "playbook.md"): [
        "../crav1-resolve-open-questions/references/apply.md",
        "../crav1-add-to-spec/SKILL.md",
        "../crav1-add-to-spec/references/fact.md",
    ],
    skill_file(WALK, "references", "readiness.md"): [
        "../crav1-plan-from-spec/SKILL.md",
        "../crav1-resolve-open-questions/SKILL.md",
        "../crav1-review-plan/SKILL.md",
        "../crav1-tighten-plan/SKILL.md",
    ],
    skill_file("crav1-build-features", "SKILL.md"): [
        "../crav1-create-feature-branch/SKILL.md",
        "../crav1-create-feature-branch/references/code-branch.md",
        "../crav1-create-feature-branch/references/task-branch.md",
        "../crav1-build-tasks/branches/several-tasks/BRANCH.md",
    ],
    skill_file("crav1-update-specs-from-changes-and-prs", "SKILL.md"): [
        "../crav1-add-to-spec/SKILL.md",
    ],
    skill_file("crav1-update-specs-from-changes-and-prs", "references", "common.md"): [
        "../crav1-add-to-spec/SKILL.md",
    ],
    skill_file("crav1-update-specs-from-changes-and-prs", "references", "manual-flow.md"): [
        "../crav1-add-to-spec/SKILL.md",
    ],
    skill_file("crav1-update-specs-from-changes-and-prs", "references", "auto-flow.md"): [
        "../crav1-add-to-spec/SKILL.md",
    ],
    skill_file("crav1-read-environment", "references", "sections.md"): [
        "../crav1-refresh-system-notes/SKILL.md",
        "../crav1-refresh-system-notes/references/handoff-read-environment.md",
        "../crav1-existing-to-specs/branches/repos-only/BRANCH.md",
        "../crav1-add-to-spec/references/handoffs-read-environment.md",
    ],
    skill_file("crav1-resolve-open-questions", "references", "apply.md"): [
        "../crav1-add-to-spec/references/fact.md",
    ],
    skill_file("crav1-suggest-tests-for-code", "SKILL.md"): [
        "../crav1-add-to-spec/SKILL.md",
        "../crav1-add-to-spec/references/handoffs-suggest-tests.md",
    ],
}

RULE_POINTERS = [
    skill_file(WALK, "SKILL.md"),
    skill_file(WALK, "references", "common.md"),
    skill_file(WALK, "references", "steps.md"),
    skill_file(WALK, "references", "playbook.md"),
    skill_file(WALK, "references", "readiness.md"),
    *REQUIRED.keys(),
    skill_file("crav1-fix-bug", "SKILL.md"),
    skill_file("crav1-add-to-spec", "references", "pr-record.md"),
    skill_file("crav1-add-to-spec", "references", "merge-safe.md"),
    skill_file("crav1-add-to-spec", "references", "handoffs-picture.md"),
]

DOES_NOT_OPEN = [
    skill_file("crav1-fix-bug", "SKILL.md"),
    skill_file("crav1-add-to-spec", "references", "pr-record.md"),
    skill_file("crav1-add-to-spec", "references", "merge-safe.md"),
    skill_file("crav1-add-to-spec", "references", "handoffs-picture.md"),
]

SCAN = (
    WALK,
    "crav1-build-features",
    "crav1-fix-bug",
    "crav1-update-specs-from-changes-and-prs",
    "crav1-add-to-spec",
    "crav1-read-environment",
    "crav1-resolve-open-questions",
    "crav1-suggest-tests-for-code",
)


def skill_dir(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if parent.name.startswith("crav1-") and (parent / "SKILL.md").is_file():
            return parent
    raise AssertionError(f"no skill folder for {path}")


def opens(path: Path) -> list[str]:
    return OPEN.findall(path.read_text(encoding="utf-8"))


class OpenSkillFile(unittest.TestCase):
    def test_rule_page_is_the_one_copy_of_the_sentences(self):
        page = ROOT / "docs" / "reference" / "open-skill-file.md"
        text = page.read_text(encoding="utf-8")
        for phrase in PHRASES:
            self.assertIn(phrase, text)
        copies = sorted(ROOT.glob("**/reference/open-skill-file.md"))
        self.assertIn(page, copies)
        for copy in copies:
            body = copy.read_text(encoding="utf-8")
            for phrase in PHRASES:
                self.assertIn(phrase, body, copy)

    def test_call_sites_point_at_the_rule_and_name_real_files(self):
        for path in RULE_POINTERS:
            text = path.read_text(encoding="utf-8")
            self.assertIn(RULE, text, path)
        for path, needed in REQUIRED.items():
            found = opens(path)
            for rel in needed:
                self.assertIn(rel, found, path)
        for path in DOES_NOT_OPEN:
            self.assertEqual(opens(path), [], path)
            text = path.read_text(encoding="utf-8").lower()
            self.assertTrue(
                "does not run" in text or "not started" in text or "do not open" in text,
                path,
            )

    def test_every_open_path_exists_in_each_install_tree(self):
        seen = []
        for skill in SCAN:
            for path in (CURSOR / skill).rglob("*.md"):
                for rel in opens(path):
                    self.assertNotIn("..", rel[3:], rel)
                    seen.append((path, rel))
                    folder = skill_dir(path)
                    self.assertEqual(folder.parent, CURSOR)
                    for tree in TREES:
                        installed = tree / folder.name
                        target = (installed / rel).resolve()
                        self.assertTrue(target.is_file(), f"{rel} from {installed}")
                        self.assertTrue(str(target).startswith(str(tree.resolve())))
        self.assertGreaterEqual(len(seen), 20)

    def test_command_only_frontmatter_stays(self):
        for name in STEP_SKILLS:
            for tree in TREES:
                text = (tree / name / "SKILL.md").read_text(encoding="utf-8")
                front = text.split("---", 2)[1]
                self.assertIn("disable-model-invocation: true", front, f"{tree.name}/{name}")
                self.assertNotIn("disable-model-invocation: false", front)
        for name in NOT_COMMAND_ONLY:
            front = (CURSOR / name / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
            self.assertNotIn("disable-model-invocation", front, name)


if __name__ == "__main__":
    unittest.main()
