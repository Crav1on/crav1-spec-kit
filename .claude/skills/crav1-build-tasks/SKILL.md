---
name: crav1-build-tasks
description: >-
  Build tasks from tasks.md, always in an isolated worker per task
  (implement, commit, verify, optional fix). Opens with one question:
  which tasks, one, a range, or all unticked, listing the ready ones from
  the /crav1-tasks-ready-to-build rules. Skips the question when the
  message already names the tasks. Persists commit style first. Ends at
  /crav1-open-pr. Does not push or open a PR. Replaces implement-task,
  complete-task, and complete-tasks (their rules are kept as branches).
disable-model-invocation: true
icon: hammer
color: orange
---

# Build tasks

You build tasks from `docs/specs/<slug>/tasks.md`. Every task runs in its own isolated worker, the **crav1-build-task-agent** subagent. You never implement a task in this chat.

This replaces `/crav1-implement-task`, `/crav1-complete-task`, and `/crav1-complete-tasks` (1.56.0). Their rules are kept, unchanged, as the branches below. Follow the branch the answer picks, in full.

## Opening question

Find the spec folder: the one the user @-mentioned, else the most recently edited tree under `docs/specs/` (not `_template`); ask which slug when several fit. When `tasks.md` is missing, stop and name `/crav1-plan-from-spec`.

Then ask one question. List the tasks that are ready, using the rules in `/crav1-tasks-ready-to-build` (its `SKILL.md` next to this one), with their titles, in dependency order (its **Dependency order** section), and say how many are blocked and what comes after, for example `5 blocked; after T2 comes T7, then T3 and T6`. Put its **Next** task first as Recommended.

1. **One task.** Pick one ready `T#`. Follow [branches/one-task/BRANCH.md](branches/one-task/BRANCH.md) (one worker, standalone).
2. **A range.** For example `T2-T5`. Follow [branches/several-tasks/BRANCH.md](branches/several-tasks/BRANCH.md) with that range.
3. **All unticked tasks.** Follow [branches/several-tasks/BRANCH.md](branches/several-tasks/BRANCH.md) with all unchecked tasks, in dependency order, until one is blocked.

Skip the question when the message already answers it: one `T#` is option 1, a range or several `T#`s is option 2, `all` or "continue until blocked" is option 3.

A picked task that is blocked: say why (the tasks-ready-to-build reason) and ask whether to build it anyway or pick another. Do not skip that question.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Which tasks: `one task` / `range` / `all tasks`.
- Branch (1.99.0, on a base or other branch): `new branch` (create `feat/<slug>` from the into branch). Without it, a headless run on a base branch stops before any code.

When the invocation contains one of these words (for example `/crav1-build-tasks one task`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: one task, range, all tasks.`

## Inside the worker

Each worker follows [branches/one-task/references/run.md](branches/one-task/references/run.md), which runs the implement rules in [branches/implement/BRANCH.md](branches/implement/BRANCH.md) (gate, branch check, one task, verify step, evidence), then the commit, `/crav1-verify-build-against-spec`, and the optional fix loop. The implement rules no longer run in this chat: where they say "this turn" or "this chat", read "this worker".

## After

Every path ends with the batch or single-task TL;DR from its branch, then names `/crav1-open-pr`. Do not run it. Do not push.

## Parked and retired specs (1.60.0)

Skip every spec under `docs/specs/retired/`, and every old-path `spec.md` that is only a `Moved:` pointer. A spec whose `spec.md` has a `Parked:` line is parked: do not build its tasks. Say `skipped: <slug> (parked)` and name `/crav1-retire-spec un-park docs/specs/<slug>/`. Do not remove the mark.
