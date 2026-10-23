# Merge-safe formats (1.84.0)

Two people run the kit on their own machines and merge. These formats keep their additions on different lines, so git merges them without a conflict most of the time. Every skill that writes a `Synced at` stamp, an open question, a `**New:**` line or a glossary row follows this file. `/crav1-finalize-commit` `references/pull.md` resolves what still conflicts.

## Synced at: one line per repo and branch

- **Slice line** in `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`, one line per repo and branch. Example: `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19` on one line and `Synced at: orders-api develop@00344be, 2026-10-15` on the next. A given-up branch ends its line with ` (dropped)`.
- **Repo lines** in `docs/system/repos.md`: a `## Synced at` section right after the repos table, one bullet per repo and branch, `- <repo> <branch>@<short sha>, <date>`. Example: `- orders-api main@abc1234, 2026-10-07`. The table has no `Synced at` column. When the section is missing, add it after the table.
- A new read of a repo and branch replaces only that line. A new repo or branch adds a line in sorted place: by repo, then by branch (plain text order). Never touch another line.
- The short sha is seven characters, the commit the read ended at. The date is the read date, `YYYY-MM-DD`.
- A consumer measuring drift takes, for each repo and branch, the older of the repo line and the slice line. No line means unknown: fall back to spec file commit dates.

## Open questions: matched by their words

- An open question is a `- ` bullet under `## Open questions`. Never a numbered item, and never a stored `Q<n>` prefix.
- `Q1`, `Q2`, … are display numbers only, counted in document order when a skill shows the list. They are never written to a file. A user's `orders Q3` picks the third question shown, then the kit finds it by its words.
- A skill finds a question by its words: the question text, ignoring case, spacing and trailing punctuation. `Blocks:`, `Asked:`, `Pending:` and `Answered:` live under the question they belong to, so they move with it.
- A new question goes in sorted place among the existing top-level bullets: before the first one whose words sort after it (case ignored). Existing questions are never reordered.

## Fixed insert order

Appending always lands at the same spot, the end, so two people's additions collide. A sorted place spreads them out: two different lines almost never sort to the same spot, and git merges inserts at different spots cleanly. Existing lines are never reordered; only the new line's position is decided.

- **`**New:**` lines** in a section: before the first existing `**New:**` line in that run of lines that sorts after the new one, by its date (the first `YYYY-MM-DD` in the line; no date sorts last), then by text. Else after the last one. A `Full source:` line and other lines that belong to it move with it.
- **Glossary rows**: before the first existing row whose term sorts after the new term (case ignored). Else at the end of the table.
- **Synced at lines**: by repo, then branch, as above.
- **Open questions**: by their words, as above.

## Migration

A project made before 1.84.0 runs `/crav1-add-to-spec migrate formats` once after updating. It runs `scripts/merge_safe_migrate.py`: the dry run first, one yes, then the write. It splits `; `-separated `Synced at` lines into one line each, moves the repos table's `Synced at` column into the `## Synced at` section, and turns numbered or `Q<n>`-prefixed open questions into plain bullets. It keeps every line and every entry, checks that nothing was lost before it writes, and a second run changes nothing. It does not commit.
