---
name: crav1-complete-tasks
description: >-
  Run /crav1-complete-task for a T# range (e.g. T1-T3) or every unimplemented
  task if they omit a range. One commit-style choice for the whole run. Stop
  the batch when a task needs input (implement fail, fix/stop after verify,
  commit failure). Use to take several tasks implement-to-done, or
  /crav1-complete-tasks.
disable-model-invocation: true
icon: list
color: green
---

# Complete several tasks

You burn down **more than one** `T#`, each through `/crav1-complete-task`. You do not flatten all tasks into one implement turn.

Command: `/crav1-complete-tasks`. One task only: `/crav1-complete-task`.

Follow sibling **`crav1-complete-task`** (drop-in `.cursor/skills/crav1/crav1-complete-task/SKILL.md` or this plugin’s `skills/crav1-complete-task/SKILL.md`) for every selected id.

## Which tasks

Spec folder: user @-mention, else most recently edited `docs/specs/` excluding `_template/`. Need `tasks.md` or stop (`/crav1-plan-from-spec`).

**Selection** (tasks.md order, skip already `[x]` unless they named a checked id and you must say it is already done):

| They typed | You run |
| --- | --- |
| `T1-T3` / `T1–T3` | Inclusive numeric range of ids that exist in `tasks.md` |
| `T1, T2, T5` | Those ids, in tasks.md order |
| No range / “all” / “rest” | Every remaining `- [ ]` |

Unknown ids: list them, continue with the ones that exist. Empty selection: say so and stop.

## Style once

Before the first `T#`, run **complete-task’s commit-style step** once. That **run style** applies to every loop-commit for every task in this batch. Do not ask again per task.

If a persist rule already exists, use it (same as the draft skill) and do not ask.

## Batch loop

For each selected `T#` in order:

1. Follow **`crav1-complete-task`** for that id (style already set).
2. If that skill **stops at a gate** (implement verify failed, they picked `stop` on the fix options, commit/attribution, spec frozen, playbook-only): **end the batch**. Recap which `T#`s finished, which is blocked, which were not started.
3. If they pick **`fix`**, stay inside that task’s Phase C until it reaches Phase D or they `stop`. Then, if Phase D, start the next selected `T#`.
4. After Phase D, start the next selected `T#` **without** asking. Other tasks still `- [ ]` are not a reason to stop.

Do not skip a failed `T#` to “keep going” unless they explicitly say skip.

## After the batch (chat)

TL;DR:

- Finished `T#`s
- Blocked `T#` + why
- Not started
- Inner-loop still open? (should be empty if you only left after Phase D or a `stop` they chose)
- Commits (hashes)

If every selected task reached Phase D and inner-loop is empty: one sentence that the requested slice is demoable against the spec (other unchecked `T#`s may remain if they passed a range).

## Hard rules

- One `T#` of product work at a time (complete-task). The batch only sequences those runs.
- Same hard rules as complete-task: no `spec.md` edits, no push, no PR, no implementing unimplemented work inside fix-from-verify.
- Do not re-ask commit style in the middle of the batch.
