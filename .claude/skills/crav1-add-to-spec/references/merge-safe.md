# Merge-safe formats (1.84.0, Branch lines 1.86.0, PR record 1.97.0)

Two people run the kit on their own machines and merge. These formats keep their additions on different lines, so git merges them without a conflict most of the time. Every skill that writes a `Synced at` stamp, a Match `Branch:` line, an open question, a `**New:**` line or a glossary row follows this file. `/crav1-finalize-commit` `references/pull.md` resolves what still conflicts.

## Synced at: one line per repo and branch

- **Slice line** in `spec.md`, after the title and before the first heading: `Synced at: <repo> <branch>@<short sha>, <date>`, one line per repo and branch. Example: `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19` on one line and `Synced at: orders-api develop@00344be, 2026-10-15` on the next. A given-up branch ends its line with ` (dropped)`.
- **Repo lines** in `docs/system/repos.md`: a `## Synced at` section right after the repos table, one bullet per repo and branch, `- <repo> <branch>@<short sha>, <date>`. Example: `- orders-api main@abc1234, 2026-10-07`. The table has no `Synced at` column. When the section is missing, add it after the table.
- A new read of a repo and branch replaces only that line. A new repo or branch adds a line in sorted place: by repo, then by branch (plain text order). Never touch another line.
- The short sha is seven characters, the commit the read ended at. The date is the read date, `YYYY-MM-DD`.
- A consumer measuring drift takes, for each repo and branch, the older of the repo line and the slice line. No line means unknown: fall back to spec file commit dates.

## Match Branch: one line per branch (1.86.0)

- Under `## Match`, one line per branch: `- Branch: [<repo> ]<branch>[ (into <branch>)| (spec branch)][ (PR <n>)]`. Example: `- Branch: orders-api feat/orders-capacity (spec branch)` on one line and `- Branch: orders-api feat/orders-capacity-t3 (into feat/orders-capacity)` on the next. Never `; `-joined. A spec with no `## Match` may hold the same lines without `- ` after the title.
- A new branch adds a line in sorted place among the `Branch:` lines: by repo, then by branch (plain text order, case ignored; a line with no repo sorts as an empty repo). Markers are not part of the sort.
- A marker for a listed branch (`(into …)`, `(spec branch)`, `(PR <n>)`) is written on that branch's own line only. Never touch another line.

## Open questions: matched by their words

- An open question is a `- ` bullet under `## Open questions`. Never a numbered item, and never a stored `Q<n>` prefix.
- `Q1`, `Q2`, … are display numbers only, counted in document order when a skill shows the list. They are never written to a file. A user's `orders Q3` picks the third question shown, then the kit finds it by its words.
- A skill finds a question by its words: the question text, ignoring case, spacing and trailing punctuation. `Blocks:`, `Asked:`, `Pending:` and `Answered:` live under the question they belong to, so they move with it.
- A new question goes in sorted place among the existing top-level bullets: before the first one whose words sort after it (case ignored). Existing questions are never reordered.

## PR record: one line per item (1.97.0)

The PR note's `## PR record` holds one line per point, other pull request, reader, readiness and state, in sorted place, as [pr-record.md](pr-record.md) says. A skill replaces only its own line, in place; a new line goes in sorted place; existing lines never move; a Point is never deleted. New history sections go in sorted place by date.

## Fixed insert order

Appending always lands at the same spot, the end, so two people's additions collide. A sorted place spreads them out: two different lines almost never sort to the same spot, and git merges inserts at different spots cleanly. Existing lines are never reordered; only the new line's position is decided.

- **`**New:**` lines** in a section: before the first existing `**New:**` line in that run of lines that sorts after the new one, by its date (the first `YYYY-MM-DD` in the line; no date sorts last), then by text. Else after the last one. A `Full source:` line and other lines that belong to it move with it.
- **Glossary rows**: before the first existing row whose term sorts after the new term (case ignored). Else at the end of the table.
- **Synced at lines**: by repo, then branch, as above.
- **Match `Branch:` lines**: by repo, then branch, as above.
- **Open questions**: by their words, as above.

## Migration

A project made before 1.84.0 runs `/crav1-add-to-spec migrate formats` once after updating. It runs `scripts/merge_safe_migrate.py`: the dry run first, one yes, then the write. It splits `; `-separated `Synced at` lines into one line each, moves the repos table's `Synced at` column into the `## Synced at` section, turns numbered or `Q<n>`-prefixed open questions into plain bullets, and (1.86.0) splits `; `-joined Match `Branch:` lists into one line per branch, markers kept. A project already on 1.84.0 runs it again after 1.86.0. A project made before 1.97.0 runs it again: (1.97.0) every PR note (`kind: pull request`) gets its `## PR record` with a `State` line from the newest `State on <date>` mention, and each review-pr follow-ups note (`review-pr-[<repo>-]<n>-follow-ups.md`, linked by `pr_note:` or by its pull request number and repo) moves into its PR note: one `Point` per bullet with the text verbatim (status `migrated`, or `done <sha>` for `(done in <sha>)`; tags `not posted`, `asked`, `answered` from its marks), its dated comment sections into the history by date, its intro and bullets into `## Review follow-ups, moved <date>`, its front matter into one `Moved from` line, `used_by` and `waiting_for` merged. Then the old file is deleted, repo-path mentions of it are rewritten, and the notes indexes are rebuilt. Thread sections are not turned into Points; the first `/crav1-pr-status` run does that. A follow-ups note with no PR note is left alone with a `NO PR NOTE` line. It keeps every line and every entry, checks that nothing was lost before it writes (a `LOST` line means that note was left alone and the run exits 2), and a second run changes nothing. `--dry-run` prints a unified diff of every change. It does not commit.

Run from the product repo root (drop-in path shown; plugin: the same script under `skills/crav1-add-to-spec/scripts/`):

```text
python3 .claude/skills/crav1-add-to-spec/scripts/merge_safe_migrate.py --dry-run
python3 .claude/skills/crav1-add-to-spec/scripts/merge_safe_migrate.py
python3 .claude/skills/crav1-add-to-spec/scripts/merge_safe_migrate.py --check
```
