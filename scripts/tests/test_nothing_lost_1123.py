"""1.123.0: the nothing-lost check is a script, and a merge is one commit.

finalize-commit makes at most the drafted commit and one merge commit.
A notes index rebuild is folded into that merge. Nothing lost is said only
when nothing_lost.py reports it.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOST = ROOT / ".cursor/skills/crav1/crav1-finalize-commit/scripts/nothing_lost.py"
NOTES = ROOT / ".cursor/skills/crav1/crav1-add-to-spec/scripts/notes_index.py"
PULL = ROOT / ".cursor/skills/crav1/crav1-finalize-commit/references/pull.md"
SKILL = ROOT / ".cursor/skills/crav1/crav1-finalize-commit/SKILL.md"


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"git {args}\n{proc.stderr}{proc.stdout}")
    return proc


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def init_repo(repo: Path) -> None:
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")


def note(title: str, day: str) -> str:
    return (
        f"---\ntitle: {title}\nkind: fact\nsource: mail\n"
        f"source_date: 2026-11-{day}\nimported: 2026-11-{day}\n"
        f"used_by: []\nwaiting_for: []\n---\n# {title}\n"
    )


def build_index(repo: Path) -> None:
    proc = subprocess.run(
        ["python3", str(NOTES), "--root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr + proc.stdout)


def index_matches(repo: Path) -> bool:
    proc = subprocess.run(
        ["python3", str(NOTES), "--check", "--root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def nothing_lost(repo: Path, *extra: str) -> tuple[int, dict]:
    proc = subprocess.run(
        ["python3", str(LOST), "--root", str(repo), *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    return proc.returncode, payload


class NothingLost(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        init_repo(self.repo)
        write(self.repo, "docs/specs/orders/spec.md", "# Orders\n\nKept.\n")
        commit_all(self.repo, "base")

    def tearDown(self):
        self.tmp.cleanup()

    def diverge(self, ours_text: str, theirs_text: str) -> None:
        git(self.repo, "checkout", "-b", "ours")
        write(self.repo, "docs/specs/orders/spec.md", ours_text)
        commit_all(self.repo, "ours")
        git(self.repo, "checkout", "main")
        git(self.repo, "checkout", "-b", "theirs")
        write(self.repo, "docs/specs/orders/spec.md", theirs_text)
        commit_all(self.repo, "theirs")
        git(self.repo, "checkout", "ours")
        git(self.repo, "merge", "--no-commit", "--no-ff", "theirs", check=False)

    def test_not_a_merge_exits_2(self):
        code, payload = nothing_lost(self.repo)
        self.assertEqual(code, 2)
        self.assertFalse(payload["nothing_lost"])
        self.assertEqual(payload["code"], "not-a-merge")

    def test_kept_lines_are_ok_and_a_dropped_line_is_named(self):
        self.diverge(
            "# Orders\n\nOurs keeps this.\n\nKept.\n\nBOTTOM\n",
            "# Orders\n\nTOP\n\nKept.\n\nTheirs keeps this.\n",
        )
        code, payload = nothing_lost(self.repo)
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["nothing_lost"])
        text = (self.repo / "docs/specs/orders/spec.md").read_text(encoding="utf-8")
        self.assertIn("Theirs keeps this.", text)
        (self.repo / "docs/specs/orders/spec.md").write_text(
            text.replace("Theirs keeps this.\n", ""),
            encoding="utf-8",
        )
        code, payload = nothing_lost(self.repo)
        self.assertEqual(code, 1)
        self.assertFalse(payload["nothing_lost"])
        self.assertTrue(any(
            row["line"] == "Theirs keeps this." and row["side"] == "theirs" for row in payload["lost"]
        ))
        self.assertTrue((self.repo / ".git/MERGE_HEAD").is_file())

    def test_newer_synced_at_and_a_split_joined_line_are_not_lost(self):
        self.diverge(
            "# Orders\n\n"
            "Synced at: orders-api develop@aaa1111, 2026-10-01; "
            "orders-api feat/orders-retry@ccc3333, 2026-10-02\n"
            "Kept.\n",
            "# Orders\n\nSynced at: orders-api develop@bbb2222, 2026-10-19\nKept.\n",
        )
        write(
            self.repo,
            "docs/specs/orders/spec.md",
            "# Orders\n\n"
            "Synced at: orders-api develop@bbb2222, 2026-10-19\n"
            "Synced at: orders-api feat/orders-retry@ccc3333, 2026-10-02\n"
            "Kept.\n",
        )
        code, payload = nothing_lost(self.repo)
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["nothing_lost"])
        self.assertEqual(payload["lost"], [])

    def test_rules_are_in_the_skill(self):
        pull = PULL.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("git pull --no-rebase --no-commit", pull)
        self.assertIn("at most two commits", pull)
        self.assertIn("nothing_lost.py", pull)
        self.assertIn("Rebuilt the notes index into this merge.", pull)
        self.assertIn("do not say nothing lost", pull.lower())
        self.assertIn("at most two commits", skill.lower())
        self.assertNotIn("git pull --no-rebase`.", pull)


class TwoCommits(unittest.TestCase):
    def test_index_rebuild_is_inside_the_one_merge_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            write(repo, "docs/notes/2026-11/2026-11-01-alpha.md", note("Alpha", "01"))
            build_index(repo)
            commit_all(repo, "base notes")
            git(repo, "checkout", "-b", "upstream")
            write(repo, "docs/notes/2026-11/2026-11-02-bravo.md", note("Bravo", "02"))
            commit_all(repo, "upstream note")
            git(repo, "checkout", "main")
            write(repo, "docs/notes/2026-11/2026-11-03-coco.md", note("Coco", "03"))
            commit_all(repo, "drafted note")
            before = git(repo, "rev-parse", "HEAD").stdout.strip()
            self.assertFalse(index_matches(repo))
            merged = git(repo, "merge", "--no-commit", "--no-ff", "upstream")
            self.assertEqual(merged.returncode, 0, merged.stderr)
            self.assertEqual(git(repo, "rev-parse", "HEAD").stdout.strip(), before)
            self.assertTrue((repo / ".git/MERGE_HEAD").is_file())
            self.assertFalse(index_matches(repo))
            build_index(repo)
            self.assertTrue(index_matches(repo))
            code, payload = nothing_lost(repo)
            self.assertEqual(code, 0, payload)
            self.assertTrue(payload["nothing_lost"])
            self.assertEqual(payload["index_check"], "pass")
            git(repo, "add", "-A")
            git(
                repo,
                "commit",
                "-m",
                "Merge branch 'upstream'",
                "-m",
                "Rebuilt the notes index into this merge.",
            )
            self.assertFalse((repo / ".git/MERGE_HEAD").exists())
            # First-parent history: the drafted commit, then one merge commit.
            # The other parent's commits were already on that branch.
            self.assertEqual(git(repo, "rev-parse", "HEAD^1").stdout.strip(), before)
            self.assertEqual(
                git(repo, "rev-list", "--first-parent", "--count", f"{before}..HEAD").stdout.strip(),
                "1",
            )
            parents = git(repo, "rev-parse", "HEAD^1", "HEAD^2").stdout.split()
            self.assertEqual(len(parents), 2)
            message = git(repo, "log", "-1", "--format=%B").stdout
            self.assertIn("Rebuilt the notes index into this merge.", message)
            index = git(repo, "show", "HEAD:docs/notes/index.md").stdout
            self.assertIn("| 3 |", index)
            code, again = nothing_lost(repo, "--merge", "HEAD")
            self.assertEqual(code, 0, again)
            self.assertTrue(again["nothing_lost"])


if __name__ == "__main__":
    unittest.main()
