# Claims (1.151.0)

Read this when `/crav1-build-walk` starts on a branch, when a claim is already in `docs/specs/<slug>/claims.md`, or when the user says `release claim`.

The file is `claims.md` in the spec folder. It is not a section of `build-map.md`, which the ready check rewrites. It is not `walk-progress.md` or `build-progress/`, which record position, not a shared lock. A claim can be committed and pushed on its own after yes.

## Start

When this walk starts on a branch, write one line per open task on that branch, or one line with several T#s:

```text
In progress: feat/orders-api-host-setup, T27, person A, since 2026-11-13T15:50:00+01:00
```

The user is `git config user.name` in the specs repo. The time is an ISO timestamp. `<interpreter> -X utf8 scripts/claims.py add --root <spec-folder> --branch <branch> --tasks T27 --user "<name>"` writes the file, as `crav1-docs/reference/running-scripts.md` says. Show the line, then one card. `yes` (Recommended) commits only `claims.md` and pushes it. `stop` does not. There is no Edits option. A headless run stops and names `yes` and `stop`. Do not guess. Nothing else is committed on that card.

If the script returns `claimed`, that task is already in progress by someone else. Say so and stop. Do not overwrite it.

## While it runs

The ready check holds a claimed task as `in progress by <user> since <date>` and does not offer it in Run next. This walk continues on its own claim.

A claim older than the max age (default 3 days, or `Claim max age: N days` in the file) gets a warning. It is not cleared on its own. The warning names `release claim`.

## Clear

Clear the claim, then commit and push `claims.md` after one yes, when:

- the branch's tasks are ticked or the pull request is merged
- the user says `stop` and is done with this walk
- the user says `release claim`

`<interpreter> -X utf8 scripts/claims.py clear --root <spec-folder> --branch <branch>` clears that branch. Add `--tasks T27` to clear one task.

Normalized content stamps ignore `In progress:` and `Claim max age:` lines.
