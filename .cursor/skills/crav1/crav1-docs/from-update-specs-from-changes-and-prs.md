# Update specs from changes and pull requests

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when several linked repos have branches and pull requests you have not brought into the specs yet. The command is [`/crav1-update-specs-from-changes-and-prs`](reference/skills/crav1-update-specs-from-changes-and-prs.md).

This is cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill, not a starter option.

## Two flows

The word picks the flow. A repo name from `docs/system/repos.md` may follow. A whole number of minutes may follow. You do not type brackets.

| You type | What happens |
| --- | --- |
| `/crav1-update-specs-from-changes-and-prs manual-flow` | Asks once before fetching, then you confirm the inventory, then each spec change is shown before it is written |
| `/crav1-update-specs-from-changes-and-prs manual-flow orders-api` | The same, for that one row |
| `/crav1-update-specs-from-changes-and-prs auto-flow` | Fetches without asking. Notes and `Synced at` are written. Spec changes stay a proposal list |
| `/crav1-update-specs-from-changes-and-prs auto-flow 30` | The same, with a 30 minute budget |
| `/crav1-update-specs-from-changes-and-prs` | Asks which flow. A headless run with no word stops and names the two words |

Both flows follow the same inventory and the same state machine, `scripts/sweep_progress.py` in the skill. Pick the interpreter as [Running a kit script](reference/running-scripts.md) says. Do not edit `docs/system/sweep-progress.md` by hand.

## What it looks at

Every `docs/system/repos.md` row with a URL that is not `proposed`, except the specs repo. Manual flow asks, in that same start prompt, whether to read the specs repo's pull request comments this time. Auto flow leaves the specs repo out unless you named it. Neither flow reads the specs repo's branches.

For each repo in scope: unmerged branches with commits past `Synced at`, open pull requests including drafts, and pull requests that closed since the last sweep. The first sweep has no earlier list, so it does not go back through old closed pull requests. Each pull request includes its conversation and review threads. A branch that is the head of one of those pull requests is not listed twice.

Left out: `main`, `master`, `develop`, `release/*`, and the row's `Merges into` branch. Also Slack, mail, issues, and a new review. The sweep does not run `/crav1-review-pr` or `/crav1-pr-status`.

## Fetch

Manual flow asks once, with the repo names on one line. Fetch is the usual answer. You can use what is already on disk. Auto flow fetches without asking. The fetch is read-only. A repo whose fetch fails, or whose checkout is missing, is skipped and named under Waiting. The rest of the run continues. The command does not log in, push, or delete.

## Manual pace

The inventory confirm comes first. You can drop items. Then the run goes one by one. When there are more than eight items it also offers small groups, at most four, and one by one stays available. A change to a spec is shown before it is written. Notes and `Synced at` do not each wait for a yes.

## Auto flow

Before the fetch you see the budget. **20 minutes** unless you passed another number. The run will not go past **45**. It does not stop to ask you to confirm a sort. It also does not pretend you did. Quotes, new open questions, and `Answered:` lines stay on the proposal list. The progress file keeps that list.

The clock is checked between items. When the time is used, the current item finishes, the place is saved, and the run stops. A later run of the same flow and scope continues the queue. It does not redo a finished item. Nothing watches between runs.

## Where the place is saved

`docs/system/sweep-progress.md` in the specs repo lists this run's items and which are done. A pull request whose threads were read gets one line on its PR note:

`- Read: sweep | 7b41a0c, push 6, newest comment 2026-10-26T15:03Z | 2026-10-27`

That line is the sweep's watermark. It is not yours. `/crav1-pr-status` `since last` still uses your own `Read` line.

`Synced at` stays the branch stamp. This command does not write a second sha.

## After

Proposals, when there are any, are printed first. Then one `Next` line.

When items are still pending, `Next` is this same command, because the queue is not finished. When a conflict or an open question was written onto a spec, `Next` is `/crav1-resolve-open-questions` for those slugs. When the only leftover is proposals, `Next` is `/crav1-update-specs-from-changes-and-prs manual-flow`, because those spec changes are not written yet. Otherwise `Next` is `nothing needed now`.

A repo that was skipped is a `Waiting` line. When files changed: `Uncommitted: 2 files; commit with /crav1-finalize-commit when ready.` This command does not commit, and it does not run the next step. See [How a run ends](reference/run-ending.md).

Reference page: [update specs from changes and pull requests](reference/skills/crav1-update-specs-from-changes-and-prs.md)
