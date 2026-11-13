---
name: crav1-build-walk
description: >-
  Use when a slice is ready to build and you want one guided walk of one
  work branch: build the tasks, verify, commit, open the pull request,
  merge the base in, merge the pull request, tick, then the next task.
  One Next while it runs.
disable-model-invocation: true
icon: workflow
color: blue
---

# Build walk

The user wants one guided walk of one work branch, from the tasks on that branch through verify, commit, the pull request, merging the base into the branch, merging that pull request, the tick, and the next task. It is in the Build lane. It is not a starter option.

Command: `/crav1-build-walk`. A slug or a `T#` may follow. `orders-capacity` is a slice. `T3` is one task.

It does not replace the skills it opens. It does not push, open a pull request, merge, or run a live change until this run's `yes`. It never rebases.

## Route first (1.142.0)

Read [references/common.md](references/common.md) once. Then open only the file for the point you are at. Do not open the others yet.

- No branch is chosen, or the user started from a ready-to-build report: read [references/grouping.md](references/grouping.md). That start may print one Next per ready branch.
- A `build-progress` file for this branch already exists: read [references/progress.md](references/progress.md). Resume reports the step. It does not start it.
- The pull request author or a commit author is someone else: read [references/other-owner.md](references/other-owner.md) before any switch.
- The task line has `(Runs live)`, or an Approval needed item holds it: read [references/live.md](references/live.md). A recorded yes that the assistant's permission check refused is not a missing yes (1.143.0).
- A task needs code that is still only on an unmerged branch: read [references/stack.md](references/stack.md).
- The step itself: read [references/steps.md](references/steps.md).

A headless or bot run stops before any step. This walk is guided only. It does not guess a mode.

## Choice words

Exact words. There are no `--flags`. A word in the invocation answers its question. A headless run with no word stops and names the valid words.

- `yes` — do the write, push, open, or merge that was just shown.
- `switch` — build on the other person's branch, in other-owner mode.
- `own` — this branch is ours. Do not switch.
- `edit description` — change that pull request's description. Other-owner mode only, and only because this run asked.
- `stop` — write nothing further.

## Locked steps

One branch at a time. The order is in [references/steps.md](references/steps.md). Open each step skill from this folder and follow it. Read [open-skill-file.md](../crav1-docs/reference/open-skill-file.md) once before the first one.

While this walk runs, print one `Next:` line, the walk's. Do not also print the step skill's Next. A ready-to-build start that has not picked a branch is the exception in [references/grouping.md](references/grouping.md).

## Stop

`build-progress/<branch>.md` only records position. Do not edit `spec.md` except the `(live yes: <name>, <date>)` note [references/live.md](references/live.md) writes after `yes`. Do not tick a task from this file. The tick is the tick-only path, after `yes`.

Do not create a git commit from this skill. `/crav1-finalize-commit` commits, after `yes`.

When the user stops partway, one line `Paused at <step>.` Then the ending in [references/progress.md](references/progress.md).

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says. The script prints the line: `scripts/build_walk.py next`. Pick the interpreter as [running-scripts.md](../crav1-docs/reference/running-scripts.md) says.
