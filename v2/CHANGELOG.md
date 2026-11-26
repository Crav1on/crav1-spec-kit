# Changelog

## 2.0.0-alpha.3 (unreleased)

`/crav1-2-link-to-spec` and `crav1-2-gap-finder-agent`. Phase 1 is complete. Not released. No tag.

- link-to-spec reads SoT notes that have not been read against one 1.x spec. Words: none, `note-<id>`, `dry-run`, `resume`, and `park`.
- The gap-finder agent returns JSON. The engine checks it. Each affected item is covered, silent, conflicting, or vague, with cited passages, impact and uncertainty (1-3), what it holds, and proposed text.
- The engine builds the cards and ranks them. A card has 2 to 4 hyphen-only options, each with an impact and an undo, plus skip. A recommendation needs a cited fact. Otherwise the card names the missing fact and who could give it.
- Low-impact gaps that do not say MUST share one card: `accept-all`, `change-some`, or `skip`. MUST is never written on an `asm:` item.
- Questions recorded by `answer.matched` share one card: "These N open questions have answers in the SoT", with `close-all`, `pick-some`, or `skip`. Each closed question gets one decision and an `Answered:` line.
- Write-back adds only `crav1-2:item` lines. No 1.x line changes. `dry-run` writes nothing. `park` and `resume` use the session file, including from a fresh chat.
- A read is recorded as `note.read`, so a later run does not ask the same note again. Installs the skill and the agent for Cursor and Claude Code. Codex stays skipped.

## 2.0.0-alpha.2 (unreleased)

`/crav1-2-add-to-sot` and `/crav1-2-show-sot`. Not released. No tag.

- add-to-sot writes one note, copies originals after secret redaction, appends `note.added`, and rebuilds the views. Kind words combine. `from-sources` writes a thin note and copies nothing. `dry-run` writes nothing. A missing word stops and lists the valid words.
- `this-session` proposes findings, answers, decisions, and open items. One card (`keep-all`, `pick-some`, `stop`) comes before the write. Claude Code and Codex quotes are checked against the session file. Cursor says the quotes were not checked. An answer is recorded with `answer.matched` and the question stays open. A second run adds only new passages (`note.extended`). A parked run resumes from its session file.
- show-sot reads the index, facts, decisions, assumptions, or one topic. It writes nothing.
- The source-extractor agent returns passages and know-about answers. The engine assigns passage ids.
- Installs the skills and the agent for Cursor (local plugin `crav1-2`) and Claude Code. Codex stays skipped.

`/crav1-2-link-to-spec` is not in this version.

## 2.0.0-alpha.1 (unreleased)

The first 2.0 skeleton. Not released. No tag.

- Event log schema v1, append-only, with ULID ids and an ISO time with an offset.
- Fold drops a duplicate id and gives a different body that shares an id a run suffix. Two streams merged in any order fold to the same state.
- Generated `sot/index.md`, `sot/facts.md`, `sot/decisions.md`, and `sot/assumptions.md`. Note pages render passage anchors from the log.
- Session files (`open`, `parked`, `ended`) and `.crav1-2/engine.json`.
- Path guard for the paths 2.0 is allowed to write. 1.x marks and 1.x lines stay put.
- User-level install, uninstall, and status. Codex is skipped because 1.x has no user-level Codex path.
- Alpha `/crav1-2-help` stub, so the install can be checked.

`/crav1-2-add-to-sot`, `/crav1-2-show-sot`, `/crav1-2-link-to-spec`, and this-session are not in this version.
