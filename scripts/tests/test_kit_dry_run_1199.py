"""1.199.0 item 9: the maintainer dry-run tester stays out of the kit and leaves the project as it was."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRY = ROOT / "scripts/kit_dry_run.py"
UPDATE = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
SKILLS = ROOT / ".cursor/skills/crav1"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "-c", "init.defaultBranch=main"]


def git(repo, *args):
    return subprocess.run([*G, "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def restamp(tree: Path, version: str) -> None:
    wf = tree / ".cursor/skills/crav1/crav1-docs/reference/workflow.md"
    text = wf.read_text(encoding="utf-8")
    wf.write_text("\n".join(f"Kit version: {version}" if line.startswith("Kit version:") else line
                            for line in text.split("\n")), encoding="utf-8")
    plugin = tree / "plugins/crav1/.cursor-plugin/plugin.json"
    data = json.loads(plugin.read_text(encoding="utf-8"))
    data["version"] = version
    plugin.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def kit_fixture(base: Path) -> Path:
    """A kit repo: tag v1.0.0, and branch feat/kit-test at 1.0.1 with one changed skill file."""
    kit = base / "kit"
    shutil.copytree(SKILLS, kit / ".cursor/skills/crav1", ignore=shutil.ignore_patterns("__pycache__"))
    (kit / "plugins/crav1/.cursor-plugin").mkdir(parents=True)
    shutil.copy(ROOT / "plugins/crav1/.cursor-plugin/plugin.json", kit / "plugins/crav1/.cursor-plugin/plugin.json")
    (kit / "plugins/crav1/skills/crav1-update-kit/scripts").mkdir(parents=True)
    shutil.copy(UPDATE, kit / "plugins/crav1/skills/crav1-update-kit/scripts/update_kit.py")
    shutil.copy(ROOT / ".cursor/skills/crav1/crav1-update-kit/vendors.json",
                kit / "plugins/crav1/skills/crav1-update-kit/vendors.json")
    (kit / "scripts").mkdir()
    shutil.copy(DRY, kit / "scripts/kit_dry_run.py")
    restamp(kit, "1.0.0")
    subprocess.run([*G, "init", "-q", str(kit)], check=True)
    git(kit, "add", "-A")
    git(kit, "commit", "-qm", "v1.0.0")
    git(kit, "tag", "v1.0.0")
    git(kit, "checkout", "-qb", "feat/kit-test")
    restamp(kit, "1.0.1")
    note = kit / ".cursor/skills/crav1/crav1-docs/reference/dry-run-marker.md"
    note.write_text("# Marker\n\nAdded on the test branch.\n", encoding="utf-8")
    skill = kit / "vendors/codex/.agents/skills/crav1-help"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "Read ../crav1-docs/reference/kit-rules.md first.\n\n`$crav1-help`\n", encoding="utf-8")
    (skill / "agents").mkdir()
    (skill / "agents/openai.yaml").write_text("policy:\n  allow_implicit_invocation: false\n", encoding="utf-8")
    docs = kit / "vendors/codex/.agents/skills/crav1-docs/reference"
    docs.mkdir(parents=True)
    (docs / "workflow.md").write_text("Kit version: 1.0.0\n", encoding="utf-8")
    git(kit, "add", "-A")
    git(kit, "commit", "-qm", "v1.0.1")
    git(kit, "checkout", "-q", "main")
    return kit


def project_fixture(base: Path, kit: Path) -> Path:
    """A drop-in project at 1.0.0 with a generic orders-api spec, committed and clean."""
    proj = base / "project"
    proj.mkdir()
    subprocess.run([*G, "init", "-q", str(proj)], check=True)
    git(kit, "worktree", "add", "-q", "--detach", str(base / "kit-old"), "v1.0.0")
    shutil.copytree(base / "kit-old/.cursor", proj / ".cursor")
    git(kit, "worktree", "remove", "--force", str(base / "kit-old"))
    spec = proj / "docs/specs/orders-api"
    spec.mkdir(parents=True)
    (spec / "spec.md").write_text("# Orders API\n\n## Problem\n\nOrders need an export.\n", encoding="utf-8")
    (spec / "plan.md").write_text("# Plan\n\nReviewed: 2026-11-19, P# open: 0\n", encoding="utf-8")
    (spec / "tasks.md").write_text("# Tasks\n\n- [ ] T1 Add the export endpoint (branch: feat/orders-export)\n", encoding="utf-8")
    git(proj, "add", "-A")
    git(proj, "commit", "-qm", "start")
    return proj


def state(repo: Path) -> dict:
    return {key: git(repo, *cmd) for key, cmd in (
        ("branch", ["branch", "--show-current"]), ("head", ["rev-parse", "HEAD"]), ("status", ["status", "--porcelain"]),
        ("stash", ["stash", "list"]), ("worktrees", ["worktree", "list", "--porcelain"]))}


class DryRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp())
        cls.kit = kit_fixture(cls.base)
        cls.proj = project_fixture(cls.base, cls.kit)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def test_block_cleanup_and_untouched_repo(self):
        before = state(self.proj)
        temp_before = set(os.listdir(tempfile.gettempdir()))
        env = dict(os.environ, CRAV1_DRY_RUN_NO_CLIPBOARD="1")
        proc = subprocess.run([sys.executable, str(DRY), "--branch", "feat/kit-test", "--spec", "orders-api",
                               "--kit-source", str(self.kit), "--extra", "build_map.py --root {folder}",
                               "--add", "codex"],
                              cwd=self.proj, capture_output=True, text=True, env=env, timeout=600)
        out = proc.stdout
        self.assertEqual(proc.returncode, 0, out + proc.stderr)
        self.assertIn("===== COPY FROM HERE =====", out)
        self.assertIn("===== COPY TO HERE =====", out)
        self.assertLess(out.index("COPY FROM HERE"), out.index("COPY TO HERE"))
        self.assertIn("Kit: 1.0.1 at", out)
        self.assertIn("$ update_kit.py apply (exit 0)", out)
        self.assertIn("dry-run-marker.md", out)
        self.assertIn("unchanged ", out)
        self.assertIn("--- Vendor codex ---", out)
        self.assertIn("project_untouched: true", out)
        self.assertIn("folder: .agents/skills", out)
        self.assertIn("skills: 1/", out)
        self.assertIn("kit.json:", out)
        self.assertNotIn("is not installed by this release", out)
        self.assertIn("$ update_kit.py vendors (exit 0)", out)
        self.assertIn("walk_progress.py readiness --root", out)
        self.assertIn("$ build_map.py --root", out)
        self.assertIn("Cleanup: worktree and temp folders removed", out)
        self.assertIn("Your repo: unchanged", out)
        self.assertIn("not on the clipboard", out.splitlines()[-1])
        self.assertEqual(state(self.proj), before)
        self.assertEqual(len(git(self.proj, "worktree", "list").splitlines()), 1)
        self.assertFalse((self.proj / ".cursor/skills/crav1/crav1-docs/reference/dry-run-marker.md").exists())
        saved = Path(out.splitlines()[-1].split("Saved to ", 1)[1].split("; ", 1)[0])
        self.assertTrue(saved.is_file())
        saved.unlink()
        leftovers = {name for name in set(os.listdir(tempfile.gettempdir())) - temp_before
                     if name.startswith(("crk", "crw"))}
        self.assertEqual(leftovers, set())

    def test_changed_repo_is_loud(self):
        dry = spec_load()
        self.assertEqual(dry.compare({"HEAD": "a"}, {"HEAD": "a"}), [])
        self.assertIn("HEAD before:", dry.compare({"HEAD": "a"}, {"HEAD": "b"})[0])


def spec_load():
    spec = importlib.util.spec_from_file_location("kit_dry_run_t", DRY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class NotPartOfTheKit(unittest.TestCase):
    def test_update_never_installs_top_level_scripts(self):
        base = Path(tempfile.mkdtemp())
        try:
            kit = kit_fixture(base)
            proj = project_fixture(base, kit)
            git(kit, "checkout", "-q", "feat/kit-test")
            old = base / "old"
            git(kit, "worktree", "add", "-q", "--detach", str(old), "v1.0.0")
            proc = subprocess.run([sys.executable, str(UPDATE), "apply", "--root", str(proj), "--old", str(old),
                                   "--new", str(kit), "--yes"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((proj / ".cursor/skills/crav1/crav1-docs/reference/dry-run-marker.md").is_file())
            installed = [p for p in proj.rglob("*") if p.name == "kit_dry_run.py" or p.parts[len(proj.parts)] == "scripts"]
            self.assertEqual(installed, [])
            self.assertNotIn("kit_dry_run", proc.stdout)
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def test_lint_rule(self):
        lint = (ROOT / "scripts/kit-lint.py").read_text(encoding="utf-8")
        self.assertIn("kit_dry_run", lint)
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(ROOT / ".cursor", tmp / ".cursor", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(ROOT / "docs", tmp / "docs")
            shutil.copytree(ROOT / "plugins", tmp / "plugins", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(ROOT / "scripts", tmp / "scripts", ignore=shutil.ignore_patterns("__pycache__", "tests"))
            for name in ("CHANGELOG.md", "CONTRIBUTING.md", "README.md", "AGENTS.md"):
                if (ROOT / name).is_file():
                    shutil.copy(ROOT / name, tmp / name)
            doc = tmp / "docs/first-run.md"
            doc.write_text(doc.read_text(encoding="utf-8") + "\nRun kit_dry_run.py first.\n", encoding="utf-8")
            proc = subprocess.run([sys.executable, str(tmp / "scripts/kit-lint.py"), str(tmp)], capture_output=True, text=True)
            self.assertIn("docs/first-run.md", proc.stdout)
            self.assertIn("maintainer-only kit_dry_run", proc.stdout)
            self.assertNotEqual(proc.returncode, 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
