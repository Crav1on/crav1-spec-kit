"""1.204.0: Codex installs from vendors/codex. .crav1/kit.json lists the vendors.

Add copies kit-owned files into .agents/skills/. Remove deletes only those files
when they still match the release. A local edit is a clash. Cursor and Claude
stay as they were when Codex is not listed.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "-c", "init.defaultBranch=main"]

PROJECT = {
    "README.md": "project readme\n",
    "AGENTS.md": "# Project\n\nKeep this file.\n",
    ".github/copilot-instructions.md": "project instructions\n",
    ".agents/skills/my-app/SKILL.md": "not the kit\n",
    "docs/specs/orders-api/spec.md": "# Orders\n\nExport orders.\n",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_kit(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), *args], capture_output=True, text=True)


def snapshot(root: Path) -> dict[str, bytes]:
    out = {}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            out[path.relative_to(root).as_posix()] = path.read_bytes()
    return out


def release_tree(base: Path, version: str = "1.204.0") -> Path:
    tree = base / "release"
    write(tree / "plugins/crav1/.cursor-plugin/plugin.json", json.dumps({"name": "crav1", "version": version}) + "\n")
    write(
        tree / "vendors/codex/.agents/skills/crav1-help/SKILL.md",
        "Read ../crav1-docs/reference/kit-rules.md first.\n\n`$crav1-help`\n",
    )
    write(
        tree / "vendors/codex/.agents/skills/crav1-help/agents/openai.yaml",
        "policy:\n  allow_implicit_invocation: false\n",
    )
    write(
        tree / "vendors/codex/.agents/skills/crav1-update-kit/SKILL.md",
        "Read ../crav1-docs/reference/kit-rules.md first.\n\n`$crav1-update-kit`\n",
    )
    write(tree / "vendors/codex/.agents/skills/crav1-docs/reference/workflow.md", f"Kit version: {version}\n")
    write(tree / "vendors/codex/.agents/skills/crav1-docs/reference/kit-rules.md", "rules\n")
    return tree


def project(base: Path) -> Path:
    root = base / "proj"
    for rel, text in PROJECT.items():
        write(root / rel, text)
    return root


def git_init(root: Path) -> None:
    subprocess.run([*G, "init", "-q", str(root)], check=True)
    subprocess.run([*G, "-C", str(root), "add", "-A"], check=True)
    subprocess.run([*G, "-C", str(root), "commit", "-qm", "start"], check=True)


class CodexRoundTrip(unittest.TestCase):
    def test_add_then_remove_leaves_project_files(self):
        base = Path(tempfile.mkdtemp())
        root = project(base)
        tree = release_tree(base)
        before = {rel: (root / rel).read_bytes() for rel in PROJECT}
        plan = run_kit(["plan", "--add", "codex", "--new", str(tree), "--root", str(root)])
        self.assertEqual(plan.returncode, 0, plan.stderr)
        body = json.loads(plan.stdout)
        self.assertTrue(body["project_untouched"])
        self.assertEqual(body["kit_json_op"], "add")
        self.assertEqual(body["vendors_after"], ["codex"])
        added = body["vendors"][0]["added"]
        self.assertIn(".agents/skills/crav1-help/SKILL.md", added)
        self.assertIn(".agents/skills/crav1-help/agents/openai.yaml", added)
        self.assertNotIn(".agents/skills/crav1-update-kit/agents/openai.yaml", added)
        self.assertTrue(body["vendors"][0]["samples"])
        self.assertLessEqual(len(body["vendors"][0]["samples"]), 10)
        self.assertEqual(body["vendors"][0]["counts"]["add"], len(added))
        refused = run_kit(["apply", "--add", "codex", "--new", str(tree), "--root", str(root)])
        self.assertEqual(refused.returncode, 2)
        self.assertIn("yes", refused.stderr)
        self.assertFalse((root / ".crav1/kit.json").exists())
        applied = run_kit(["apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        done = json.loads(applied.stdout)
        self.assertTrue(done["project_untouched"])
        self.assertEqual(done["vendors_after"], ["codex"])
        skill = (root / ".agents/skills/crav1-help/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("Read ../crav1-docs/reference/kit-rules.md first."))
        self.assertIn("$crav1-help", skill)
        self.assertFalse((root / "AGENTS.md").read_text(encoding="utf-8").startswith("Read "))
        listed = json.loads((root / ".crav1/kit.json").read_text(encoding="utf-8"))
        self.assertEqual(listed, {"schema": 1, "vendors": ["codex"]})
        for rel, data in before.items():
            self.assertEqual((root / rel).read_bytes(), data, rel)
        self.assertFalse((root / ".cursor").exists())
        self.assertFalse((root / ".github/skills").exists())

        again = run_kit(["apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(again.returncode, 0, again.stderr)
        second = json.loads(again.stdout)
        self.assertEqual(second["touched"], [])
        self.assertEqual((root / ".agents/skills/crav1-help/SKILL.md").read_text(encoding="utf-8"), skill)

        write(root / ".agents/skills/crav1-help/local-note.txt", "kept note\n")
        removed = run_kit(["plan", "--remove", "codex", "--old", str(tree), "--root", str(root)])
        self.assertEqual(removed.returncode, 0, removed.stderr)
        plan_rm = json.loads(removed.stdout)
        self.assertIn(".agents/skills/crav1-help/SKILL.md", plan_rm["vendors"][0]["delete"])
        self.assertIn(".agents/skills/crav1-help/local-note.txt", plan_rm["vendors"][0]["left_extra"])
        self.assertEqual(plan_rm["vendors_after"], [])
        applied_rm = run_kit(["apply", "--remove", "codex", "--old", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(applied_rm.returncode, 0, applied_rm.stderr)
        self.assertFalse((root / ".agents/skills/crav1-help/SKILL.md").exists())
        self.assertFalse((root / ".agents/skills/crav1-docs").exists())
        self.assertEqual((root / ".agents/skills/crav1-help/local-note.txt").read_text(encoding="utf-8"), "kept note\n")
        self.assertEqual((root / ".agents/skills/my-app/SKILL.md").read_text(encoding="utf-8"), "not the kit\n")
        for rel, data in before.items():
            self.assertEqual((root / rel).read_bytes(), data, rel)
        cleared = json.loads((root / ".crav1/kit.json").read_text(encoding="utf-8"))
        self.assertEqual(cleared["vendors"], [])

    def test_existing_file_is_a_clash_with_both_sides(self):
        base = Path(tempfile.mkdtemp())
        root = project(base)
        tree = release_tree(base)
        write(root / ".agents/skills/crav1-help/SKILL.md", "hand made\n")
        plan = run_kit(["plan", "--add", "codex", "--new", str(tree), "--root", str(root)])
        self.assertEqual(plan.returncode, 0, plan.stderr)
        body = json.loads(plan.stdout)
        clashes = {item["path"]: item for item in body["vendors"][0]["clash"]}
        self.assertIn(".agents/skills/crav1-help/SKILL.md", clashes)
        hunks = json.dumps(clashes[".agents/skills/crav1-help/SKILL.md"]["hunks"])
        self.assertIn("hand made", hunks)
        self.assertIn("kit-rules.md", hunks)
        blocked = run_kit(["apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("keep or take", blocked.stderr)
        self.assertEqual((root / ".agents/skills/crav1-help/SKILL.md").read_text(encoding="utf-8"), "hand made\n")
        kept = run_kit([
            "apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root),
            "--keep", ".agents/skills/crav1-help/SKILL.md",
        ])
        self.assertEqual(kept.returncode, 0, kept.stderr)
        self.assertEqual((root / ".agents/skills/crav1-help/SKILL.md").read_text(encoding="utf-8"), "hand made\n")
        self.assertTrue((root / ".agents/skills/crav1-docs/reference/kit-rules.md").is_file())
        self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), PROJECT["AGENTS.md"])

    def test_kit_json_is_created_and_updated(self):
        base = Path(tempfile.mkdtemp())
        root = project(base)
        tree = release_tree(base)
        write(root / ".cursor/skills/crav1/crav1-docs/reference/workflow.md", "Kit version: 1.202.0\n")
        write(root / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["cursor"]}) + "\n")
        git_init(root)
        write(root / ".crav1/.gitignore", "*\n")
        write(root / ".crav1/glossary-list.md", "not committed\n")
        applied = run_kit(["apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        listed = json.loads((root / ".crav1/kit.json").read_text(encoding="utf-8"))
        self.assertEqual(listed["vendors"], ["codex", "cursor"])
        unknown = run_kit(["plan", "--add", "nope", "--root", str(root)])
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("not a vendor", unknown.stderr)
        bad = root / ".crav1/kit.json"
        bad.write_text('{"schema": 1, "vendors": ["made-up"]}\n', encoding="utf-8")
        refused = run_kit(["detect", "--root", str(root), "--home", str(base / "empty")])
        self.assertEqual(refused.returncode, 2)
        self.assertIn("not a vendor", refused.stderr)
        bad.write_text(json.dumps({"schema": 1, "vendors": ["codex", "cursor"]}, indent=2) + "\n", encoding="utf-8")
        write(root / "README.md", "edited during the walk\n")
        committed = run_kit([
            "commit", "--yes", "--add", "codex", "--to-version", "1.204.0", "--root", str(root),
        ])
        self.assertEqual(committed.returncode, 0, committed.stderr)
        payload = json.loads(committed.stdout)
        self.assertEqual(payload["message"], "Add CRAV1 kit vendor codex v1.204.0")
        self.assertIn("README.md", payload["left_uncommitted"])
        names = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"], cwd=root, check=True, capture_output=True, text=True,
        ).stdout
        self.assertIn(".crav1/kit.json", names)
        self.assertIn(".agents/skills/crav1-help/SKILL.md", names)
        self.assertNotIn("glossary-list.md", names)
        self.assertNotIn("AGENTS.md", names)
        self.assertNotIn("README.md", names)
        self.assertNotIn("spec.md", names)

    def test_ignored_kit_json_is_committed(self):
        base = Path(tempfile.mkdtemp())
        root = project(base)
        tree = release_tree(base)
        git_init(root)
        write(root / ".crav1/.gitignore", "*\n")
        write(root / ".crav1/glossary-list.md", "not committed\n")
        applied = run_kit(["apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        committed = run_kit(["commit", "--yes", "--add", "codex", "--to-version", "1.204.0", "--root", str(root)])
        self.assertEqual(committed.returncode, 0, committed.stderr)
        names = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"], cwd=root, check=True, capture_output=True, text=True,
        ).stdout
        self.assertIn(".crav1/kit.json", names)
        self.assertNotIn("glossary-list.md", names)
        self.assertEqual((root / ".crav1/glossary-list.md").read_text(encoding="utf-8"), "not committed\n")

    def test_remove_commit_drops_only_kit_files(self):
        base = Path(tempfile.mkdtemp())
        root = project(base)
        tree = release_tree(base)
        git_init(root)
        applied = run_kit(["apply", "--add", "codex", "--new", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        run_kit(["commit", "--yes", "--add", "codex", "--to-version", "1.204.0", "--root", str(root)])
        write(root / "README.md", "edited during the walk\n")
        removed = run_kit(["apply", "--remove", "codex", "--old", str(tree), "--yes", "--root", str(root)])
        self.assertEqual(removed.returncode, 0, removed.stderr)
        committed = run_kit([
            "commit", "--yes", "--remove", "codex", "--to-version", "1.204.0", "--root", str(root),
        ])
        self.assertEqual(committed.returncode, 0, committed.stderr)
        payload = json.loads(committed.stdout)
        self.assertEqual(payload["message"], "Remove CRAV1 kit vendor codex v1.204.0")
        self.assertIn("README.md", payload["left_uncommitted"])
        names = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"], cwd=root, check=True, capture_output=True, text=True,
        ).stdout
        self.assertIn(".crav1/kit.json", names)
        self.assertIn(".agents/skills/crav1-help/SKILL.md", names)
        self.assertNotIn("README.md", names)
        self.assertNotIn("my-app/SKILL.md", names)
        self.assertFalse((root / ".agents/skills/crav1-help/SKILL.md").exists())
        self.assertTrue((root / ".agents/skills/my-app/SKILL.md").is_file())

    def test_cursor_and_claude_stay_when_codex_is_not_listed(self):
        base = Path(tempfile.mkdtemp())
        old, new, root = base / "old", base / "new", base / "proj"
        for folder, version in ((old, "1.202.0"), (new, "1.204.0"), (root, "1.202.0")):
            write(folder / ".cursor/skills/crav1/crav1-docs/reference/workflow.md", f"Kit version: {version}\n")
            write(folder / ".cursor/skills/crav1/crav1-help/SKILL.md", f"help {version}\n")
            write(folder / ".claude/skills/crav1-docs/reference/workflow.md", f"Kit version: {version}\n")
            write(folder / ".claude/skills/crav1-help/SKILL.md", f"help {version}\n")
            write(folder / ".claude/CLAUDE.md", "claude\n")
        write(new / "vendors/codex/.agents/skills/crav1-docs/reference/workflow.md", "Kit version: 1.204.0\n")
        write(new / "vendors/codex/.agents/skills/crav1-help/SKILL.md", "new codex help\n")
        write(root / ".agents/skills/crav1-docs/reference/workflow.md", "Kit version: 9.9.9\n")
        write(root / ".agents/skills/crav1-help/SKILL.md", "local codex\n")
        write(root / "README.md", "project readme\n")
        write(root / "AGENTS.md", "project agents\n")
        write(root / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["claude", "cursor"]}, indent=2) + "\n")
        codex_before = snapshot(root / ".agents")
        readme = (root / "README.md").read_bytes()
        agents = (root / "AGENTS.md").read_bytes()
        plan = run_kit([
            "plan", "--root", str(root), "--old", str(old), "--new", str(new), "--to-version", "1.204.0",
            "--home", str(base / "home"),
        ])
        self.assertEqual(plan.returncode, 0, plan.stderr)
        body = json.loads(plan.stdout)
        paths = []
        for items in body["files"].values():
            for item in items:
                paths.append(item["path"] if isinstance(item, dict) else item)
        self.assertTrue(any(path.startswith(".cursor/") for path in paths))
        self.assertFalse(any(path.startswith(".agents/") for path in paths))
        self.assertNotIn(".crav1/kit.json", paths)
        applied = run_kit([
            "apply", "--root", str(root), "--old", str(old), "--new", str(new), "--yes", "--home", str(base / "home"),
        ])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(snapshot(root / ".agents"), codex_before)
        self.assertEqual((root / "README.md").read_bytes(), readme)
        self.assertEqual((root / "AGENTS.md").read_bytes(), agents)
        self.assertEqual((root / ".cursor/skills/crav1/crav1-help/SKILL.md").read_text(encoding="utf-8"), "help 1.204.0\n")
        self.assertEqual((root / ".claude/skills/crav1-help/SKILL.md").read_text(encoding="utf-8"), "help 1.204.0\n")
        listed = json.loads((root / ".crav1/kit.json").read_text(encoding="utf-8"))
        self.assertEqual(listed["vendors"], ["claude", "cursor"])

    def test_real_codex_tree_plans_as_adds(self):
        base = Path(tempfile.mkdtemp())
        root = base / "proj"
        root.mkdir()
        write(root / "README.md", "project\n")
        plan = run_kit(["plan", "--add", "codex", "--new", str(ROOT), "--root", str(root)])
        self.assertEqual(plan.returncode, 0, plan.stderr)
        body = json.loads(plan.stdout)
        added = body["vendors"][0]["added"]
        self.assertGreater(body["vendors"][0]["counts"]["add"], 100)
        self.assertIn(".agents/skills/crav1-help/SKILL.md", added)
        self.assertNotIn(".agents/skills/crav1-help/agents/openai.yaml", added)
        self.assertIn(".agents/skills/crav1-fix-bug/agents/openai.yaml", added)
        self.assertTrue(body["project_untouched"])
        self.assertEqual(body["vendors"][0]["clash"], [])
        self.assertLessEqual(len(body["vendors"][0]["samples"]), 10)
        self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "project\n")
        self.assertFalse((root / ".agents").exists())


if __name__ == "__main__":
    unittest.main()
