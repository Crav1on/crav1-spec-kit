---
name: crav1-update-specs-from-changes-and-prs
description: >-
  Use when the user wants changed branches and open or recently closed
  pull requests, with their conversation and review threads, brought
  into the specs across linked repos. manual-flow confirms the
  inventory and each spec write. auto-flow writes notes and Synced at
  only and lists spec changes as proposals. Optional repo. Not a starter.
disable-model-invocation: true
---

# Update specs from changes and pull requests

One command sweeps the linked repos, finds changed branches and open or recently closed pull requests, and feeds each one through `/crav1-add-to-spec`. It is its own skill. It is not a choice on `/crav1-add-to-spec`.

Command: `/crav1-update-specs-from-changes-and-prs`.

This is cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill, not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`.

## Flow words (1.124.0)

Route first, load second. The word after the command is the flow. A repo name from `docs/system/repos.md` may follow. A whole number of minutes may follow. Do not ask the user to type brackets.

- **No flow word:** ask one question. Options: `manual-flow` (Recommended), `auto-flow`. A headless or bot run with no word stops and names those two words. It does not guess.
- **`manual-flow`:** read [references/manual-flow.md](references/manual-flow.md), then [references/common.md](references/common.md). Do not open `references/auto-flow.md`.
- **`auto-flow`:** read [references/auto-flow.md](references/auto-flow.md), then [references/common.md](references/common.md). Do not open `references/manual-flow.md`.

Both flows use `scripts/sweep_progress.py` in this skill. That script is the state machine. Do not keep a second copy of its gates in chat, and do not hand-edit `docs/system/sweep-progress.md`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

## What the words change

The inventory is the same. Manual flow asks once before fetching, then confirms the inventory, then shows each spec change before it is written. One by one is the pace. Small groups are offered when there are many. Auto flow fetches without asking and writes notes and `Synced at` only. Every spec change stays a proposal.

## Runs these

This skill runs `/crav1-add-to-spec` for each item, with the choice words in [references/common.md](references/common.md). An inner ending is not this run's ending. Do not print it.

It does not run `/crav1-review-pr`, `/crav1-pr-status`, `/crav1-resolve-open-questions`, `/crav1-finalize-commit`, or `/crav1-tighten-spec`. It does not commit, push, delete, post, vote, or resolve a thread.

## Stop

Do not invent a repo that is not in `repos.md`. Do not read Slack, mail, or issues. Do not sweep a base branch. The specs repo's branches are never read.

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says. The lines come from the script's `ending` command. Print proposals first when that list is not empty, then `Next`, then `Waiting`, then `Uncommitted`. Do not run the next step.
