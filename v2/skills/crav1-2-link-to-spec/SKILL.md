---
name: crav1-2-link-to-spec
description: >-
  Link unread SoT notes into one 1.x spec. Use when the user runs
  /crav1-2-link-to-spec with a spec slug, note-<id>, dry-run, resume, or
  park. Shows cards, then writes item lines. Does not commit.
---

# Link to spec

One invocation reads SoT notes that have not been read against one 1.x spec. It does not commit. The gap-finder agent returns JSON. The engine builds the cards, writes the events, and writes the item lines.

## Words

Take a word that is already in the invocation. Do not ask which word it was.

| Word | Meaning |
| --- | --- |
| (none) | every note not yet read against this spec |
| `note-<id>` | one note, for example `note-2026-11-25-outbound-channel` |
| `dry-run` | show the cards and the proposed items, write nothing |
| `resume` | carry on a parked run from its session file |
| `park` | stop and keep that run for resume |

## Which file to read

- `resume`, `park`, or a card word: `references/cards.md`
- any other word, including a slug on its own: `references/read.md`

Card words are `skip`, `close-all`, `pick-some`, `accept-all`, `change-some`, `add-pointer`, `open-question`, `leave-out`, `prefer-source`, `keep-spec`, `ask-owner`, and `use-proposed`. `dry-run` stays on the read path.

## Engine

Run `python -X utf8 -m crav1_2` with `~/.crav1-2/engine` on `PYTHONPATH`. In this kit repo, put `v2` on `PYTHONPATH` instead. The project is the working directory. Add `repo <path>` only when the project is somewhere else.

Run `init` once when `.crav1-2/engine.json` is missing. Then run `link-to-spec` and the words, with one JSON object on stdin. Send `{}` when there is no finder JSON yet.

Print the engine's `ending` first when it is present. It already starts with `Run next:`. Do not add a `Next:` line. Do not add a second step. Do not ask a card about writing the event or the index. Do not tell the user to edit a file.

When `dry_run` is true, print every entry in `cards`, then `proposed_items`. Nothing was written.

When `needs_finder` is true, follow `references/read.md`.

When `wrote` is false and `card_text` is set, print `card_text` and stop. The ending waits until the card is answered.
