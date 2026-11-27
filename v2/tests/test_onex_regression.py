"""With v2/ in the kit repo, 1.x update_kit plan, apply, and remove leave 2.0 bytes alone."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from support import REPO, temp_dir

UPDATE = REPO / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
GIT = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "-c", "init.defaultBranch=main"]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_kit(args):
    return subprocess.run([sys.executable, "-X", "utf8", str(UPDATE), *args], capture_output=True, text=True)


def git_init(root):
    subprocess.run([*GIT, "init", "-q", str(root)], check=True)
    subprocess.run(["git", "config", "user.email", "a@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "person A"], cwd=root, check=True)
    subprocess.run([*GIT, "-C", str(root), "add", "-A"], check=True)
    subprocess.run([*GIT, "-C", str(root), "commit", "-qm", "start"], check=True)


SHIPPED = {
    ".cursor/skills/crav1/crav1-docs/reference/workflow.md": "Kit version: 1.204.0\n",
    ".cursor/skills/crav1/crav1-help/SKILL.md": "help\n",
    ".cursor/agents/crav1-review-agent.md": "review\n",
    ".cursor/rules/crav1.mdc": "rule\n",
}

PLANTED = {
    ".cursor/skills/crav1/crav1-2-help/SKILL.md": "two skill\n",
    ".cursor/agents/crav1-2-review.md": "two agent\n",
    ".crav1-2/events.jsonl": "kit 2 events\n",
    ".crav1-2/engine.json": '{"engine": "2.0.0-alpha.1", "schema": 1}\n',
    "sot/index.md": "source of truth\n",
    "sot/2026-11-25-outbound-channel/note.md": "note\n",
}


class Regression(unittest.TestCase):
    def test_plan_apply_and_remove_leave_v2_bytes(self):
        self.assertTrue((REPO / "v2" / "crav1_2" / "__init__.py").is_file())
        base = temp_dir()
        self.addCleanup(lambda: __import__("shutil").rmtree(base, ignore_errors=True))
        root, old, new = base / "proj", base / "old", base / "new"
        for folder in (old, new, root):
            for rel, text in SHIPPED.items():
                write(folder / rel, text)
        write(new / ".cursor/rules/crav1.mdc", "rule new\n")
        for rel, text in PLANTED.items():
            write(root / rel, text)
        write(root / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["cursor"]}, indent=2) + "\n")
        git_init(root)
        write(root / ".cursor/rules/crav1.mdc", "rule new\n")
        write(root / "sot/index.md", "source of truth, dirty\n")
        before = {rel: (root / rel).read_bytes() for rel in PLANTED}
        before["sot/index.md"] = (root / "sot/index.md").read_bytes()
        plan = run_kit([
            "plan", "--list-unchanged", "--old", str(old), "--new", str(new),
            "--to-version", "1.205.0", "--root", str(root),
        ])
        self.assertEqual(plan.returncode, 0, plan.stderr)
        body = json.loads(plan.stdout)
        kit_paths = []
        for bucket in body["files"].values():
            if not isinstance(bucket, list):
                continue
            for item in bucket:
                kit_paths.append(item if isinstance(item, str) else item.get("path", ""))
        for rel in PLANTED:
            self.assertNotIn(rel, kit_paths)
        self.assertTrue(any("crav1-help" in path for path in kit_paths))
        applied = run_kit([
            "apply", "--yes", "--old", str(old), "--new", str(new), "--root", str(root),
        ])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual((root / ".cursor/rules/crav1.mdc").read_text(encoding="utf-8"), "rule new\n")
        for rel, data in before.items():
            self.assertEqual((root / rel).read_bytes(), data, rel)
        remove_plan = run_kit(["plan", "--remove", "cursor", "--old", str(new), "--root", str(root)])
        self.assertEqual(remove_plan.returncode, 0, remove_plan.stderr)
        removal = json.loads(remove_plan.stdout)
        delete_paths = []
        for vendor in removal.get("vendors") or []:
            for item in vendor.get("delete") or []:
                delete_paths.append(item if isinstance(item, str) else item.get("path", ""))
        for rel in before:
            self.assertNotIn(rel, delete_paths)
        removed = run_kit(["apply", "--remove", "cursor", "--yes", "--old", str(new), "--root", str(root)])
        self.assertEqual(removed.returncode, 0, removed.stderr)
        for rel, data in before.items():
            self.assertEqual((root / rel).read_bytes(), data, rel)
        self.assertFalse((root / ".cursor/skills/crav1/crav1-help/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
