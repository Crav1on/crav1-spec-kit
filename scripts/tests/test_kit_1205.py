"""1.205.0: 1.x leaves kit 2.0 alone, and is never offered a 2.0 tag.

The update commit stages files the release ships. remove leaves crav1-2-
skills and agents, .crav1-2/, and sot/ in every vendor tree. Lint and the
generators match crav1-[a-z]. The dry-run copy block stays on stdout.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPDATE = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "-c", "init.defaultBranch=main"]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit = load(UPDATE, "update_kit_1205")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_kit(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-X", "utf8", str(UPDATE), *args], capture_output=True, text=True)


def git_init(root: Path) -> None:
    subprocess.run([*G, "init", "-q", str(root)], check=True)
    subprocess.run(["git", "config", "user.email", "a@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "person A"], cwd=root, check=True)
    subprocess.run([*G, "-C", str(root), "add", "-A"], check=True)
    subprocess.run([*G, "-C", str(root), "commit", "-qm", "start"], check=True)


V2 = {
    ".crav1-2/keep.txt": "kit 2 state\n",
    "sot/orders-api.md": "source of truth\n",
}


def v2_for(vendor: str) -> dict[str, str]:
    """2.0 skills and agents beside that vendor's 1.x tree, plus the shared folders."""
    extra = {
        "cursor": {
            ".cursor/skills/crav1/crav1-2-help/SKILL.md": "two skill\n",
            ".cursor/agents/crav1-2-review.md": "two agent\n",
            ".cursor/agent-assets/crav1-2-review/note.md": "two asset\n",
        },
        "claude": {
            ".claude/skills/crav1-2-help/SKILL.md": "two skill\n",
            ".claude/agents/crav1-2-review.md": "two agent\n",
            ".claude/agent-assets/crav1-2-review/note.md": "two asset\n",
        },
        "codex": {
            ".agents/skills/crav1-2-help/SKILL.md": "two skill\n",
        },
        "copilot": {
            ".github/skills/crav1-2-help/SKILL.md": "two skill\n",
        },
    }
    out = dict(V2)
    out.update(extra[vendor])
    return out


def ship(vendor: str, version: str = "1.204.0") -> dict[str, str]:
    """The 1.x files this release ships for one vendor, at consumer paths."""
    if vendor == "cursor":
        return {
            ".cursor/skills/crav1/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
            ".cursor/skills/crav1/crav1-help/SKILL.md": "help\n",
            ".cursor/agents/crav1-review-agent.md": "review\n",
            ".cursor/rules/crav1.mdc": "rule\n",
        }
    if vendor == "claude":
        return {
            ".claude/skills/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
            ".claude/skills/crav1-help/SKILL.md": "help\n",
            ".claude/agents/crav1-review-agent.md": "review\n",
            ".claude/CLAUDE.md": "claude\n",
        }
    if vendor == "codex":
        return {
            ".agents/skills/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
            ".agents/skills/crav1-help/SKILL.md": "help\n",
        }
    return {
        ".github/skills/crav1-docs/reference/workflow.md": f"Kit version: {version}\n",
        ".github/skills/crav1-help/SKILL.md": "help\n",
        ".github/instructions/crav1.instructions.md": "instructions\n",
    }


def release_paths(vendor: str, files: dict[str, str]) -> dict[str, str]:
    """Codex and Copilot live under vendors/ in a release checkout."""
    if vendor == "codex":
        return {f"vendors/codex/{rel}": text for rel, text in files.items()}
    if vendor == "copilot":
        return {f"vendors/copilot/{rel}": text for rel, text in files.items()}
    return dict(files)


class ReleaseList(unittest.TestCase):
    def test_commit_stages_shipped_files_and_leaves_v2(self):
        base = Path(tempfile.mkdtemp())
        root, old, new = base / "proj", base / "old", base / "new"
        shipped = ship("cursor")
        for folder, text_map in ((old, shipped), (new, shipped), (root, shipped)):
            for rel, text in text_map.items():
                write(folder / rel, text)
        write(new / ".cursor/rules/crav1.mdc", "rule new\n")
        for rel, text in v2_for("cursor").items():
            write(root / rel, text)
        write(root / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["cursor"]}, indent=2) + "\n")
        git_init(root)
        write(root / ".cursor/rules/crav1.mdc", "rule new\n")
        write(root / "docs/specs/orders-api/spec.md", "edited during the walk\n")
        before = {rel: (root / rel).read_bytes() for rel in v2_for("cursor")}
        committed = run_kit([
            "commit", "--yes", "--from-version", "1.204.0", "--to-version", "1.205.0",
            "--old", str(old), "--new", str(new), "--root", str(root),
        ])
        self.assertEqual(committed.returncode, 0, committed.stderr)
        payload = json.loads(committed.stdout)
        self.assertEqual(payload["message"], "Update CRAV1 kit v1.204.0 to v1.205.0")
        self.assertIn("docs/specs/orders-api/spec.md", payload["left_uncommitted"])
        names = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"], cwd=root, check=True, capture_output=True, text=True,
        ).stdout
        self.assertIn(".cursor/rules/crav1.mdc", names)
        for rel in before:
            self.assertNotIn(rel, names)
            self.assertEqual((root / rel).read_bytes(), before[rel], rel)
        self.assertNotIn("spec.md", names)

    def test_write_refuses_a_v2_path_and_does_not_create_it(self):
        base = Path(tempfile.mkdtemp())
        for rel in (".crav1-2/keep.txt", "sot/orders-api.md", ".cursor/agents/crav1-2-review.md",
                    ".agents/skills/crav1-2-help/SKILL.md"):
            with self.assertRaises(kit.Refuse) as caught:
                kit._write(base, rel, b"no\n")
            self.assertIn("kit 2.0", caught.exception.message)
            self.assertFalse((base / rel).exists(), rel)

    def test_commit_without_a_release_tree_is_refused(self):
        base = Path(tempfile.mkdtemp())
        root = base / "proj"
        write(root / ".cursor/skills/crav1/crav1-docs/reference/workflow.md", "Kit version: 1.204.0\n")
        git_init(root)
        write(root / ".cursor/rules/crav1.mdc", "rule\n")
        refused = run_kit([
            "commit", "--yes", "--from-version", "1.204.0", "--to-version", "1.205.0", "--root", str(root),
        ])
        self.assertEqual(refused.returncode, 2)
        self.assertIn("release tree", refused.stderr)


