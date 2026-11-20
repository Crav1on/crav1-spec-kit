# Specs-repo sync (1.151.0)

Read this at the start of `/crav1-build-walk`, and again when a walk branch finishes or the user stops.

**Merged since sync (1.194.0).** When a walk branch's pull request has merged, before the next branch starts, run `scripts/merged_since_sync.py check --spec <spec.md> --code-repo <code checkout> --base <Merges into>` in `crav1-add-to-spec` (the one shared check), as `crav1-docs/reference/running-scripts.md` says. It fetches origin once first (1.196.0; `--no-fetch` skips it), prefers `origin/<branch>` over a stale local branch, catches a tip that is already merged, and compares each branch in the spec's `Synced at:` lines with that branch's base, found per branch (1.195.0): `--base`, which callers pass as the repo's `Merges into` branch from `docs/system/repos.md` when it names one (leave `--base` out otherwise), then that `Merges into` column, then the base branch's own `Synced at` line, then `origin/develop`, then the default branch and writes nothing. When `offer` is `take-in`, ask its one yes card with its `question` and two `options`. On yes, Open `../crav1-add-to-spec/SKILL.md` for its `command` and follow the PR or branch step inline with that skill's own confirms, then run its `after_yes` (`merged_since_sync.py stamp ... --yes`) to move `Synced at` to the merge. On `not now`, write nothing. Either way the walk goes on with the next branch. With no card (`not-merged`, `already-synced` or `skipped`), say nothing.

## Pull before reading

Before reading or writing the spec folder, run `<interpreter> -X utf8 scripts/repo_sync.py status --repo <specs-repo>`, as `crav1-docs/reference/running-scripts.md` says. That fetch is read-only.

- Behind origin: stop. Print the script's `ending`. Run next is `git pull --no-rebase` (merge, never rebase). Do not read or write yet.
- Diverged: stop. The same Run next applies. Merge origin in, never rebase.
- Ahead: continue. The ready check shows it in the `**Catch up first**` block with `git push` (1.167.0); in a walk, the push is the settle card below.
- No upstream, or the fetch failed (offline): say so once and continue from the local copy.
- No git repository: continue. Say nothing.
- In step: continue.

## Settle and push at the end

When the walk finishes, or the user says `stop`, list every uncommitted file in the specs repo that this walk or its step skills wrote: the progress file, `claims.md`, `verify.md`, `tasks.md` ticks, `build-map.md`, and notes such as `docs/notes/<month>/…` and their indexes. `<interpreter> -X utf8 scripts/repo_sync.py settle --repo <specs-repo> --written <path> <path>` lists them. Files this walk did not write are listed and left uncommitted.

Name the files in one sentence, then one card:

Card: Commit the walk's files and push the specs repo?
- **Commit and push (Recommended)** (`yes`): commit the walk's files with the persisted commit style, the draft-commit rule already in the repo, then push the specs repo, for example 2 commits ahead. Why: others then see the progress.
- **Leave them** (`stop`): commit and push nothing, and the ending shows a Waiting line.

One yes covers the commit and the push (1.164.0). When the walk pauses on the merge card's `Not yet`, that answer already covers this commit and push (1.198.0): do it without this card. Do not ask a second card for the push. `stop` does not push. A headless run stops and names `yes` and `stop`.

If the branch is behind origin, fetch and merge origin in first. Never rebase. On a conflict, stop and name the files. Nothing is pushed.

After a successful push, the ending says the specs repo is in step with origin. An unpushed repo is a Waiting line, never a buried note.

`Run next:` stays first, in the 1.150.0 shape, with the full command alone in a code span.
