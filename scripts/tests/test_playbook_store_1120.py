"""1.120.0: copy a filled playbook into docs/playbooks on apply.

These tests run playbook_store.py and walk_progress.py on temp folders.
They are not a live replay of a walk, and they do not create a git commit.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / ".cursor/skills/crav1/crav1-resolve-open-questions/scripts/playbook_store.py"
WALK = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/scripts/walk_progress.py"
WHEN = "2026-11-09T10:19:09+01:00"


def run(script: Path, args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc
    return proc.returncode, payload


def must(script: Path, args: list[str]) -> dict:
    code, payload = run(script, args)
    if code != 0 or not payload.get("ok", False):
        raise AssertionError(payload)
    return payload


FILLED = """# CC Process 1.0: playbook

Report: report-playbook-full · 2026-11-09 · kit 1.120.0

## Kept

- **K1:** DEV deploy has its own Bicep
  - From: Ada, 2026-11-01
  - Change: DEV deploy runs from the shared pipeline

## Needs your answer

- **N1:** Which branch carries the fix
  - Answer: yes
- **C1:** The clash on the release branch
  - Answer: take the newer quote
"""

PARTIAL = """# CC Process 1.0: playbook

Report: report-playbook-short · 2026-11-09 · kit 1.120.0

```
- **N9:** example only
  - Answer: yes
```

## Needs your answer

- **N1:** Which branch carries the fix
  - Answer: yes
- **N2:** Who signs the release
  - Answer:
"""

DRAFT = """# CC Process 1.0: playbook

Report: report-playbook-short · 2026-11-09 · kit 1.120.0

```
- **N1:** …
  - Answer: yes
```

## Needs your answer

- **N1:** Which branch carries the fix
  - Answer:
- **K1:** DEV deploy has its own Bicep
  - Change:
