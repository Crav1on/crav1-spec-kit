# Branches sweep (1.79.0)

Read only on `branches`, as in `/crav1-add-to-spec branches` or `/crav1-add-to-spec orders-api branches` (a repo from `docs/system/repos.md`). It is the code-change branch, run once per chosen branch.

## List

Read-only. Never fetch, push or delete. Use local branches and the remote-tracking copies already on disk (one entry per branch name; the newer tip wins).

Keep a branch when it is not merged into its base ([branches.md](branches.md) **Base branch and Merges into**, **Merged**) and has commits not yet read: past its `Synced at` and not dropped by the overlap check of [notes.md](notes.md). Leave out merged branches, branches with nothing new, and the base branches. No date cutoff.

One line per branch: new commit count, last commit date, and the age of its remote copy (`remote: 4 days`, or `local only`). No commit in 3 months or more: add `stale (no commits since <date>)`, as the Azure DevOps and GitHub Stale views do. A stale branch stays listed.

Nothing to list: say so and stop.

## Confirm

One question:

- A) Yes, all
- B) Yes, skip the stale ones
- C) Name the ones I want
- D) Stop

`branches all` takes A and `branches skip stale` takes B without asking. A headless or bot run with neither stops: `Missing choice. Use one of: branches all, branches skip stale.`

## Import

For each chosen branch, run the branch import of `branches/code-change/BRANCH.md`: diff from its parent, overlap, PR note lookup, `Synced at`, the `Branch:` list. A commit shared by two branches is imported once, with the first branch; the other says `<n> commits already in <note>`. Show all sorts in one batch with one confirmation at the end, plus that batch's into and Merges into questions.

## Report

One line per branch imported. Name each stale branch left out once, as `<branch>: stale since <date>, worth deleting on the host`. The kit does not delete it.
