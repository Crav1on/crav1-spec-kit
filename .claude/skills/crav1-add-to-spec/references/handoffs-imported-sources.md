# crav1-add-to-spec: handoff

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0 and from `handoffs.md` in 1.71.1; the rules are unchanged.

## Imported sources

When the new information is a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that will be quoted, or a paste of a mail, transcript, minutes, or chat, follow [references/sources.md](sources.md) (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: this skill’s `references/sources.md`).

Its personal-data and secrets check is in that file; flagged items, the transfer data policy, and the one question are in `references/sources-flagged.md`, and a mail's images in `references/sources-mail.md` and `references/sources-binary.md`, all in `crav1-add-to-spec`.

Write `docs/sources/YYYY-MM-DD-<slug>/` once for that source, before the quote, when this run has not already written that folder. Then add the `Source:` and `Trace:` lines on the quote. Do not commit.

A short fact the user typed, a read-environment fact, and a test suggestion are not imported sources. Do not write `docs/sources/` for those.
