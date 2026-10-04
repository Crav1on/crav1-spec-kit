---
name: crav1-exploratory-test
description: >-
  After a build of a slice already exists, use the slice in two passes and
  write down bugs. Pass one learns the slice by using it once. Pass two is
  no longer careful. It adds randomness and follows what the last action
  showed. It lasts about as long as the first pass, long enough to provoke
  bugs, then it stops. It stops sooner when the user says stop. The user
  does not set a clock. It does not write the checks the plan already named.
  It does not start Specify, Plan, or Build. A bug is not sent to
  /crav1-fix-bug unless the user says so in that turn. Cross-cutting. Not a
  starter option.
disable-model-invocation: true
icon: mouse-pointer
color: purple
---

# Exploratory test

Use a slice that already has a build. Learn it once. Then use it again, no longer careful, and write down what breaks.

Command: `/crav1-exploratory-test`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane.

Other skills do not run this one. Spark, specify, plan, and verify do not run it. It is not started automatically.

## When a build is missing

Run only when a build of the slice already exists. A build exists when `tasks.md` in that slice has at least one checked `T#`, or the code that slice already built is in the tree.

If the slice has no build, stop. Say that. Write nothing. Do not start Build. Do not name a lane.

If the slice cannot be used (nothing to open, run, or click), stop. Say that. Write nothing. Do not start Build.

## Which slice

Everything after `/crav1-exploratory-test`, and every `@`, is the pointer.

If the user named one `docs/specs/<slug>/` (skip `_template`) and that slice has a build, that is the slice.

If the user named none and exactly one spec folder has a build, that is the slice.

If more than one spec folder has a build and the user named none, ask with options only. Use the questions tool when it is available. One option per spec folder that has a build. Label each option with `docs/specs/<slug>/` and the title line of that `spec.md` when it has one. Do not ask the user to type a slug. Stop until the user picks.

If no spec folder has a build, stop. Write nothing.

## Read

Read that slice’s `spec.md` and `plan.md` when they exist, and `tasks.md` when it exists. Read them to know the slice and to keep the plan’s checks out of the file this skill writes.

Do not run those checks. Do not copy them into the file. Do not mark them pass or fail.

## Pass one

Use the slice once. The point of this pass is to learn how the slice works.

Stay on what the slice shows. Each step follows what the last action showed.

Count each action. An action is one thing done with the slice: open, click, type, submit, choose, or the same kind of step the slice showed. Write the count down. The second pass uses that count.

This pass ends when the slice has been used once. It does not continue into the random pass until that one use is done.

If something breaks during this pass, write that bug before the next action.

If the user says stop during this pass, stop. The second pass does not run. The stop name is `the user said stop`.

## Pass two

This pass is no longer careful. It does not walk the first pass again as a script. It does not walk the checks the plan already named.

It follows what the last action showed. The next action starts from what is on screen now, or from the last response. A control that is not there is not used.

Some actions add randomness. Use one of these, chosen from what the last action showed:

- a double-click
- a hover back and forth
- repeating an action
- using the same control more than once

Not every action is one of those. When the slice is not a screen, a double-click and a hover do not apply. Repeating an action and using the same control more than once still apply.

Write a bug when something breaks, before the next action. A bug is what broke while using the slice. Record what broke, what was done, and what the last action showed.

## The stop

The second pass does not run forever. The user does not set a clock. Do not ask for a time, a minute count, or a timer.

The second pass lasts about as long as the first pass. That length is the action count from pass one. It is long enough to provoke bugs. When the second pass has taken that many actions, it stops.

Name the stop in the file and in the chat, so a run can tell it is done. Use one of these names:

| Stop | When |
| --- | --- |
| `matched the first pass` | The second pass has taken as many actions as pass one took to learn the slice once. That is about as long as the first pass. Then it stops. |
| `the user said stop` | The user says stop before that count. The pass ends on that action. Bugs already written stay. |

Do not start another pass after either stop.

## Write the bugs

Write `docs/specs/<slug>/explore.md` in that slice’s folder. That folder already exists. Do not create a slug. Do not create a folder.

When the file is missing, write it. When it exists, append the next run. Leave earlier runs as they are. Continue bug numbers after the highest `B#` already in the file.

```text
# Explore

## Run 1

Slice: docs/specs/<slug>/
Pass one actions: <n>
Stop: matched the first pass

### Learned

<what the slice does, from using it once>

### Bugs

#### B1
What broke: <one line>
Did: <one line>
Last action showed: <one line>
Pass: one

```

`Stop` is `matched the first pass` or `the user said stop`.

When nothing broke, write `Bugs: none` under `### Bugs`. Still write the stop.

Do not write the checks the plan already named. A verify note, a task check, or an acceptance line stays in `plan.md`, `tasks.md`, or `spec.md`. This file records what broke while using the slice.

Do not edit `spec.md`, `plan.md`, `tasks.md`, `verify.md`, `fix-log.md`, or application code. Do not commit. Do not push. Do not open a pull request.

## A bug and `/crav1-fix-bug`

A bug this skill finds stays in `explore.md`. Do not send it to `/crav1-fix-bug`. Do not name that command.

When the user says so in that turn, for a bug this skill found, follow `/crav1-fix-bug` (drop-in: `.cursor/skills/crav1/crav1-fix-bug/SKILL.md`; plugin: sibling `skills/crav1-fix-bug/SKILL.md`) for that bug. Do not start the lane it names.

## Stop

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-complete-task`, `/crav1-verify-spec`, `/crav1-fix-from-verify`, `/crav1-fix-live`, or `/crav1-finalize-commit`.

When `explore.md` changed, name `/crav1-finalize-commit`. Do not run it.

Output only:

- Slice (`docs/specs/<slug>/`)
- File written
- Stop name
- Bugs written, or `Bugs: none`

## Hard rules

- No build of the slice: stop. Write nothing. Do not start Build.
- Pass one uses the slice once and counts its actions.
- Pass two lasts about as long as that count, long enough to provoke bugs, then stops. The stop name is `matched the first pass`.
- The user saying stop ends the run sooner. The stop name is `the user said stop`.
- The user does not set a clock. The second pass does not run forever.
- Do not write the checks the plan already named.
- Do not start Specify, Plan, or Build. Do not move work into a lane.
- Do not send a bug to `/crav1-fix-bug` unless the user says so in that turn.
- Later skill. Not a starter option. Asking for startup options names only the seven and does not run this command.
