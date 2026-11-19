"""1.194.0: the walk's spec findings go to the skill that owns them.

A code finding (unrecorded commits, a merged PR, Synced at drift, new PR
comments) recommends /crav1-add-to-spec; wording, diagrams and constraints
stay with /crav1-tighten-spec, the default when unclear. A finding spec.md
already covers is offer already-fixed with no card; a typed already-done
closes it only when the spec shows it. code-drift offers add-to-spec before
the plan review. Generic fixtures only (orders-api, person A).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".cursor/skills/crav1/crav1-tighten-and-plan-ready-to-build"
WALK = SKILL / "scripts/walk_progress.py"
GIT = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com"]


def run(args: list[str]) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(WALK), *args], capture_output=True, text=True, check=False)
    try:
        return proc.returncode, json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AssertionError(proc.stderr + proc.stdout) from exc


def slice_dir(spec: str) -> Path:
    root = Path(tempfile.mkdtemp()) / "orders-api"
    root.mkdir(parents=True)
    (root / "spec.md").write_text(spec, encoding="utf-8")
    (root / "plan.md").write_text("# Plan\n\n## Risks\n", encoding="utf-8")
    (root / "tasks.md").write_text("# Tasks\n\n- [ ] T1 Record the lane (after: )\n", encoding="utf-8")
    return root


SPEC_OLD = "# Orders API\nSynced at: orders-api develop@4ef3776, 2026-11-18\n\n## Problem\n\nSlow.\n"
SPEC_NEW = "# Orders API\nSynced at: orders-api develop@f6aad4d, 2026-11-19\n\n## Problem\n\nSlow.\n"
DRIFT = ("PR 73 merged into develop at f6aad4d on 2026-11-19; Synced at and In the code still say 4ef3776 "
         "and miss three later commits")
WORDING = "diagrams.md Context draws a solid edge to the monitor, but the spec says the monitor does not read the tables"


class Owner(unittest.TestCase):
    def test_code_finding_routes_to_add_to_spec(self):
        root = slice_dir(SPEC_OLD)
        code, out = run(["spec-finding", "--root", str(root), "--id", "P9", "--text", DRIFT])
        self.assertEqual(code, 0)
        self.assertEqual(out["offer"], "jump-back")
        self.assertEqual(out["owner"], "add-to-spec")
        self.assertEqual(out["command"], "/crav1-add-to-spec pr73")
        first = out["options"][0]
        self.assertEqual(first["id"], "add-to-spec")
        self.assertIn("/crav1-add-to-spec", first["label"])
        self.assertIn("/crav1-add-to-spec pr73", first["text"])
        self.assertNotIn("tighten-spec", first["label"] + first["text"])
        self.assertEqual(out["path"], "../crav1-add-to-spec/SKILL.md")
        self.assertEqual(len(out["options"]), 2)

    def test_wording_and_unclear_stay_with_tighten_spec(self):
        root = slice_dir(SPEC_OLD)
        for text, kind in ((WORDING, None), ("the retry limit is stated twice", None), (DRIFT, "spec-text")):
            args = ["spec-finding", "--root", str(root), "--id", "P10", "--text", text]
            if kind:
                args += ["--kind", kind]
            code, out = run(args)
            self.assertEqual(out["owner"], "tighten-spec", text)
            self.assertEqual(out["options"][0]["id"], "tighten-spec")
            self.assertIn("/crav1-tighten-spec", out["options"][0]["label"])

    def test_kind_hint_routes_a_plain_finding(self):
        root = slice_dir(SPEC_OLD)
        code, out = run(["spec-finding", "--root", str(root), "--id", "P4", "--text", "the retry store changed",
                         "--kind", "code-drift", "--branch", "feat/orders-retry"])
        self.assertEqual(out["command"], "/crav1-add-to-spec feat/orders-retry")

    def test_add_to_spec_choice_records_the_jump(self):
        root = slice_dir(SPEC_OLD)
        code, out = run(["spec-finding", "--root", str(root), "--id", "P9", "--text", DRIFT, "--choice", "add-to-spec", "--yes"])
        self.assertEqual(code, 0, out)
        self.assertEqual(out["path"], "../crav1-add-to-spec/SKILL.md")
        text = (root / "walk-progress.md").read_text(encoding="utf-8")
        self.assertIn("../crav1-add-to-spec/SKILL.md", text)
        code, out = run(["resume", "--root", str(root)])
        self.assertEqual(code, 0, out)


class AlreadyFixed(unittest.TestCase):
    def test_covered_finding_has_no_card(self):
        root = slice_dir(SPEC_NEW)
        code, out = run(["spec-finding", "--root", str(root), "--id", "P9", "--text", DRIFT])
        self.assertEqual(out["offer"], "already-fixed")
        self.assertEqual(out["options"], [])
        self.assertIn("f6aad4d", out["note"])
        self.assertIsNone(out["wrote"])
        self.assertFalse((root / "walk-progress.md").exists())

    def test_expect_words_cover_a_wording_finding(self):
        root = slice_dir(SPEC_OLD + "\nThe monitor does not read the audit tables yet.\n")
        code, out = run(["spec-finding", "--root", str(root), "--id", "P10", "--text", WORDING,
                         "--expect", "the monitor does not read the audit tables"])
        self.assertEqual(out["offer"], "already-fixed")

    def test_typed_already_done_with_the_fix_closes(self):
        root = slice_dir(SPEC_NEW)
        code, out = run(["spec-finding", "--root", str(root), "--id", "P9", "--text", DRIFT, "--choice", "already-done", "--yes"])
        self.assertEqual(code, 0, out)
        self.assertEqual(out["recorded"], "already-fixed")
        self.assertIn("Result: already-fixed", (root / "walk-progress.md").read_text(encoding="utf-8"))
        code, out = run(["resume", "--root", str(root)])
        self.assertEqual(code, 0, out)

    def test_typed_already_done_without_the_fix_says_what_is_missing(self):
        root = slice_dir(SPEC_OLD)
        code, out = run(["spec-finding", "--root", str(root), "--id", "P9", "--text", DRIFT, "--choice", "already-done", "--yes"])
        self.assertEqual(out["offer"], "jump-back")
        self.assertIn("f6aad4d", " ".join(out["still_missing"]))
        self.assertIn("does not show P9 fixed", out["message"])
        self.assertFalse((root / "walk-progress.md").exists())


class EarlyOffer(unittest.TestCase):
    def setUp(self):
        self.code = Path(tempfile.mkdtemp()) / "orders-api"
        self.code.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "develop", str(self.code)], check=True)
        shas = []
        for i in range(3):
            (self.code / "app.py").write_text(f"x = {i}\n", encoding="utf-8")
            subprocess.run(GIT + ["-C", str(self.code), "add", "-A"], check=True)
            subprocess.run(GIT + ["-C", str(self.code), "commit", "-q", "-m", f"step {i}"], check=True)
            shas.append(subprocess.run(["git", "-C", str(self.code), "rev-parse", "--short=7", "HEAD"],
                                       capture_output=True, text=True, check=True).stdout.strip())
        self.shas = shas

    def test_behind_offers_add_to_spec_card(self):
        root = slice_dir(f"# Orders API\nSynced at: orders-api develop@{self.shas[0]}, 2026-11-18\n\n## Problem\n")
        code, out = run(["code-drift", "--root", str(root), "--code-repo", str(self.code), "--pr", "73"])
        self.assertEqual(out["offer"], "add-to-spec")
        self.assertEqual(out["drift"][0]["count"], 2)
        self.assertEqual(out["command"], "/crav1-add-to-spec pr73")
        self.assertEqual(len(out["options"]), 2)
        self.assertTrue(out["options"][0]["recommended"])
        self.assertIn("Do not report it as a new finding", out["reviewer_note"])
        self.assertIsNone(out["wrote"])

    def test_current_spec_has_no_offer(self):
        root = slice_dir(f"# Orders API\nSynced at: orders-api develop@{self.shas[-1]}, 2026-11-19\n\n## Problem\n")
        code, out = run(["code-drift", "--root", str(root), "--code-repo", str(self.code), "--merged", self.shas[1]])
        self.assertFalse(out["behind"])
        self.assertIsNone(out["offer"])

    def test_steps_doc_offers_before_the_review(self):
        text = (SKILL / "references/steps.md").read_text(encoding="utf-8")
        self.assertIn("code-drift --root", text)
        self.assertIn("never list that drift as a new item", text)


MSS = ROOT / ".cursor/skills/crav1/crav1-add-to-spec/scripts/merged_since_sync.py"


def mss(args: list[str]) -> dict:
    proc = subprocess.run([sys.executable, str(MSS), *args], capture_output=True, text=True, check=False)
    return json.loads(proc.stdout)


class MergedSinceSync(unittest.TestCase):
    """A base main, a work branch feat/orders-retry with commits, merged with a merge commit (PR 73)."""

    def git(self, *args):
        return subprocess.run(GIT + ["-C", str(self.code), *args], capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, name):
        (self.code / f"{name}.py").write_text(name + "\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", name)
        return self.git("rev-parse", "--short=7", "HEAD")

    def setUp(self):
        self.code = Path(tempfile.mkdtemp()) / "orders-api"
        self.code.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.code)], check=True)
        self.commit("base")
        self.git("checkout", "-q", "-b", "feat/orders-retry")
        self.recorded = self.commit("retry1")
        self.commit("retry2")
        self.commit("retry3")
        self.git("checkout", "-q", "main")
        self.commit("other")
        self.git("merge", "-q", "--no-ff", "feat/orders-retry", "-m", "Merge pull request #73 from contoso/feat/orders-retry")
        self.merge = self.git("rev-parse", "--short=7", "HEAD")
        self.spec = Path(tempfile.mkdtemp()) / "spec.md"

    def write(self, *lines):
        self.spec.write_text("# Orders API\n" + "".join(l + "\n" for l in lines) + "\n## Problem\n", encoding="utf-8")

    def test_merged_offers_one_card(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        out = mss(["check", "--spec", str(self.spec), "--code-repo", str(self.code), "--base", "main"])
        self.assertEqual(out["offer"], "take-in")
        self.assertEqual(out["question"], f"PR 73 merged at {self.merge} with 2 commits the spec hasn't recorded. Take them in now?")
        self.assertEqual(out["command"], "/crav1-add-to-spec pr73")
        self.assertEqual(len(out["options"]), 2)
        self.assertIsNone(out["wrote"])

    def test_headless_only_reports(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        out = mss(["check", "--spec", str(self.spec), "--code-repo", str(self.code), "--base", "main", "--headless"])
        self.assertIsNone(out["offer"])
        self.assertIn("PR 73 merged at", out["report"])

    def test_not_merged(self):
        self.git("checkout", "-q", "-b", "feat/orders-export", self.recorded)
        sha = self.commit("export1")
        self.git("checkout", "-q", "main")
        self.write(f"Synced at: orders-api feat/orders-export@{self.recorded}, 2026-11-18")
        out = mss(["check", "--spec", str(self.spec), "--code-repo", str(self.code), "--base", "main"])
        self.assertEqual(out["status"], "not-merged")
        self.assertIsNone(out["offer"])

    def test_already_synced(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18",
                   f"Synced at: orders-api main@{self.merge}, 2026-11-19")
        out = mss(["check", "--spec", str(self.spec), "--code-repo", str(self.code), "--base", "main"])
        self.assertEqual(out["status"], "already-synced")
        self.assertIsNone(out["offer"])

    def test_default_branch_without_origin_is_skipped(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        out = mss(["check", "--spec", str(self.spec), "--code-repo", str(self.code)])
        self.assertEqual(out["status"], "skipped")

    def test_stamp_needs_yes_then_moves_synced_at(self):
        self.write(f"Synced at: orders-api feat/orders-retry@{self.recorded}, 2026-11-18")
        base = ["stamp", "--spec", str(self.spec), "--repo", "orders-api", "--branch", "feat/orders-retry",
                "--base", "main", "--merge", self.merge, "--date", "2026-11-19"]
        before = self.spec.read_text(encoding="utf-8")
        self.assertFalse(mss(base)["written"])
        self.assertEqual(self.spec.read_text(encoding="utf-8"), before)
        self.assertTrue(mss(base + ["--yes"])["written"])
        text = self.spec.read_text(encoding="utf-8")
        self.assertIn(f"Synced at: orders-api main@{self.merge}, 2026-11-19", text)
        self.assertIn(f"(merged {self.merge})", text)
        out = mss(["check", "--spec", str(self.spec), "--code-repo", str(self.code), "--base", "main"])
        self.assertEqual(out["status"], "already-synced")

    def test_every_caller_runs_the_shared_check(self):
        callers = {
            "walk start": "crav1-tighten-and-plan-ready-to-build/references/steps.md",
            "pr-status": "crav1-pr-status/references/offers.md",
            "sweep manual": "crav1-update-specs-from-changes-and-prs/references/manual-flow.md",
            "sweep auto (headless)": "crav1-update-specs-from-changes-and-prs/references/auto-flow.md",
            "merge-pr": "crav1-merge-pr/references/after-merge.md",
            "build-walk merges": "crav1-build-walk/references/sync.md",
        }
        for who, rel in callers.items():
            text = (ROOT / ".cursor/skills/crav1" / rel).read_text(encoding="utf-8")
            self.assertIn("merged_since_sync.py check --spec", text, who)
            if "auto" in who:
                self.assertIn("--headless", text)
            else:
                self.assertIn("after_yes", text, who)


if __name__ == "__main__":
    unittest.main()
