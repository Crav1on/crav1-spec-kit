# Claims (1.151.0)

Read this when `$crav1-build-walk` starts on a branch, when a claim is already in `docs/specs/<slug>/claims.md`, or when the user says `release-claim`.

The file is `claims.md` in the spec folder. It is not a section of `build-map.md`, which the ready check rewrites. It is not `walk-progress.md` or `build-progress/`, which record position, not a shared lock. A claim can be committed and pushed on its own after yes.

## Start

When this walk starts on a branch, write one line per open task on that branch, or one line with several T#s:

```text
In progress: feat/orders-api-host-setup, T27, person A, since 2026-11-13T15:50:00+01:00
```

The user is `git config user.name` in the specs repo. The time is an ISO timestamp in local time with the local offset, to the second, for example `2026-11-14T23:40:00+01:00` (1.160.0). An older line written in UTC (`+00:00`, with or without microseconds) still reads, and is written back in local time. A `--since` with its own non-UTC offset keeps it. Run `<interpreter> -X utf8 scripts/claims.py add --root <spec-folder> --branch <branch> --tasks T27 --user "<name>"` with no `--yes` first, as `crav1-docs/reference/running-scripts.md` says. It prints the line and leaves `claims.md` unchanged (1.201.1). Show that line, then one card. After `yes`, run the same command with `--yes`, which writes the line. A second start on the same claim keeps the original since time.

Card: Claim T27 for you and push the claim?
- **Claim and push (Recommended)** (`yes`): commit only `claims.md` and push it, so others see T27 is taken. Why: it stops two people building the same task.
- **Do not claim** (`stop`): write nothing, and T27 stays open for anyone.

There is no Edits option. A headless run stops and names `yes` and `stop`. Do not guess. Nothing else is committed on that card. A whole-branch start is different: it also commits `walk-progress.md` and its progress file; see [branch-run.md](branch-run.md).

## Whole-branch run (1.155.0)

A run started with a branch, as [branch-run.md](branch-run.md) says, writes one line that names every open task on that branch:

```text
In progress: feat/orders-cicd, T2, T3, T5, person A, since 2026-11-14T09:00:00+01:00
```

It is the same line format, so an older ready check reads it too, and every task on it shows as in progress. Rerunning the same command reuses that line. It does not write a new one. Before each task the run checks the file again. Someone else's claim on one of those tasks is a stop that names who.

If the script returns `claimed`, that task is already in progress by someone else. Say so and stop. Do not overwrite it.

## While it runs

The ready check holds a claimed task as `in progress by <user> since <date>`, or `built by <user>, waits for PR <n> to merge` once its build-progress file shows it built (1.175.0), and does not offer it in Run next. It offers to continue a branch walk only to the walk's claim user; `Owner: self` in the progress file is never trusted alone. This walk continues on its own claim.

Your own claim does not hold a task (1.160.0). `walk_progress.py readiness --root <spec-folder> --vendor codex` takes `--user <name>` (default `git config user.name` in the specs repo) and `--branch <branch>` (the branch being walked). A claim by that user, on that branch when `--branch` is given, keeps the task's own state: its gate has `refused` false and `reason` `in progress by you`, and the reply says `T# is yours; the walk resumes it.` (1.171.0). When that task's `build-progress/<branch>.md` ends at `comment` or `wait-merge`, it is waiting, not offered in Run next, and the reply says `T# is yours and waits for PR <n>'s merge.` Someone else's claim, or your claim on another branch when `--branch` is given, still holds the task and refuses it.

A claim older than the max age (default 3 days, or `Claim max age: N days` in the file) gets a warning. It is not cleared on its own. The warning names `release-claim`.

## Clear

Clear the claim, then commit and push `claims.md` after one yes, when:

- the branch's tasks are ticked or the pull request is merged
- the user says `stop` and is done with this walk
- the user says `release-claim`

A mid-walk stop, such as before a merge step, does not clear the claim.

`<interpreter> -X utf8 scripts/claims.py clear --root <spec-folder> --branch <branch>` clears that branch. Add `--tasks T27` to clear one task.

Normalized content stamps ignore `In progress:` and `Claim max age:` lines.
