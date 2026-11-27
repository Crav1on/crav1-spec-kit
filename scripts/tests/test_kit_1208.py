"""1.208.0: pristine kit-copy conflicts, merge messages, update-kit ending.

Synthetic releases only. Versions 1.8.1, 1.8.2 and 1.8.3 are fixtures, not tags.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MERGE = ROOT / ".cursor/skills/crav1/crav1-finalize-commit/scripts/kit_merge.py"
UPDATE = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
PULL = ROOT / ".cursor/skills/crav1/crav1-finalize-commit/references/pull.md"

OLDER = "1.8.2"
NEWER = "1.8.3"
BASE = "1.8.1"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_merge(*args: str) -> tuple[int, dict, str]:
    proc = subprocess.run([sys.executable, str(MERGE), *args], capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw": proc.stdout}
    return proc.returncode, payload, proc.stderr


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr or proc.stdout}")
    return proc


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def kit_files(version: str, *, kept: str, old: str | None, retired: str | None, extra: str | None, skill: str | None = None) -> dict[str, str]:
    skill_body = skill if skill is not None else f"Help text for {version}.\n"
    files = {
        ".crav1/kit.json": json.dumps({"schema": 1, "vendors": ["claude", "codex", "cursor"]}, indent=2) + "\n",
        ".cursor/skills/crav1/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
        ".cursor/skills/crav1/crav1-docs/CHANGELOG.md": f"## {version}\n",
        ".cursor/skills/crav1/crav1-help/SKILL.md": skill_body,
        ".cursor/skills/crav1/crav1-help/references/kept.md": kept,
        ".claude/skills/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
        ".claude/skills/crav1-help/SKILL.md": f"Claude help {version}.\n",
        ".agents/skills/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
        ".agents/skills/crav1-help/SKILL.md": f"Codex help {version}.\n",
    }
    if old is not None:
        files[".cursor/skills/crav1/crav1-help/references/old.md"] = old
    if retired is not None:
        files[".cursor/skills/crav1/crav1-help/references/retired.md"] = retired
    if extra is not None:
        files[".cursor/skills/crav1/crav1-help/references/extra.md"] = extra
    return files


def dump(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        write(root / rel, text)


def publish(install: Path, dest: Path) -> None:
    """Release layout: Cursor and Claude at the root, Codex under vendors/codex."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(install / ".cursor", dest / ".cursor")
    shutil.copytree(install / ".claude", dest / ".claude")
    shutil.copytree(install / ".agents", dest / "vendors" / "codex" / ".agents")


def init_repo(repo: Path) -> None:
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "a@example.com")
    git(repo, "config", "user.name", "person A")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "config", "commit.gpgsign", "false")


