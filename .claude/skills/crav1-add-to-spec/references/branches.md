# Branches (1.64.0)

One spec can have its work on several branches, and in several repos. This file is the rule for every skill that reads a spec's branches, works out where a branch split off, or reports whether the work is merged. Everything here is read-only git on the refs already on disk. Never fetch, check out, commit, or push because of this file.

Examples use made-up names: the spec repo `orders-specs`, the code repo `orders-api`, which merges into `develop`, and the branches `feat/orders-retry`, `feature/orders-openapi` and `feature/orders-export`.

## Where each branch is named

- **`Synced at` slice line** in `spec.md`, one line per repo, one entry per branch, separated by `; `: `Synced at: orders-api feat/orders-retry@155b5c4, 2026-10-19; develop@00344be, 2026-10-15`. An entry may end in `(dropped)`.
- **Match `Branch:` list** under `## Match`: `- Branch: feat/orders-retry; feature/orders-openapi`. When the spec spans repos, an item may start with the repo: `- Branch: orders-api feat/orders-retry`. An item may end in `(into <branch>)` (it merges into that branch, not the base; offered and written after a yes since 1.68.0) or `(spec branch)` (the spec's long-lived branch that its task sub-branches merge into, 1.68.0): `- Branch: orders-api feat/orders-capacity (spec branch); feat/orders-capacity-t3 (into feat/orders-capacity)`.
- **Task branch** at the end of a task line in `tasks.md`: `(branch: feat/orders-retry)`, or `(branch: orders-api feat/orders-retry)` when the spec spans repos.

A spec's **work branches**, per repo, are every branch named in those three places, minus the base branches and minus entries marked `(dropped)`.

## Base branch and Merges into

- `docs/system/repos.md` has an optional `Merges into` column. Its cell names the branch the repo's work merges into, for example `develop`. Empty, or no column, means the default branch: the branch `origin/HEAD` points at, else `main`, else `master`.
- A repo's **base branches** are its `Merges into` branch and its default branch. A base branch is never a work branch that still has to merge. Its `Synced at` entry is only a read stamp.
- A branch's **into branch** is its `(into …)` marker, else the repo's `Merges into` branch, else the default branch.

## Which refs

Use the remote copy (`origin/<name>`) when it exists, and the local branch otherwise. Never fetch. Each report names the age of each remote copy it used, from the date of its newest commit, for example `origin/develop newest commit 2026-10-17 (2 days old)`, so stale refs are visible. Count the age in whole calendar days (1.67.1): today's local date minus the commit's committer date in local time (`git log -1 --format=%cd --date=short-local <ref>`), not counting the commit day itself and never rounding up. A commit made today is `today`, yesterday is `1 day old`. Say `fetch to refresh` once when a copy is older than seven days. Do not run the fetch.

## Sibling checkout

The code of a repo other than the open one is read from `../<repo>`, the folder with that repo's name next to the spec repo. When it isn't there, ask for the path with options only: the sibling folders that are git checkouts, plus Other. A headless run stops and names the repo: `No checkout found for <repo>. Name its path.` The sibling checkout is read-only: never check out, fetch, commit, or write there. One exception (1.65.0): `/crav1-review-pr`, for an Azure DevOps pull request whose branches on disk are missing or older than the pull request, may fetch only that pull request's two branches there, after the user picks **Fetch only the PR's two branches** or a bot passes `fetch pr branches`. Notes, spec points and `Synced at` go into the spec repo.

## Fork point

For branch B in repo R, the candidates are:

1. B's `(into …)` branch, when it has one; then it is the parent and the search below doesn't run
2. R's `Merges into` branch, else the default branch
3. the default branch
4. when R's `Merges into` cell is empty (1.64.1): the integration branches that exist on disk, by name: `develop`, `development`, `dev`, `integration`. This is how a repo whose work merges into `develop` is found before the cell is filled; the code-change question then offers to record it
5. every other work branch of the same spec in R (stacked branches); since 1.68.0 never a branch whose `(into …)` names B (B's own sub-branch), and none at all when B is marked `(spec branch)`: a spec branch's parent comes from the base candidates only

Candidates 2 to 4 are the **base candidates**.

For each candidate C, take `git merge-base B C` and count B's own commits since then (`git rev-list --count <merge-base>..B`). The candidate with the fewest own commits is the parent. Another spec branch C counts only when B really sits on it (1.64.1): the merge-base of B and C is not B's own tip (C is built on B, or already contains it), and it is not already in any base candidate (`git merge-base --is-ancestor <merge-base> <candidate>` fails for each). Two branches cut from the same `develop` commit share that commit as their merge-base, and neither is the other's parent. On a tie, prefer a spec branch that counts (stacked), then the `Merges into` branch, then the default branch. The change is the commits from that split point to B's tip. Name it in the report: `Branch diff of feature/orders-openapi from develop (split at 00344be): 1 commit.`

When no candidate shares history with B (a shallow clone, or the branch is missing), say so and fall back to the default branch. When even that fails, ask with options only: the repo's branches, plus **A commit range instead**. A headless run stops: `No fork point found for <branch>. Name a commit range.`

## Merged

A work branch is **merged** into its into branch when any of these holds:

1. its tip is contained in the into branch (`git merge-base --is-ancestor <tip> <into>`)
2. every commit on it is already in the into branch as the same change (`git cherry <into> <branch>` shows no `+` line; this is `git patch-id` matching)
3. the host shows its pull request merged. Only for a GitHub remote with `gh`, or an Azure DevOps remote with `az`, and only when that CLI is already signed in. Read-only: `gh pr list --head <branch> --state merged`, `az repos pr list --source-branch <branch> --status completed`. This is the only way to see a squash merge. Any other host, or a missing or signed-out CLI, skips this test; say which (`gh is not signed in`, `no host check for this remote`). Never log in or install anything.

## Gone, rewritten, shared

- **Gone** means neither the local branch nor `origin/<name>` exists. A gone branch is **merged** when the SHA in its `Synced at` entry is contained in the into branch, or the `commits:` of the notes that imported it are all in the into branch as the same change, or the host shows its PR merged (test 3). The report says `merged, branch deleted`. Only a branch that is gone and not merged by any of these is `unknown (branch gone)`: then the spec isn't done, and `/crav1-tighten-spec` offers `(dropped)` for it.
- **Rewritten** means the SHA in a branch's `Synced at` entry no longer exists on disk, or is not an ancestor of the branch tip (a rebase or a force push). Say `<branch>: branch rewritten since last read (was <sha>)`. Measure that branch from its fork point, not from the old SHA. Match its commits by content (`git patch-id`) so nothing already imported is imported again. When an imported commit is no longer on disk (pruned after the force push), its commit line in the note (`<short sha> <author date> <subject>`, 1.64.1) is the key: a commit with the same author date and subject is the same change, and the report says so. Never stop with an error because a SHA is missing. The next read replaces the entry.
- **Shared** means one branch is listed in several specs. Report it under each spec that lists it, followed by `(also in <other slug>)`. A count across specs (the build-features board, help `where am I`) counts each branch once. One code-change note serves every spec it feeds (its `used_by` lists each one); never write a second note for the same commits.

## The Branches line

The same line everywhere, per repo, after the base branch is known:

`Branches: 1 of 3 merged into develop. Not merged: feat/orders-retry (2 commits), feature/orders-export (3 commits). origin/develop newest commit 2026-10-17.`

Commit counts are own commits since the fork point. Add `merged, branch deleted`, `branch rewritten since last read`, `unknown (branch gone)` `(also in <slug>)` and (1.68.0) `merged, reverted on <base> (<sha>)` where they apply. Sub-branches (1.68.0) are left out of this count; they get their own `Sub-branches:` line, and done counts top-level branches only. A spec with no work branches has no Branches line. Done across branches means every work branch is merged into its into branch, and the tasks are done by today's rules. This is report only: no skill writes a Match `Status:` line, a mark, or any file because of it.

## Spec branch and sub-branches (1.68.0)

Setup 4: the spec has a long-lived **spec branch**, a normal work branch, usually `feat/<slug>` (never `spec/<slug>`, which means specify only). Each task gets a short **sub-branch**, for example `feat/orders-capacity-t3`, that merges into the spec branch; the spec branch later merges into the base branch.

- **Markers.** A sub-branch carries `(into <spec branch>)` on the Match `Branch:` list. The spec branch may carry `(spec branch)` so the setup reads at a glance. Both are written only after a yes, by `/crav1-add-to-spec` code change, `/crav1-tighten-spec`, `/crav1-create-feature-branch` and `/crav1-build-tasks` (when they create a sub-branch), or by hand. A marker already there is never changed or removed by the kit.
- **The into question.** When the fork-point search (no `(into …)` marker) finds that a branch's closest parent is another spec branch, ask one yes/no question: "feat/orders-capacity-t3 split off feat/orders-capacity. Does it merge into feat/orders-capacity?" A yes writes `(into feat/orders-capacity)` on that branch's entry (adding the entry when the branch isn't listed yet) and, when the parent carries no marker, `(spec branch)` on the parent's entry (adding it too). A no writes nothing, and the branch is treated as stacked (setup 3). A **headless run doesn't ask, writes nothing, and treats the branch as stacked**; it says so in the report.
- **Fork point.** A branch with `(into X)` always has X as its parent (candidate 1 above).
- **Commit list.** List commits with `git log --no-merges`. A merge commit that changes code beyond its two sides (for example a conflict fix) is listed in the sort for the user to keep or drop.
- **Spec branch read after its sub-branches.** Its range runs from where it split off the base branch to its tip, so it holds the merged sub-branch commits. The overlap check drops every commit already in a sub-branch note (`commits:` and `git patch-id`); only commits made directly on the spec branch are imported. A sub-branch squash-merged into the spec branch is one new commit no patch-id matches: it counts as covered when the host (test 3 under **Merged**) shows that sub-branch's PR merged as that commit; otherwise list it on the sort as `may already be in <note>` for the user to keep or drop.
- **Sub-branch read after the spec branch.** Its commits are already covered: `already imported`, the reuse-or-skip path.
- **Top-level branches** are the work branches whose into branch is the base branch. **Done** across branches means every top-level branch is merged into the base branch (and the tasks are done by today's rules). A sub-branch never blocks done; it counts toward progress only.
- **Sub-branches line**, per spec branch, after the Branches line: `Sub-branches: 1 of 2 merged into feat/orders-capacity.` A sub-branch is merged into its into branch by the same three tests under **Merged**.
- **Left behind.** When the spec branch has reached the base branch but a sub-branch never merged into it, add `left behind: feat/orders-capacity-t4 (not in feat/orders-capacity)` to the Sub-branches line. Report only; it never blocks done. `(dropped)` is still offered only for a branch that is gone and unmerged.

## Reverted (1.68.0)

A merged work branch whose change was later undone on its base branch is reported as `<branch>: merged, reverted on <base> (<revert sha>)` on the Branches line. It is reverted when a commit on the base after the merge either says `This reverts commit <sha>` naming one of the branch's commits, or has a patch that is the reverse of the branch's change (`git show <commit> | git patch-id` equals the patch-id of `git diff <tip> <split point>`, the branch change reversed). Read-only local git on the refs on disk. Report only: the branch still counts as merged, done is unaffected, and no file changes.

## Promotion (1.69.0)

Done stays **merged into the base branch**. How far the work has got after that (test, prod) is a separate, report-only line, read from `docs/environments/promotion.md` in the spec repo. No file means no Promotion line, and nothing else changes.

- **promotion.md.** One line per branch and environment, the four-field shape of `docs/environments/marks.md`: `<repo> | <branch, pattern or tag <pattern>> | <environment>[ (after <environment>)] | <source>`, for example `orders-api | develop | test | pipeline orders-cd, stage DeployTest`, `orders-api | release/* | prod | marked by the user`, `orders-api | tag v* | prod | marked by the user`. The environment is one of the known words `dev`, `test`, `stage`, `uat`, `qa`, `pre-prod`, `prod` (`development` is `dev`). Any other word must say its place, `sandbox (after dev)`; without `(after …)` the line is listed as `Unclear` and not used. Written by `/crav1-map-pipeline-environments` (Azure DevOps definitions) or by hand (`marked by the user`); lines are appended, never rewritten.
- **The chain.** Per repo, order the environments dev < test < stage, uat, qa < pre-prod < prod, with an `(after X)` environment right after X. Several lines for one environment (for example `main` and `release/*` for prod) are all kept; reaching any one counts.
- **Reached.** An environment is reached when every top-level work branch of the spec in that repo (merged or not) is merged, by the tests under **Merged**, into a branch its line names: the branch itself; for a pattern such as `release/*`, any matching branch on disk (name the newest one that contains the work, `on release/2026.11 (deploys to prod)`); for `tag <pattern>`, any matching tag that contains the work tip (`git tag --contains <tip>` filtered by the pattern; name the newest, `in tag v2.3.0 (deploys to prod)`; none: `not yet tagged`).
- **The Promotion line**, after the Branches line, per repo: `Promotion: on the branch that deploys to test (develop); not yet on the branch that deploys to prod (main).` Name the furthest environment reached, then each later environment not yet reached (all lines for it), and end with the chain, `(chain: dev → sandbox → test → prod)`. This is **branch reach, not deployment proof**: say "on the branch that deploys to <env>", never "deployed to <env>". Add `Unclear: <line> (unknown environment word, no (after …))` for a line that can't be placed.
- **Release fixes.** A work branch with `(into release/<x>)` is a fix made on a release branch. It is reached on that release line but counts toward done only once it is also on the base branch; until then add `<branch>: not back on <base>`.
- **Pipeline runs (optional extra).** When a Promotion line shows and at least one promotion.md line behind it has a `pipeline <name>, stage <stage>` source, end the report with one question, **Also check the latest pipeline runs?**, options **Check pipeline runs** and **No, keep the git answer**. Asked each run; no setting. The choice word `pipeline runs` in the invocation runs the check without the question. A headless or bot run without the word doesn't stop: it gives the git answer and ends with `Pipeline runs not checked. Add the word: pipeline runs.` The check is Azure DevOps only and read-only: `az pipelines runs list --pipeline-name <name> --result succeeded --top 1 --detect false` (plus that run's stage results and source commit); never queue, re-run, approve, or read logs. Say `Promotion (pipeline runs): test, DeployTest succeeded 2026-10-18 at 63e334b, which contains the work; prod, no successful DeployProd run contains the work.` A line written by hand or for GitHub Actions keeps the branch-reach answer: `pipeline runs: Azure DevOps only; <line> checked by branch reach`. `az` missing or not signed in: say `az is not installed` or `az has no login`, keep the git answer, never log in or install.
- **Report only.** Promotion never blocks done, never writes a spec line or Match `Status:`, and writes no file except verify.md, which carries the line like the Branches line.

