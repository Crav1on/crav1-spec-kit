"""install, uninstall, and status against a temp home. Project sot/ is left alone."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from support import V2, temp_dir

INSTALL = V2 / "install.py"


def run(home, *words):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(INSTALL), "--home", str(home), *words],
        text=True,
        capture_output=True,
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class Install(unittest.TestCase):
    def setUp(self):
        self.home = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.home, ignore_errors=True))

    def test_no_1x_installs_and_round_trips(self):
        dry = run(self.home, "install", "dry-run")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertFalse((self.home / ".crav1-2").exists())
        body = json.loads(dry.stdout)
        self.assertFalse(body["one_x"]["found"])
        self.assertIn("No installed 1.x", body["one_x"]["note"])
        self.assertIn("no user-level", body["codex"])
        installed = run(self.home, "install")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        plugin = self.home / ".cursor" / "plugins" / "local" / "crav1-2" / ".cursor-plugin" / "plugin.json"
        manifest = json.loads(plugin.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "crav1-2")
        self.assertEqual(manifest["version"], "2.0.0-alpha.2")
        skill = self.home / ".claude" / "skills" / "crav1-2-help" / "SKILL.md"
        self.assertIn("alpha", skill.read_text(encoding="utf-8").lower())
        self.assertFalse((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertFalse((self.home / ".agents").exists())
        agent = self.home / ".claude" / "agents" / "crav1-2-source-extractor-agent.md"
        cursor_agent = self.home / ".cursor" / "plugins" / "local" / "crav1-2" / "agents" / agent.name
        self.assertEqual(agent.read_bytes(), cursor_agent.read_bytes())
        for name in ("crav1-2-add-to-sot", "crav1-2-show-sot"):
            claude_skill = self.home / ".claude" / "skills" / name / "SKILL.md"
            cursor_skill = self.home / ".cursor" / "plugins" / "local" / "crav1-2" / "skills" / name / "SKILL.md"
            self.assertEqual(claude_skill.read_bytes(), cursor_skill.read_bytes())
        engine = self.home / ".crav1-2" / "engine"
        probe = subprocess.run(
            [sys.executable, "-c", "import crav1_2; print(crav1_2.ENGINE)"],
            text=True,
            capture_output=True,
            env={**__import__("os").environ, "PYTHONPATH": str(engine)},
        )
        self.assertEqual(probe.stdout.strip(), "2.0.0-alpha.2", probe.stderr)
        report = json.loads(run(self.home, "status").stdout)
        self.assertTrue(report["installed"])
        self.assertEqual(report["changed"], [])
        self.assertIn("skipped", report["codex"])
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        removed = run(self.home, "uninstall")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        kept = json.loads(removed.stdout)["kept"]
        self.assertTrue(any(item["path"].endswith("SKILL.md") and item["reason"] == "hash differs" for item in kept))
        self.assertTrue(skill.is_file())
        self.assertFalse(plugin.exists())
        self.assertIn("local edit", skill.read_text(encoding="utf-8"))

    def test_old_1x_is_refused_and_a_current_1x_is_allowed(self):
        plugin = self.home / ".cursor" / "plugins" / "local" / "crav1" / ".cursor-plugin" / "plugin.json"
        write(plugin, json.dumps({"name": "crav1", "version": "1.204.0"}) + "\n")
        refused = run(self.home, "install")
        self.assertEqual(refused.returncode, 2)
        self.assertIn("1.205.0", refused.stderr)
        self.assertFalse((self.home / ".crav1-2").exists())
        self.assertFalse((self.home / ".claude" / "skills" / "crav1-2-help").exists())
        plugin.write_text(json.dumps({"name": "crav1", "version": "1.205.0"}) + "\n", encoding="utf-8")
        workflow = self.home / ".claude" / "skills" / "crav1-docs" / "reference" / "workflow.md"
        write(workflow, "Kit version: 1.204.0\n")
        still = run(self.home, "install")
        self.assertEqual(still.returncode, 2, still.stderr)
        self.assertIn("1.204.0", still.stderr)
        workflow.write_text("Kit version: 1.205.0\n", encoding="utf-8")
        ok = run(self.home, "install")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        status = json.loads(run(self.home, "status").stdout)
        self.assertTrue(status["one_x"]["found"])
        self.assertTrue(status["one_x"]["ok"])

    def test_uninstall_leaves_project_state_and_protected_paths(self):
        project = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(project, ignore_errors=True))
        write(project / "sot" / "index.md", "project index\n")
        write(project / ".crav1-2" / "events.jsonl", "project events\n")
        before = {
            "sot/index.md": (project / "sot" / "index.md").read_bytes(),
            ".crav1-2/events.jsonl": (project / ".crav1-2" / "events.jsonl").read_bytes(),
        }
        self.assertEqual(run(self.home, "install").returncode, 0)
        write(self.home / "sot" / "index.md", "home sot\n")
        write(self.home / ".crav1-2" / "events.jsonl", "home events\n")
        record = self.home / ".crav1-2" / "installed.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["files"]["sot/index.md"] = __import__("hashlib").sha256(b"home sot\n").hexdigest()
        data["files"][".crav1-2/events.jsonl"] = __import__("hashlib").sha256(b"home events\n").hexdigest()
        record.write_text(json.dumps(data), encoding="utf-8")
        removed = run(self.home, "uninstall")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        kept = json.loads(removed.stdout)["kept"]
        self.assertTrue(any(item["path"] == "sot/index.md" and item["reason"] == "protected" for item in kept))
        self.assertEqual((self.home / "sot" / "index.md").read_text(encoding="utf-8"), "home sot\n")
        self.assertEqual((self.home / ".crav1-2" / "events.jsonl").read_text(encoding="utf-8"), "home events\n")
        self.assertEqual((project / "sot" / "index.md").read_bytes(), before["sot/index.md"])
        self.assertEqual((project / ".crav1-2" / "events.jsonl").read_bytes(), before[".crav1-2/events.jsonl"])

    def test_dry_run_uninstall_deletes_nothing(self):
        self.assertEqual(run(self.home, "install").returncode, 0)
        before = sorted(p.relative_to(self.home).as_posix() for p in self.home.rglob("*") if p.is_file())
        dry = run(self.home, "uninstall", "dry-run")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertTrue(json.loads(dry.stdout)["dry_run"])
        after = sorted(p.relative_to(self.home).as_posix() for p in self.home.rglob("*") if p.is_file())
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
