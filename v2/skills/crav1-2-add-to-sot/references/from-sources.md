# from-sources

The source already lives in `docs/sources/<folder>/`. The note points at those files. The engine copies nothing and does not edit `docs/sources/`.

Pass `from_sources` as that folder, with a trailing slash. Each passage is a path, an optional line span such as `L40-L42`, and the quote. The quote must already be in the file. If a line span is omitted, the engine finds the line.

```json
{
  "title": "Outbound messaging channel",
  "date": "2026-11-25",
  "from_sources": "docs/sources/2026-11-25-outbound-channel/",
  "extractor": {
    "passages": [
      {
        "path": "docs/sources/2026-11-25-outbound-channel/README.md",
        "lines": "L2-L2",
        "quote": "The feed stays on the current channel."
      }
    ]
  }
}
```

A secret in the quote stops the run. This path does not rewrite the source to hide it.

`dry-run` still writes nothing.
