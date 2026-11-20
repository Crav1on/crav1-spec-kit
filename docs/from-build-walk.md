# Build one branch, then the next

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when a slice is ready, or ready with some tasks held, and you want one path from the tasks on a work branch through the pull request and the merge. Since 1.144.0 the ending comes from `build_walk.py next --json <file>`, and the branch offer is `build_map.py docs/specs/<slug> --recommend T#`. The interpreter is [Running a kit script](reference/running-scripts.md). The walk opens the skills that already build, verify, commit, open, and merge. It does not replace them. The ending is the Run next block first, then what was built, what is left, and Waiting. It has no Next line (1.157.0).

## First prompt

```text
/crav1-build-walk
@docs/specs/orders-capacity/
```

A task id works too: `/crav1-build-walk T3`.

## Build a whole branch in one run (1.155.0)

Name the branch instead of a task:

```text
/crav1-build-walk orders-capacity feat/orders-cicd
```

The walk lists the open tasks on that branch in task order, shows the first thing that would stop it, and asks one `yes`. That yes writes one claim line that names every open task on the branch, such as `In progress: feat/orders-cicd, T2, T3, T5, person A, since 2026-11-14T09:00:00+01:00`, and covers every commit and push in the run. Then, for each task, it fetches and merges origin in when behind (never a rebase), builds the task, runs its tests, commits it, records it, and pushes, with one line such as `T2 done, tests green, starting T3`. Every few tasks that line adds a soft hint to continue in a fresh session. It is never a stop.

It stops only for:

- an open question on the next task
- a stakeholder yes that is not recorded
- a `(manual, secret)`, `(host setup)`, or `(Runs live)` step
- tests or lint still red after a fair try
- a change it wants outside the task's scope
- someone else claiming or changing one of the run's tasks
- the pull request merge, always

When every task is built, it opens or updates the pull request and stops. The reply is Run next first, each command alone on its own line, for example `` `/crav1-build-walk orders-capacity feat/orders-cicd` `` to merge after your yes and `` `/crav1-build-walk orders-capacity feat/orders-dev-switch` `` for the next ready branch. Then each built task with its commit and test result, then anything left: skipped tasks, open questions, and verify rows that are behind. It never merges by itself.

Each task also updates one line in `docs/specs/orders-capacity/walk-progress.md`, such as `- Branch run: feat/orders-cicd: running, T2 done, next T3 (2026-11-14T09:40:00+01:00). Log: build-progress/feat--orders-cicd.md`, then `stopped before merge`, then `merged`. That file stays the one place to look, and the ready check prints those lines. Run next in the ready check, tighten-and-plan, and this walk offers the whole branch beside the next task whenever a branch has two or more open tasks.

To resume after a stop or in a new session, run the same command. It picks up at the next open task, keeps its own claim, and does not build a task twice. A stop partway keeps the claim unless you say `release-claim`.

When the walk waits for someone else to merge the pull request (1.171.0), Run next no longer offers the same task again: the Waiting line says what it waits for, and Run next starts with the branches you can build now. The ready check reads `build-progress/<branch>.md` too, so a task that is pushed and waits on a merge is not offered anywhere until that merge. One lead sentence comes before Run next, for example `T5 is pushed to PR 71 and waits for its merge.`, and it never says there is nothing to commit when an Uncommitted line follows. Two tasks on one branch are one branch command, `/crav1-build-walk orders-api feat/orders-incoming`, never `T43, T8`. Task names are shown in full. In someone else's pull request, a built and pushed task's verify row says `Implemented, verified, tick pending`.

The walk reads its own state from the files (1.172.0): `build_walk.py next --root docs/specs/orders-api --branch feat/orders-readme` takes the step and owner from `build-progress/<branch>.md`, the task names from `tasks.md` and the Uncommitted line from `git status`, and `build_walk.py progress record` writes each step with its stamps. When the branch waits on someone else's merge, the walk prints the ending straight from the script without reading its reference files.

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Branches | Pick one ready branch | When you start from a ready-to-build report, each ready branch is its own Run next entry, with the T number beside the task name. One checkout follows one branch |
| Build | Watch the diff | Opens `/crav1-build-tasks` for the tasks on that branch. A merged or deleted branch is not offered |
| Runs live | `yes` before the live run, or stop | A `(Runs live)` task gets a script and a dry run (`check`) first. `yes` records `(live yes: person A, 2026-11-12)` and then runs it. Without `yes` the task stays unticked. An unapproved Approval needed item holds the task. When that yes is on record and the assistant's permission check refuses the command, Waiting says so and does not say the yes is missing. Run the exact command yourself, or allow that one command and rerun. Run next is this walk after the command has run |
| Verify | Read the report | Opens `/crav1-verify-build-against-spec` |
| Commit | `yes` | Opens `/crav1-finalize-commit` |
| Pull request | `yes` | Opens `/crav1-open-pr`. Own mode only |
| Base | `yes` | Merges `develop` (the into branch) into the work branch. Never a rebase. Own mode only |
| Merge | `yes`, and the card names the pull request | Opens `/crav1-merge-pr`. That yes is the ask. Own mode only |
| Tick | `yes` when the only leftover is the checkbox | Ticks a recorded-merged row. Does not re-implement |
| Next task | Pick the next branch, or stop | One Run next entry per ready branch, or verify when no work branch remains |

Someone else's branch or pull request asks `switch` before other-owner mode. In that mode the walk does not open a pull request, does not merge the base in, and does not merge the pull request. Each push gets one comment. The description changes only if you say `edit-description`. Ticks wait until that pull request is merged.

A task that needs code from an unmerged branch is cut from that branch. The progress file and the report list which branch merges back into which, child first.

## What gets written

