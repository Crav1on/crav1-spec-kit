"""1.206.0: per-repo early-access flags. No flag file matches today's plan and apply."""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPDATE = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/update_kit.py"
FLAGS = ROOT / ".cursor/skills/crav1/crav1-update-kit/scripts/flags.py"
DRY = ROOT / "scripts/kit_dry_run.py"
G = ["git", "-c", "user.name=person A", "-c", "user.email=a@example.com", "-c", "init.defaultBranch=main"]
MALFORMED = "Flags file .crav1/flags.local.json is not readable; continuing with no flags."
MARKER = ".cursor/skills/crav1/crav1-docs/reference/workflow.md"


def load(path: Path, name: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit = load(UPDATE, "update_kit_1206")
dry = load(DRY, "kit_dry_run_1206")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_kit(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess[str]:
    merged = dict(os.environ, PYTHONUTF8="1")
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(UPDATE), *args],
        capture_output=True,
        text=True,
        env=merged,
    )


def git_init(root: Path) -> None:
    subprocess.run([*G, "init", "-q", str(root)], check=True)
    subprocess.run([*G, "-C", str(root), "add", "-A"], check=True)
    subprocess.run([*G, "-C", str(root), "commit", "-qm", "start"], check=True)


def tree_files(root: Path) -> dict[str, bytes]:
    out = {}
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        out[path.relative_to(root).as_posix()] = path.read_bytes()
    return out


def seed_kit(folder: Path, version: str) -> None:
    write(folder / MARKER, f"Kit version: {version}\n")
    write(folder / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["cursor"]}, indent=2) + "\n")


def expected_plan(root: Path, old: Path, new: Path, home: Path, target: str) -> str:
    info = kit.detect(root, home)
    hosts = kit.hosts_for_update(root, info)
    actions = kit.build_actions(root, old, new, hosts)
    names, source = kit.read_selection(root)
    kit.ensure_kit_json(root, actions, sorted(hosts) if source == "inferred" else names)
    view = kit.plan_view(info, actions, target)
    view["vendors_from"] = source
    registry = kit.migration_registry(new, None)
    if registry and registry.is_file() and info.get("version") and target:
        view["migration_ids"] = [
            item["id"]
            for item in kit.select_migrations(kit.load_migrations(registry), info["version"], target.lstrip("v"))
        ]
    else:
        view["migration_ids"] = []
    return json.dumps(view, indent=2, sort_keys=True) + "\n"