def commit_tree(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


class KitCopyConflicts(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        init_repo(self.repo)
        dump(self.repo, kit_files(BASE, kept="kept base\n", old="old base\n", retired=None, extra=None))
        commit_tree(self.repo, "kit base")
        git(self.repo, "switch", "-c", "older")
        dump(self.repo, kit_files(OLDER, kept="kept older\n", old="old older\n", retired="retired\n", extra=None))
        # The base file that the newer release deletes must be gone from the index on that branch only.
        commit_tree(self.repo, "kit older")
        git(self.repo, "switch", "main")
        git(self.repo, "switch", "-c", "newer")
        newer = kit_files(NEWER, kept="kept base\n", old=None, retired=None, extra="extra\n")
        dump(self.repo, newer)
        old = self.repo / ".cursor/skills/crav1/crav1-help/references/old.md"
        if old.exists():
            old.unlink()
        commit_tree(self.repo, "kit newer")
        self.older_release = self.tmp / "rel-older"
        self.newer_release = self.tmp / "rel-newer"
        # Publish from the commits, not from a dirty tree.
        git(self.repo, "switch", "older")
        publish(self.repo, self.older_release)
        git(self.repo, "switch", "newer")
        publish(self.repo, self.newer_release)

    def _settle(self) -> tuple[int, dict, str]:
        return run_merge(
            "settle",
            "--root",
            str(self.repo),
            "--no-fetch",
            "--release",
            f"{OLDER}={self.older_release}",
            "--release",
            f"{NEWER}={self.newer_release}",
        )

    def test_pristine_copies_take_the_newer_release(self):
        git(self.repo, "switch", "older")
        merged = git(self.repo, "merge", "--no-commit", "newer", check=False)
        self.assertNotEqual(merged.returncode, 0)
        code, payload, err = self._settle()
        self.assertEqual(code, 0, err or payload)
        self.assertTrue(payload["settled"])
        self.assertTrue(payload["nothing_lost"])
        self.assertEqual(payload["version"], NEWER)
        self.assertIn(f"Settled kit copies to v{NEWER}", payload["line"])
        self.assertIn("Nothing lost.", payload["line"])
        self.assertIn("added", payload["line"])
        self.assertIn("deleted", payload["line"])
        self.assertEqual(payload["files"], [])
        help_text = (self.repo / ".cursor/skills/crav1/crav1-help/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(help_text, f"Help text for {NEWER}.\n")
        self.assertEqual(
            (self.repo / ".claude/skills/crav1-help/SKILL.md").read_text(encoding="utf-8"),
            f"Claude help {NEWER}.\n",
        )
        self.assertEqual(
            (self.repo / ".agents/skills/crav1-help/SKILL.md").read_text(encoding="utf-8"),
            f"Codex help {NEWER}.\n",
        )
        self.assertEqual(
            (self.repo / ".cursor/skills/crav1/crav1-help/references/kept.md").read_text(encoding="utf-8"),
            "kept base\n",
        )
        self.assertEqual(
            (self.repo / ".cursor/skills/crav1/crav1-help/references/extra.md").read_text(encoding="utf-8"),
            "extra\n",
        )
        self.assertFalse((self.repo / ".cursor/skills/crav1/crav1-help/references/old.md").exists())
        self.assertFalse((self.repo / ".cursor/skills/crav1/crav1-help/references/retired.md").exists())
        still = git(self.repo, "diff", "--name-only", "--diff-filter=U").stdout
        self.assertNotIn("crav1-help", still)
        code, committed, err = run_merge("commit", "--root", str(self.repo))
        self.assertEqual(code, 0, err or committed)
        message = git(self.repo, "log", "-1", "--format=%B").stdout
        self.assertNotIn("# Conflicts:", message)
        self.assertIn("Merge", message)

    def test_newer_wins_when_it_is_already_head(self):
        git(self.repo, "switch", "newer")
        merged = git(self.repo, "merge", "--no-commit", "older", check=False)
        self.assertNotEqual(merged.returncode, 0)
        code, payload, err = self._settle()
        self.assertEqual(code, 0, err or payload)
        self.assertEqual(payload["version"], NEWER)
        self.assertEqual(
            (self.repo / ".cursor/skills/crav1/crav1-help/references/kept.md").read_text(encoding="utf-8"),
            "kept base\n",
        )
        self.assertFalse((self.repo / ".cursor/skills/crav1/crav1-help/references/retired.md").exists())
        self.assertTrue((self.repo / ".cursor/skills/crav1/crav1-help/references/extra.md").is_file())

    def test_hand_edited_copy_is_named_and_left(self):
        skill = self.repo / ".cursor/skills/crav1/crav1-help/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "Local note.\n", encoding="utf-8")
        commit_tree(self.repo, "hand edit on newer")
        git(self.repo, "switch", "older")
        merged = git(self.repo, "merge", "--no-commit", "newer", check=False)
        self.assertNotEqual(merged.returncode, 0)
        code, payload, err = self._settle()
        self.assertEqual(code, 1, err or payload)
        self.assertFalse(payload["settled"])
        self.assertEqual(payload["code"], "hand-edited")
        self.assertEqual(payload["files"], [".cursor/skills/crav1/crav1-help/SKILL.md"])
        self.assertNotIn("workflow.md", payload["line"])
        workflow = (self.repo / ".cursor/skills/crav1/crav1-docs/reference/workflow.md").read_text(encoding="utf-8")
        self.assertIn("<<<<<<<", workflow)


class MergeMessage(unittest.TestCase):
    def test_commit_strips_conflict_comments(self):
        repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, repo, True)
        init_repo(repo)
        write(repo / "notes.txt", "one\n")
        commit_tree(repo, "base")
        git(repo, "switch", "-c", "side")
        write(repo / "notes.txt", "side\n")
        commit_tree(repo, "side")
        git(repo, "switch", "main")
        write(repo / "notes.txt", "main\n")
        commit_tree(repo, "main")
        merged = git(repo, "merge", "--no-commit", "side", check=False)
        self.assertNotEqual(merged.returncode, 0)
        located = git(repo, "rev-parse", "--git-path", "MERGE_MSG")
        message_path = Path(located.stdout.strip())
        if not message_path.is_absolute():
            message_path = repo / message_path
        self.assertIn("# Conflicts:", message_path.read_text(encoding="utf-8"))
        write(repo / "notes.txt", "both\n")
        git(repo, "add", "--", "notes.txt")
        code, payload, err = run_merge(
            "commit",
            "--root",
            str(repo),
            "--append",
            "Rebuilt the notes index into this merge.",
        )
        self.assertEqual(code, 0, err or payload)
        message = git(repo, "log", "-1", "--format=%B").stdout
        self.assertNotIn("# Conflicts:", message)
        self.assertIn("Rebuilt the notes index into this merge.", message)
        self.assertIn("Merge", message)


class UpdateEnding(unittest.TestCase):
    def test_zero_repo_files_names_kit2_and_does_not_offer_commit(self):
        uk = load(UPDATE, "update_kit_1208")
        self.assertIsNone(uk.update_card(0, False))
        card = uk.update_card(0, True)
        self.assertEqual(card["words"], ["install-kit2", "stop"])
        self.assertFalse(card["commits"])
        self.assertNotIn("commit", " ".join(card["words"]))
        commit_card = uk.update_card(3, False, "work")
        self.assertEqual(commit_card["words"][0], "yes, write and commit")
        self.assertTrue(commit_card["commits"])
        text = uk.ending_text(Path(tempfile.mkdtemp()), 0, updated=False, kit2=True)
        self.assertTrue(text.startswith("Run next:\n"))
        self.assertIn("Kit 2.0 installed in your user folder; reload to load its skills.", text)
        self.assertNotIn("kit files changed", text)
        self.assertNotIn("Uncommitted:", text)
        self.assertNotIn("write and commit", text)
        both = uk.ending_text(Path(tempfile.mkdtemp()), 0, updated=True, kit2=True)
        self.assertIn("The kit files changed; reload the window so the new skills load.", both)
        self.assertIn("Kit 2.0 installed in your user folder; reload to load its skills.", both)
        self.assertEqual(uk.ending_args(0, "Kit 2.0: installed 2.0 at user level, 3 files."), ["--not-updated", "--kit2"])
        self.assertEqual(uk.ending_args(2, None), [])
        proc = subprocess.run(
            [sys.executable, str(UPDATE), "ending", "--root", str(Path(tempfile.mkdtemp())), "--not-updated", "--kit2"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Kit 2.0 installed in your user folder; reload to load its skills.", proc.stdout)
        self.assertNotIn("kit files changed", proc.stdout)


class MergeCommandWording(unittest.TestCase):
    def test_sources_do_not_commit_a_merge_with_bare_no_edit(self):
        roots = [ROOT / ".cursor", ROOT / "docs"]
        bad = []
        for base in roots:
            for path in base.rglob("*"):
                if path.suffix not in {".md", ".py"}:
                    continue
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if "git commit --no-edit" in line and "--cleanup=strip" not in line:
                        bad.append(f"{path.relative_to(ROOT)}: {line.strip()}")
        self.assertEqual(bad, [])
        self.assertIn("git commit --no-edit --cleanup=strip", PULL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
