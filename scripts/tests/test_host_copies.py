"""1.107.0: the Claude Code copy of a skill file is byte-identical to the Cursor copy,
except the files that name a host-only path (rules, agents, agent-assets, a command line,
or the help docs folder). Paths inside the kit are written host-neutral:
"this skill's `references/x.md`" or "skill `crav1-other`, `references/x.md`"."""
import filecmp, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUR, CLA = ROOT / ".cursor/skills/crav1", ROOT / ".claude/skills"
HOST_SPECIFIC = {
    "crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc",
    "crav1-add-to-spec/references/merge-safe.md",
    "crav1-add-to-spec/references/notes.md",
    "crav1-add-to-spec/references/sources-flagged.md",
    "crav1-build-features/SKILL.md",
    "crav1-build-tasks/branches/one-task/BRANCH.md",
    "crav1-build-tasks/branches/one-task/references/run.md",
    "crav1-build-tasks/branches/one-task/references/style-persist.md",
    "crav1-build-tasks/branches/several-tasks/BRANCH.md",
    "crav1-bundle-to-specs/SKILL.md",
    "crav1-bundle-to-specs/references/worker.md",
    "crav1-finalize-commit/SKILL.md",
    "crav1-finalize-commit/branches/message-only/BRANCH.md",
    "crav1-finalize-commit/branches/message-only/assets/draft-commit-gitlog.mdc",
    "crav1-finalize-commit/branches/message-only/assets/draft-commit-style.mdc",
    "crav1-finalize-commit/branches/message-only/assets/trailer-hook.mdc",
    "crav1-finalize-commit/references/trailer-hook.md",
    "crav1-help/SKILL.md",
    "crav1-review-architecture/SKILL.md",
    "crav1-review-plan/SKILL.md",
}


class HostCopies(unittest.TestCase):
    def test_only_host_specific_files_differ(self):
        differ = set()
        for f in CUR.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                rel = f.relative_to(CUR).as_posix()
                other = CLA / rel
                if other.is_file() and not filecmp.cmp(f, other, shallow=False):
                    differ.add(rel)
        self.assertEqual(differ, HOST_SPECIFIC, "a new host difference: write the path host-neutral, or list it here")

    def test_no_drop_in_plugin_path_pairs_left(self):
        for f in CUR.rglob("*.md"):
            if "crav1-docs" in f.parts:
                continue
            self.assertNotIn("; plugin: sibling `", f.read_text(), f.relative_to(CUR).as_posix())


if __name__ == "__main__":
    unittest.main()
