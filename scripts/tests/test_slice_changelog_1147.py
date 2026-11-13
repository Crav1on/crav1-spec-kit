"""1.147.0: install bundles keep the newest 15 changelog releases."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "slice-changelog.py"

spec = importlib.util.spec_from_file_location("slice_changelog", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BUNDLES = (
    ROOT / ".cursor/skills/crav1/crav1-docs/CHANGELOG.md",
    ROOT / "plugins/crav1/skills/crav1-docs/CHANGELOG.md",
    ROOT / ".claude/skills/crav1-docs/CHANGELOG.md",
)


def _headings(text: str) -> list[str]:
    return mod.HEADING.findall(text)


class SliceChangelog(unittest.TestCase):
    def test_keeps_newest_15_and_points_at_github(self):
        sections = [f"## 1.{i}.0 (2026-01-01)\n\n- note {i}\n" for i in range(20, 0, -1)]
        full = "# Changelog\n\nIntro.\n\n" + "\n".join(sections)
        sliced = mod.slice_text(full, 15)
        heads = _headings(sliced)
        self.assertEqual(heads, [f"1.{i}.0" for i in range(20, 5, -1)])
        self.assertIn("# Changelog", sliced)
        self.assertIn("Intro.", sliced)
        self.assertNotIn("## 1.5.0", sliced)
        self.assertIn(mod.FULL_URL, sliced)
        self.assertTrue(sliced.endswith(mod.FOOTER + "\n"))
        self.assertLess(len(sliced), len(full))

    def test_short_file_still_ends_with_the_pointer(self):
        full = "# Changelog\n\n## 1.0.0\n\n- first\n"
        sliced = mod.slice_text(full, 15)
        self.assertEqual(_headings(sliced), ["1.0.0"])
        self.assertIn(mod.FULL_URL, sliced)

    def test_update_kit_still_reads_the_newest_heading(self):
        kit = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
        spec = importlib.util.spec_from_file_location("update_kit", kit)
        update_kit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(update_kit)
        full = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        sliced = mod.slice_text(full)
        self.assertEqual(_headings(sliced)[0], _headings(full)[0])
        self.assertEqual(len(_headings(sliced)), 15)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text(sliced, encoding="utf-8")
            self.assertEqual(update_kit.version_in_changelog(path), _headings(full)[0])

    def test_check_rejects_the_full_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--check", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("is not the newest 15 releases", proc.stderr)

    def test_committed_bundles_match_the_slice(self):
        full = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        sliced = mod.slice_text(full)
        self.assertGreater(len(full.split()), len(sliced.split()))
        for path in BUNDLES:
            self.assertEqual(path.read_text(encoding="utf-8"), sliced, path)


if __name__ == "__main__":
    unittest.main()