`docs/specs/orders-capacity/claims.md`, after yes when the walk starts on a branch: an `In progress:` line such as `In progress: feat/orders-host-setup-scripts, T3, person A, since 2026-11-13T15:50:00+01:00`. That file is committed and pushed on its own after that yes, so another session can see the walk.

`docs/specs/orders-capacity/build-progress/feat--orders-host-setup-scripts.md`, after yes. On a whole-branch run it also has a `## Run` section with `Next task:` and one `- Built: T2, commit a1b2c3d4e5f6, tests green` line per task, committed and pushed after each task. It records the step, the normalized hashes, and the merge list. That file is committed after the yes, in the same commit when the step already commits other files, otherwise on its own, using the persisted commit style. When the walk ends, or the user stops, the files this walk wrote are committed and the specs repo is pushed after one yes. The spec, plan, and tasks stay the source of truth, except `(live yes: …)` on a Runs live task after yes.

## After

The walk fetches the specs repo before it reads. If that copy is behind origin, it stops and Run next is `git pull --no-rebase`.


```text
Run next:

Build T5 Note the policy on feat/orders-note:
`/crav1-build-walk T5`
```

When no work branch remains:

```text
Run next:

`/crav1-verify-build-against-spec orders-capacity`
```

Reference page: [build-walk](reference/skills/crav1-build-walk.md)

Since 1.176.0 a whole-branch run keeps the specs repo and the code repo apart: the record step takes `--code-repo` (the specs repo is the top level of the spec folder), checks both before it writes, and commits `verify.md` with the progress file in one specs commit that ends with the work-item mention. The ending reads `build-progress/<branch>.md` itself (`branch_run.py ending --root <spec-folder> --branch <branch>`), and notes for the user go under `Before the merge:` after what was built. The ready check lists open pull requests as `Merge these PRs, in this order:`, one numbered PR per line with its owner and what merging it ticks and lets start, and Branch runs reads `built, PR 82 open` instead of `stopped before merge`. Since 1.177.0, when one of those pull requests is yours, Run next leads with merging it, for example `Merge your PRs 71 and 73 first (PR 82 is person B's):` above `/crav1-merge-pr 71`, above the entry that resumes the walk, and a blank line keeps the Waiting line under the list out of its last item. Since 1.177.1 the merge list is the only place a pull request waits: no Waiting line repeats it. When none of the listed pull requests is yours, Run next leads with `Ask the PR owners to merge, in this order:` and one line per owner, above the entry that resumes the walk. A pull request with no recorded author is looked up read-only on its own host and the name is recorded in build-progress; when the host does not say, the ready check asks you once who opened it and records the answer.

Since 1.176.0 the yes card of a whole-branch run names each task by its short title from `verify.md`, for example `T10 Orders CI/CD: deploy pipeline`, not the first 80 characters of the task line.

Since 1.182.0 you can add a second task to a branch that already has a pull request, including someone else's: `progress record --step 'build T47'` accepts a build step for any task and adds it to the progress file's `Tasks:` line, so the lead, the ending, the merge list (`ticks T43 and T47`) and the build map name both. Before the build step the walk checks the code branch against origin with `repo_sync.py code-behind --repo <code repo>`. When it is behind, you get a card, `fast-forward` or `stop`, and the walk fast-forwards only after `fast-forward`; a diverged branch stops with the merge in Run next.

Since 1.184.0 a progress file written by an older kit, where a second task's build is a plain `- Step: build` and the task appears only in the result (`Result: done (T47: ...)`), is read the same way: the walk names both tasks, for example `T43 and T47 are pushed to PR 73 and wait for its merge`, and adds T47 to the header the next time it writes the file.

Since 1.186.0 `/crav1-build-walk <slug> T4` starts an open task on a branch whose other tasks already wait for the pull request's merge. The walk claims T4, adds it to the progress file and builds it. On another person's branch, a task that takes in develop merges develop into that branch with its own yes, runs the whole suite and the linter, pushes after yes and comments once; the owner still merges the pull request, and the ending names them.

Since 1.187.0 a task is named by its text up to the first verify item. A task line such as `PR 12 takes in develop after PR 10 merges, with the conflicts resolved; integration — ...; system — ...` shows as `Build T8 PR 12 takes in develop after PR 10 merges, with the conflicts resolved on feat/orders-api:` under Run next and in the lead, not the whole line with its checks.

## Finished claims (1.196.0)

A claim stays only while its tasks are open. `/crav1-merge-pr` and the start of `/crav1-tighten-and-plan-ready-to-build` clear claims whose tasks are all ticked or whose branch is merged into `origin/develop`, with one line such as `Cleared 2 finished claims: T5 (ticked), T8 (PR 71).` An unfinished claim is never cleared, and a finished claim gets no age warning. Both fetch origin first, so a stale local `develop` does not hide a merge.

## Local base update (1.197.0)

When the code repo's local base branch is behind origin, the walk asks `Your local develop in orders-api is 2 commits behind origin/develop. Update it locally before the build?` **Update local develop** fast-forwards your local branch (`git merge --ff-only`) and pushes nothing, then cuts the work branch from it and builds the task. **Stop** builds nothing.

## 1.198.0 changes

`/crav1-build-walk` labels each Run next entry by the step the branch is on, such as `Merge PR 71 for T5:` or `Check PR 71's merge for T5:`, with short task names. It checks whether the branch is really behind its base before it says so, moves on after a `nothing-to-do` step, and leaves release-gated tasks out of its ending; a manual task with no branch is listed on its own. `progress record --step build,verify --pr 71` records several steps and the PR in one call. One yes opens the pull request, and `Not yet` on the merge card also commits and pushes the walk's specs files. When a newer kit release is out it says `Kit update available: 1.197.0 -> 1.198.0` once, with `/crav1-update-kit` in Run next.
