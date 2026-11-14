---
name: crav1-build-walk
description: >-
  Use when a slice is ready to build and you want one guided walk of one
  work branch: build the tasks, verify, commit, open the pull request,
  merge the base in, merge the pull request, tick, then the next task.
  Name a branch to build all its open tasks in one run, stopping before
  the merge.
disable-model-invocation: true
icon: workflow
color: blue
---

# Build walk

The user wants one guided walk of one work branch, from the tasks on that branch through verify, commit, the pull request, merging the base into the branch, merging that pull request, the tick, and the next task. It is in the Build lane. It is not a starter option.

Command: `/crav1-build-walk`. A slug, then a `T#` or a branch, may follow. `orders-capacity` is a slice. `T3` is one task. `feat/orders-cicd` builds every open task on that branch in task order, in one run that stops only for a real stop and always before the merge (1.155.0).

It does not replace the skills it opens. It does not push, open a pull request, merge, or run a live change until this run's `yes`. It never rebases.

Before it reads the spec folder, it fetches the specs repo (1.151.0). The rule is [references/sync.md](references/sync.md). When it starts on a branch, it writes an `In progress:` line in `docs/specs/<slug>/claims.md` and, after yes, commits and pushes only that file. The rule is [references/claims.md](references/claims.md). When the walk ends, or the user stops, it commits the files it wrote and pushes the specs repo after one yes.

The in-walk reply prints `ending` from `scripts/build_walk.py next --json <file>`, as-is. That text is the shared walk ending (1.156.0): `Run next:` first, then Built and Left, then Waiting and Uncommitted, then the walk's own Next line. Each command is alone in a code span, such as `` `/crav1-build-walk orders-api T3` ``, and another ready branch gets its own entries. The shape is in [run-ending.md](../crav1-docs/reference/run-ending.md); never add a line of your own.

The JSON object is documented in [references/common.md](references/common.md). Fields include `phase`, `owner`, `branch`, `tasks`, `base`, `pr`, `slug`, `root`, `spec_count`, `ready_branches`, `waiting`, and `uncommitted`. `tasks` may be `"T3"` or `{"id": "T3", "title": "Apply the CI build policy"}`. `T3` and `3` are the same id. Bad input returns `{"ok": false, "code", "line"}` and does not traceback.

## Route first (1.142.0)

Read [references/common.md](references/common.md) once. Then open only the file for the point you are at. Do not open the others yet.

- The invocation names a branch, not a `T#`: read [references/branch-run.md](references/branch-run.md). It replaces the per-step cards with one start yes, until a stop.
- No branch is chosen, or the user started from a ready-to-build report: read [references/grouping.md](references/grouping.md). That start may print one Next per ready branch.
- A `build-progress` file for this branch already exists: read [references/progress.md](references/progress.md). Resume reports the step. It does not start it.
- The pull request author or a commit author is someone else: read [references/other-owner.md](references/other-owner.md) before any switch.
- The task line has `(Runs live)`, or an Approval needed item holds it: read [references/live.md](references/live.md). A recorded yes that the assistant's permission check refused is not a missing yes (1.143.0).
- A task needs code that is still only on an unmerged branch: read [references/stack.md](references/stack.md).
- Starting on a branch, or `release claim`: read [references/claims.md](references/claims.md).
- The first action of a run, or the walk is ending or the user stopped: read [references/sync.md](references/sync.md).
- The step itself: read [references/steps.md](references/steps.md).

A headless or bot run stops before any step. This walk is guided only. It does not guess a mode.

## Choice words

Exact words. There are no `--flags`. A word in the invocation answers its question. A headless run with no word stops and names the valid words.

- `yes` — do the write, push, open, or merge that was just shown.
- `switch` — build on the other person's branch, in other-owner mode.
- `own` — this branch is ours. Do not switch.
- `edit description` — change that pull request's description. Other-owner mode only, and only because this run asked.
- `stop` — write nothing further. At the end of a walk, still offer the settle-and-push card unless the user already refused it.
- `release claim` — clear this branch's claim, then commit and push `claims.md` after yes.

## Locked steps

One branch at a time. The order is in [references/steps.md](references/steps.md). Open each step skill from this folder and follow it. Read [open-skill-file.md](../crav1-docs/reference/open-skill-file.md) once before the first one.

While this walk runs, print `ending`. Do not also print the step skill's Next. A start with no branch picked is in [references/grouping.md](references/grouping.md).

## Stop

`build-progress/<branch>.md` only records position. Do not edit `spec.md` except the `(live yes: <name>, <date>)` note [references/live.md](references/live.md) writes after `yes`. Do not tick a task from this file. The tick is the tick-only path, after `yes`.

Recording a step commits `docs/specs/<slug>/build-progress/<branch>.md` after that yes (1.150.0). When the step already commits other files, such as the tick or verify, include the progress file in that same commit. Otherwise commit the progress file on its own after the yes. Use the persisted commit style, the draft-commit rule already in the repo. Nothing is pushed. `/crav1-finalize-commit` still commits the product files on the commit step, after `yes`.

When the user stops partway, one line `Paused at <step>.` Then the settle-and-push card in [references/sync.md](references/sync.md), then the ending in [references/progress.md](references/progress.md).

## Run ending (1.122.0)

Print the script's `ending` (shared, skill `crav1-tasks-ready-to-build` `scripts/walk_ending.py`). Pick the interpreter as [running-scripts.md](../crav1-docs/reference/running-scripts.md) says.
