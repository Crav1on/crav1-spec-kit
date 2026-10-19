# Branches (1.64.0)

One spec can have its work on several branches, and in several repos. This file is the rule for every skill that reads a spec's branches, works out where a branch split off, or reports whether the work is merged. Everything here is read-only git on the refs already on disk. Never fetch, check out, commit, or push because of this file.

Examples use made-up names: the spec repo `orders-specs`, the code repo `orders-api`, which merges into `develop`, and the branches `feat/orders-retry`, `feature/orders-openapi` and `feature/orders-export`.

## Where each branch is named

- **`Synced at` slice line** in `spec.md`, one line per repo, one entry per branch, separated by `; `: `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`. An entry may end in `(dropped)`.
- **Match `Branch:` list** under `## Match`: `- Branch: feat/orders-retry; feature/orders-openapi`. When the spec spans repos, an item may start with the repo: `- Branch: orders-api feat/orders-retry`. An item may end in `(into <branch>)`, written by hand in 1.64.0 (the kit reads it; it doesn't offer it yet).
- **Task branch** at the end of a task line in `tasks.md`: `(branch: feat/orders-retry)`, or `(branch: orders-api feat/orders-retry)` when the spec spans repos.

A spec's **work branches**, per repo, are every branch named in those three places, minus the base branches and minus entries marked `(dropped)`.

## Base branch and Merges into

- `docs/system/repos.md` has an optional `Merges into` column. Its cell names the branch the repo's work merges into, for example `develop`. Empty, or no column, means the default branch: the branch `origin/HEAD` points at, else `main`, else `master`.
- A repo's **base branches** are its `Merges into` branch and its default branch. A base branch is never a work branch that still has to merge. Its `Synced at` entry is only a read stamp.
- A branch's **into branch** is its `(into …)` marker, else the repo's `Merges into` branch, else the default branch.

## Which refs

Use the remote copy (`origin/<name>`) when it exists, and the local branch otherwise. Never fetch. Each report names the age of each remote copy it used, from the date of its newest commit, for example `origin/develop newest commit 2026-10-17 (2 days old)`, so stale refs are visible. Say `fetch to refresh` once when a copy is older than seven days. Do not run the fetch.

## Sibling checkout

The code of a repo other than the open one is read from `../<repo>`, the folder with that repo's name next to the spec repo. When it isn't there, ask for the path with options only: the sibling folders that are git checkouts, plus Other. A headless run stops and names the repo: `No checkout found for <repo>. Name its path.` The sibling checkout is read-only: never check out, fetch, commit, or write there. Notes, spec points and `Synced at` go into the spec repo.

## Fork point

For branch B in repo R, the candidates are:

1. B's `(into …)` branch, when it has one; then it is the parent and the search below doesn't run
2. R's `Merges into` branch, else the default branch
3. the default branch
4. every other work branch of the same spec in R (stacked branches)

For each candidate C, take `git merge-base B C` and count B's own commits since then (`git rev-list --count <merge-base>..B`). The candidate with the fewest own commits is the parent. Another spec branch C counts only when B really sits on it: the merge-base of B and C is not already in B's base branch (`git merge-base --is-ancestor <merge-base> <base>` fails). Two branches cut from the same `develop` commit share that commit as their merge-base, and neither is the other's parent. On a tie, prefer a spec branch that counts (stacked), then the `Merges into` branch, then the default branch. The change is the commits from that split point to B's tip. Name it in the report: `Branch diff of feature/orders-openapi from develop (split at 00344be): 1 commit.`

When no candidate shares history with B (a shallow clone, or the branch is missing), say so and fall back to the default branch. When even that fails, ask with options only: the repo's branches, plus **A commit range instead**. A headless run stops: `No fork point found for <branch>. Name a commit range.`

## Merged

A work branch is **merged** into its into branch when any of these holds:

1. its tip is contained in the into branch (`git merge-base --is-ancestor <tip> <into>`)
2. every commit on it is already in the into branch as the same change (`git cherry <into> <branch>` shows no `+` line; this is `git patch-id` matching)
3. the host shows its pull request merged. Only for a GitHub remote with `gh`, or an Azure DevOps remote with `az`, and only when that CLI is already signed in. Read-only: `gh pr list --head <branch> --state merged`, `az repos pr list --source-branch <branch> --status completed`. This is the only way to see a squash merge. Any other host, or a missing or signed-out CLI, skips this test; say which (`gh is not signed in`, `no host check for this remote`). Never log in or install anything.

## Gone, rewritten, shared

- **Gone** means neither the local branch nor `origin/<name>` exists. A gone branch is **merged** when the SHA in its `Synced at` entry is contained in the into branch, or the `commits:` of the notes that imported it are all in the into branch as the same change, or the host shows its PR merged (test 3). The report says `merged, branch deleted`. Only a branch that is gone and not merged by any of these is `unknown (branch gone)`: then the spec isn't done, and `/crav1-tighten-spec` offers `(dropped)` for it.
- **Rewritten** means the SHA in a branch's `Synced at` entry no longer exists on disk, or is not an ancestor of the branch tip (a rebase or a force push). Say `<branch>: branch rewritten since last read (was <sha>)`. Measure that branch from its fork point, not from the old SHA. Match its commits by content (`git patch-id`) so nothing already imported is imported again. Never stop with an error because a SHA is missing. The next read replaces the entry.
- **Shared** means one branch is listed in several specs. Report it under each spec that lists it, followed by `(also in <other slug>)`. A count across specs (the build-features board, help `where am I`) counts each branch once. One code-change note serves every spec it feeds (its `used_by` lists each one); never write a second note for the same commits.

## The Branches line

The same line everywhere, per repo, after the base branch is known:

`Branches: 1 of 3 merged into develop. Not merged: feat/orders-retry (2 commits), feature/orders-export (3 commits). origin/develop newest commit 2026-10-17.`

Commit counts are own commits since the fork point. Add `merged, branch deleted`, `branch rewritten since last read`, `unknown (branch gone)` and `(also in <slug>)` where they apply. A spec with no work branches has no Branches line. Done across branches means every work branch is merged into its into branch, and the tasks are done by today's rules. This is report only: no skill writes a Match `Status:` line, a mark, or any file because of it.
