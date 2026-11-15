"""1.162.0: the build map opens as a zoomable page and exports as one file."""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SK = ROOT / ".cursor/skills/crav1/crav1-tasks-ready-to-build"
PAGE = SK / "scripts/open_build_map.py"
BUILD_MAP = SK / "scripts/build_map.py"
VENDOR = SK / "scripts/vendor"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mp = load(PAGE, "open_build_map_1162")
bm = load(BUILD_MAP, "build_map_1162")

MAP = """# Build map

To zoom the diagram, run `/crav1-tasks-ready-to-build orders-api open map`.

One branch per plan step.

```mermaid
flowchart LR
  subgraph w1["Wave 1"]
    direction TB
    b1["feat/orders-cicd"]
  end
  subgraph w2["Wave 2"]
    direction TB
    b2["feat/orders-dev-switch </script><script>alert(1)</script>"]
  end
  b1 --> b2
```

An arrow means the later branch waits for the earlier one.

<details>
<summary>Wave 1 done (1 task)</summary>

## Wave 1: 1 branch, 0 can start now, 1 done

### feat/orders-cicd

- Tasks: ~~T1 Pipeline build stage~~ ✓ done
- Waited for: none

</details>

```mermaid
flowchart LR
  a --> b
```
"""

PLAN = """# Plan

## Approach

1. feat/orders-cicd: build the pipeline. (T1, T2)
2. feat/orders-dev-switch: switch the app. (T3)
"""

TASKS = """# Tasks

- [x] T1: Pipeline build stage (map: feat/orders-cicd)
- [x] T2: Pipeline deploy stage (map: feat/orders-cicd) (after: T1)
- [ ] T3: Repoint the pipeline to the new app (map: feat/orders-dev-switch) (after: T2)
"""

SPEC = """# Orders

## Open questions

None.
"""


def section(markdown, name):
    return markdown.split(f"### {name}", 1)[1].split("\n### ", 1)[0]


class Extraction(unittest.TestCase):
    def test_finds_each_mermaid_block_unchanged(self):
        blocks = mp.mermaid_blocks(MAP)
        self.assertEqual(len(blocks), 2)
        self.assertTrue(blocks[0].startswith("flowchart LR\n  subgraph w1"))
        self.assertTrue(blocks[0].endswith("b1 --> b2"))
        self.assertEqual(blocks[1], "flowchart LR\n  a --> b")

    def test_page_uses_the_same_pattern(self):
        page = mp.build_html(MAP, "orders-api build map", export=False, source_name="build-map.md")
        self.assertIn("```[ \\t]*mermaid[ \\t]*\\r?\\n([\\s\\S]*?)```", page)
        self.assertEqual(mp.MERMAID_BLOCK_RE.pattern, "```[ \\t]*mermaid[ \\t]*\\r?\\n([\\s\\S]*?)```")

    def test_no_diagram_still_renders(self):
        self.assertEqual(mp.mermaid_blocks("# Build map\n\nNothing left to build.\n"), [])


class Escaping(unittest.TestCase):
    def test_label_cannot_close_the_script(self):
        page = mp.build_html(MAP, "orders-api build map", export=False, source_name="build-map.md")
        config = page.split("const CONFIG = ", 1)[1].split(";\n", 1)[0]
        self.assertNotIn("</script", config)
        self.assertNotIn("<script", config)
        self.assertNotIn("<", config)
        data = json.loads(config)
        self.assertEqual(data["markdown"], MAP)

    def test_line_separators_are_escaped(self):
        text = mp.json_for_script("a\u2028b\u2029c & <d>")
        self.assertNotIn("\u2028", text)
        self.assertNotIn("\u2029", text)
        self.assertEqual(json.loads(text), "a\u2028b\u2029c & <d>")

    def test_title_is_escaped(self):
        page = mp.build_html(MAP, 'x"><script>', export=False, source_name="build-map.md")
        self.assertIn("<title>x&quot;&gt;&lt;script&gt;</title>", page)

    def test_inlined_library_cannot_close_its_tag(self):
        self.assertEqual(mp.inline_js("a</script>b\n//# sourceMappingURL=x.map"), "a<\\/script>b\n")


