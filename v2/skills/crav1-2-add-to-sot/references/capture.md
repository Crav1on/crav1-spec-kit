# Capture one source

Use this path for `mail`, `chat`, `meeting`, `session`, `document`, and `fact`. Kind words in the invocation are the note's kinds. Do not ask.

A `fact` is the one sentence the user typed. Build the extractor JSON yourself: one passage, kind `fact`, speaker `user`, quote word for word.

For every other kind, hand the raw text to `crav1-2-source-extractor-agent` and use the JSON it returns. Do not assign passage ids. The engine does.

In this project's `sot/`, a quote stays word for word, including the names the source uses. Do not replace a name with person A, person B, or partner B. Do not write `[redacted: personal data]`. Remove only a secret value (a key, a token, or a password). The engine removes secret values and records the kind. The names in the example below are synthetic. A real source keeps its own names.

`date` is the source date. Leave it as the day the source is about. The engine sets the Added date from its own clock. Do not copy the source date into Added.

`added_by` is the person running the command. Read `git config user.name` and pass that name, unless the user names a different person. Do not use a speaker's name. Leave `added_by` unset when you cannot know it; the engine reads git. The engine refuses a name that matches a speaker.

A mail file is an original. Pass its path as `source`. The engine copies that file into the note and removes secret values. Do not skip the mail file, and do not leave the copy to the extractor. A `.eml` word on the command is the same path. Screenshots and other files still go in `originals`.

A mail passage's `when` is the date and time it was sent, `YYYY-MM-DD HH:MM`, plus a zone when the mail has one (`2026-11-24 15:57+01:00`). Do not drop the day. A same-day chat may use `HH:MM`. The note shows the value as given.

Stdin shape:

```json
{
  "title": "Outbound messaging channel",
  "date": "2026-11-24",
  "added_by": "Alex Example",
  "slug": "outbound-channel",
  "source": "inbox/thread.eml",
  "extractor": {
    "passages": [
      {"kind": "mail", "who": "Jordan Example", "when": "2026-11-24 15:57+01:00", "quote": "The channel is agreed long term."}
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

`dry-run` shows the note and the events and writes nothing. Say `add-to-sot mail dry-run` when those words were given.
