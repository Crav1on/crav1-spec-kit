---
name: crav1-build-tasks
description: >-
  Use to build tasks from tasks.md, one isolated worker per task (implement,
  commit, verify, optional fix). Asks which tasks (one, a range, or all ready)
  unless the message names them. Ends by naming /crav1-open-pr. Does not push
  or open a pull request.
disable-model-invocation: true
icon: hammer
color: orange
---

# Build tasks

You build tasks from `docs/specs/<slug>/tasks.md`. Every task runs in its own isolated worker, the **crav1-build-task-agent** subagent. You never implement a task in this chat.

This replaces `/crav1-implement-task`, `/crav1-complete-task`, and `/crav1-complete-tasks` (1.56.0). Their rules are kept, unchanged, as the branches below. Follow the branch the answer picks, in full.

## Opening question

Find the spec folder: the user's @-mention, or the one folder `scripts/resolve_spec.py` prints (skill `crav1-tasks-ready-to-build`, `--root docs/specs`). Exact folder first, then hyphen and space forms (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`, then one unique ordered token subsequence of those names (`cc 1.0` matches `cc-process-1-0`). Several matches: list them and stop. No match: say so and list the nearest slugs. Do not pick the most recently edited tree. No name: ask which slug. When `tasks.md` is missing, stop and name `/crav1-plan-from-spec`.

Then ask one question. List the tasks that are ready, using the rules in `/crav1-tasks-ready-to-build` (its `SKILL.md` next to this one), with their titles, in dependency order (its **Dependency order** section), and say how many are blocked and what comes after, for example `5 blocked; after T2 comes T7, then T3 and T6`. Put its **Next** task first as Recommended.

1. **One task.** Pick one ready `T#`. Follow [branches/one-task/BRANCH.md](branches/one-task/BRANCH.md) (one worker, standalone).
2. **A range.** For example `T2-T5`. Follow [branches/several-tasks/BRANCH.md](branches/several-tasks/BRANCH.md) with that range.
3. **All unticked tasks.** Follow [branches/several-tasks/BRANCH.md](branches/several-tasks/BRANCH.md) with all unchecked tasks, in dependency order, until one is blocked.

Skip the question when the message already answers it: one `T#` is option 1, a range or several `T#`s is option 2, `all` or "continue until blocked" is option 3.

A picked task that is blocked by a cycle, or by an `(after:)` that names no task: say why and ask whether to build it anyway or pick another. Do not skip that question.

**Held tasks (1.132.0).** Run `walk_progress.py readiness --root <spec-folder>` (skill `crav1-tighten-and-plan-ready-to-build`). When `result` is `ready` or `ready-partial`, start each task in `can_start`. A gate with `refused` true is held: say its `reason` (`open question …` or `held, waits on T#`) and do not ask to build it anyway. Do not start it. Continue with the other tasks that can start. When `result` is `not-ready`, do not start a worker.

**Tick only (1.137.0).** Before a worker, run `scripts/tick_only.py --root <spec-folder> T#`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. A recorded-merged or already-verified row that is still `[ ]` is tick-only. Pass `--yes`, tick `[x]` in `tasks.md`, and start no worker, whatever the ready-check result, including `not-ready`. Do not re-implement. The task may already be done for `can_start`. That tick is not a worker and is not a way to build a held task. When the result is `not-ready`, do not start a worker for any other task. A task the script calls `not-tick-only` follows the worker path.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Which tasks: `one task` / `range` / `all tasks`.
- Branch (1.99.0, on a base or other branch): `new branch` (create `feat/<slug>` from the into branch). Without it, a headless run on a base branch stops before any code.

When the invocation contains one of these words (for example `/crav1-build-tasks one task`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: one task, range, all tasks.`

## Inside the worker

Each worker follows [branches/one-task/references/run.md](branches/one-task/references/run.md), which runs the implement rules in [branches/implement/BRANCH.md](branches/implement/BRANCH.md) (gate, branch check, one task, verify step, evidence), then the commit, `/crav1-verify-build-against-spec`, and the optional fix loop. The implement rules no longer run in this chat: where they say "this turn" or "this chat", read "this worker".

Branch and permissions are two questions (1.129.0). The branch question comes first, on its own card, and a typed branch name on that card is the answer. The permissions question comes after. A missing answer, or an answer that belongs on the other card, is re-asked. Do not guess. The branch is the first line of `scripts/build_map.py --recommend T#` (skill `crav1-tasks-ready-to-build`). A name on the task line wins over the plan step. A merged or deleted branch is not offered. The card says where the name came from (1.140.0). A different pick is written as `(map: <picked>)`. Details: skill `crav1-create-feature-branch`, `references/task-branch.md`. A worker that needs a person's yes returns `needs_yes`. That is waiting, not blocked. The task stays unticked. The parent writes or offers the Approval needed item. Read `references/approval-needed.md`. The worker does not edit `spec.md` and does not write `Approved:`.

## After

Every path ends with the batch or single-task TL;DR from its branch, then names `/crav1-open-pr`. Do not run it. Do not push.

## Parked and retired specs (1.60.0)

Skip every spec under `docs/specs/retired/`, and every old-path `spec.md` that is only a `Moved:` pointer. A spec whose `spec.md` has a `Parked:` line is parked: do not build its tasks. Say `skipped: <slug> (parked)` and name `/crav1-retire-spec un-park docs/specs/<slug>/`. Do not remove the mark.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
