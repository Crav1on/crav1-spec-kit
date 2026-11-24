# Map page (1.162.0)

Read this only on `open-map` or `export-map`. The page shows the whole `build-map.md`, with a diagram you can zoom. The `.md` file stays the main view and is not changed.

Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. On Windows that is `python` with `PYTHONUTF8=1`. Elsewhere it is `python3`. Pass `-X utf8`.

```text
<interpreter> -X utf8 <this skill folder>/scripts/open_build_map.py docs/specs/<slug>
<interpreter> -X utf8 <this skill folder>/scripts/open_build_map.py docs/specs/<slug> --export
```

With no slug and one slice, use that slice. With several, list them and stop. When `build-map.md` is missing, run the ready check first, then the command.

## Open map

The first command writes a small page to a temp file, opens it in the browser, and prints `Map page: <path>`. Print that line. The page renders the text, the lists, the links, and the wave lists, which still fold. Each Mermaid diagram sits in place, unchanged, with zoom at the mouse wheel, drag to pan, and the buttons `-`, `+`, `Fit`, `100%` and `Fullscreen`. With the diagram focused, `+`, `-` and `0` zoom. The text stays in a readable column. The diagram pane uses the full width of the browser window, and refits when the window changes size while it is at Fit.

The page loads Mermaid and marked from `scripts/vendor/` beside the script, so it works offline. When that folder is missing it loads the same pinned versions from jsDelivr. `--no-open` writes the page and does not open the browser.

## Export map

`--export` writes one HTML file with both libraries inside, about 2.6 MB. It works offline in any browser, with nothing to install, for anyone you send it to. It prints `Exported: <path>`. Print that line, then say once that the file holds everything the map shows, so send it only to people who may see the plan, and that it is a snapshot: export again after the plan changes.

The default is `<slug>-build-map-<YYYY-MM-DD>.html` in the Downloads folder, else the current folder, else the temp folder. It is never written inside the specs repo, and `--out <path>` inside that repo is refused. The page has a small `Exported <date> from build-map.md` line at the top.

## Libraries

`scripts/vendor/VERSIONS.txt` names the pinned versions, mermaid@11.4.1 and marked@18.2.0, and `scripts/vendor/LICENSES.txt` has their MIT licences. Do not edit those files by hand.
