---
name: crav1-fix-bug
description: >-
  Name one real bug the user already named. Say where it was seen (verify,
  a report, or production), point at the spec or the shipped behavior it
  breaks, and name the lane. Cross-cutting. Not a lane and not a stretch of
  verify. Does not hunt, start the lane, edit code, open a pull request, or
  create an Azure Boards work item.
disable-model-invocation: true
icon: alert-triangle
color: orange
---

# Fix a bug

Name **one** real bug they already named. Say where it was seen, what it breaks, and which lane owns it. Then stop.

Command: `/crav1-fix-bug`.

This is cross-cutting. It is not a lane. It is not a stretch of verify. It is not `/crav1-fix-from-verify` and not `/crav1-fix-live`. Those walk the inner loop on work that is still in Build. This skill is an intake for a bug that already exists.

Run it only when **this turn** names a real bug. If this turn does not name one, stop. Do not go hunting. Do not scan the repo, `verify.md`, issues, tickets, or production. Do not pick a bug for them. Do not ask them to choose from bugs you found.

It is not a skill that runs because a repo is new. Spark, ideas, intake, and match do not run it. Specify, plan, and verify do not run it. It is not started automatically. Other skills do not run this one.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill. This command still runs only when the user names a real bug.

## A real bug

A real bug is one of these:

- A verify failure on work that is **already shipping**
- A defect that comes in from **outside** (a report, or production)

These stay where they are. Say which row it is and stop. Do not name a lane for them.

| What they brought | Where it stays |
| --- | --- |
| A design gap found before Build | The spec |
| An unfinished task | That task |
| A one-off flaky check | A note, unless it keeps blocking ship |
| A verify failure on work that is not shipping yet | The inner loop. Point at `/crav1-fix-from-verify` (drop-in: `.claude/skills/crav1-fix-from-verify/SKILL.md`; plugin: sibling `skills/crav1-fix-from-verify/SKILL.md`). Do not run it |

A one-off flaky check that **keeps blocking ship** is a real bug. They have to say it keeps blocking ship. Do not decide that by hunting.

Work is already shipping when they say it shipped, it is in production, or the failure is on the default branch after the change merged. A failure on the feature branch still in Build is the inner loop.

## Where it was seen

Say one of: **verify**, **a report**, or **production**.

Use the place they already named. If they named the bug and not the place, ask with options only. Use the questions tool when it is available. The options are verify, a report, and production. Stop until they pick. Do not guess. Do not hunt for the place.

## What to say

Read only what they pointed at, plus the spec or the shipped behavior they said it breaks, when that file is already in front of you. Do not search the repo for a matching bug. Do not write files.

```text
Bug: <the name they gave, or one line from what they named>
Seen: <verify | a report | production>
Breaks: <docs/specs/<slug>/ or the shipped behavior, one line>
Lane: <Specify | Plan | Build>
Why: <one line>
```

Name the lane. Do not start it. Do not run the command that lane would use.

| What is wrong | Lane |
| --- | --- |
| Spec miss. The spec does not say what shipping behavior must be true, or shipping behavior and the spec disagree | Specify |
| Plan miss. The plan never named the file or the check this bug needed | Plan |
| Verify miss, or the implementation is broken against a spec and a plan that already say the right thing | Build |

A spec miss goes to Specify. A plan miss goes to Plan. A verify miss or a broken implementation goes to Build.

If the bug is a defect from outside and no spec says what shipping must do, the lane is Specify. Do not invent the spec text. Do not create a slug.

If they did not point at a spec and none is already in front of you, `Breaks` is the shipped behavior in their words. Do not write `spec.md`.

## Stop

Do not edit code. Do not edit `spec.md`, `plan.md`, `tasks.md`, or `verify.md`. Do not open a pull request. Do not create an Azure Boards work item. Do not write `work-item.md`. Do not call Azure DevOps. Do not pass `--work-items`. Do not commit. Do not push.

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-tighten-spec`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-fix-from-verify`, `/crav1-fix-live`, `/crav1-verify-spec`, `/crav1-open-pr`, or `/crav1-finalize-commit`.

## Hard rules

- No bug named in this turn: stop. Do not hunt.
- Not a real bug: say where it stays and stop. Do not name a lane.
- Name the lane for a real bug. Do not start that lane.
- No code edits. No spec edits. No pull request. No Azure Boards work item.
- Not a stretch of verify. It is not a skill that runs because a repo is new. It is not started automatically.