class NoFlagFile(unittest.TestCase):
    def test_plan_and_apply_match_today_and_files_match(self):
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, True)
        home = base / "home"
        home.mkdir()
        old, new = base / "old", base / "new"
        seed_kit(old, "1.204.0")
        seed_kit(new, "1.204.0")
        write(new / MARKER, "Kit version: 1.205.0\n")
        spec = "docs/specs/orders-api/spec.md"
        for name in ("a", "b"):
            root = base / name
            seed_kit(root, "1.204.0")
            write(root / spec, "Orders for partner B.\n")
            write(root / ".gitignore", "build/\n")
        target = "1.205.0"
        plan = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", target,
            "--root", str(base / "a"), "--home", str(home),
        ])
        self.assertEqual(plan.returncode, 0, plan.stderr)
        self.assertEqual(plan.stderr, "")
        expected = expected_plan(base / "a", old, new, home, target)
        self.assertEqual(plan.stdout.encode(), expected.encode())
        self.assertNotIn("kit2", plan.stdout)
        self.assertNotIn("flag", plan.stdout.lower())
        before = tree_files(base / "a")
        applied = run_kit([
            "apply", "--old", str(old), "--new", str(new), "--yes",
            "--root", str(base / "a"), "--home", str(home),
        ])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(applied.stderr, "")
        other = base / "b"
        info = kit.detect(other, home)
        hosts = kit.hosts_for_update(other, info)
        names, source = kit.read_selection(other)
        result = kit.apply_overlay(
            other, old, new, hosts, True, set(), set(),
            sorted(hosts) if source == "inferred" else names,
        )
        self.assertEqual(applied.stdout.encode(), (json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
        self.assertEqual(tree_files(base / "a"), tree_files(other))
        self.assertEqual((base / "a" / spec).read_bytes(), before[spec])
        self.assertEqual((base / "a" / ".gitignore").read_bytes(), before[".gitignore"])
        self.assertEqual((base / "a" / MARKER).read_text(encoding="utf-8"), "Kit version: 1.205.0\n")
        self.assertFalse((home / ".crav1-2").exists())


class FlagWords(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base, True)
        self.root = self.base / "proj"
        self.home = self.base / "home"
        self.home.mkdir()
        self.root.mkdir()
        write(self.root / ".gitignore", "build/\n")
        git_init(self.root)
        self.ignore_before = (self.root / ".gitignore").read_bytes()

    def test_on_off_and_list(self):
        on = run_kit(["flags-on", "kit2", "--root", str(self.root), "--home", str(self.home)])
        self.assertEqual(on.returncode, 0, on.stderr)
        self.assertEqual(on.stderr, "")
        body = json.loads(on.stdout)
        self.assertEqual(body["line"], "kit2: off -> on")
        self.assertEqual(body["wrote"], [".crav1/.gitignore", ".crav1/flags.local.json"])
        stored = json.loads((self.root / ".crav1/flags.local.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, {"kit2": True})
        ignore = (self.root / ".crav1/.gitignore").read_text(encoding="utf-8")
        self.assertIn("flags.local.json\n", ignore)
        self.assertEqual((self.root / ".gitignore").read_bytes(), self.ignore_before)
        listed = run_kit(["flags-list", "--root", str(self.root)])
        self.assertEqual(listed.returncode, 0, listed.stderr)
        shown = json.loads(listed.stdout)
        self.assertTrue(shown["registry"][0]["on"])
        self.assertEqual(shown["registry"][0]["name"], "kit2")
        self.assertEqual(shown["registry"][0]["status"], "experimental")
        off = run_kit(["flags-off", "kit2", "--root", str(self.root), "--home", str(self.home)])
        self.assertEqual(off.returncode, 0, off.stderr)
        self.assertEqual(json.loads(off.stdout)["line"], "kit2: on -> off")
        self.assertFalse(json.loads((self.root / ".crav1/flags.local.json").read_text(encoding="utf-8"))["kit2"])
        self.assertEqual((self.root / ".crav1/.gitignore").read_text(encoding="utf-8").count("flags.local.json"), 1)

    def test_several_known_names(self):
        flags = kit.flags_module()
        flags.REGISTRY["sample"] = {"description": "Synthetic second flag.", "status": "beta"}
        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = kit.main(["flags-on", "sample", "kit2", "--root", str(self.root), "--home", str(self.home)])
        finally:
            del flags.REGISTRY["sample"]
        self.assertEqual(code, 0, stderr.getvalue())
        self.assertEqual(stderr.getvalue(), "")
        body = json.loads(stdout.getvalue())
        self.assertEqual(body["line"], "kit2: off -> on, sample: off -> on")
        stored = json.loads((self.root / ".crav1/flags.local.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, {"kit2": True, "sample": True})
        self.assertEqual(stored["sample"], True)
        self.assertEqual(len(stored), 2)

    def test_mixed_known_and_unknown_names(self):
        mixed = run_kit(["flags-on", "kit2", "nope", "--root", str(self.root), "--home", str(self.home)])
        self.assertEqual(mixed.returncode, 2)
        self.assertEqual(mixed.stderr, "Refused: nope is not a known flag. Known flags: kit2.\n")
        self.assertEqual(mixed.stderr.count("\n"), 1)
        body = json.loads(mixed.stdout)
        self.assertEqual(body["line"], "kit2: off -> on")
        self.assertEqual(body["refused"], ["nope"])
        stored = json.loads((self.root / ".crav1/flags.local.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, {"kit2": True})
        self.assertNotIn("nope", stored)

    def test_ignore_rule_and_project_gitignore(self):
        write(self.root / ".crav1/.gitignore", "*\n")
        first = run_kit(["flags-on", "kit2", "--root", str(self.root), "--home", str(self.home)])
        self.assertEqual(first.returncode, 0, first.stderr)
        text = (self.root / ".crav1/.gitignore").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("*\n"))
        self.assertEqual(text.count("flags.local.json"), 1)
        second = run_kit(["flags-on", "kit2", "--root", str(self.root), "--home", str(self.home)])
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual((self.root / ".crav1/.gitignore").read_text(encoding="utf-8"), text)
        self.assertEqual((self.root / ".gitignore").read_bytes(), b"build/\n")
        ignored = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", "--", ".crav1/flags.local.json"],
            capture_output=True, text=True,
        )
        self.assertEqual(ignored.returncode, 0, ignored.stderr)
        status = subprocess.run(
            ["git", "-C", str(self.root), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertNotIn("flags.local.json", status)

    def test_malformed_file_and_unknown_stored_flag(self):
        old, new = self.base / "old", self.base / "new"
        seed_kit(old, "1.204.0")
        seed_kit(new, "1.205.0")
        seed_kit(self.root, "1.204.0")
        write(self.root / ".crav1/.gitignore", "flags.local.json\n")
        git_init(self.root)
        clean = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.205.0",
            "--root", str(self.root), "--home", str(self.home),
        ])
        self.assertEqual(clean.returncode, 0, clean.stderr)
        write(self.root / ".crav1/flags.local.json", "{")
        bad = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.205.0",
            "--root", str(self.root), "--home", str(self.home),
        ])
        self.assertEqual(bad.returncode, 0, bad.stderr)
        self.assertEqual(bad.stderr, MALFORMED + "\n")
        self.assertEqual(bad.stderr.count("\n"), 1)
        self.assertEqual(bad.stdout.encode(), clean.stdout.encode())
        self.assertNotIn("kit2_line", bad.stdout)
        write(self.root / ".crav1/flags.local.json", json.dumps({"future": True, "kit2": False}) + "\n")
        kept = (self.root / ".crav1/flags.local.json").read_bytes()
        unknown = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.205.0",
            "--root", str(self.root), "--home", str(self.home),
        ])
        self.assertEqual(unknown.returncode, 0, unknown.stderr)
        self.assertEqual(unknown.stderr, "")
        body = json.loads(unknown.stdout)
        self.assertEqual(body["unknown_flags"], ["future"])
        self.assertNotIn("kit2_line", body)
        self.assertEqual(body["files"], json.loads(clean.stdout)["files"])
        self.assertEqual((self.root / ".crav1/flags.local.json").read_bytes(), kept)
        listed = run_kit(["flags-list", "--root", str(self.root)])
        self.assertIn("Unknown flag kept: future.", json.loads(listed.stdout)["line"])
        self.assertEqual(listed.returncode, 0, listed.stderr)


class Kit2Install(unittest.TestCase):
    def test_on_installs_off_offers_and_project_stays(self):
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, True)
        home, root = base / "home", base / "proj"
        old, new = base / "old", base / "new"
        home.mkdir()
        seed_kit(old, "1.205.0")
        seed_kit(new, "1.205.0")
        seed_kit(root, "1.205.0")
        shutil.copytree(ROOT / "v2", new / "v2", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        releases = base / "releases.txt"
        releases.write_text("v1.205.0\n", encoding="utf-8")
        spec = root / "docs/specs/orders-api/spec.md"
        write(spec, "Orders for partner B.\n")
        write(root / "sot/index.md", "project source\n")
        write(root / ".gitignore", "build/\n")
        on = run_kit(["flags-on", "kit2", "--root", str(root), "--home", str(home)])
        self.assertEqual(on.returncode, 0, on.stderr)
        before = tree_files(root)
        plain_root = base / "plain"
        seed_kit(plain_root, "1.205.0")
        write(plain_root / "docs/specs/orders-api/spec.md", "Orders for partner B.\n")
        write(plain_root / "sot/index.md", "project source\n")
        write(plain_root / ".gitignore", "build/\n")
        plain = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.205.0",
            "--root", str(plain_root), "--home", str(home), "--releases-file", str(releases),
        ])
        flagged = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.205.0",
            "--root", str(root), "--home", str(home), "--releases-file", str(releases),
        ])
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertEqual(flagged.returncode, 0, flagged.stderr)
        plain_body, flagged_body = json.loads(plain.stdout), json.loads(flagged.stdout)
        self.assertEqual(plain_body["files"], flagged_body["files"])
        self.assertNotIn("kit2_line", plain_body)
        self.assertIn("Kit 2.0: dry-run ", flagged_body["kit2_line"])
        self.assertIn("Will install ", flagged_body["kit2_line"])
        self.assertIn("installed now none", flagged_body["kit2_line"])
        self.assertIn("A newer 2.0 may exist.", flagged_body["kit2_line"])
        applied = run_kit([
            "apply", "--old", str(old), "--new", str(new), "--yes",
            "--root", str(root), "--home", str(home), "--releases-file", str(releases),
        ])
        self.assertEqual(applied.returncode, 0, applied.stderr)
        applied_body = json.loads(applied.stdout)
        self.assertIn("Kit 2.0: installed ", applied_body["kit2_line"])
        self.assertTrue((home / ".crav1-2" / "installed.json").is_file())
        self.assertTrue((home / ".cursor/plugins/local/crav1-2/.cursor-plugin/plugin.json").is_file())
        self.assertEqual(tree_files(root), before)
        self.assertEqual(spec.read_text(encoding="utf-8"), "Orders for partner B.\n")
        off = run_kit(["flags-off", "kit2", "--root", str(root), "--home", str(home)])
        self.assertEqual(off.returncode, 0, off.stderr)
        offer = json.loads(off.stdout)
        self.assertIn("uninstall-kit2", offer["kit2_line"])
        self.assertIn("keep-kit2", offer["kit2_line"])
        self.assertTrue((home / ".crav1-2" / "installed.json").is_file())
        offered = run_kit([
            "plan", "--old", str(old), "--new", str(new), "--to-version", "1.205.0",
            "--root", str(root), "--home", str(home), "--releases-file", str(releases),
        ])
        self.assertIn("uninstall offered", json.loads(offered.stdout)["kit2_line"])
        self.assertEqual(json.loads(offered.stdout)["files"], plain_body["files"])
        snapshot = tree_files(root)
        removed = run_kit([
            "uninstall-kit2", "--yes", "--new", str(new), "--root", str(root), "--home", str(home),
        ])
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertIn("uninstalled", json.loads(removed.stdout)["kit2_line"])
        self.assertFalse((home / ".cursor/plugins/local/crav1-2/.cursor-plugin/plugin.json").exists())
        self.assertEqual(tree_files(root), snapshot)
        self.assertEqual((root / "sot/index.md").read_text(encoding="utf-8"), "project source\n")


