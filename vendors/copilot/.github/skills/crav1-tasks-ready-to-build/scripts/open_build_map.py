#!/usr/bin/env python3
"""Open or export a build map as a zoomable page (1.162.0).

Renders the whole docs/specs/<slug>/build-map.md as one dark page: the text,
the lists, the wave lists that fold, and each Mermaid diagram in place with
zoom, pan, Fit, 100% and Fullscreen. The text stays in a readable column; the
diagram pane uses the full width of the browser window.

Open (default): writes a small page to a temp file and opens the browser. The
page loads Mermaid and marked from vendor/ beside this script, and falls back
to the same pinned versions on jsDelivr when that folder is missing.

Export (--export): writes one self-contained HTML file with both libraries
inlined, which works offline for anyone. The default is
<spec-slug>-build-map-<YYYY-MM-DD>.html in ~/Downloads, never inside the specs
repo. --out PATH picks another place outside that repo.

The build-map.md file is read only. Nothing is written in the repo.

Usage:
  open_build_map.py <spec-folder-or-build-map.md> [--no-open]
  open_build_map.py <spec-folder-or-build-map.md> --export [--out PATH]
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import html as html_lib
import json
import re
import subprocess
import tempfile
import webbrowser
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VENDOR_DIR = SCRIPT_DIR / "vendor"
MERMAID_FILE = VENDOR_DIR / "mermaid.min.js"
MARKED_FILE = VENDOR_DIR / "marked.min.js"

CDN_MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"
CDN_MARKED = "https://cdn.jsdelivr.net/npm/marked@18.2.0/lib/marked.umd.js"

MERMAID_BLOCK_RE = re.compile(r"```[ \t]*mermaid[ \t]*\r?\n([\s\S]*?)```", re.IGNORECASE)
SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {
      --bg: #0d1117;
      --bg-raised: #161b22;
      --bg-btn: #21262d;
      --bg-btn-hover: #30363d;
      --border: #30363d;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --danger: #f85149;
      --code-bg: rgba(110, 118, 129, 0.28);
    }
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 16px;
      line-height: 1.5;
    }
    .export-banner {
      font-size: 12px;
      color: var(--text-muted);
      padding: 8px 32px;
      border-bottom: 1px solid var(--border);
      background: var(--bg-raised);
    }
    .page {
      padding: 28px 24px 96px;
    }
    .page > * {
      max-width: 1040px;
    }
    .page > .diagram {
      max-width: none;
    }
    .markdown-body h1 {
      margin: 0 0 16px;
      font-size: 32px;
      font-weight: 600;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border);
    }
    .markdown-body h2, .markdown-body h3 {
      margin: 28px 0 12px;
      font-weight: 600;
    }
    .markdown-body p { margin: 0 0 16px; }
    .markdown-body a { color: var(--accent); text-decoration: none; }
    .markdown-body a:hover { text-decoration: underline; }
    .markdown-body code {
      background: var(--code-bg);
      padding: 0.15em 0.4em;
      border-radius: 6px;
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
      font-size: 85%;
    }
    .markdown-body ul, .markdown-body ol { margin: 0 0 16px; padding-left: 2em; }
    .markdown-body li { margin: 0.25em 0; }
    .markdown-body details {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 16px;
      margin: 0 0 12px;
      background: var(--bg-raised);
    }
    .markdown-body details[open] { padding-bottom: 4px; }
    .markdown-body summary {
      cursor: pointer;
      font-weight: 600;
      list-style-position: outside;
    }
    .markdown-body summary:hover { color: var(--accent); }
    .markdown-body details ul { margin: 8px 0 8px; }
    .diagram {
      margin: 20px 0 28px;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      background: var(--bg);
      outline: none;
    }
    .diagram:focus, .diagram:focus-within {
      border-color: var(--accent);
    }
    .diagram-toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 44px;
      padding: 0 10px;
      background: var(--bg-raised);
      border-bottom: 1px solid var(--border);
      user-select: none;
    }
    .diagram-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      margin-right: auto;
    }
    .diagram-toolbar .controls {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }
    .diagram-toolbar button {
      background: var(--bg-btn);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 6px;
      padding: 4px 10px;
      font-size: 13px;
      line-height: 1.2;
      cursor: pointer;
    }
    .diagram-toolbar button:hover { background: var(--bg-btn-hover); }
    .diagram-toolbar button:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 1px;
    }
    .zoom-label {
      min-width: 3.5em;
      text-align: center;
      font-variant-numeric: tabular-nums;
      font-size: 13px;
      color: var(--text-muted);
    }
    .diagram-hint {
      font-size: 11px;
      color: var(--text-muted);
      white-space: nowrap;
    }
    .diagram-viewport {
      position: relative;
      height: clamp(360px, 70vh, 900px);
      overflow: hidden;
      cursor: grab;
      background:
        radial-gradient(circle at 1px 1px, #21262d 1px, transparent 0) 0 0 / 24px 24px,
        var(--bg);
    }
    .diagram-viewport.panning { cursor: grabbing; }
    .diagram-canvas {
      position: absolute;
      top: 0; left: 0;
      transform-origin: 0 0;
      will-change: transform;
    }
    .diagram-canvas svg {
      display: block;
      max-width: none !important;
      height: auto;
    }
    .diagram-status {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);
      font-size: 14px;
      padding: 24px;
      text-align: center;
      pointer-events: none;
    }
    .diagram-status.error { color: var(--danger); pointer-events: auto; }
    .diagram-status.hidden { display: none; }
    .diagram.is-fullscreen,
    .diagram:fullscreen,
    .diagram:-webkit-full-screen {
      position: fixed;
      inset: 0;
      z-index: 100;
      margin: 0;
      border-radius: 0;
      width: 100%;
      height: 100%;
      max-width: none;
    }
    .diagram.is-fullscreen .diagram-viewport,
    .diagram:fullscreen .diagram-viewport,
    .diagram:-webkit-full-screen .diagram-viewport {
      height: calc(100vh - 44px);
    }
    @media (max-width: 800px) {
      .page { padding: 20px 12px 64px; }
      .diagram-hint { display: none; }
    }
  </style>
</head>
<body>
__BANNER__
  <article class="page markdown-body" id="content"></article>
__LIB_SCRIPTS__
  <script>
    const CONFIG = __CONFIG__;

    function loadScript(src) {
      return new Promise(function (resolve, reject) {
        const s = document.createElement("script");
        s.src = src;
        s.onload = function () { resolve(); };
        s.onerror = function () { reject(new Error("Failed to load " + src)); };
        document.head.appendChild(s);
      });
    }

    async function ensureLibs() {
      if (!window.mermaid) {
        if (CONFIG.mermaidSrc) {
          try { await loadScript(CONFIG.mermaidSrc); }
          catch (err) { /* fall through to CDN */ }
        }
        if (!window.mermaid && CONFIG.cdnMermaid) {
          await loadScript(CONFIG.cdnMermaid);
        }
      }
      if (!window.marked) {
        if (CONFIG.markedSrc) {
          try { await loadScript(CONFIG.markedSrc); }
          catch (err) { /* fall through to CDN */ }
        }
        if (!window.marked && CONFIG.cdnMarked) {
          await loadScript(CONFIG.cdnMarked);
        }
      }
      if (!window.mermaid) throw new Error("Mermaid library is not available.");
      if (!window.marked) throw new Error("Markdown library is not available.");
    }

    function extractMermaid(md) {
      const blocks = [];
      const text = md.replace(/```[ \t]*mermaid[ \t]*\r?\n([\s\S]*?)```/gi, function (_, src) {
        const i = blocks.length;
        blocks.push(src.replace(/\s+$/, ""));
        return "\n\n<!--mermaid-slot:" + i + "-->\n\n";
      });
      return { text: text, blocks: blocks };
    }

    function diagramMarkup(index) {
      return (
        '<figure class="diagram" id="diagram-' + index + '" tabindex="0" data-index="' + index + '">' +
          '<div class="diagram-toolbar">' +
            '<span class="diagram-label">Diagram</span>' +
            '<div class="controls">' +
              '<button type="button" data-act="out" title="Zoom out (−)">−</button>' +
              '<span class="zoom-label">…</span>' +
              '<button type="button" data-act="in" title="Zoom in (+)">+</button>' +
              '<button type="button" data-act="fit" title="Fit to the diagram pane">Fit</button>' +
              '<button type="button" data-act="reset" title="Reset to 100%">100%</button>' +
              '<button type="button" data-act="full" title="Toggle fullscreen">Fullscreen</button>' +
            '</div>' +
            '<span class="diagram-hint">Scroll to zoom, drag to pan. + / − / 0 when focused</span>' +
          '</div>' +
          '<div class="diagram-viewport">' +
            '<div class="diagram-canvas"></div>' +
            '<div class="diagram-status">Loading diagram…</div>' +
          '</div>' +
        '</figure>'
      );
    }

    function attachZoom(root, svg) {
      const viewport = root.querySelector(".diagram-viewport");
      const canvas = root.querySelector(".diagram-canvas");
      const zoomLabel = root.querySelector(".zoom-label");
      const fullBtn = root.querySelector('[data-act="full"]');
      const MIN_SCALE = 0.05;
      const MAX_SCALE = 8;
      const ZOOM_STEP = 1.25;
      const FIT_PADDING = 32;
      let scale = 1, tx = 0, ty = 0;
      let atFit = true;

      function sizeOf() {
        if (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width) {
          return { width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height };
        }
        const bbox = svg.getBBox();
        return { width: bbox.width, height: bbox.height };
      }

      function prepare() {
        const size = sizeOf();
        svg.setAttribute("width", String(size.width));
        svg.setAttribute("height", String(size.height));
        svg.style.width = size.width + "px";
        svg.style.height = size.height + "px";
        svg.style.maxWidth = "none";
      }

      function apply() {
        canvas.style.transform = "translate(" + tx + "px, " + ty + "px) scale(" + scale + ")";
        zoomLabel.textContent = Math.round(scale * 100) + "%";
      }

      function clamp(next) { return Math.min(MAX_SCALE, Math.max(MIN_SCALE, next)); }

      function zoomAt(clientX, clientY, factor) {
        const rect = viewport.getBoundingClientRect();
        const x = clientX - rect.left;
        const y = clientY - rect.top;
        const wx = (x - tx) / scale;
        const wy = (y - ty) / scale;
        scale = clamp(scale * factor);
        tx = x - wx * scale;
        ty = y - wy * scale;
        atFit = false;
        apply();
      }

      function zoomTowardCenter(factor) {
        const rect = viewport.getBoundingClientRect();
        zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, factor);
      }

      function fit() {
        const size = sizeOf();
        const vw = viewport.clientWidth;
        const vh = viewport.clientHeight;
        if (!size.width || !size.height || !vw || !vh) return;
        scale = clamp(Math.min((vw - FIT_PADDING * 2) / size.width, (vh - FIT_PADDING * 2) / size.height));
        tx = (vw - size.width * scale) / 2;
        ty = (vh - size.height * scale) / 2;
        atFit = true;
        apply();
      }

      function reset100() {
        const size = sizeOf();
        scale = 1;
        tx = (viewport.clientWidth - size.width) / 2;
        ty = (viewport.clientHeight - size.height) / 2;
        atFit = false;
        apply();
      }

      function zoomToPoint(svgX, svgY, nextScale) {
        const rect = viewport.getBoundingClientRect();
        scale = clamp(nextScale);
        tx = rect.width / 2 - svgX * scale;
        ty = rect.height / 2 - svgY * scale;
        atFit = false;
        apply();
      }

      function isFull() {
        return root.classList.contains("is-fullscreen") || document.fullscreenElement === root;
      }

      async function toggleFull() {
        if (isFull()) {
          if (document.fullscreenElement) {
            try { await document.exitFullscreen(); } catch (e) { /* ignore */ }
          }
          root.classList.remove("is-fullscreen");
        } else {
          let usedApi = false;
          if (root.requestFullscreen) {
            try { await root.requestFullscreen(); usedApi = true; }
            catch (e) { usedApi = false; }
          }
          if (!usedApi) root.classList.add("is-fullscreen");
        }
        fullBtn.textContent = isFull() ? "Exit fullscreen" : "Fullscreen";
        requestAnimationFrame(fit);
      }

      prepare();
      canvas.appendChild(svg);
      fit();

      root.querySelector('[data-act="in"]').addEventListener("click", function () { zoomTowardCenter(ZOOM_STEP); });
      root.querySelector('[data-act="out"]').addEventListener("click", function () { zoomTowardCenter(1 / ZOOM_STEP); });
      root.querySelector('[data-act="fit"]').addEventListener("click", fit);
      root.querySelector('[data-act="reset"]').addEventListener("click", reset100);
      fullBtn.addEventListener("click", function () { toggleFull(); });

      viewport.addEventListener("wheel", function (event) {
        event.preventDefault();
        zoomAt(event.clientX, event.clientY, Math.exp(-event.deltaY * 0.0015));
      }, { passive: false });

      let dragging = false, lastX = 0, lastY = 0;
      viewport.addEventListener("pointerdown", function (event) {
        if (event.button !== 0) return;
        dragging = true;
        lastX = event.clientX;
        lastY = event.clientY;
        viewport.classList.add("panning");
        viewport.setPointerCapture(event.pointerId);
        root.focus({ preventScroll: true });
      });
      viewport.addEventListener("pointermove", function (event) {
        if (!dragging) return;
        tx += event.clientX - lastX;
        ty += event.clientY - lastY;
        atFit = false;
        lastX = event.clientX;
        lastY = event.clientY;
        apply();
      });
      function endPan(event) {
        if (!dragging) return;
        dragging = false;
        viewport.classList.remove("panning");
        try { viewport.releasePointerCapture(event.pointerId); } catch (e) { /* already released */ }
      }
      viewport.addEventListener("pointerup", endPan);
      viewport.addEventListener("pointercancel", endPan);

      root.addEventListener("keydown", function (event) {
        if (event.ctrlKey || event.metaKey || event.altKey) return;
        if (event.key === "+" || event.key === "=") {
          event.preventDefault();
          zoomTowardCenter(ZOOM_STEP);
        } else if (event.key === "-" || event.key === "_") {
          event.preventDefault();
          zoomTowardCenter(1 / ZOOM_STEP);
        } else if (event.key === "0") {
          event.preventDefault();
          reset100();
        }
      });

      let lastWidth = viewport.clientWidth, lastHeight = viewport.clientHeight;
      function onResize() {
        const w = viewport.clientWidth, h = viewport.clientHeight;
        if (w === lastWidth && h === lastHeight) return;
        lastWidth = w;
        lastHeight = h;
        if (atFit) fit();
      }
      if (window.ResizeObserver) {
        new ResizeObserver(onResize).observe(viewport);
      }
      window.addEventListener("resize", onResize);

      document.addEventListener("fullscreenchange", function () {
        fullBtn.textContent = isFull() ? "Exit fullscreen" : "Fullscreen";
        requestAnimationFrame(fit);
      });

      return {
        fit: fit,
        reset100: reset100,
        zoomIn: function () { zoomTowardCenter(ZOOM_STEP); },
        zoomOut: function () { zoomTowardCenter(1 / ZOOM_STEP); },
        zoomAt: zoomAt,
        zoomToPoint: zoomToPoint,
        toggleFull: toggleFull,
        getScale: function () { return scale; },
        isAtFit: function () { return atFit; },
        root: root,
      };
    }

    async function renderDiagrams(blocks) {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: "dark",
        themeVariables: {
          darkMode: true,
          background: "#0d1117",
          fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif",
          fontSize: "16px",
          primaryColor: "#21262d",
          primaryTextColor: "#e6edf3",
          primaryBorderColor: "#388bfd",
          secondaryColor: "#161b22",
          secondaryTextColor: "#e6edf3",
          secondaryBorderColor: "#30363d",
          tertiaryColor: "#21262d",
          tertiaryTextColor: "#e6edf3",
          tertiaryBorderColor: "#30363d",
          lineColor: "#8b949e",
          textColor: "#e6edf3",
          mainBkg: "#21262d",
          nodeBorder: "#388bfd",
          clusterBkg: "#161b22",
          clusterBorder: "#30363d",
          titleColor: "#e6edf3",
          edgeLabelBackground: "#0d1117",
          nodeTextColor: "#e6edf3",
        },
        flowchart: {
          htmlLabels: true,
          curve: "basis",
          padding: 16,
          nodeSpacing: 40,
          rankSpacing: 56,
          useMaxWidth: false,
        },
      });

      window.__diagrams = [];
      for (let i = 0; i < blocks.length; i++) {
        const root = document.getElementById("diagram-" + i);
        if (!root) continue;
        const status = root.querySelector(".diagram-status");
        try {
          const id = "build-map-diagram-" + i;
          const result = await mermaid.render(id, blocks[i]);
          const holder = document.createElement("div");
          holder.innerHTML = result.svg;
          const svg = holder.querySelector("svg");
          if (!svg) throw new Error("Mermaid did not produce an SVG.");
          status.classList.add("hidden");
          const api = attachZoom(root, svg);
          window.__diagrams.push(api);
        } catch (err) {
          status.textContent = "Could not render the diagram: " + (err && err.message ? err.message : String(err));
          status.classList.add("error");
          console.error(err);
        }
      }
      if (window.__diagrams.length) {
        window.__mapZoom = window.__diagrams[0];
      }
    }

    async function main() {
      const content = document.getElementById("content");
      try {
        await ensureLibs();
      } catch (err) {
        content.innerHTML = '<p style="color:#f85149">Could not load Mermaid or marked. ' +
          (CONFIG.exportMode
            ? "This export should work offline; the inlined libraries may be missing."
            : "The page needs the kit's vendor folder, or an internet connection for the pinned copy.") +
          "</p><p>" + String(err && err.message ? err.message : err) + "</p>";
        document.body.setAttribute("data-error", String(err && err.message ? err.message : err));
        return;
      }
      const extracted = extractMermaid(CONFIG.markdown);
      let html = marked.parse(extracted.text);
      html = html.replace(/<!--mermaid-slot:(\d+)-->/g, function (_, n) {
        return diagramMarkup(Number(n));
      });
      content.innerHTML = html;
      await renderDiagrams(extracted.blocks);
      document.body.setAttribute("data-ready", "true");
      document.body.setAttribute("data-diagrams", String(extracted.blocks.length));
    }

    main().catch(function (err) {
      document.body.setAttribute("data-error", String(err && err.message ? err.message : err));
      console.error(err);
    });
  </script>
</body>
</html>
"""


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def mermaid_blocks(text: str) -> list[str]:
    """The source of each ```mermaid block, in order, without trailing space.

    The page's own extraction (extractMermaid in the template) uses the same
    pattern, so this is what the page draws.
    """
    return [block.rstrip() for block in MERMAID_BLOCK_RE.findall(text)]


