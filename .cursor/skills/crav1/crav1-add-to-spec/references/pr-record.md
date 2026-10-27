# The PR record (1.97.0)

One pull request, one PR note, one record. The PR note (`docs/notes/YYYY-MM/YYYY-MM-DD-pr-<repo>-<n>.md`, [notes.md](notes.md) **PR note**) holds a `## PR record` section: what is done, what is left and why, who owes the next step, the merge order and whether it can merge. `/crav1-pr-status`, `/crav1-review-pr`, `/crav1-add-to-spec` and `/crav1-merge-pr` all read and write this one section. There is no separate follow-ups note and no `State on <date>` line any more; a project made before 1.97.0 runs `/crav1-add-to-spec migrate formats` once ([merge-safe.md](merge-safe.md) **Migration**).

## Layout of the PR note

1. Front matter, title, `Source date: … Imported: …`, then the header lines (`URL:`, `Author:`, `<target> <- <source>`). Older notes may also have `State on <date>: <state>` header lines; they stay as they are and are only read.
2. `## PR record`, right after the header lines. Written when missing, by the first skill that needs it.
3. The history: dated sections, each verbatim and never rewritten. Only these headings start a history section: `## Description as of <date>`, `## PR updates as of <date>`, `## Comment as drafted, <date>`, `## Comment as posted, <date> (by <name>)[, edited]`, `## Replies as drafted, <date> (not posted)`, `## Review follow-ups, moved <date>`. A `## ` line inside a description is part of that description.

A new history section goes in **sorted place by date**: before the first history section whose date is later, else at the end. Same date: after the ones already there.

## Record lines

One line per item, `- <Kind>: …`, fields split by ` | `. Kinds, in this order:

| Kind | Line | One per |
| --- | --- | --- |
| Order | `- Order: <after \| before> PR <n> <repo> (<branch>) \| <why, with its source> \| <YYYY-MM-DD>` | other pull request |
| Point | `- Point: <anchor> \| <status> \| <owner> \| <tags or -> \| <text>` | point |
| Read | `- Read: <name> \| <head short sha>, push <n>, newest comment <YYYY-MM-DDTHH:MMZ> \| <YYYY-MM-DD>` | person who ran `/crav1-pr-status` |
| Ready | `- Ready: <yes \| no \| merged> \| <why> \| <YYYY-MM-DD> by <skill>` | pull request |
| State | `- State: <active \| draft \| merged \| abandoned \| closed> \| <YYYY-MM-DD>` | pull request |

Examples:

```text
- Order: after PR 40 orders-api (feat/orders-queue) | merge order asked in thread 106, reply 2026-10-20 | 2026-10-27
- Point: general | needs Robin K. | Alex Doe | thread 106 | Merge order of feat/orders-queue: Sam asks Alex to check with Robin K.
- Point: src/orders/audit.py | waiting on Alex Doe | Alex Doe | thread 104; to decision | 20 s timeouts accepted for the pilot; Sam asks what Alex thinks
- Point: src/orders/retry_store.py:401 | declined | Sam Lee | thread 101 | Random row key: one row per attempt is intended, for traceability; a resend with the same id is a bug upstream
- Point: tests/test_retry_store.py:45 | done 3c9d2e1 | Sam Lee | thread 98; host fixed | Fixture could clean live tables; the local emulator is now forced
- Read: Alex Doe | 7b41a0c, push 6, newest comment 2026-10-26T15:03Z | 2026-10-27
- Ready: no | 1 waiting on Alex Doe; 1 needs Robin K.; after PR 40 (not merged) | 2026-10-27 by pr-status
- State: active | 2026-10-27
```

### Point fields

- **Anchor:** `<path>:<line>`, `<path>:<start>-<end>`, `<path>`, `branch <name>`, or `general`. The path is repo-relative, the line on the source branch when the point was made.
- **Status**, exactly one:
  - `done <short sha>`: the change is in the code. Needs the commit.
  - `agreed`: the other side said yes or will do it; no commit shows it yet.
  - `declined`: the other side will not do it; the text says why.
  - `open`: still being discussed, or not answered yet.
  - `waiting on <name>`: the last message asks that person something or hands them the next step.
  - `needs <name>`: someone outside the thread has to act or answer.
  - `follow-up`: not for this pull request; it becomes later work. `/crav1-ado-sync` reads it like an open note item.
  - `migrated`: written by the migration from an older note; the next `/crav1-pr-status` run sorts it.
- **Owner:** who acts next, as the host shows the name, or `-`.
- **Tags**, `; `-separated, or `-`: `thread <id>`, `host <status>` (the host's thread status: `active`, `fixed`, `wontFix`, `closed`, `byDesign`, `pending`, or GitHub `resolved` / `outdated`), `resolved, code unchanged`, `to spec`, `to decision`, `in spec <slug>`, `asked`, `answered <date>`, `not posted <date>`, `from <skill> <date>`, `from description <date>` (pr-status, from the description's Questions for reviewers or Not in this PR, 1.98.0).
- **Text:** the point in plain words, with the reason when there is one. Last, so it may hold anything except a line break.

## Merge-safe rules

These follow [merge-safe.md](merge-safe.md) so two people's runs rarely conflict:

- Kinds in the order above. Within a kind, in sorted place by key, case ignored: Order by PR number, Point by anchor then text, Read by name.
- A skill changes only its own line: it finds a Point by its thread id, else by anchor and text words (case, spacing and trailing punctuation ignored), and replaces that line where it is. A status or tag change does not move the line. Existing lines are never reordered.
- Change a record line with the host's file edit tool, one edit per line, showing the old and new line. Find the line by reading the note, not with a script; when the words match two lines, ask instead of guessing. The only scripts a record write runs are the ones a skill names (`notes_index.py`) (1.99.1).
- A new line goes in sorted place. `Ready` and `State` are replaced in place; `Read` is one line per person.
- Never delete a Point. A point that no longer applies becomes `declined` or `done <sha>` with the reason in its text.

## Who writes what

| Skill | Writes |
| --- | --- |
| `/crav1-pr-status` | Every kind: classifies each Point, adds Points for new threads and for the description's Questions for reviewers (and Not in this PR on a yes, 1.98.0), sets `Order`, its own `Read`, `Ready` and `State`, and adds `## Replies as drafted` history. |
| `/crav1-review-pr` | One Point per finding, follow-up and question of its review (`open`, `follow-up`, `waiting on <author>` with `asked`), `not posted <date>` tags, `done <sha>` on a re-review, `State`, and the `## Comment as drafted` / `## Comment as posted` history. |
| `/crav1-add-to-spec` | `pr<n> all`: a Point (`open`, `thread <id>`, `host <status>`) for each new thread and the `## PR updates as of` history; `in spec <slug>` when a point is taken into a spec; `answered <date>` when a comment answers a spec open question. |
| `/crav1-merge-pr` | Reads `Ready` before the merge. After the merge: `State: merged` and `Ready: merged`. |

## Reading the record

- `Ready` is stale when a push or a comment on the host is newer than its date; a reader says `stale since <date>` and still shows it.
- A Point whose `host` tag says resolved while its status is `open`, `agreed` or `waiting on …`, with no later push touching its anchor, is flagged `resolved, code unchanged`.
- An old follow-ups note (`review-pr-[<repo>-]<n>-follow-ups.md`) that is still there is read as if its bullets were `migrated` Points, and the run says once: `Old follow-ups note found; run /crav1-add-to-spec migrate formats.`
