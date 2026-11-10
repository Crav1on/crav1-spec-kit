# Sweep rules (1.124.0)

Both flows use this file. The script `scripts/sweep_progress.py` in this skill owns `docs/system/sweep-progress.md`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Pass `--yes` only after this run is going ahead: after the manual fetch answer, or at the start of auto flow. A call without `--yes` writes nothing.

## Scope

`scope --root <specs repo> --specs-url <origin url>` reads `docs/system/repos.md`. In scope: every row with a URL whose status is not `proposed`, except the specs repo. A named repo narrows to that one row. A proposed row, or a row with no URL, is listed and skipped.

The specs repo is the checkout that holds `docs/specs/`. Match its URL to a row with no trailing `.git`, case ignored, and `dev.azure.com/<org>` the same as `<org>.visualstudio.com`. Its branches are never items. Manual flow reads its pull request comments only after the start question says yes, or when that repo was named. Auto flow reads them only when that repo was named.

Another repo's code is the sibling `../<repo>`. Manual flow, when the folder is missing, asks for a path once in the start prompt (that is part of the fetch question, not a new one). Auto flow, and a headless run, records `missing` and does not ask. No path: that repo is out.

## Fetch

Read-only `git fetch`. Never push, delete, or rebase. Record `note-fetch` before any item:

- `ok` after a fetch
- `local` when manual flow was told not to fetch
- `failed` with the reason (a login that expired is a failure)
- `missing` when no checkout was found
- `signed-out` when `gh` or `az` for that URL is not signed in

`failed` and `missing` skip the repo. `signed-out` still allows branch items from refs already on disk, and skips pull request threads. Do not log in. One Waiting line per skipped repo or rate limit. The run continues.

## Inventory

Unread branches, as skill `crav1-add-to-spec`, `references/branches-sweep.md`: unmerged, commits past `Synced at`, not a base branch. Base branches are `main`, `master`, `develop`, `release/*`, and that row's `Merges into` branch. A stale branch stays in the list. The script rejects a base branch.

Open pull requests, including drafts, from `gh` or `az` for that row's URL. Plus pull requests that closed or merged since the last sweep's inventory time. The first sweep has no earlier time: do not add closed pull requests. The script stores the open numbers and refuses `closed-since` until a finished sweep has been archived.

A branch that is the head of a pull request in this inventory is not its own item. Pass `--head-branch` on the pull request. The pull request item covers its commits and its threads.

Not in the inventory: Slack, mail, issues, and a new `/crav1-review-pr`. Host conversation and review threads are the pull request item. Bot and system threads stay skipped, as skill `crav1-add-to-spec`, `references/pr-comments.md`.

Item commands the script stores:

- branch: `/crav1-add-to-spec code change <repo> <branch>`
- pull request: `/crav1-add-to-spec pr <repo> <n> all`

Run that command's note and `Synced at` rules. The personal-data and secrets check stays inside add-to-spec. In this sweep, do not print add-to-spec's own ending, and do not run the `/crav1-pr-status` it names.

## Read line

When a pull request's threads were read, add or replace one line on its PR note, with the file edit tool, in sorted place by the name `sweep`. Leave every other `Read` line alone.

`- Read: sweep | 7b41a0c, push 6, newest comment 2026-10-26T15:03Z | 2026-10-27`

`read-line` prints the line. `<n>` is the Azure DevOps iteration id, or the GitHub commit count. No comment yet: `newest comment none`. This line is not a person. `since last` on `/crav1-pr-status` does not use it.

## Clock

The budget starts at `start`. Default 20 minutes. The hard stop is 45, which the script will not exceed. Check `budget` between items. Time running out finishes the current item, then `pause`. A later `start` with the same flow and scope keeps done and collected items, resets the clock, and does not ask again for repos already fetched. A different scope while items are pending stops until the user says to replace that run. Replacing keeps the last open-PR list and drops the unfinished queue. Say that before `--replace`.

`Synced at` is still the branch stamp. This file does not write a second sha. Add-to-spec writes the line when the read earned it. When `resume` has no next item, call `finish`.

## Ending

`ending --files <n>` is the run's ending. `<n>` is how many files this run changed and did not commit, counting the progress file when it changed.

Print the proposal lines first when the list is not empty. Then one `Next` line, then each `Waiting` line, then `Uncommitted` when files changed. A commit is not `Next`. A failed fetch is `Waiting`, not `Next`.

Pending items: `Next` is this command, same flow and scope. A conflict or an open question that was written onto a spec: `Next` is `/crav1-resolve-open-questions` for those slugs. Proposals and nothing pending: `Next` is this command's `manual-flow`. Otherwise `Next` is `nothing needed now`.

Do not commit. Do not start a watcher.
