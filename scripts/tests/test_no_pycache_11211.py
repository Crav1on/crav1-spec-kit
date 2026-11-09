"""1.121.1: importing a sibling helper does not write __pycache__ beside it.

These tests copy the kit scripts into a temporary directory and run them the
way a project runs them. They also check that kit-lint fails a script that
imports a local module without setting sys.dont_write_bytecode first.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WHEN = "2026-11-09T10:19:09+01:00"
TREES = (
    ROOT / ".cursor/skills/crav1",
    ROOT / ".claude/skills",
    ROOT / "plugins/crav1/skills",
)
WALK = "crav1-tighten-and-plan-ready-to-build"
STORE = "crav1-resolve-open-questions"


def clean_env():
    env = os.environ.copy()
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.pop("PYTHONPYCACHEPREFIX", None)
    return env


def caches(root: Path) -> list[Path]:
    found = []
    for path in root.rglob("*"):
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            found.append(path)
    return found


def load_kit_lint():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("kit_lint_under_test", ROOT / "scripts/kit-lint.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class NoPycache(unittest.TestCase):
    def test_walk_progress_leaves_no_pycache_beside_playbook_store(self):
        for tree in TREES:
            with self.subTest(tree=tree.relative_to(ROOT).as_posix()):
                with tempfile.TemporaryDirectory() as tmp:
                    base = Path(tmp)
                    for skill in (WALK, STORE):
                        dest = base / skill / "scripts"
                        dest.mkdir(parents=True)
                        for py in (tree / skill / "scripts").glob("*.py"):
                            shutil.copy(py, dest / py.name)
                    spec = base / "work" / "docs" / "specs" / "orders"
                    spec.mkdir(parents=True)
                    playbook = base / "playbook.md"
                    playbook.write_text("# CC Process 1.0: playbook\n\n- Answer: yes\n", encoding="utf-8")
                    script = base / WALK / "scripts" / "walk_progress.py"
                    proc = subprocess.run(
                        [
                            sys.executable, str(script), "record",
                            "--root", str(spec), "--slice", "docs/specs/orders",
                            "--step", "playbook", "--result", "applied", "--when", WHEN,
                            "--playbook", str(playbook), "--yes",
                        ],
                        capture_output=True, text=True, env=clean_env(),
                    )
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertIn('"ok": true', proc.stdout)
                    self.assertIn("Playbook:", (spec / "walk-progress.md").read_text(encoding="utf-8"))
                    self.assertEqual(caches(base), [])

    def test_task_order_wrapper_leaves_no_pycache(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            wrapper = base / "scripts"
            wrapper.mkdir()
            shutil.copy(ROOT / "scripts/task-order.py", wrapper / "task-order.py")
            target = base / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts"
            target.mkdir(parents=True)
            shutil.copy(
                ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/task_order.py",
                target / "task_order.py",
            )
            tasks = base / "tasks.md"
            tasks.write_text("- [ ] T1: first\n- [ ] T2: second\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(wrapper / "task-order.py"), str(tasks)],
                capture_output=True, text=True, env=clean_env(),
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Ready (dependency order)", proc.stdout)
            self.assertEqual(caches(base), [])

    def test_installed_scripts_set_the_flag_before_a_local_import(self):
        self.assertEqual(load_kit_lint().bytecode_problems(str(ROOT)), [])

    def test_lint_rejects_a_local_import_without_the_flag(self):
        mod = load_kit_lint()
        missing = "without sys.dont_write_bytecode = True after import sys and before that import"
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            scripts = base / ".cursor/skills/crav1/crav1-example/scripts"
            scripts.mkdir(parents=True)
            (scripts / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            entry = scripts / "entry.py"
            entry.write_text("import sys\nimport helper\n", encoding="utf-8")
            problems = mod.bytecode_problems(str(base))
            self.assertEqual(len(problems), 1)
            self.assertIn("entry.py", problems[0])
            self.assertIn("line 2", problems[0])
            self.assertIn(missing, problems[0])

            entry.write_text(
                "import helper\nimport sys\nsys.dont_write_bytecode = True\n",
                encoding="utf-8",
            )
            late = mod.bytecode_problems(str(base))
            self.assertEqual(len(late), 1)
            self.assertIn("line 1", late[0])

            entry.write_text(
                "import sys\nsys.dont_write_bytecode = True\nimport helper\n",
                encoding="utf-8",
            )
            self.assertEqual(mod.bytecode_problems(str(base)), [])

            (scripts / "stdlib_only.py").write_text("import sys\nimport json\n", encoding="utf-8")
            self.assertEqual(mod.bytecode_problems(str(base)), [])

    def test_lint_rejects_importlib_load_without_the_flag(self):
        mod = load_kit_lint()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            folder = base / "scripts"
            folder.mkdir()
            entry = folder / "load_helper.py"
            entry.write_text(
                "import importlib.util\n"
                "import sys\n"
                "spec = importlib.util.spec_from_file_location('helper', 'helper.py')\n"
                "mod = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(mod)\n",
                encoding="utf-8",
            )
            problems = mod.bytecode_problems(str(base))
            self.assertEqual(len(problems), 1)
            self.assertIn("line 3", problems[0])

            entry.write_text(
                "import sys\n"
                "sys.dont_write_bytecode = True\n"
                "import importlib.util\n"
                "spec = importlib.util.spec_from_file_location('helper', 'helper.py')\n"
                "mod = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(mod)\n",
                encoding="utf-8",
            )
            self.assertEqual(mod.bytecode_problems(str(base)), [])


if __name__ == "__main__":
    unittest.main()
