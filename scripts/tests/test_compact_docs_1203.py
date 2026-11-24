"""1.203.0: compact crav1-docs for installed skills, human pages stay in docs/.

Generic names only. The bundle is what an install reads. docs/ stays the human edition.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/gen-compact-docs.py"
SK = ROOT / ".cursor/skills/crav1"
BUNDLES = (
    SK / "crav1-docs",
    ROOT / "plugins/crav1/skills/crav1-docs",
    ROOT / ".claude/skills/crav1-docs",
)
CITE = re.compile(r"crav1-docs/([A-Za-z0-9_./-]+\.(?:md|yaml|yml))")
DROPPED = re.compile(
    r"crav1-docs/(?:proposals|specs|system|notes)/|crav1-docs/reference/(?:skills|marks)\.yaml"
)


def load():
    spec = importlib.util.spec_from_file_location("gen_compact_docs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class CompactDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()
        cls.files, cls.llms = cls.mod.build()

    def test_nine_rule_files_match_the_human_pages_by_hash(self):
        self.assertEqual(len(self.mod.VERBATIM), 9)
        for rel in self.mod.VERBATIM:
            source = (ROOT / "docs" / rel).read_text(encoding="utf-8")
            digest = sha(source)
            self.assertEqual(sha(self.files[rel]), digest, rel)
            for bundle in BUNDLES:
                got = (bundle / rel).read_text(encoding="utf-8")
                self.assertEqual(sha(got), digest, f"{bundle.name} {rel}")

    def test_every_skill_choice_and_next_step_is_in_the_bundle(self):
        problems = self.mod.coverage_problems(self.files, self.llms)
        self.assertEqual(problems, [], "\n".join(problems[:20]))

    def test_human_links_name_real_docs_files(self):
        ver = self.mod.version()
        for rel, text in self.files.items():
            if not rel.endswith(".md") or rel in self.mod.VERBATIM or rel == "CHANGELOG.md":
                continue
            link = self.mod.human(rel, ver)
            self.assertTrue(text.rstrip().endswith(link), rel)
            self.assertTrue((ROOT / "docs" / rel).is_file(), rel)

    def test_generator_sources_and_human_only_folders_are_absent(self):
        for rel in ("reference/skills.yaml", "reference/marks.yaml"):
            self.assertNotIn(rel, self.files)
        for rel in self.files:
            top = rel.split("/", 1)[0]
            self.assertNotIn(top, self.mod.DROP_DIRS, rel)

    def test_size_budget_is_under_the_source_copy(self):
        before = self.mod.source_tokens()
        after = self.mod.bundle_tokens(self.files)
        self.assertLess(after, before, f"before {before} after {after}")
        self.assertLessEqual(after, self.mod.TOKEN_BUDGET, f"after {after}")
        self.assertLess(after, before * self.mod.TOKEN_RATIO, f"before {before} after {after}")

    def test_tighten_spec_keeps_thresholds_and_drops_version_stamps(self):
        page = self.files["reference/skills/crav1-tighten-spec.md"]
        self.assertIn("more than 8", page)
        self.assertIn("batch_offer.py", page)
        self.assertIn("mark-dropped", page)
        self.assertIn("you run next: /crav1-resolve-open-questions", page)
        self.assertNotRegex(page, r"(?m)^\d+\.\d+\.\d+:")
        self.assertIn("## Choice words", self.files["reference/skills/crav1-ado-sync.md"])

    def test_renamed_skills_table_stays(self):
        readme = self.files["README.md"]
        self.assertIn("| `/crav1-implement-task`", readme)
        self.assertIn("`one-task`", readme)

    def test_cited_bundle_paths_still_exist(self):
        roots = [p for p in SK.iterdir() if p.is_dir() and p.name != "crav1-docs"]
        roots.append(ROOT / ".cursor/agents")
        roots.append(ROOT / ".cursor/rules")
        missing = []
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".md", ".mdc"}:
                    continue
                text = path.read_text(encoding="utf-8")
                for match in CITE.finditer(text):
                    rel = match.group(1)
                    if rel not in self.files:
                        missing.append(f"{path.relative_to(ROOT)} -> {rel}")
                for line in text.splitlines():
                    if DROPPED.search(line) and not re.search(r"do not read|never read|not read", line, re.I):
                        missing.append(f"{path.relative_to(ROOT)} reads a dropped path: {line.strip()[:160]}")
        self.assertEqual(missing, [], "\n".join(missing[:20]))

    def test_llms_txt_indexes_the_human_docs(self):
        self.assertTrue(self.llms.startswith("# CRAV1 Spec Kit\n"))
        self.assertIn("\n> ", self.llms)
        self.assertIn("\n## Optional\n", self.llms)
        self.assertIn("docs/proposals/multi-vendor.md", self.llms)
        self.assertNotIn("docs/proposals/multi-vendor.md", "\n".join(self.files))
        disk = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertEqual(disk, self.llms)

    def test_committed_copies_match_the_generator(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