"""


class Names(unittest.TestCase):
    def test_subject_becomes_kebab_case(self):
        cases = {
            "CC Process 1.0": "cc-process-1-0.md",
            "cc process 1.0": "cc-process-1-0.md",
            "Orders — retry!": "orders-retry.md",
            "v2.1 (beta)": "v2-1-beta.md",
            "CC Process 1.0: playbook": "cc-process-1-0.md",
        }
        for subject, name in cases.items():
            payload = must(STORE, ["name", "--subject", subject])
            self.assertEqual(payload["name"], name, subject)
            self.assertEqual(payload["path"], f"docs/playbooks/{name}")


class ApplyCopy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.spec_dir = self.repo / "docs" / "specs" / "orders"
        self.spec_dir.mkdir(parents=True)
        self.spec = self.spec_dir / "spec.md"
        self.spec.write_text("# Orders retry\n\n## Open questions\n\n- Which branch?\n", encoding="utf-8")
        self.outside = self.repo / "outside" / "playbook.md"
        self.outside.parent.mkdir()
        self.outside.write_text(FILLED, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def prepare(self, playbook: Path | None = None) -> dict:
        return must(STORE, ["prepare", "--repo", str(self.repo), "--playbook", str(playbook or self.outside)])

    def write(self, *extra: str, playbook: Path | None = None) -> dict:
        return must(STORE, [
            "write", "--repo", str(self.repo), "--playbook", str(playbook or self.outside),
            "--yes", "--spec", str(self.spec), *extra,
        ])

    def test_draft_is_not_copied(self):
        self.outside.write_text(DRAFT, encoding="utf-8")
        prepared = self.prepare()
        self.assertEqual(prepared["action"], "draft")
        code, payload = run(STORE, [
            "write", "--repo", str(self.repo), "--playbook", str(self.outside),
            "--yes", "--name", "cc-process-1-0.md",
        ])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "draft")
        self.assertFalse((self.repo / "docs" / "playbooks" / "cc-process-1-0.md").exists())

    def test_first_apply_proposes_the_name_then_copies(self):
        prepared = self.prepare()
        self.assertEqual(prepared["action"], "propose-name")
        self.assertEqual(prepared["name"], "cc-process-1-0.md")
        self.assertEqual(prepared["path"], "docs/playbooks/cc-process-1-0.md")
        refused, payload = run(STORE, [
            "write", "--repo", str(self.repo), "--playbook", str(self.outside), "--yes",
        ])
        self.assertEqual(refused, 2)
        self.assertEqual(payload["code"], "needs-name")
        self.assertEqual(payload["name"], "cc-process-1-0.md")

        wrote = self.write("--name", "cc-process-1-0.md")
        self.assertEqual(wrote["path"], "docs/playbooks/cc-process-1-0.md")
        stored = (self.repo / wrote["path"]).read_text(encoding="utf-8")
        self.assertIn("Docs path: docs/playbooks/cc-process-1-0.md", stored)
        self.assertIn("Applied as: " + wrote["applied_as"], stored)
        self.assertIn("- Answer: yes", stored)
        self.assertIn("- Answer: take the newer quote", stored)
        self.assertIn("- Change: DEV deploy runs from the shared pipeline", stored)
        self.assertEqual(stored.count("Docs path:"), 1)
        self.assertEqual(stored.count("Applied as:"), 1)
        self.assertIn("Playbook: docs/playbooks/cc-process-1-0.md", self.spec.read_text(encoding="utf-8"))
        self.assertNotIn("Docs path:", self.outside.read_text(encoding="utf-8"))

    def test_partial_answers_are_copied_and_empty_lines_stay(self):
        self.outside.write_text(PARTIAL, encoding="utf-8")
        self.write("--name", "cc-process-1-0.md")
        stored = (self.repo / "docs" / "playbooks" / "cc-process-1-0.md").read_text(encoding="utf-8")
        self.assertIn("- **N1:** Which branch carries the fix\n  - Answer: yes", stored)
        self.assertIn("- **N2:** Who signs the release\n  - Answer:\n", stored)
        self.assertIn("```\n- **N9:** example only", stored)

    def test_reapply_overwrites_the_same_file_and_keeps_the_name(self):
        self.write("--name", "orders-flow.md")
        first = self.repo / "docs" / "playbooks" / "orders-flow.md"
        self.assertTrue(first.is_file())
        self.assertFalse((self.repo / "docs" / "playbooks" / "cc-process-1-0.md").exists())
        self.outside.write_text(FILLED.replace("Answer: yes", "Answer: keep the release branch"), encoding="utf-8")
        prepared = self.prepare()
        self.assertEqual(prepared["action"], "write")
        self.assertEqual(prepared["recognized"], "subject")
        self.assertEqual(prepared["path"], "docs/playbooks/orders-flow.md")
        self.assertFalse(prepared["edited"])
        again = self.write("--name", "something-else.md")
        self.assertEqual(again["path"], "docs/playbooks/orders-flow.md")
        self.assertTrue(again["name_fixed"])
        stored = first.read_text(encoding="utf-8")
        self.assertIn("Answer: keep the release branch", stored)
        self.assertNotIn("Answer: yes", stored)
        self.assertIn("Docs path: docs/playbooks/orders-flow.md", stored)
        self.assertEqual(self.spec.read_text(encoding="utf-8").count("Playbook:"), 1)

    def test_edited_since_last_apply_asks_before_overwrite(self):
        self.write("--name", "cc-process-1-0.md")
        target = self.repo / "docs" / "playbooks" / "cc-process-1-0.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nHand edit in the repo.\n", encoding="utf-8")
        prepared = self.prepare()
        self.assertEqual(prepared["action"], "ask-overwrite")
        self.assertTrue(prepared["edited"])
        self.assertIn("Hand edit in the repo.", prepared["diff"])
        code, payload = run(STORE, [
            "write", "--repo", str(self.repo), "--playbook", str(self.outside),
            "--yes", "--name", "cc-process-1-0.md",
        ])
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "edited")
        self.assertIn("Hand edit in the repo.", target.read_text(encoding="utf-8"))
        self.write("--name", "cc-process-1-0.md", "--overwrite")
        self.assertNotIn("Hand edit in the repo.", target.read_text(encoding="utf-8"))
        self.assertIn("Answer: yes", target.read_text(encoding="utf-8"))

    def test_docs_path_line_is_the_same_playbook_after_a_rename(self):
        self.write("--name", "orders-flow.md")
        committed = self.repo / "docs" / "playbooks" / "orders-flow.md"
        # A later file is the committed copy itself, not a fresh subject match.
        prepared = self.prepare(committed)
        self.assertEqual(prepared["recognized"], "docs-path")
        self.assertEqual(prepared["path"], "docs/playbooks/orders-flow.md")
        self.assertEqual(prepared["action"], "write")

    def test_walk_progress_records_the_docs_path_and_accepts_it(self):
        self.write("--name", "cc-process-1-0.md")
        recorded = must(WALK, [
            "record", "--root", str(self.spec_dir), "--slice", "docs/specs/orders",
            "--step", "playbook", "--result", "applied", "--when", WHEN,
            "--playbook", str(self.outside), "--yes",
        ])
        self.assertTrue(recorded["ok"])
        progress = (self.spec_dir / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Playbook: docs/playbooks/cc-process-1-0.md@", progress)
        self.assertNotIn(str(self.outside), progress)
        committed = self.repo / "docs" / "playbooks" / "cc-process-1-0.md"
        digest = hashlib.sha256(committed.read_bytes()).hexdigest()[:12]
        self.assertIn(f"docs/playbooks/cc-process-1-0.md@{digest}", progress)

        # Resume on a tree that has the committed copy and not the outside file.
        self.outside.unlink()
        resumed = must(WALK, ["resume", "--root", str(self.spec_dir)])
        by_id = {row["id"]: row for row in resumed["steps"]}
        self.assertEqual(by_id["playbook"]["status"], "keep")

        status = must(WALK, [
            "playbook-status", "--root", str(self.spec_dir),
            "--playbook", "docs/playbooks/cc-process-1-0.md",
        ])
        self.assertEqual(status["status"], "already-applied")
        self.assertTrue(status["already_applied"])
        self.assertEqual(status["offer"], "skip-or-reapply")

        direct = must(WALK, [
            "record", "--root", str(self.spec_dir), "--slice", "docs/specs/orders",
            "--step", "playbook", "--result", "reapplied", "--when", WHEN,
            "--playbook", str(committed), "--yes",
        ])
        self.assertTrue(direct["ok"])
        again = (self.spec_dir / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("Playbook: docs/playbooks/cc-process-1-0.md@", again)
        self.assertIn("Result: reapplied", again)


class Rules(unittest.TestCase):
    def test_skills_state_the_apply_time_exception(self):
        know = (ROOT / ".cursor/skills/crav1/crav1-what-do-we-know-about-this")
        common = (know / "reports/common.md").read_text(encoding="utf-8")
        self.assertIn("Never inside the project", common)
        self.assertIn("docs/playbooks/", common)
        walk = (know / "references/walk.md").read_text(encoding="utf-8")
        self.assertIn("docs/playbooks/", walk)
        apply = (ROOT / ".cursor/skills/crav1/crav1-resolve-open-questions/references/apply.md").read_text(encoding="utf-8")
        self.assertIn("Docs path:", apply)
        self.assertIn("Applied as:", apply)
        self.assertIn("Playbook: docs/playbooks/", apply)
        step = (ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build/references/playbook.md").read_text(encoding="utf-8")
        self.assertIn("docs/playbooks/", step)
        self.assertIn("Docs path:", step)


if __name__ == "__main__":
    unittest.main()