class RemoveLeavesV2(unittest.TestCase):
    def test_each_vendor_tree(self):
        for vendor in ("cursor", "claude", "codex", "copilot"):
            with self.subTest(vendor=vendor):
                base = Path(tempfile.mkdtemp())
                root = base / "proj"
                tree = base / "release"
                shipped = ship(vendor)
                for rel, text in release_paths(vendor, shipped).items():
                    write(tree / rel, text)
                for rel, text in shipped.items():
                    write(root / rel, text)
                planted = v2_for(vendor)
                for rel, text in planted.items():
                    write(root / rel, text)
                write(root / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": [vendor]}, indent=2) + "\n")
                before = {rel: (root / rel).read_bytes() for rel in planted}
                plan = run_kit(["plan", "--remove", vendor, "--old", str(tree), "--root", str(root)])
                self.assertEqual(plan.returncode, 0, plan.stderr)
                body = json.loads(plan.stdout)
                listed = json.dumps(body["vendors"][0].get("delete", []))
                for rel in planted:
                    self.assertNotIn(rel, listed)
                applied = run_kit(["apply", "--remove", vendor, "--old", str(tree), "--yes", "--root", str(root)])
                self.assertEqual(applied.returncode, 0, applied.stderr)
                for rel, data in before.items():
                    self.assertEqual((root / rel).read_bytes(), data, f"{vendor} {rel}")
                marker = next(rel for rel in shipped if rel.endswith("SKILL.md") and "crav1-help" in rel)
                if vendor != "copilot":
                    self.assertFalse((root / marker).exists(), marker)
                else:
                    self.assertTrue((root / marker).is_file())
                    owned: dict[str, bytes] = {}
                    kit._collect_owns(root, [{"skills": ".github/skills", "names": "crav1"}], owned)
                    self.assertIn(marker, owned)
                    self.assertNotIn(".github/skills/crav1-2-help/SKILL.md", owned)


class OneXTags(unittest.TestCase):
    def test_latest_ignores_v2_and_prerelease(self):
        text = "\n".join([
            "aaaa\trefs/tags/v1.204.0",
            "bbbb\trefs/tags/v1.205.0",
            "cccc\trefs/tags/v2.0.0",
            "dddd\trefs/tags/v2.1.3",
            "eeee\trefs/tags/v2.0.0-alpha.1",
            "ffff\trefs/tags/v2.0.0-alpha.10",
            "gggg\trefs/tags/v3.0.0",
        ])
        tags = kit.published_tags(text)
        self.assertEqual(tags, ["v1.204.0", "v1.205.0"])
        resolved = kit.resolve_target(None, tags)
        self.assertEqual(resolved["tag"], "v1.205.0")
        self.assertTrue(resolved["latest"])
        for raw in ("v2.0.0", "v2.1.3", "v2.0.0-alpha.1"):
            with self.assertRaises(kit.Refuse) as caught:
                kit.resolve_target(kit.normalize_request(raw), tags)
            self.assertNotIn("v1.205.0", caught.exception.message)
        path = Path(tempfile.mkdtemp()) / "tags.txt"
        path.write_text(text + "\n", encoding="utf-8")
        cli = run_kit(["resolve-target", "--releases-file", str(path)])
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(json.loads(cli.stdout)["tag"], "v1.205.0")
        old = os.environ.get("CRAV1_KIT_LATEST")
        try:
            os.environ["CRAV1_KIT_LATEST"] = "2.0.0"
            self.assertIsNone(kit._latest_release())
            os.environ["CRAV1_KIT_LATEST"] = "v2.0.0-alpha.3"
            self.assertIsNone(kit._latest_release())
            os.environ["CRAV1_KIT_LATEST"] = "1.205.0"
            self.assertEqual(kit._latest_release(), "1.205.0")
        finally:
            if old is None:
                os.environ.pop("CRAV1_KIT_LATEST", None)
            else:
                os.environ["CRAV1_KIT_LATEST"] = old


class NameGlobs(unittest.TestCase):
    def test_kit_lint_skips_crav1_2(self):
        lint = load(ROOT / "scripts/kit-lint.py", "kit_lint_1205")
        self.assertTrue(lint.is_v1_skill_name("crav1-help"))
        self.assertFalse(lint.is_v1_skill_name("crav1-2-help"))
        self.assertFalse(lint.is_v1_skill_name("crav1-docs"))
        base = Path(tempfile.mkdtemp())
        (base / "crav1-help").mkdir()
        (base / "crav1-2-help").mkdir()
        (base / "crav1-docs").mkdir()
        self.assertEqual(lint.skill_names(str(base)), ("crav1-help",))

    def test_claude_sync_skips_crav1_2(self):
        claude = load(ROOT / "scripts/sync-crav1-claude.py", "sync_claude_1205")
        base = Path(tempfile.mkdtemp())
        skills = base / "skills"
        agents = base / "agents"
        write(skills / "crav1-help/SKILL.md", "one\n")
        write(skills / "crav1-2-help/SKILL.md", "two\n")
        write(agents / "crav1-review-agent.md", "one\n")
        write(agents / "crav1-2-review.md", "two\n")
        self.assertEqual([p.name for p in claude.v1_skill_dirs(skills)], ["crav1-help"])
        self.assertEqual([p.name for p in claude.v1_agent_files(agents)], ["crav1-review-agent.md"])
        dest = base / "out"
        claude.copy_v1_tree(skills, dest)
        self.assertTrue((dest / "crav1-help/SKILL.md").is_file())
        self.assertFalse((dest / "crav1-2-help").exists())

    def test_vendor_sync_skips_crav1_2(self):
        vendors = load(ROOT / "scripts/sync-crav1-vendors.py", "sync_vendors_1205")
        base = Path(tempfile.mkdtemp())
        agents = base / "agents"
        write(agents / "crav1-review-agent.md", "one\n")
        write(agents / "crav1-2-review.md", "two\n")
        self.assertEqual([p.name for p in vendors.v1_agent_files(agents)], ["crav1-review-agent.md"])
        skills = base / "skills"
        write(skills / "crav1-help/SKILL.md", "one\n")
        write(skills / "crav1-2-help/SKILL.md", "two\n")
        self.assertEqual([p.name for p in vendors.v1_skill_dirs(skills)], ["crav1-help"])

    def test_skill_docs_generator_skips_crav1_2(self):
        docs = load(ROOT / "scripts/gen-skill-docs.py", "gen_skill_docs_1205")
        base = Path(tempfile.mkdtemp())
        write(base / "crav1-review-agent.md", "one\n")
        write(base / "crav1-2-review.md", "two\n")
        self.assertEqual(docs.v1_agent_stems(base), ["crav1-review-agent"])

    def test_plugin_sync_glob_skips_crav1_2(self):
        script = (ROOT / "scripts/sync-crav1-plugin.sh").read_text(encoding="utf-8")
        self.assertIn("crav1-[a-z]*.md", script)
        self.assertNotIn("name 'crav1-*.md'", script)
        self.assertIn("crav1-2-*)", script)
        workflow = (ROOT / ".github/workflows/drop-in-plugin-sync.yml").read_text(encoding="utf-8")
        self.assertIn("crav1-[a-z]*.md", workflow)
        self.assertNotIn("name 'crav1-*.md'", workflow)
        base = Path(tempfile.mkdtemp())
        agents = base / "agents"
        write(agents / "crav1-review-agent.md", "one\n")
        write(agents / "crav1-2-review.md", "two\n")
        found = subprocess.run(
            ["bash", "-c", "find agents -maxdepth 1 -type f -name 'crav1-[a-z]*.md' -print"],
            cwd=base, check=True, capture_output=True, text=True,
        ).stdout.split()
        self.assertEqual(found, ["agents/crav1-review-agent.md"])


class DryRunProgress(unittest.TestCase):
    def test_dots_go_to_stderr_and_the_copy_block_is_separate(self):
        dry = load(ROOT / "scripts/kit_dry_run.py", "kit_dry_run_1205")
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            with dry.Step("cloning kit", interval=0.05):
                time.sleep(0.16)
        finally:
            sys.stderr = old
        text = buf.getvalue()
        self.assertTrue(text.startswith("cloning kit"))
        self.assertIn(".", text[len("cloning kit"):])
        self.assertTrue(text.endswith("\n"))
        self.assertNotIn("\x1b", text)
        block = "\n".join([dry.FROM, "Kit: 1.205.0", dry.TO])
        self.assertNotIn("cloning kit", block)
        self.assertNotIn("done (", block)
        self.assertEqual(dry.STEP_DOT_SECONDS, 3.0)


if __name__ == "__main__":
    unittest.main()
