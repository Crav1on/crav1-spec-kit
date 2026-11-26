# Capture one source

Use this path for `mail`, `chat`, `meeting`, `session`, `document`, and `fact`. Kind words in the invocation are the note's kinds. Do not ask.

A `fact` is the one sentence the user typed. Build the extractor JSON yourself: one passage, kind `fact`, speaker `user`, quote word for word.

For every other kind, hand the raw text to `crav1-2-source-extractor-agent` and use the JSON it returns. Do not assign passage ids. The engine does.

Screenshots and other originals are copied by the engine. List them as `originals`. Read a screenshot well enough to put its words in a passage quote. Do not retype a secret. The engine removes secret values and records the kind only.

Stdin shape:

```json
{
  "title": "Outbound messaging channel",
  "date": "2026-11-25",
  "added_by": "person A",
  "slug": "outbound-channel",
  "extractor": {
    "passages": [
      {"kind": "chat", "who": "person A", "when": "09:12", "quote": "The channel is agreed long term."}
    ],
    "know": [
      {"heading": "Which options are realistic before go-live?", "body": "The channel is agreed long term.", "cites": [0]}
    ]
  },
  "originals": [
    {"name": "screenshot-1.png", "from": "/path/to/screenshot-1.png"}
  ]
}
```

`cites` are indexes into `passages`, starting at 0. A passage quote is one line.

`dry-run` shows the note and the events and writes nothing. Say `add-to-sot session chat dry-run` when those words were given.
