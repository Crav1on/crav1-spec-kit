"""1.210.0: kit 2.0 follows the newest v2.0.0-* pre-release, and the plan stays small.

Synthetic tags only. Versions such as 2.0.0-alpha.10 are fixtures, not a published tag.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPDATE = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
SKILL = ROOT / ".cursor/skills/crav1/crav1-update-kit"
MARKER = ".cursor/skills/crav1/crav1-docs/reference/workflow.md"

STUB = """import json, sys
version = "{version}"
if "install" not in sys.argv:
    raise SystemExit(2)
print(json.dumps({{"version": version, "files": ["a.md"], "dry_run": "dry-run" in sys.argv}}))
"""


def load():
    import importlib.util

    spec = importlib.util.spec_from_file_location("update_kit_1210", UPDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit = load()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_kit(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-X", "utf8", str(UPDATE), *args], capture_output=True, text=True)


def git(repo: Path, *args: str) -> None:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)


def init_repo(repo: Path) -> None:
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    git(repo, "config", "user.email", "a@example.com")
    git(repo, "config", "user.name", "person A")
    git(repo, "config", "commit.gpgsign", "false")


def tag_tree(repo: Path, version: str, tag: str) -> None:
    write(repo / "v2/install.py", STUB.format(version=version))
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", tag)
    git(repo, "tag", tag)


def seed(folder: Path, version: str = "1.210.0") -> None:
    write(folder / MARKER, f"Kit version: {version}\n")
    write(folder / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["cursor"]}, indent=2) + "\n")


def engine(home: Path, version: str) -> None:
    write(
        home / ".crav1-2/installed.json",
        json.dumps({"engine": version, "version": version, "files": {}}, indent=2) + "\n",
    )


RELEASES = """\
111\trefs/tags/v1.208.0
222\trefs/tags/v2.0.0
333\trefs/tags/v2.0.0-alpha.3
444\trefs/tags/v2.0.0-alpha.4
555\trefs/tags/v2.0.0-alpha.10
666\trefs/tags/v2.0.1-alpha.1
555\trefs/tags/v2.0.0-alpha.10^{}
"""


class TagOrder(unittest.TestCase):
    def test_newest_pre_release_skips_stable_and_other_minors(self):
        self.assertEqual(kit.newest_v2_prerelease(RELEASES), "v2.0.0-alpha.10")
        self.assertEqual(
            kit.v2_prerelease_tags(RELEASES),
            ["v2.0.0-alpha.3", "v2.0.0-alpha.4", "v2.0.0-alpha.10"],
        )
        self.assertEqual(kit.published_tags(RELEASES), ["v1.208.0"])
        self.assertIsNone(kit.newest_v2_prerelease("v1.210.0\nv2.0.0\n"))


class FetchSameWay(unittest.TestCase):
    def test_v2_tag_uses_the_short_clone_and_a_1x_fetch_still_refuses_it(self):
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, True)
        repo = base / "rel"
        init_repo(repo)
        tag_tree(repo, "2.0.0-alpha.4", "v2.0.0-alpha.4")
        tag_tree(repo, "2.0.0-alpha.10", "v2.0.0-alpha.10")
        dest = kit._clone_release("v2.0.0-alpha.10", None, str(repo))
        self.addCleanup(shutil.rmtree, dest, True)
        kit.verify_checkout(dest)
        self.assertEqual(dest.parent, Path(tempfile.gettempdir()))
        self.assertTrue(dest.name.startswith("ck"))
        self.assertLess(len(dest.name), 16)
        autocrlf = subprocess.run(["git", "-C", str(dest), "config", "--get", "core.autocrlf"], capture_output=True, text=True)
        longpaths = subprocess.run(["git", "-C", str(dest), "config", "--get", "core.longpaths"], capture_output=True, text=True)
        self.assertEqual(autocrlf.stdout.strip(), "false")
        self.assertEqual(longpaths.stdout.strip(), "true")
        self.assertIn("2.0.0-alpha.10", (dest / "v2/install.py").read_text(encoding="utf-8"))
        refused = run_kit(["fetch", "--tag", "v2.0.0-alpha.10", "--url", str(repo)])
        self.assertEqual(refused.returncode, 2, refused.stdout)
        self.assertIn("Refused:", refused.stderr)


class Kit2Install(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, True)
        self.repo = self.base / "rel"
        init_repo(self.repo)
        tag_tree(self.repo, "2.0.0-alpha.4", "v2.0.0-alpha.4")
        tag_tree(self.repo, "2.0.0-alpha.10", "v2.0.0-alpha.10")
        tag_tree(self.repo, "2.0.1-alpha.1", "v2.0.1-alpha.1")
        git(self.repo, "tag", "v2.0.0", "v2.0.0-alpha.10")
        self.releases = self.base / "releases.txt"
        self.releases.write_text(RELEASES, encoding="utf-8")
        self.old, self.new, self.root = self.base / "old", self.base / "new", self.base / "proj"
        self.home = self.base / "home"
        self.home.mkdir()
        for folder in (self.old, self.new, self.root):
            seed(folder)
        write(self.new / "v2/install.py", STUB.format(version="2.0.0-alpha.3"))
        write(self.root / ".crav1/flags.local.json", json.dumps({"kit2": True}) + "\n")

    def plan(self, *extra: str) -> dict:
        proc = run_kit([
            "plan", "--old", str(self.old), "--new", str(self.new), "--to-version", "1.210.0",
            "--root", str(self.root), "--home", str(self.home),
            "--releases-file", str(self.releases), "--url", str(self.repo), *extra,
        ])
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return json.loads(proc.stdout)

    def test_plan_installs_the_newest_pre_release_and_names_both_versions(self):
        body = self.plan()
        line = body["kit2_line"]
        self.assertTrue(line.startswith("Kit 2.0: dry-run 2.0.0-alpha.10,"), line)
        self.assertIn("Will install 2.0.0-alpha.10; installed now none.", line)
        self.assertNotIn("alpha.4", line)
        self.assertNotIn("alpha.3", line)
        self.assertNotIn("A newer 2.0 may exist.", line)
        self.assertEqual(body["card"]["words"], ["install-kit2", "stop"])
        self.assertEqual(body["card"]["question"], "Install kit 2.0 for this repo?")
        self.assertEqual(body["repo_writes"], 0)

    def test_matching_engine_has_no_card_and_no_reload(self):
        engine(self.home, "2.0.0-alpha.10")
        body = self.plan()
        line = body["kit2_line"]
        self.assertTrue(line.startswith("Kit 2.0: current 2.0.0-alpha.10."), line)
        self.assertIn("Will install 2.0.0-alpha.10; installed now 2.0.0-alpha.10.", line)
        self.assertIsNone(body["card"])
        self.assertEqual(body["ending_args"], ["--not-updated", "--kit2-current"])
        self.assertNotIn("install-kit2", json.dumps(body["card"]))
        ending = run_kit(["ending", "--root", str(self.root), "--not-updated", "--kit2-current"])
        self.assertEqual(ending.returncode, 0, ending.stderr)
        self.assertEqual(
            ending.stdout,
            "Run next:\nThe repo kit is current and kit 2.0 is current. Nothing to do.\n",
        )
        self.assertNotIn("Reload", ending.stdout)
        self.assertNotIn("Developer:", ending.stdout)
        applied = run_kit([
            "apply", "--yes", "--old", str(self.old), "--new", str(self.new),
            "--root", str(self.root), "--home", str(self.home),
            "--releases-file", str(self.releases), "--url", str(self.repo),
        ])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        result = json.loads(applied.stdout)
        self.assertEqual(result["touched"], [])
        self.assertTrue(result["kit2_line"].startswith("Kit 2.0: current "), result["kit2_line"])
        self.assertEqual(result["ending_args"], ["--not-updated", "--kit2-current"])

    def test_failed_lookup_falls_back_and_does_not_downgrade(self):
        missing = self.base / "missing.txt"
        missing.write_text("v2.0.0-alpha.99\n", encoding="utf-8")
        self.releases = missing
        fresh = self.plan()
        self.assertIn("Will install 2.0.0-alpha.3; installed now none.", fresh["kit2_line"])
        self.assertIn("A newer 2.0 may exist.", fresh["kit2_line"])
        self.assertTrue(fresh["kit2_line"].startswith("Kit 2.0: dry-run "), fresh["kit2_line"])
        engine(self.home, "2.0.0-alpha.10")
        newer = self.plan()
        self.assertTrue(newer["kit2_line"].startswith("Kit 2.0: current 2.0.0-alpha.10."), newer["kit2_line"])
        self.assertIn("Will install 2.0.0-alpha.3; installed now 2.0.0-alpha.10.", newer["kit2_line"])
        self.assertIn("A newer 2.0 may exist.", newer["kit2_line"])
        self.assertIsNone(newer["card"])


class CompactPlan(unittest.TestCase):
    def test_unchanged_paths_stay_behind_the_flag_and_under_20kb(self):
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, True)
        old, new, root = base / "old", base / "new", base / "proj"
        home = base / "home"
        home.mkdir()
        for folder in (old, new, root):
            seed(folder)
            for i in range(500):
                write(folder / f".cursor/skills/crav1/crav1-help/refs/f{i:03d}.md", "same\n")
        common = [
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.210.0",
            "--root", str(root), "--home", str(home),
        ]
        plain = run_kit(common)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertLess(len(plain.stdout.encode()), 20 * 1024, len(plain.stdout.encode()))
        body = json.loads(plain.stdout)
        self.assertNotIn("unchanged", body["files"])
        self.assertGreaterEqual(body["files"]["counts"]["unchanged"], 500)
        self.assertEqual(body["files"]["counts"]["update"], 0)
        self.assertNotIn("refs/f000.md", plain.stdout)
        self.assertEqual(body["repo_writes"], 0)
        listed = run_kit([*common, "--list-unchanged"])
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertGreater(len(listed.stdout.encode()), 20 * 1024)
        listed_body = json.loads(listed.stdout)
        self.assertIn(".cursor/skills/crav1/crav1-help/refs/f000.md", listed_body["files"]["unchanged"])
        self.assertEqual(len(listed_body["files"]["unchanged"]), listed_body["files"]["counts"]["unchanged"])


class PipeRule(unittest.TestCase):
    def test_plan_and_apply_repeat_the_no_pipe_rule(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        heads = (SKILL / "references/heads-up.md").read_text(encoding="utf-8")
        overlay = (SKILL / "references/overlay.md").read_text(encoding="utf-8")
        for text, name in ((skill, "SKILL.md"), (heads, "heads-up.md"), (overlay, "overlay.md")):
            self.assertIn("plan", text)
            self.assertIn("apply", text)
            self.assertIn("`| python -c`", text, name)
            self.assertIn("`| head`", text, name)
            self.assertIn("`>`", text, name)
            self.assertIn("Read it directly.", text, name)


if __name__ == "__main__":
    unittest.main()
