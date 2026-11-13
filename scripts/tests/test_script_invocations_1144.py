"""1.144.0: documented kit-script commands name required arguments and do not hardcode python3 alone."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "scripts" / "check-script-invocations.py"
RESOLVE = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/resolve_spec.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_script_invocations", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check = _load()


class DocumentedCommands(unittest.TestCase):
    def test_repo_instructions_pass(self):
        self.assertEqual(check.problems(str(ROOT)), [])

    def test_python3_alone_and_a_missing_root_fail(self):
        known = check.catalog(str(ROOT))
        paragraph = 'python3 scripts/resolve_spec.py "orders-export"'
        found = check._problems_in_paragraph("sample.md", 1, paragraph, known)
        self.assertTrue(any("missing --root" in item for item in found))
        self.assertTrue(any("python3" in item for item in check._python3_alone("sample.md", paragraph)))

    def test_windows_python_and_root_pass(self):
        known = check.catalog(str(ROOT))
        paragraph = (
            "python -X utf8 scripts/resolve_spec.py \"<query>\" --root docs/specs\n"
            "PYTHONUTF8=1 python3 -X utf8 scripts/resolve_spec.py \"<query>\" --root docs/specs"
        )
        self.assertEqual(check._problems_in_paragraph("sample.md", 1, paragraph, known), [])
        self.assertEqual(check._python3_alone("sample.md", paragraph), [])

    def test_interpreter_command_passes(self):
        known = check.catalog(str(ROOT))
        paragraph = (
            '`<interpreter> -X utf8 scripts/resolve_spec.py "<query>" --root docs/specs` '
            "as `crav1-docs/reference/running-scripts.md` says."
        )
        self.assertEqual(check._problems_in_paragraph("sample.md", 1, paragraph, known), [])


class ResolveSpecRoot(unittest.TestCase):
    def test_omitted_root_uses_docs_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "docs" / "specs" / "orders-export"
            spec.mkdir(parents=True)
            (spec / "spec.md").write_text("# Orders export\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(RESOLVE), "orders export"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("orders-export", proc.stdout)

    def test_omitted_root_names_the_flag_when_the_folder_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(RESOLVE), "orders"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--root docs/specs", proc.stdout)

    def test_explicit_root_still_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            spec = root / "orders-export"
            spec.mkdir(parents=True)
            (spec / "spec.md").write_text("# Orders export\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(RESOLVE), "Orders export", "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("orders-export", proc.stdout)

    def test_checker_script_exits_zero_on_this_repo(self):
        proc = subprocess.run(
            [sys.executable, str(CHECK), str(ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("0 problem", proc.stdout)


if __name__ == "__main__":
    unittest.main()
