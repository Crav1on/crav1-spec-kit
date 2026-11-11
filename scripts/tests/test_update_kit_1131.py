"""1.131.0: /crav1-update-kit overlay. Published tags only, three-way merge, no project writes, no push."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"


def load():
    spec = importlib.util.spec_from_file_location("update_kit_1131", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit = load()


def run_cli(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def marker(root: Path, version: str) -> None:
    write(
        root / ".cursor/skills/crav1/crav1-docs/reference/workflow.md",
        f"# Workflow\n\nKit version: {version}\n",
    )


def project_files(root: Path) -> None:
    write(root / "docs/specs/orders-retry/walk-progress.md", "position only\n")
    write(root / "docs/specs/orders-retry/spec.md", "spec stays\n")
    write(root / "docs/specs/orders-retry/plan.md", "plan stays\n")
    write(root / "docs/specs/orders-retry/tasks.md", "tasks stay\n")
    write(root / "docs/specs/orders-retry/build-map.md", "map stays\n")
    write(root / "docs/notes/2026-11/note.md", "note stays\n")
    write(root / "docs/playbooks/orders.md", "playbook stays\n")
    write(root / "docs/system/landscape.md", "landscape stays\n")
    write(root / ".cursor/rules/draft-commit-style.mdc", "style stays\n")
    write(root / ".cursor/rules/crav1-transfer-data-policy.mdc", "policy stays\n")
    write(root / "AGENTS.md", "a consumer project\n")


PROJECT_PATHS = [
    "docs/specs/orders-retry/walk-progress.md",
    "docs/specs/orders-retry/spec.md",
    "docs/specs/orders-retry/plan.md",
    "docs/specs/orders-retry/tasks.md",
    "docs/specs/orders-retry/build-map.md",
    "docs/notes/2026-11/note.md",
    "docs/playbooks/orders.md",
    "docs/system/landscape.md",
    ".cursor/rules/draft-commit-style.mdc",
    ".cursor/rules/crav1-transfer-data-policy.mdc",
    "AGENTS.md",
]


def git_init(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "kit@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Kit Test"], cwd=root, check=True)


class VersionsAndTargets(unittest.TestCase):
    def test_version_from_workflow_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker(root, "1.129.0")
            info = kit.detect(root, Path(tmp) / "empty-home")
        self.assertEqual(info["mode"], "drop-in")
        self.assertEqual(info["version"], "1.129.0")
        self.assertEqual(info["version_from"], "workflow.md")
        self.assertTrue(info["writes_kit_files"])

    def test_version_from_plugin_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            plugin = home / ".cursor/plugins/local/crav1/.cursor-plugin/plugin.json"
            write(plugin, json.dumps({"name": "crav1", "version": "1.120.0"}))
            root = Path(tmp) / "repo"
            root.mkdir()
            info = kit.detect(root, home)
        self.assertEqual(info["mode"], "plugin")
        self.assertEqual(info["version"], "1.120.0")
        self.assertEqual(info["version_from"], "plugin.json")
        self.assertFalse(info["writes_kit_files"])

    def test_changelog_marker_when_workflow_line_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".cursor/skills/crav1/crav1-docs/reference/workflow.md",
                "# Workflow\n\nNo stamp here.\n",
            )
            write(root / ".cursor/skills/crav1/crav1-docs/CHANGELOG.md", "## 1.128.0 (2026-11-10)\n")
            info = kit.detect(root, Path(tmp) / "empty-home")
        self.assertEqual(info["version"], "1.128.0")
        self.assertEqual(info["version_from"], "CHANGELOG.md")

    def test_kit_source_checkout_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".cursor/rules/kit-maintainer.mdc", "maintainer\n")
            write(
                root / "plugins/crav1/.cursor-plugin/plugin.json",
                json.dumps({"name": "crav1", "version": "1.131.0"}),
            )
            marker(root, "1.131.0")
            result = run_cli(["plan", "--root", str(root), "--old", str(root), "--new", str(root)])
        self.assertEqual(result.returncode, 2)
        self.assertIn("kit source", result.stderr)
        self.assertNotIn("\n", result.stderr.strip())

    def test_latest_published_tag(self):
        tags = kit.published_tags("aaaa\trefs/tags/v1.2.0\nbbbb\trefs/tags/v1.10.0\ncccc\trefs/tags/v1.9.0\n")
        resolved = kit.resolve_target(None, tags)
        self.assertEqual(resolved["tag"], "v1.10.0")
        self.assertTrue(resolved["latest"])

    def test_explicit_published_tag(self):
        tags = kit.published_tags("v1.129.0\nv1.128.0\n")
        resolved = kit.resolve_target(kit.normalize_request("to v1.128.0"), tags)
        self.assertEqual(resolved["tag"], "v1.128.0")
        self.assertFalse(resolved["latest"])

    def test_refuses_main_branch_pr_sha_and_unpublished(self):
        tags = kit.published_tags("v1.129.0\n")
        cases = {
            "main": "not a published release tag",
            "develop": "not a published release tag",
            "cursor/question-card-free-text-f412": "is a branch",
            "205": "open pull request",
            "#205": "open pull request",
            "pr 205": "open pull request",
            "abcdef1": "a commit",
            "v1.130.0": "v1.130.0 is not a published release tag",
        }
        for raw, snippet in cases.items():
            with self.subTest(raw=raw):
                with self.assertRaises(kit.Refuse) as caught:
                    kit.resolve_target(kit.normalize_request(raw), tags)
                self.assertIn(snippet, caught.exception.message)
                self.assertNotIn("\n", caught.exception.message)

    def test_fetch_refuses_a_branch_without_cloning(self):
        result = run_cli(["fetch", "--tag", "main", "--dest", "/tmp/crav1-update-kit-should-not-exist"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a published release tag", result.stderr)
        self.assertFalse(Path("/tmp/crav1-update-kit-should-not-exist").exists())

    def test_fetch_clones_with_autocrlf_off(self):
        dest = Path(tempfile.mkdtemp()) / "release"
        with patch("subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0)
            kit.fetch_release("v1.131.0", dest, "https://example.invalid/kit.git")
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[0], "git")
        self.assertIn("-c", cmd)
        self.assertIn("core.autocrlf=false", cmd)
        self.assertIn("clone", cmd)


class Overlay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / "repo"
        self.old = self.base / "old"
        self.new = self.base / "new"
        self.root.mkdir()
        self.old.mkdir()
        self.new.mkdir()
        marker(self.root, "1.100.0")
        marker(self.old, "1.100.0")
        marker(self.new, "1.110.0")
        project_files(self.root)
        self.before = {path: (self.root / path).read_bytes() for path in PROJECT_PATHS}

    def tearDown(self):
        self.tmp.cleanup()

    def test_non_overlapping_edits_merge_and_a_clash_keeps_both_sides(self):
        rel = ".cursor/skills/crav1/crav1-example/SKILL.md"
        old = "alpha\nbeta\ngamma\n"
        local = "alpha local\nbeta local\ngamma\n"
        new = "alpha\nbeta kit\ngamma new\n"
        write(self.old / rel, old)
        write(self.root / rel, local)
        write(self.new / rel, new)
        merged = kit.merge_text(old, local, new)
        self.assertEqual(merged["status"], "clash")
        self.assertIn("beta local", merged["hunks"][0]["local"])
        self.assertIn("beta kit", merged["hunks"][0]["kit"])
        self.assertEqual(merged["keep_text"], "alpha local\nbeta local\ngamma new\n")
        self.assertEqual(merged["take_text"], "alpha local\nbeta kit\ngamma new\n")
        clean_old = "one\ntwo\nthree\n"
        clean = kit.merge_text(clean_old, "one local\ntwo\nthree\n", "one\ntwo\nthree new\n")
        self.assertEqual(clean["status"], "merged")
        self.assertEqual(clean["text"], "one local\ntwo\nthree new\n")

    def test_apply_merges_and_resolves_a_clash_without_touching_project_files(self):
        clean = ".cursor/rules/crav1.mdc"
        clash = ".cursor/skills/crav1/crav1-example/SKILL.md"
        write(self.old / clean, "rule\n")
        write(self.root / clean, "rule\n")
        write(self.new / clean, "rule new\n")
        write(self.old / clash, "alpha\nbeta\ngamma\n")
        write(self.root / clash, "alpha local\nbeta local\ngamma\n")
        write(self.new / clash, "alpha\nbeta kit\ngamma new\n")
        refused = run_cli(
            ["apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new), "--keep", clash]
        )
        self.assertEqual(refused.returncode, 2)
        self.assertIn("needs a yes", refused.stderr)
        self.assertEqual((self.root / clean).read_text(encoding="utf-8"), "rule\n")
        applied = run_cli(
            [
                "apply",
                "--root",
                str(self.root),
                "--old",
                str(self.old),
                "--new",
                str(self.new),
                "--yes",
                "--keep",
                clash,
            ]
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual((self.root / clean).read_text(encoding="utf-8"), "rule new\n")
        self.assertEqual((self.root / clash).read_text(encoding="utf-8"), "alpha local\nbeta local\ngamma new\n")
        for path in PROJECT_PATHS:
            self.assertEqual((self.root / path).read_bytes(), self.before[path], path)
        taken = run_cli(
            [
                "apply",
                "--root",
                str(self.root),
                "--old",
                str(self.old),
                "--new",
                str(self.new),
                "--yes",
                "--take",
                clash,
            ]
        )
        self.assertEqual(taken.returncode, 0, taken.stderr)
        self.assertIn("beta kit", (self.root / clash).read_text(encoding="utf-8"))
        self.assertIn("alpha local", (self.root / clash).read_text(encoding="utf-8"))
        for path in PROJECT_PATHS:
            self.assertEqual((self.root / path).read_bytes(), self.before[path], path)

    def test_line_endings_alone_are_an_update_and_the_write_keeps_local_lf(self):
        rel = ".cursor/skills/crav1/crav1-example/SKILL.md"
        (self.old / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.old / rel).write_bytes(b"alpha\r\nbeta\r\n")
        (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.root / rel).write_bytes(b"alpha\nbeta\n")
        (self.new / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.new / rel).write_bytes(b"alpha\r\nbeta kit\r\n")
        plan = json.loads(run_cli(
            ["plan", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new)]
        ).stdout)
        self.assertIn(rel, plan["files"]["update"])
        self.assertNotIn(rel, [item["path"] for item in plan["files"]["clash"]])
        applied = run_cli(
            ["apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new), "--yes"]
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        written = (self.root / rel).read_bytes()
        self.assertEqual(written, b"alpha\nbeta kit\n")
        self.assertNotIn(b"\r", written)

    def test_a_real_edit_still_clashes_when_line_endings_differ(self):
        rel = ".cursor/skills/crav1/crav1-example/SKILL.md"
        (self.old / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.old / rel).write_bytes(b"alpha\r\nbeta\r\ngamma\r\n")
        (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.root / rel).write_bytes(b"alpha local\nbeta local\ngamma\n")
        (self.new / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.new / rel).write_bytes(b"alpha\r\nbeta kit\r\ngamma new\r\n")
        plan = json.loads(run_cli(
            ["plan", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new)]
        ).stdout)
        clashes = {item["path"]: item for item in plan["files"]["clash"]}
        self.assertIn(rel, clashes)
        blob = json.dumps(clashes[rel]["hunks"])
        self.assertIn("beta local", blob)
        self.assertIn("beta kit", blob)
        applied = run_cli(
            [
                "apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new),
                "--yes", "--keep", rel,
            ]
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        written = (self.root / rel).read_bytes()
        self.assertEqual(written, b"alpha local\nbeta local\ngamma new\n")
        self.assertNotIn(b"\r", written)

    def test_template_updates_only_when_it_still_matches_the_old_kit(self):
        rel_same = "docs/specs/_template/spec.md"
        rel_edit = "docs/system/_template/landscape.md"
        write(self.old / rel_same, "template\n")
        write(self.root / rel_same, "template\n")
        write(self.new / rel_same, "template new\n")
        write(self.old / rel_edit, "landscape\n")
        write(self.root / rel_edit, "landscape local\n")
        write(self.new / rel_edit, "landscape new\n")
        result = run_cli(
            ["apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new), "--yes"]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / rel_same).read_text(encoding="utf-8"), "template new\n")
        self.assertEqual((self.root / rel_edit).read_text(encoding="utf-8"), "landscape local\n")
        plan = json.loads(
            run_cli(["plan", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new)]).stdout
        )
        self.assertIn(rel_edit, [item["path"] for item in plan["templates"]["left"]])

    def test_new_template_is_not_copied_into_a_project_that_never_had_it(self):
        write(self.new / "docs/specs/_template/extra.md", "new only\n")
        result = run_cli(
            ["apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new), "--yes"]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "docs/specs/_template/extra.md").exists())

    def test_removed_unedited_kit_file_is_deleted_and_a_local_extra_stays(self):
        gone = ".cursor/skills/crav1/crav1-old/SKILL.md"
        extra = ".cursor/skills/crav1/local-notes.md"
        write(self.old / gone, "old skill\n")
        write(self.root / gone, "old skill\n")
        write(self.root / extra, "project note inside the kit tree\n")
        result = run_cli(
            ["apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new), "--yes"]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / gone).exists())
        self.assertEqual((self.root / extra).read_text(encoding="utf-8"), "project note inside the kit tree\n")

    def test_commit_uses_the_kit_message_and_leaves_project_files_unstaged(self):
        git_init(self.root)
        write(self.root / ".cursor/rules/crav1.mdc", "rule\n")
        subprocess.run(["git", "add", "--", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "start"], cwd=self.root, check=True)
        write(self.old / ".cursor/rules/crav1.mdc", "rule\n")
        write(self.new / ".cursor/rules/crav1.mdc", "rule new\n")
        write(self.root / "docs/specs/orders-retry/spec.md", "spec edited during a walk\n")
        applied = run_cli(
            ["apply", "--root", str(self.root), "--old", str(self.old), "--new", str(self.new), "--yes"]
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        no = run_cli(["commit", "--root", str(self.root), "--from-version", "1.100.0", "--to-version", "1.110.0"])
        self.assertEqual(no.returncode, 2)
        self.assertIn("needs a yes", no.stderr)
        yes = run_cli(
            [
                "commit",
                "--root",
                str(self.root),
                "--from-version",
                "1.100.0",
                "--to-version",
                "1.110.0",
                "--yes",
            ]
        )
        self.assertEqual(yes.returncode, 0, yes.stderr)
        payload = json.loads(yes.stdout)
        self.assertEqual(payload["message"], "Update CRAV1 kit v1.100.0 to v1.110.0")
        self.assertIn("docs/specs/orders-retry/spec.md", payload["left_uncommitted"])
        subject = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(subject, "Update CRAV1 kit v1.100.0 to v1.110.0")
        names = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn(".cursor/rules/crav1.mdc", names)
        self.assertNotIn("walk-progress.md", names)
        self.assertNotIn("spec.md", names)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("docs/specs/orders-retry/spec.md", status)


class PluginAndMigrations(unittest.TestCase):
    def test_plugin_plan_writes_nothing_and_advises(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            home = base / "home"
            root = base / "repo"
            plugin = home / ".cursor/plugins/local/crav1/.cursor-plugin/plugin.json"
            write(plugin, json.dumps({"name": "crav1", "version": "1.120.0"}))
            write(root / "docs/specs/orders-retry/walk-progress.md", "position only\n")
            before = (root / "docs/specs/orders-retry/walk-progress.md").read_bytes()
            result = run_cli(
                ["plan", "--root", str(root), "--home", str(home), "--to-version", "v1.129.0"]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "plugin")
            self.assertFalse(payload["writes_kit_files"])
            self.assertIn("not updated by a commit", payload["advice"])
            self.assertIn("v1.129.0", payload["advice"])
            self.assertEqual((root / "docs/specs/orders-retry/walk-progress.md").read_bytes(), before)
            apply = run_cli(["apply", "--root", str(root), "--home", str(home), "--yes"])
            self.assertEqual(apply.returncode, 2)
            self.assertIn("plugin install", apply.stderr)
            self.assertEqual((root / "docs/specs/orders-retry/walk-progress.md").read_bytes(), before)

    def test_migration_dry_run_lists_the_jump_and_writes_nothing_until_yes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / ".cursor/skills/crav1/fake/migrate.py"
            write(
                script,
                "\n".join(
                    [
                        "import sys",
                        "from pathlib import Path",
                        "root = Path(sys.argv[sys.argv.index('--root') + 1])",
                        "if '--dry-run' in sys.argv:",
                        "    print('would rewrite docs/specs/orders-retry/spec.md')",
                        "    raise SystemExit(0)",
                        "(root / 'docs/specs/orders-retry').mkdir(parents=True, exist_ok=True)",
                        "(root / 'docs/specs/orders-retry/spec.md').write_text('migrated\\n', encoding='utf-8')",
                        "(root / 'migration-applied').write_text('yes\\n', encoding='utf-8')",
                        "",
                    ]
                ),
            )
            write(root / "docs/specs/orders-retry/spec.md", "spec stays\n")
            write(root / "docs/specs/orders-retry/walk-progress.md", "position only\n")
            registry = root / "migrations.json"
            write(
                registry,
                json.dumps(
                    {
                        "migrations": [
                            {
                                "id": "sample-formats",
                                "below": "1.97.0",
                                "at_least": "1.84.0",
                                "summary": "Sample format step for a consumer project.",
                                "script": "fake/migrate.py",
                            }
                        ]
                    }
                ),
            )
            skipped = kit.select_migrations(kit.load_migrations(registry), "1.129.0", "1.131.0")
            self.assertEqual(skipped, [])
            chosen = kit.select_migrations(kit.load_migrations(registry), "1.80.0", "1.100.0")
            self.assertEqual([item["id"] for item in chosen], ["sample-formats"])
            dry = run_cli(
                [
                    "migrations",
                    "--root",
                    str(root),
                    "--migrations",
                    str(registry),
                    "--from-version",
                    "1.80.0",
                    "--to-version",
                    "1.100.0",
                ]
            )
            self.assertEqual(dry.returncode, 0, dry.stderr)
            payload = json.loads(dry.stdout)
            self.assertEqual(payload["migrations"][0]["id"], "sample-formats")
            self.assertIn("would rewrite", payload["migrations"][0]["output"])
            self.assertFalse(payload["migrations"][0]["applied"])
            self.assertEqual((root / "docs/specs/orders-retry/spec.md").read_text(encoding="utf-8"), "spec stays\n")
            self.assertFalse((root / "migration-applied").exists())
            no = run_cli(
                [
                    "migrations",
                    "--root",
                    str(root),
                    "--migrations",
                    str(registry),
                    "--from-version",
                    "1.80.0",
                    "--to-version",
                    "1.100.0",
                    "--apply",
                ]
            )
            self.assertEqual(no.returncode, 2)
            self.assertIn("needs a yes", no.stderr)
            self.assertFalse((root / "migration-applied").exists())
            yes = run_cli(
                [
                    "migrations",
                    "--root",
                    str(root),
                    "--migrations",
                    str(registry),
                    "--from-version",
                    "1.80.0",
                    "--to-version",
                    "1.100.0",
                    "--apply",
                    "--yes",
                ]
            )
            self.assertEqual(yes.returncode, 0, yes.stderr)
            self.assertTrue((root / "migration-applied").is_file())
            self.assertEqual(
                (root / "docs/specs/orders-retry/walk-progress.md").read_text(encoding="utf-8"),
                "position only\n",
            )

    def test_migration_that_mentions_walk_progress_is_not_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / ".cursor/skills/crav1/fake/migrate.py"
            write(
                script,
                "\n".join(
                    [
                        "import sys",
                        "print('would edit docs/specs/orders-retry/walk-progress.md')",
                        "if '--dry-run' not in sys.argv:",
                        "    raise SystemExit('should not apply')",
                        "",
                    ]
                ),
            )
            write(root / "docs/specs/orders-retry/walk-progress.md", "position only\n")
            registry = root / "migrations.json"
            write(
                registry,
                json.dumps(
                    {
                        "migrations": [
                            {
                                "id": "bad",
                                "below": "2.0.0",
                                "at_least": "1.0.0",
                                "summary": "bad",
                                "script": "fake/migrate.py",
                            }
                        ]
                    }
                ),
            )
            result = run_cli(
                [
                    "migrations",
                    "--root",
                    str(root),
                    "--migrations",
                    str(registry),
                    "--from-version",
                    "1.0.0",
                    "--to-version",
                    "1.1.0",
                    "--apply",
                    "--yes",
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["migrations"][0]["blocked"])
            self.assertFalse(payload["migrations"][0]["applied"])
            self.assertEqual(
                (root / "docs/specs/orders-retry/walk-progress.md").read_text(encoding="utf-8"),
                "position only\n",
            )

    def test_shipped_registry_covers_the_merge_safe_jump_only(self):
        registry = SCRIPT.parent.parent / "migrations.json"
        items = kit.load_migrations(registry)
        self.assertEqual(
            [item["id"] for item in kit.select_migrations(items, "1.80.0", "1.100.0")],
            ["merge-safe-formats"],
        )
        self.assertEqual(kit.select_migrations(items, "1.129.0", "1.131.0"), [])
        self.assertEqual(items[0]["script"], "crav1-add-to-spec/scripts/merge_safe_migrate.py")


class NoPush(unittest.TestCase):
    def test_the_script_has_no_push_command(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("git push", text)
        self.assertNotIn('["git", "push"', text)
        self.assertNotIn("git', 'push'", text)
        result = run_cli(["push"])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr.strip(), "Refused: this script does not push.")
        again = run_cli(["--push"])
        self.assertEqual(again.returncode, 2)
        self.assertIn("does not push", again.stderr)


if __name__ == "__main__":
    unittest.main()