def resolve_map(target: str) -> Path:
    """A spec folder or a build-map.md path, to the build-map.md file."""
    path = Path(target)
    if path.is_dir():
        path = path / "build-map.md"
    return path


def spec_slug(map_path: Path) -> str:
    """The spec folder name, docs/specs/<slug>/build-map.md -> <slug>."""
    folder = map_path.resolve().parent.name
    slug = SLUG_RE.sub("-", folder).strip("-.")
    return slug or "spec"


def json_for_script(value: object) -> str:
    """JSON-encode a value so it is safe inside a <script> tag."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def strip_source_map(js: str) -> str:
    return re.sub(r"[ \t]*//[#@][ \t]*sourceMappingURL=.*$", "", js, flags=re.MULTILINE)


def inline_js(js: str) -> str:
    return strip_source_map(js).replace("</script", "<\\/script")


def repo_root(path: Path) -> Path | None:
    """The git work tree that holds path, or None."""
    start = path if path.is_dir() else path.parent
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        out = None
    if out is not None and out.returncode == 0 and out.stdout.strip():
        return Path(out.stdout.strip()).resolve()
    for folder in [start.resolve(), *start.resolve().parents]:
        if (folder / ".git").exists():
            return folder
    return None


def inside(path: Path, root: Path | None) -> bool:
    if root is None:
        return False
    resolved = path.resolve()
    return resolved == root or root in resolved.parents


def export_name(slug: str, day: str | None = None) -> str:
    return f"{slug}-build-map-{day or date.today().isoformat()}.html"


def default_export_path(slug: str, specs_root: Path | None, home: Path | None = None,
                        cwd: Path | None = None, day: str | None = None) -> Path:
    """~/Downloads, else the current folder, else the temp folder; never the specs repo."""
    name = export_name(slug, day)
    downloads = (home or Path.home()) / "Downloads"
    for folder in (downloads, cwd or Path.cwd(), Path(tempfile.gettempdir())):
        if folder.is_dir() and not inside(folder, specs_root):
            return folder / name
    return Path(tempfile.gettempdir()) / name


def build_html(markdown: str, title: str, *, export: bool, source_name: str,
               export_date: str | None = None) -> str:
    config = {
        "exportMode": export,
        "markdown": markdown,
        "sourceName": source_name,
        "mermaidSrc": "",
        "markedSrc": "",
        "cdnMermaid": "" if export else CDN_MERMAID,
        "cdnMarked": "" if export else CDN_MARKED,
    }
    if export:
        mermaid_js = inline_js(MERMAID_FILE.read_text(encoding="utf-8"))
        marked_js = inline_js(MARKED_FILE.read_text(encoding="utf-8"))
        lib_scripts = (
            "<script>\n" + mermaid_js + "\n</script>\n"
            "<script>\n" + marked_js + "\n</script>\n"
        )
        shown_date = export_date or date.today().isoformat()
        banner = (
            f'  <div class="export-banner">Exported {html_lib.escape(shown_date)} '
            f"from {html_lib.escape(source_name)}</div>\n"
        )
    else:
        if MERMAID_FILE.is_file():
            config["mermaidSrc"] = MERMAID_FILE.resolve().as_uri()
        if MARKED_FILE.is_file():
            config["markedSrc"] = MARKED_FILE.resolve().as_uri()
        lib_scripts = ""
        banner = ""
    return (
        HTML_TEMPLATE
        .replace("__TITLE__", html_lib.escape(title, quote=True))
        .replace("__BANNER__", banner)
        .replace("__LIB_SCRIPTS__", lib_scripts)
        .replace("__CONFIG__", json_for_script(config))
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open or export a build map as a zoomable page (1.162.0)."
    )
    parser.add_argument("target", help="docs/specs/<slug> or its build-map.md")
    parser.add_argument("--export", action="store_true",
                        help="write one self-contained HTML file to share")
    parser.add_argument("--out", help="export path, outside the specs repo")
    parser.add_argument("--no-open", action="store_true",
                        help="open mode: write the page and do not open a browser")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    args = parse_args(argv)
    path = resolve_map(args.target)
    if not path.is_file():
        print(f"No build map at {path}. Run /crav1-tasks-ready-to-build first.", file=sys.stderr)
        return 1
    if args.out and not args.export:
        print("--out is for --export. Open mode writes a temp file.", file=sys.stderr)
        return 2
    if args.export and (not MERMAID_FILE.is_file() or not MARKED_FILE.is_file()):
        print(f"--export needs the vendored libraries in {VENDOR_DIR}. Run /crav1-update-kit.", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    slug = spec_slug(path)
    page = build_html(text, f"{slug} build map", export=args.export, source_name=path.name)

    if not args.export:
        with tempfile.NamedTemporaryFile(prefix=f"{slug}-build-map-", suffix=".html", delete=False,
                                         mode="w", encoding="utf-8") as handle:
            handle.write(page)
            out_path = Path(handle.name)
        print(f"Map page: {out_path}")
        if not args.no_open:
            webbrowser.open(out_path.resolve().as_uri())
        return 0

    specs_root = repo_root(path)
    if args.out:
        out_path = Path(args.out).expanduser()
        if out_path.is_dir():
            out_path = out_path / export_name(slug)
        if inside(out_path, specs_root):
            print(f"Refused: {out_path} is inside the specs repo. The export is never saved there. Pick a path outside it.", file=sys.stderr)
            return 2
    else:
        out_path = default_export_path(slug, specs_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    print(f"Exported: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