class DryRunFlags(unittest.TestCase):
    def test_banner_absent_without_a_file_and_present_with_kit2(self):
        sample = json.dumps({"kept": [], "project_untouched": True, "touched": []}, indent=2, sort_keys=True)
        self.assertEqual(
            dry._summarise("apply", 0, sample),
            f"$ update_kit.py apply (exit 0)\n{sample}",
        )
        with_line = json.dumps({"kit2_line": "Kit 2.0: dry-run 2.0.0-alpha.3, 3 files.", "touched": []}, indent=2, sort_keys=True)
        summary = dry._summarise("apply", 0, with_line)
        self.assertTrue(summary.endswith("\nKit 2.0: dry-run 2.0.0-alpha.3, 3 files."))
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, True)
        kit_repo = base / "kit"
        plugin = kit_repo / "plugins/crav1/.cursor-plugin"
        plugin.mkdir(parents=True)
        (plugin / "plugin.json").write_text(json.dumps({"name": "crav1", "version": "1.0.0"}) + "\n", encoding="utf-8")
        scripts = kit_repo / "plugins/crav1/skills/crav1-update-kit/scripts"
        scripts.mkdir(parents=True)
        shutil.copy(UPDATE, scripts / "update_kit.py")
        shutil.copy(FLAGS, scripts / "flags.py")
        shutil.copy(ROOT / ".cursor/skills/crav1/crav1-update-kit/vendors.json", scripts.parent / "vendors.json")
        write(kit_repo / MARKER, "Kit version: 1.0.0\n")
        subprocess.run([*G, "init", "-q", str(kit_repo)], check=True)
        subprocess.run([*G, "-C", str(kit_repo), "add", "-A"], check=True)
        subprocess.run([*G, "-C", str(kit_repo), "commit", "-qm", "v1.0.0"], check=True)
        subprocess.run([*G, "-C", str(kit_repo), "tag", "v1.0.0"], check=True)
        subprocess.run([*G, "-C", str(kit_repo), "checkout", "-qb", "feat/kit-test"], check=True)
        (plugin / "plugin.json").write_text(json.dumps({"name": "crav1", "version": "1.0.1"}) + "\n", encoding="utf-8")
        write(kit_repo / MARKER, "Kit version: 1.0.1\n")
        shutil.copytree(ROOT / "v2", kit_repo / "v2", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        subprocess.run([*G, "-C", str(kit_repo), "add", "-A"], check=True)
        subprocess.run([*G, "-C", str(kit_repo), "commit", "-qm", "v1.0.1"], check=True)
        proj = base / "proj"
        proj.mkdir()
        subprocess.run([*G, "init", "-q", str(proj)], check=True)
        shutil.copytree(kit_repo / ".cursor", proj / ".cursor")
        # The project stays on the tagged kit. The branch commit is not this tree.
        subprocess.run([*G, "-C", str(kit_repo), "checkout", "-q", "main"], check=True)
        write(proj / MARKER, "Kit version: 1.0.0\n")
        write(proj / ".crav1/kit.json", json.dumps({"schema": 1, "vendors": ["cursor"]}, indent=2) + "\n")
        write(proj / "docs/specs/orders-api/spec.md", "# Orders API\n")
        subprocess.run([*G, "-C", str(proj), "add", "-A"], check=True)
        subprocess.run([*G, "-C", str(proj), "commit", "-qm", "start"], check=True)
        releases = base / "releases.txt"
        releases.write_text("v1.0.0\n", encoding="utf-8")
        env = dict(
            os.environ,
            CRAV1_DRY_RUN_NO_CLIPBOARD="1",
            PYTHONUTF8="1",
            HOME=str(base / "home"),
            CRAV1_KIT_RELEASES_FILE=str(releases),
        )
        (base / "home").mkdir()
        first = subprocess.run(
            [sys.executable, "-X", "utf8", str(DRY), "--branch", "feat/kit-test", "--spec", "orders-api",
             "--kit-source", str(kit_repo), "--repo", str(proj)],
            capture_output=True, text=True, env=env, timeout=180,
        )
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertNotIn("Flags:", first.stdout)
        self.assertNotIn("Kit 2.0", first.stdout)
        self.assertIn("Your repo: unchanged", first.stdout)
        write(proj / ".crav1/flags.local.json", json.dumps({"kit2": True}) + "\n")
        second = subprocess.run(
            [sys.executable, "-X", "utf8", str(DRY), "--branch", "feat/kit-test", "--spec", "orders-api",
             "--kit-source", str(kit_repo), "--repo", str(proj)],
            capture_output=True, text=True, env=env, timeout=180,
        )
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("Flags: kit2", second.stdout)
        self.assertIn("Kit 2.0: dry-run ", second.stdout)
        self.assertIn("Your repo: unchanged", second.stdout)
        status = subprocess.run(
            ["git", "-C", str(proj), "status", "--porcelain"], capture_output=True, text=True, check=True,
        ).stdout
        self.assertIn("flags.local.json", status)


class Wording(unittest.TestCase):
    def test_old_spaced_flag_words_are_gone(self):
        needles = ("flag list", "flag kit2 on", "flag kit2 off", "flag kit2")
        roots = [
            ROOT / ".cursor/skills/crav1/crav1-update-kit",
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "v2/README.md",
            ROOT / "docs/from-update-kit.md",
            ROOT / "docs/install.md",
            ROOT / "docs/concepts/glossary.md",
            ROOT / "docs/concepts/data-layout.md",
            ROOT / "plugins/crav1/README.md",
            ROOT / "scripts/kit_dry_run.py",
        ]
        for path in roots:
            files = [path] if path.is_file() else list(path.rglob("*"))
            for item in files:
                if not item.is_file() or item.suffix not in {".md", ".py", ".mdc"}:
                    continue
                text = item.read_text(encoding="utf-8")
                for needle in needles:
                    self.assertNotIn(needle, text, f"{item} still has {needle}")


if __name__ == "__main__":
    unittest.main()
