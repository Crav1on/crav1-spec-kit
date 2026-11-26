---
name: crav1-2-add-to-sot
description: >-
  Capture one source as one note under sot/. Use when the user runs
  /crav1-2-add-to-sot with mail, chat, meeting, session, document, fact,
  from-sources, this-session, or dry-run. Kind words combine. Writes the
  note and the event log. Does not commit.
---

# Add to SoT

One invocation writes one note under `sot/`. It does not commit. It does not link a spec. The same words apply in Cursor, Claude Code, and Codex.

## Words

Take a word that is already in the invocation. Do not ask which word it was.

Kind words are `mail`, `chat`, `meeting`, `session`, `document`, and `fact`. Several kind words are still one note. `from-sources`, `this-session`, and `dry-run` are the other words.

If no kind word, `from-sources`, or `this-session` is present, run the engine with no source word. It stops and lists the valid words. Print that list and stop. Do this in chat and in a headless run. Do not guess a word. Do not open a card to pick the word.

## Which file to read

Read only the file for the word that was given:

- `this-session`: `references/this-session.md`
- `from-sources`: `references/from-sources.md`
- any other kind word: `references/capture.md`

`dry-run` stays on that same path and is passed through to the engine.

## Engine

Run `python -X utf8 -m crav1_2` with `~/.crav1-2/engine` on `PYTHONPATH`. In this kit repo, put `v2` on `PYTHONPATH` instead. The project is the working directory. Add `repo <path>` only when the project is somewhere else.

Run `init` once when `.crav1-2/engine.json` is missing. Then run `add-to-sot` and the words, with one JSON object on stdin.

Print the engine's `ending` first when it is present. It already starts with `Run next:`. Do not add a `Next:` line. Do not add a second step. Do not ask a card about writing the event or the index. Do not tell the user to edit a file.

When `dry_run` is true, print the ending, then `note_markdown`, then `events`. Nothing was written.

When `wrote` is false and `card_text` is set, print `proposal` and `card_text` and stop. The ending waits until the card is answered. Pass `keep-all`, `pick-some`, or `stop` back as a word. `pick-some` takes line numbers, for example `pick-some 1 3`.
