# Manual flow (1.124.0)

Read this only for `manual-flow`, then [common.md](common.md). Do not open the auto-flow file.

## Start

Call `scope` first. It does not write. One line lists the repos it returned, by name.

One prompt, two questions when a specs-repo row exists and this run did not name it:

- Fetch: `Fetch` (Recommended), `Use what is already on disk`, `Stop`.
- Specs repo: `Leave the specs repo out` (Recommended), `Read its pull request comments this time`. The question text says this run never reads that repo's branches.

No specs-repo row: ask only the fetch question. The repo was named and it is the specs repo: do not ask; say its pull request comments are in and its branches are out.

A word in the invocation answers its question. `fetch` takes Fetch. `no-fetch` takes what is already on disk. `specs-comments` takes the comments. A headless or bot run with neither `fetch` nor `no-fetch` stops and names those two words. It does not fetch.

State the budget in that same prompt's reply, after they answer. Default 20 minutes. A number in the invocation is the budget. Above 45, the script uses 45. Do not ask for a number.

Then `start` with `--yes`. `fetch` is a result of `ok` after a read-only `git fetch`. `no-fetch` is `local`. Do not push or delete.

## Inventory

Build the inventory in [common.md](common.md). Then one question, unless the invocation said `all` or the run is headless (headless `fetch` or `no-fetch` takes every item and writes no spec line):

- Eight or fewer items: `All, one by one` (Recommended), `I'll name which to drop`, `Stop`.
- More than eight: `All, one by one` (Recommended), `All, in small groups`, `I'll name which to drop`, `Stop`.

A small group is at most four items. One by one stays available: they can say so later and the pace changes. `drop` records each named item. Stop calls `pause` and ends.

## Each item

Take the next item from `resume`. Run the note and `Synced at` part of `/crav1-add-to-spec` for that item's command. That part does not need a yes.

If the sort, an `Answered:` line, or a new open question would change a spec, show that change and wait. Yes writes it (`complete --outcome spec`, and `--question` or `--conflict` when that line was written). No leaves the spec alone (`complete --outcome notes` or `synced-at`, no proposal). Do not ask a second time for the same change.

A headless run does not write the spec line. `complete --outcome proposal` with the text, and do not pass `--question` or `--conflict` for a line that was not written.

Nothing to show: complete with `notes`, `synced-at`, or `notes+synced-at` and continue.

Between items, `budget`. When it says stop, finish the item already begun, `pause`, and end. Do not begin another.
