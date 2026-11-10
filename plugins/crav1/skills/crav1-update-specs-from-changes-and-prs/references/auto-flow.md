# Auto flow (1.124.0)

Read this only for `auto-flow`, then [common.md](common.md). Do not open the manual-flow file.

## Start

No fetch question. No specs-repo question. The specs repo stays out unless the invocation named that row. Naming it reads its pull request comments and never its branches.

State the budget in one line and go on. Default 20 minutes. A number in the invocation replaces it. Above 45, say the run will use 45 and go on. A headless run uses 20 unless a number was given. Do not ask.

`start` with `--yes`. Do not pass `--include-specs-comments yes` unless the named repo is the specs repo; the script refuses that.

Then a read-only `git fetch` for each repo in scope. Do not push or delete. Record each result. A failure skips that repo. The run continues.

## Queue

Take every item `common.md` would inventory. Do not ask which to drop. Do not drop stale branches; they are items, and their spec text stays a proposal.

For each item, run the note and `Synced at` part of the item's command. Write the PR note, its history, its new Points, and the `Synced at` line the read actually earned. Do not give the yes a sort would need. Do not write a quote, an `Answered:` line, a new open question, or a `Conflict:` line onto a spec.

`complete --outcome proposal` with one short line of that spec change. Notes that were written stay written; the outcome is still `proposal` when any spec line was held back. Do not pass `--question` or `--conflict` unless that line was written onto a spec, which auto flow does not do.

`complete --outcome notes+synced-at` when the only writes were notes and `Synced at`.

## Budget

Check `budget` between items. When it says stop, finish the item already begun, `pause`, and end. Do not begin another. A later invocation resumes the same queue and gets its own budget. It does not redo a done or collected item.

## What the user sees

The proposal list first, then the ending from `ending`. The list is the spec changes this run did not write. Applying them is the manual flow named on `Next` when that is the step.