class Modes(unittest.TestCase):
    def test_export_has_no_external_url(self):
        page = mp.build_html(MAP, "orders-api build map", export=True, source_name="build-map.md",
                             export_date="2026-11-15")
        self.assertNotRegex(page, r"<script[^>]*\bsrc=")
        self.assertNotRegex(page, r"<link\b")
        self.assertNotIn("cdn.jsdelivr", page)
        self.assertNotIn("file://", page)
        self.assertNotIn("sourceMappingURL", page)
        self.assertIn("globalThis.mermaid", page)
        self.assertIn("Exported 2026-11-15 from build-map.md", page)
        config = json.loads(page.split("const CONFIG = ", 1)[1].split(";\n", 1)[0])
        self.assertTrue(config["exportMode"])
        self.assertEqual([config[key] for key in ("mermaidSrc", "markedSrc", "cdnMermaid", "cdnMarked")], ["", "", "", ""])
        # Every script tag in the export is inline.
        self.assertEqual(page.count("<script>"), 3)

    def test_open_mode_references_the_vendor_folder(self):
        page = mp.build_html(MAP, "orders-api build map", export=False, source_name="build-map.md")
        config = json.loads(page.split("const CONFIG = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual(config["mermaidSrc"], (VENDOR / "mermaid.min.js").resolve().as_uri())
        self.assertEqual(config["markedSrc"], (VENDOR / "marked.min.js").resolve().as_uri())
        self.assertEqual(config["cdnMermaid"], "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js")
        self.assertEqual(config["cdnMarked"], "https://cdn.jsdelivr.net/npm/marked@18.2.0/lib/marked.umd.js")
        self.assertNotIn("Exported", page.split("<body>", 1)[1].split("<script>", 1)[0])
        self.assertLess(len(page.encode("utf-8")), 60_000)

    def test_diagram_pane_spans_the_window(self):
        page = mp.build_html(MAP, "t", export=False, source_name="build-map.md")
        css = page.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertRegex(css, r"\.page > \* \{\s*max-width: \d+px;")
        self.assertRegex(css, r"\.page > \.diagram \{\s*max-width: none;")
        page_rule = re.search(r"\.page \{([^}]*)\}", css).group(1)
        self.assertNotIn("max-width", page_rule)
        self.assertIn("ResizeObserver", page)
        self.assertIn("if (atFit) fit();", page)
        for act in ("out", "in", "fit", "reset", "full"):
            self.assertIn(f'data-act="{act}"', page)


class Paths(unittest.TestCase):
    def test_slug_is_the_spec_folder(self):
        self.assertEqual(mp.spec_slug(pathlib.Path("docs/specs/orders-api/build-map.md")), "orders-api")
        self.assertEqual(mp.export_name("orders-api", "2026-11-15"), "orders-api-build-map-2026-11-15.html")

    def test_default_export_goes_to_downloads_never_the_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = pathlib.Path(tmp) / "home"
            repo = pathlib.Path(tmp) / "specs"
            (home / "Downloads").mkdir(parents=True)
            (repo / "docs/specs/orders-api").mkdir(parents=True)
            out = mp.default_export_path("orders-api", repo.resolve(), home=home, cwd=repo, day="2026-11-15")
            self.assertEqual(out, home / "Downloads" / "orders-api-build-map-2026-11-15.html")
            (home / "Downloads").rmdir()
            out = mp.default_export_path("orders-api", repo.resolve(), home=home, cwd=repo / "docs", day="2026-11-15")
            self.assertFalse(mp.inside(out, repo.resolve()))
            self.assertEqual(out.name, "orders-api-build-map-2026-11-15.html")

    def run_page(self, cwd, *args):
        home = cwd.parent / "home"
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
        return subprocess.run([sys.executable, "-X", "utf8", str(PAGE), *args], cwd=cwd, env=env,
                              capture_output=True, text=True, timeout=60)

    def test_cli_open_export_and_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            repo = tmp / "specs"
            folder = repo / "docs/specs/orders-api"
            folder.mkdir(parents=True)
            (tmp / "home/Downloads").mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (folder / "build-map.md").write_text(MAP, encoding="utf-8")
            opened = self.run_page(repo, "docs/specs/orders-api", "--no-open")
            self.assertEqual(opened.returncode, 0, opened.stderr)
            page_path = pathlib.Path(opened.stdout.strip().removeprefix("Map page: "))
            self.assertTrue(page_path.is_file())
            self.assertFalse(mp.inside(page_path, repo.resolve()))
            page_path.unlink()
            exported = self.run_page(repo, "docs/specs/orders-api/build-map.md", "--export")
            self.assertEqual(exported.returncode, 0, exported.stderr)
            out = pathlib.Path(exported.stdout.strip().removeprefix("Exported: "))
            self.assertEqual(out.parent, (tmp / "home/Downloads"))
            self.assertRegex(out.name, r"^orders-api-build-map-\d{4}-\d{2}-\d{2}\.html$")
            self.assertGreater(out.stat().st_size, 2_000_000)
            refused = self.run_page(repo, "docs/specs/orders-api", "--export", "--out", "docs/map.html")
            self.assertEqual(refused.returncode, 2)
            self.assertIn("inside the specs repo", refused.stderr)
            self.assertFalse((repo / "docs/map.html").exists())
            missing = self.run_page(repo, "docs/specs/nothing")
            self.assertEqual(missing.returncode, 1)
            self.assertIn("No build map", missing.stderr)
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ["build-map.md"])


class Vendor(unittest.TestCase):
    def test_vendor_files_and_licences(self):
        versions = (VENDOR / "VERSIONS.txt").read_text(encoding="utf-8")
        licences = (VENDOR / "LICENSES.txt").read_text(encoding="utf-8")
        self.assertIn("mermaid@11.4.1", versions)
        self.assertIn("marked@18.2.0", versions)
        self.assertEqual(licences.count("Permission is hereby granted, free of charge"), 2)
        self.assertIn("Knut Sveidqvist", licences)
        self.assertIn("MarkedJS", licences)
        self.assertEqual((VENDOR / "mermaid.min.js").stat().st_size, 2571900)
        self.assertEqual((VENDOR / "marked.min.js").stat().st_size, 51349)
        self.assertIn("mermaid@11.4.1", mp.CDN_MERMAID)
        self.assertIn("marked@18.2.0", mp.CDN_MARKED)

    def test_every_install_tree_ships_the_vendor_folder(self):
        for tree in (ROOT / ".claude/skills", ROOT / "plugins/crav1/skills"):
            copy = tree / "crav1-tasks-ready-to-build/scripts/vendor"
            for name in ("mermaid.min.js", "marked.min.js", "VERSIONS.txt", "LICENSES.txt"):
                self.assertEqual((copy / name).read_bytes(), (VENDOR / name).read_bytes(), copy / name)


class MapFile(unittest.TestCase):
    def test_done_branch_says_waited_for(self):
        markdown = bm.build("orders-api", SPEC, PLAN, TASKS)["markdown"]
        done = section(markdown, "feat/orders-cicd")
        open_ = section(markdown, "feat/orders-dev-switch")
        self.assertIn("- Waited for: none", done)
        self.assertNotIn("- Waits for:", done)
        self.assertIn("- Waits for: feat/orders-cicd", open_)
        self.assertNotIn("Waited for", open_)

    def test_page_line_under_the_heading(self):
        markdown = bm.build("orders-api", SPEC, PLAN, TASKS)["markdown"]
        lines = markdown.splitlines()
        self.assertEqual(lines[0], "# Build map")
        self.assertEqual(
            lines[2],
            "To zoom the diagram, run `/crav1-tasks-ready-to-build orders-api open map`. "
            "To share the map as one file, run `/crav1-tasks-ready-to-build orders-api export map`.",
        )

    def test_choice_words_parse(self):
        parsed = bm.parse_invocation("/crav1-tasks-ready-to-build orders-api export map")
        self.assertEqual((parsed["scope"], parsed["page"]), ("orders-api", "export"))
        parsed = bm.parse_invocation("cc 1.0 open map")
        self.assertEqual((parsed["scope"], parsed["page"]), ("cc 1.0", "open"))
        self.assertIsNone(bm.parse_invocation("cc 1.0")["page"])

    def test_skill_names_the_words_and_the_reference(self):
        skill = (SK / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`open map`", skill)
        self.assertIn("`export map`", skill)
        self.assertIn("references/map-page.md", skill)
        ref = (SK / "references/map-page.md").read_text(encoding="utf-8")
        self.assertIn("scripts/open_build_map.py docs/specs/<slug> --export", ref)
        routing = (ROOT / "docs/guild-routing.md").read_text(encoding="utf-8")
        self.assertIn("| `/crav1-tasks-ready-to-build` | Open the map as a zoomable page? | `open map` · `export map` |", routing)


if __name__ == "__main__":
    unittest.main()
