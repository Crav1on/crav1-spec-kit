"""1.185.0: build-map.md branch blocks nest their lists, one item per
sub-bullet, and Delivers is merged into Tasks."""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1"
WP = SK / "crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
SNAP = ROOT / "scripts/tests/snapshots/orders-api-merge-wait"


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SK / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load("crav1-tasks-ready-to-build/scripts/build_map.py", "bm_1185")
MAP = (SNAP / "expected/build-map.md").read_text(encoding="utf-8")


class NestedLists(unittest.TestCase):
    def test_no_delivers_and_no_semicolon_joins(self):
        self.assertNotIn("- Delivers:", MAP)
        for line in MAP.splitlines():
            if line.startswith(("- Tasks:", "- Waits for:", "- Waited for:")):
                self.assertNotIn("; ", line)

    def test_done_item_on_its_own_sub_bullet(self):
        self.assertIn("- Tasks:\n  - ~~T1 Add the idempotency key column~~ ✓ done (feat/orders-store)\n"
                      "  - T2 Store a retried order once\n", MAP)
        self.assertEqual(bm.map_marks(MAP), {1: "feat/orders-store"})

    def test_empty_waits_is_one_line(self):
        self.assertIn("- Waits for: none\n", MAP)
        self.assertIn("- Waits for:\n  - feat/orders-store\n", MAP)

    def test_single_value_bullets_stay_on_one_line(self):
        self.assertIn("- Ready now: held, waits on feat/orders-store\n", MAP)
        self.assertIn("- Question: none\n", MAP)

    def test_every_delivers_item_is_in_tasks(self):
        tasks = "- [x] T1 Add the column (branch: feat/x)\n- [ ] T2 Store it once (branch: feat/x)\n"
        out = bm.build("orders-api", "# Spec\n", None, tasks)
        text = out["markdown"]
        block = text.split("### feat/x", 1)[1]
        self.assertIn("  - ~~T1 Add the column~~ ✓ done", block)
        self.assertIn("  - T2 Store it once", block)

    def test_diagram_unchanged_by_the_block_format(self):
        diagram = MAP.split("```mermaid", 1)[1].split("```", 1)[0]
        self.assertNotIn("Tasks", diagram)
        self.assertIn("flowchart LR", diagram)


class OldMapRewrittenOnce(unittest.TestCase):
    def run_ready(self, root: Path) -> str:
        proc = subprocess.run([sys.executable, str(WP), "readiness", "--root", str(root), "--text", "--write-map",
                               "--user", "Person C"], capture_output=True, text=True)
        return proc.stdout

    def test_an_older_map_is_rewritten_then_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "orders-api"
            shutil.copytree(SNAP / "spec", root)
            old = re.sub(r"- Tasks:\n((?:  - .*\n)+)",
                         lambda m: "- Delivers: old\n- Tasks: " + "; ".join(l[4:] for l in m.group(1).splitlines()) + "\n",
                         MAP)
            (root / "build-map.md").write_text(old, encoding="utf-8")
            first = self.run_ready(root)
            self.assertIn("build-map.md (updated)", first)
            text = (root / "build-map.md").read_text(encoding="utf-8")
            self.assertNotIn("- Delivers:", text)
            self.assertIn("✓ done (feat/orders-store)", text)
            second = self.run_ready(root)
            self.assertIn("build-map.md (unchanged", second)


if __name__ == "__main__":
    unittest.main()
