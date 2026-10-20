# crav1-add-to-spec: handoff

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0 and from `handoffs.md` in 1.71.1; the rules are unchanged.

## Imported sources

When the new information is a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that will be quoted, or a paste of a mail, transcript, minutes, or chat, follow [references/sources.md](sources.md) (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`; plugin: this skill’s `references/sources.md`).

That check flags personal data with a keep or redact recommendation. An item it cannot place has no recommendation and is asked, all such items in one questions call. Secrets are redacted, by kind only, and are never a choice. When no transfer data policy exists, it asks once, then may write the rule after a yes. Cursor: `.cursor/rules/crav1-transfer-data-policy.mdc`. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. It never writes a secrets choice into that file. The template is `assets/crav1-transfer-data-policy.mdc`. For a mail, it lists each embedded image, inline or attached. It recommends convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. It asks once. Nothing is written to the source folder until every image has an answer. Auto-accept applies to those recommendations only when the transfer data policy clearly covers them.

Write `docs/sources/YYYY-MM-DD-<slug>/` once for that source, before the quote, when this run has not already written that folder. Then add the `Source:` and `Trace:` lines on the quote. Do not commit.

A short fact the user typed, a read-environment fact, and a test suggestion are not imported sources. Do not write `docs/sources/` for those.
