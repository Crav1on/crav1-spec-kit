# this-session

Capture the chat you are in. The words and the checks are the same in Cursor, Claude Code, and Codex. Only the session file differs, and the engine does that check.

Read the conversation already in context. Ask `crav1-2-source-extractor-agent` for the lines worth keeping. Each line is `finding`, `answer`, `decision`, `open`, or `todo`. The quote is word for word. `who` is `user` or `assistant`. For an answer, set `answers` to the open question's words. Do not close the question. Do not edit `spec.md`.

Set `vendor` to `cursor`, `claude`, or `codex` for the host you are running in. Set `session_id` when the host exposes one. Set `captured_from` is unnecessary: the engine records live context.

```json
{
  "title": "Certificate alert",
  "date": "2026-11-26",
  "vendor": "claude",
  "session_id": "sess-synthetic-1",
  "home": "/tmp/crav1-2-home",
  "compacted": false,
  "extractor": {
    "passages": [
      {
        "kind": "session",
        "who": "user",
        "label": "answer",
        "quote": "The certificate expiry alert goes to person A two weeks before it lapses.",
        "answers": "who gets the certificate expiry alert"
      }
    ]
  }
}
```

Leave `home` unset on a real machine. Set it only when the session files are under a stand-in home. `compacted` true means early turns may be missing. The engine says so on the card and names the `session` word. It does not add a fourth option.

The engine checks quotes:

- Claude Code: `~/.claude/projects/<encoded-repo>/*.jsonl`
- Codex: `~/.codex/sessions/` and `~/.codex/archived_sessions/` when the file names this repo
- Cursor: no readable session file. The note says the quotes were not checked. Do not mark a quote verified yourself.

A quote that is missing from a file that was checked is unverified. An assistant line that was not checked is `ai-summary`.

One card comes before the write: `keep-all`, `pick-some`, or `stop`. `keep-all` is recommended only when a quote was checked against a file. With no checked quote, the card names the missing fact and recommends nothing. Print the engine's `proposal` and `card_text`. Do not write a `Next:` line yet.

A second `this-session` in the same `session_id` adds only new lines (`note.extended`).

If the run parks, a fresh chat resumes from `.crav1-2/sessions/<id>.json`. Run `add-to-sot this-session` with `{}` to show the same card, or pass `keep-all`, `pick-some`, or `stop`. Do not ask the user to paste the chat again or to edit the session file.

When the note holds an answer, the ending names `/crav1-2-link-to-spec`. That command is not in this build. Do not run it. Do not write `Answered:` into the spec.
