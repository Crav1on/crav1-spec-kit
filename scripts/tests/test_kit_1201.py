"""1.201.0: the vendor table drives the Cursor and Claude allow-lists with no plan/apply change.

Codex and Copilot are rows in the table and are not installed. Golden plan and apply
output was captured from v1.200.0 on this fixture.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
TABLE = ROOT / ".cursor/skills/crav1/crav1-update-kit/vendors.json"
PREFIX = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/vendor_prefix.py"
ENDING = ROOT / ".cursor/skills/crav1/crav1-finalize-commit/scripts/ending.py"
DRY = ROOT / "scripts/kit_dry_run.py"
GOLDEN = ROOT / "scripts/tests/fixtures"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "-c", "init.defaultBranch=main"]

PATHS = [
    ".cursor/skills/crav1/crav1-help/SKILL.md",
    ".cursor/skills/crav1-other/SKILL.md",
    ".cursor/agents/crav1-spec-reviewer-agent.md",
    ".cursor/agents/crav1-nested/skip.md",
    ".cursor/agents/readme.md",
    ".cursor/agent-assets/README.md",
    ".cursor/agent-assets/crav1-x/prompt.md",
    ".cursor/agent-assets/crav1-note.md",
    ".cursor/agent-assets/other.txt",
    ".cursor/rules/crav1.mdc",
    ".cursor/rules/kit-maintainer.mdc",
    ".claude/skills/crav1-help/SKILL.md",
    ".claude/skills/crav1-docs/reference/workflow.md",
    ".claude/skills/notes/SKILL.md",
    ".claude/skills/crav1-help.md",
    ".claude/agents/crav1-spec-reviewer-agent.md",
    ".claude/agents/crav1-nested/skip.md",
    ".claude/agent-assets/README.md",
    ".claude/agent-assets/crav1-x/a.md",
    ".claude/CLAUDE.md",
    ".claude/CLAUDE.md.bak",
    ".agents/skills/crav1-help/SKILL.md",
    ".github/skills/crav1-help/SKILL.md",
    ".github/instructions/crav1.instructions.md",
    "docs/specs/orders-api/spec.md",
    "README.md",
]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kit = load(SCRIPT, "update_kit_1201")
prefix = load(PREFIX, "vendor_prefix_1201")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture(base: Path):
    """The same Cursor + Claude tree the 1.200 golden was captured from."""
    old, new, proj, home = base / "old", base / "new", base / "proj", base / "home"
    home.mkdir()
    files = {
        ".cursor/skills/crav1/crav1-docs/reference/workflow.md": "Kit version: 1.200.0\n",
        ".cursor/skills/crav1/crav1-help/SKILL.md": "old help\n",
        ".cursor/agents/crav1-spec-reviewer-agent.md": "agent\n",
        ".cursor/agents/crav1-nested/skip.md": "not a kit agent\n",
        ".cursor/agent-assets/README.md": "readme\n",
        ".cursor/agent-assets/crav1-spec-reviewer-agent/prompt.md": "prompt\n",
        ".cursor/agent-assets/other.txt": "not kit\n",
        ".cursor/rules/crav1.mdc": "rule\n",
        ".cursor/rules/kit-maintainer.mdc": "maintainer\n",
        ".claude/skills/crav1-docs/reference/workflow.md": "Kit version: 1.200.0\n",
        ".claude/skills/crav1-help/SKILL.md": "old help\n",
        ".claude/skills/notes/SKILL.md": "not a kit skill\n",
        ".claude/agents/crav1-spec-reviewer-agent.md": "agent\n",
        ".claude/agent-assets/README.md": "readme\n",
        ".claude/agent-assets/crav1-spec-reviewer-agent/prompt.md": "prompt\n",
        ".claude/CLAUDE.md": "claude\n",
        ".agents/skills/crav1-help/SKILL.md": "hand made\n",
        "docs/specs/orders-api/spec.md": "# Orders API\n\nExport orders.\n",
        "README.md": "project readme\n",
    }
    for folder in (old, new, proj):
        for rel, text in files.items():
            write(folder / rel, text)
    write(new / ".cursor/skills/crav1/crav1-help/SKILL.md", "new help\n")
    write(new / ".claude/skills/crav1-help/SKILL.md", "new help\n")
    write(new / ".cursor/skills/crav1/crav1-help/extra.md", "extra\n")
    (new / ".cursor/rules/crav1.mdc").unlink()
    write(new / ".claude/CLAUDE.md", "claude new\n")
    write(new / ".cursor/skills/crav1/crav1-docs/reference/workflow.md", "Kit version: 1.201.0\n")
    write(new / ".claude/skills/crav1-docs/reference/workflow.md", "Kit version: 1.201.0\n")
    write(proj / ".claude/CLAUDE.md", "claude local\n")
    subprocess.run([*G, "init", "-q", str(proj)], check=True)
    subprocess.run([*G, "-C", str(proj), "add", "-A"], check=True)
    subprocess.run([*G, "-C", str(proj), "commit", "-qm", "start"], check=True)
    return old, new, proj, home


def run_kit(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), *args], capture_output=True, text=True)


class Table(unittest.TestCase):
    def test_rows_and_flags(self):
        data = json.loads(TABLE.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 1)
        self.assertEqual(set(data["vendors"]), {"cursor", "claude", "codex", "copilot"})
        for name, row in data["vendors"].items():
            for key in ("prefix", "install", "skills", "tree", "marker", "frontmatter", "extras", "owns"):
                self.assertIn(key, row, name)
            self.assertIsInstance(row["frontmatter"], list)
            self.assertTrue(row["frontmatter"], name)
            self.assertIsInstance(row["extras"], list)
            self.assertIsInstance(row["owns"], list)
        self.assertEqual(data["vendors"]["cursor"]["prefix"], "/")
        self.assertEqual(data["vendors"]["claude"]["prefix"], "/")
        self.assertEqual(data["vendors"]["copilot"]["prefix"], "/")
        self.assertEqual(data["vendors"]["codex"]["prefix"], "$")
        self.assertTrue(data["vendors"]["cursor"]["install"])
        self.assertTrue(data["vendors"]["claude"]["install"])
        self.assertTrue(data["vendors"]["codex"]["install"])
        self.assertFalse(data["vendors"]["copilot"]["install"])
        self.assertEqual(data["vendors"]["cursor"]["marker"], kit.CURSOR_DROPIN_MARKER)
        self.assertEqual(data["vendors"]["claude"]["marker"], kit.CLAUDE_DROPIN_MARKER)
        self.assertIn("icon", data["vendors"]["cursor"]["frontmatter"])
        self.assertNotIn("icon", data["vendors"]["codex"]["frontmatter"])
        self.assertEqual(data["vendors"]["codex"]["extras"], ["<skill>/agents/openai.yaml"])
        self.assertEqual(data["vendors"]["copilot"]["extras"], [".github/instructions/crav1.instructions.md"])

    def test_allow_list_matches_the_1_200_checks(self):
        for path in PATHS:
            self.assertEqual(kit.is_cursor_kit(path), kit._legacy_is_cursor_kit(path), path)
            self.assertEqual(kit.is_claude_kit(path), kit._legacy_is_claude_kit(path), path)
            legacy = kit._legacy_is_cursor_kit(path) or kit._legacy_is_claude_kit(path)
            self.assertEqual(kit.is_kit_path(path), legacy, path)
        self.assertFalse(kit.is_kit_path(".agents/skills/crav1-help/SKILL.md"))
        self.assertFalse(kit.is_kit_path(".github/skills/crav1-help/SKILL.md"))
        self.assertFalse(kit.is_kit_path(".github/instructions/crav1.instructions.md"))

    def test_collect_matches_the_1_200_reader(self):
        base = Path(tempfile.mkdtemp())
        try:
            old, new, proj, _home = fixture(base)
            hosts = {"cursor", "claude"}
            for tree in (old, new, proj):
                self.assertEqual(kit.collect_kit(tree, hosts), kit._legacy_collect_kit(tree, hosts))
            self.assertEqual(kit.collect_kit(proj, {"copilot"}), {})
            self.assertEqual(
                set(kit.collect_kit(proj, {"codex"})),
                {".agents/skills/crav1-help/SKILL.md"},
            )
        finally:
            shutil.rmtree(base, ignore_errors=True)


class GoldenPlanApply(unittest.TestCase):
    def test_plan_and_apply_match_1_200(self):
        base = Path(tempfile.mkdtemp())
        try:
            old, new, proj, home = fixture(base)
            common = ["--root", str(proj), "--home", str(home), "--old", str(old), "--new", str(new)]
            plan = run_kit(["plan", *common, "--to-version", "1.201.0"])
            plan_vendor = run_kit(["plan", *common, "--to-version", "1.201.0", "--vendor", "codex"])
            self.assertEqual(plan.returncode, 0, plan.stderr)
            self.assertEqual(plan_vendor.stdout, plan.stdout)
            got = json.loads(plan.stdout)
            want = json.loads((GOLDEN / "kit-1200-plan.json").read_text(encoding="utf-8"))
            self.assertEqual(got.pop("vendors_from"), "inferred")
            self.assertEqual(got.pop("repo_writes"), 8)
            self.assertTrue(got.pop("card")["commits"])
            self.assertIn(".crav1/kit.json", got["files"]["add"])
            got["files"]["add"].remove(".crav1/kit.json")
            counts = got["files"].get("counts")
            if isinstance(counts, dict):
                counts["add"] -= 1
            self.assertEqual(got, want)
            self.assertNotIn("unchanged", got["files"])
            self.assertEqual(got["files"]["counts"]["unchanged"], 6)
            self.assertFalse(any(
                str(item["path"] if isinstance(item, dict) else item).startswith(".agents/")
                for items in got["files"].values()
                if isinstance(items, list)
                for item in items
            ))
            spec = (proj / "docs/specs/orders-api/spec.md").read_bytes()
            readme = (proj / "README.md").read_bytes()
            handmade = (proj / ".agents/skills/crav1-help/SKILL.md").read_bytes()
            apply = run_kit(["apply", *common, "--yes", "--keep", ".claude/CLAUDE.md"])
            self.assertEqual(apply.returncode, 0, apply.stderr)
            applied = json.loads(apply.stdout)
            want_apply = json.loads((GOLDEN / "kit-1200-apply.json").read_text(encoding="utf-8"))
            self.assertIn(".crav1/kit.json", applied["touched"])
            applied["touched"].remove(".crav1/kit.json")
            self.assertEqual(applied.pop("repo_touched"), 8)
            self.assertEqual(applied.pop("ending_args"), [])
            self.assertEqual(applied, want_apply)
            listed = json.loads((proj / ".crav1/kit.json").read_text(encoding="utf-8"))
            self.assertEqual(listed["vendors"], ["claude", "cursor"])
            self.assertEqual((proj / "docs/specs/orders-api/spec.md").read_bytes(), spec)
            self.assertEqual((proj / "README.md").read_bytes(), readme)
            self.assertEqual((proj / ".agents/skills/crav1-help/SKILL.md").read_bytes(), handmade)
            self.assertEqual((proj / ".claude/CLAUDE.md").read_text(encoding="utf-8"), "claude local\n")
            self.assertFalse((proj / ".cursor/rules/crav1.mdc").exists())
            self.assertEqual((proj / ".cursor/rules/kit-maintainer.mdc").read_text(encoding="utf-8"), "maintainer\n")
        finally:
            shutil.rmtree(base, ignore_errors=True)


class VendorsCommand(unittest.TestCase):
    def test_lists_folder_and_skill_count_and_writes_nothing(self):
        base = Path(tempfile.mkdtemp())
        try:
            root = base / "proj"
            write(root / ".cursor/skills/crav1/crav1-help/SKILL.md", "---\nname: crav1-help\n---\n")
            write(root / ".cursor/skills/crav1/crav1-docs/reference/workflow.md", "Kit version: 1.200.0\n")
            write(root / ".claude/skills/crav1-help/SKILL.md", "---\nname: crav1-help\n---\n")
            write(root / ".claude/skills/crav1-docs/reference/workflow.md", "Kit version: 1.200.0\n")
            before = {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            proc = run_kit(["vendors", "--root", str(root)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            by_name = {row["name"]: row for row in data["vendors"]}
            self.assertEqual(set(by_name), {"claude", "codex", "copilot", "cursor"})
            self.assertEqual(by_name["cursor"]["folder"], ".cursor/skills/crav1")
            self.assertEqual(by_name["cursor"]["skills"], 1)
            self.assertEqual(by_name["claude"]["folder"], ".claude/skills")
            self.assertEqual(by_name["claude"]["skills"], 1)
            self.assertEqual(by_name["codex"]["folder"], ".agents/skills")
            self.assertEqual(by_name["codex"]["skills"], 0)
            self.assertEqual(by_name["copilot"]["skills"], 0)
            after = {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(after, before)
            (base / "empty").mkdir()
            detect = run_kit(["detect", "--root", str(root), "--home", str(base / "empty")])
            self.assertEqual(detect.returncode, 0, detect.stderr)
            info = json.loads(detect.stdout)
            self.assertEqual(info["vendors"], ["claude", "cursor"])
            self.assertEqual(info["vendors_from"], "inferred")
            self.assertEqual(info["mode"], "drop-in")
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def test_copilot_add_writes_nothing(self):
        base = Path(tempfile.mkdtemp())
        try:
            root = base / "proj"
            write(root / "README.md", "project\n")
            write(root / ".agents/skills/crav1-help/SKILL.md", "hand made\n")
            before = (root / ".agents/skills/crav1-help/SKILL.md").read_bytes()
            plan = run_kit(["plan", "--add", "copilot", "--root", str(root)])
            self.assertEqual(plan.returncode, 0, plan.stderr)
            body = json.loads(plan.stdout)
            self.assertTrue(body["project_untouched"])
            self.assertEqual(body["vendors"][0]["added"], [])
            self.assertIn("not installed by this release", body["vendors"][0]["note"])
            self.assertEqual(body["kit_json_op"], "unchanged")
            refused = run_kit(["apply", "--add", "copilot", "--root", str(root)])
            self.assertEqual(refused.returncode, 2)
            self.assertIn("yes", refused.stderr)
            applied = run_kit(["apply", "--add", "copilot", "--yes", "--root", str(root)])
            self.assertEqual(applied.returncode, 0, applied.stderr)
            done = json.loads(applied.stdout)
            self.assertEqual(done["touched"], [])
            self.assertTrue(done["project_untouched"])
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "project\n")
            self.assertEqual((root / ".agents/skills/crav1-help/SKILL.md").read_bytes(), before)
            self.assertFalse((root / ".github").exists())
            self.assertFalse((root / ".crav1/kit.json").exists())
            unknown = run_kit(["plan", "--add", "nope", "--root", str(root)])
            self.assertEqual(unknown.returncode, 2)
            self.assertIn("not a vendor", unknown.stderr)
        finally:
            shutil.rmtree(base, ignore_errors=True)


class VendorPrefix(unittest.TestCase):
    def test_default_is_slash_and_codex_is_dollar(self):
        self.assertEqual(prefix.prefix_for(None), "/")
        self.assertEqual(prefix.prefix_for("cursor"), "/")
        self.assertEqual(prefix.prefix_for("claude"), "/")
        self.assertEqual(prefix.prefix_for("copilot"), "/")
        self.assertEqual(prefix.prefix_for("codex"), "$")
        text = "Run next:\n\nGo on:\n`/crav1-design-architecture orders-platform`\n.cursor/skills/crav1/crav1-help/SKILL.md\n"
        self.assertEqual(prefix.rewrite(text, None), text)
        self.assertEqual(prefix.rewrite(text, "cursor"), text)
        rewritten = prefix.rewrite(text, "codex")
        self.assertIn("`$crav1-design-architecture orders-platform`", rewritten)
        self.assertNotIn("`/crav1-", rewritten)
        self.assertIn(".cursor/skills/crav1/crav1-help/SKILL.md", rewritten)
        with self.assertRaises(SystemExit):
            prefix.prefix_for("nope")

    def test_ending_scripts_print_the_prefix(self):
        root = Path(tempfile.mkdtemp())
        try:
            (root / "docs/architecture/designs/orders-platform").mkdir(parents=True)
            (root / "docs/architecture/designs/orders-platform/goal.md").write_text(
                "# Goal\n\nStatus: open\n", encoding="utf-8")
            plain = run_kit(["ending", "--root", str(root)])
            codex = run_kit(["ending", "--root", str(root), "--vendor", "codex"])
            cursor = run_kit(["ending", "--root", str(root), "--vendor", "cursor"])
            self.assertEqual(plain.returncode, 0, plain.stderr)
            self.assertIn("`/crav1-design-architecture orders-platform`", plain.stdout)
            self.assertEqual(cursor.stdout, plain.stdout)
            self.assertIn("`$crav1-design-architecture orders-platform`", codex.stdout)
            self.assertNotIn("`/crav1-", codex.stdout)
            self.assertIn("`Developer: Reload Window`", plain.stdout)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_finalize_commit_ending_accepts_vendor(self):
        def ending(vendor: list[str]) -> str:
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", str(ENDING), "--feature", *vendor],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            return proc.stdout
        plain = ending([])
        self.assertIn("`/crav1-open-pr`", plain)
        self.assertEqual(ending(["--vendor", "claude"]), plain)
        codex = ending(["--vendor", "codex"])
        self.assertIn("`$crav1-open-pr`", codex)
        self.assertNotIn("`/crav1-", codex)

    def test_codex_ending_still_passes_the_run_next_check(self):
        run_ending = load(ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build/scripts/run_ending.py", "run_ending_1201")
        text = prefix.rewrite(
            "Run next:\nThe commit is only local and no pull request is open.\n\n"
            "Push and open the pull request:\n`/crav1-open-pr`\n",
            "codex",
        )
        self.assertEqual(run_ending.check_ending(text), [])
        self.assertIn("`$crav1-open-pr`", text)


class PlanSummary(unittest.TestCase):
    def test_counts_by_kind_and_at_most_ten_paths(self):
        dry = load(DRY, "kit_dry_run_1201")
        files = {kind: [] for kind in ("update", "add", "merge", "delete", "clash", "left_extra")}
        files["update"] = [f".cursor/skills/crav1/crav1-docs/n{i}.md" for i in range(12)]
        files["add"] = [".cursor/skills/crav1/crav1-help/extra.md"]
        files["counts"] = {
            "update": 12,
            "add": 1,
            "merge": 0,
            "delete": 0,
            "clash": 0,
            "left_extra": 0,
            "unchanged": 30,
        }
        payload = json.dumps({"files": files})
        text = dry._plan_summary(0, payload)
        self.assertIn("unchanged 30", text)
        self.assertIn("update 12", text)
        self.assertIn("add 1", text)
        self.assertNotIn("f0.md", text)
        self.assertIn("… and 3 more", text)
        shown = [line for line in text.splitlines() if line.startswith(".cursor/")]
        self.assertEqual(len(shown), 10)


if __name__ == "__main__":
    unittest.main()
