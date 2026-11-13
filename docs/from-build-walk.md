# Build one branch, then the next

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when a slice is ready, or ready with some tasks held, and you want one path from the tasks on a work branch through the pull request and the merge. Since 1.144.0 the next line is `build_walk.py next --json <file>`, and the branch offer is `build_map.py docs/specs/<slug> --recommend T#`. The interpreter is [Running a kit script](reference/running-scripts.md). The walk opens the skills that already build, verify, commit, open, and merge. It does not replace them. While one branch is in progress there is one Next line.

## First prompt

```text
/crav1-build-walk
@docs/specs/orders-capacity/
```

A task id works too: `/crav1-build-walk T3`.

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Branches | Pick one ready branch | When you start from a ready-to-build report, each ready branch is its own Next, with the T number beside the task name. One checkout follows one branch |
| Build | Watch the diff | Opens `/crav1-build-tasks` for the tasks on that branch. A merged or deleted branch is not offered |
| Runs live | `yes` before the live run, or stop | A `(Runs live)` task gets a script and a dry run (`check`) first. `yes` records `(live yes: person A, 2026-11-12)` and then runs it. Without `yes` the task stays unticked. An unapproved Approval needed item holds the task. When that yes is on record and the assistant's permission check refuses the command, Waiting says so and does not say the yes is missing. Run the exact command yourself, or allow that one command and rerun. Next is this walk after the command has run |
| Verify | Read the report | Opens `/crav1-verify-build-against-spec` |
| Commit | `yes` | Opens `/crav1-finalize-commit` |
| Pull request | `yes` | Opens `/crav1-open-pr`. Own mode only |
| Base | `yes` | Merges `develop` (the into branch) into the work branch. Never a rebase. Own mode only |
| Merge | `yes`, and the card names the pull request | Opens `/crav1-merge-pr`. That yes is the ask. Own mode only |
| Tick | `yes` when the only leftover is the checkbox | Ticks a recorded-merged row. Does not re-implement |
| Next task | Pick the next branch, or stop | One Next for the next ready branch, or verify when no work branch remains |

Someone else's branch or pull request asks `switch` before other-owner mode. In that mode the walk does not open a pull request, does not merge the base in, and does not merge the pull request. Each push gets one comment. The description changes only if you say `edit description`. Ticks wait until that pull request is merged.

A task that needs code from an unmerged branch is cut from that branch. The progress file and the report list which branch merges back into which, child first.

## What gets written

`docs/specs/orders-capacity/build-progress/feat--orders-host-setup-scripts.md`, after yes. It records the step, the normalized hashes, and the merge list. That file is committed after the yes, in the same commit when the step already commits other files, otherwise on its own, using the persisted commit style. Nothing is pushed. The spec, plan, and tasks stay the source of truth, except `(live yes: …)` on a Runs live task after yes.

## After

```text
Run next:

`/crav1-build-walk T5`
branch feat/orders-note, T5 Note the policy

Next: /crav1-build-walk T5, because that work is on feat/orders-note (T5 Note the policy).
```

When no work branch remains:

`Next: /crav1-verify-build-against-spec orders-capacity, because no work branch remains.`

Reference page: [build-walk](reference/skills/crav1-build-walk.md)
