---
name: crav1-suggest-tests-for-code
description: >-
  The user points at code that already exists, one repo or one area, not
  the whole system. Read that code and suggest tests for what it can
  actually break. A function gets a few checks. A page gets a browser
  check. A boundary gets an integration check. Do not dump every test
  type. Every suggestion stays listed. The user takes them one at a time:
  keep, leave, or dismiss. Dismiss means it is not offered again. A kept
  suggestion goes onto the existing spec through /crav1-add-to-spec. Plan
  turns it into a task. Does not write the tests, change the code, or
  start Specify, Plan, or Build. Cross-cutting. Not a starter option.
disable-model-invocation: true
icon: list-checks
color: yellow
---

# Suggest tests for code

The user points at code that already exists. You read that code and suggest tests for what that code can actually break. Then the user takes the suggestions one at a time.

Command: `/crav1-suggest-tests-for-code`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. The seven starter options stay unchanged.

Other skills do not run this one. Spark, specify, plan, and verify do not run it. It is not started automatically.

## What the user points at

Everything after `/crav1-suggest-tests-for-code`, and every `@`, is the pointer.

The pointer is **one repo** or **one area**. An area is one folder, one file, one module, or one page. It is not the whole system.

If the user pointed at the whole system, at more than one repo, or at `docs/system/` as the code, stop. Say this command reads one repo or one area. Do not read the whole system. Do not invent an area. When the message already names more than one real area, ask with options only. Use the questions tool when it is available. One option per area the user already named. Do not offer the whole system. Stop until the user picks.

If the user pointed at no code, stop. Ask the user to point at one repo or one area. Do not scan the repo to pick one. Do not suggest tests.

## Which spec

A kept suggestion goes onto the **existing** spec. A dismissed suggestion is recorded on that same spec so it is not offered again. This command does not create a slug. It does not create a folder.

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

If the user named one existing spec, that is the spec.

If the user named none and exactly one spec folder exists, that is the spec.

If more than one spec folder exists and the user named none, ask with options only. One option per spec folder. Label each option with `docs/specs/<slug>/` and the title line of that `spec.md` when it has one. Do not ask the user to type a slug. Stop until the user picks.

If no spec folder exists, stop. Say there is no existing spec. Point at the starter that fits what the user brought, and do not run it. Write nothing. Do not suggest tests that have nowhere to be kept.

## Read

Read only the code the user pointed at, the tests that already sit with that code, and that spec.

Do not read the rest of the system to grow the list.

Skip a break the tests already cover. Skip a check already on that spec as acceptance. Skip a line under `## Dismissed test suggestions`. Those are not suggestions. A skipped line is not a dropped suggestion.

## Suggest

Suggest a test only for a way that code can actually break. Do not invent a behavior the code does not have.

The kind follows the code. Do not dump every test type onto one thing.

- A **function** gets a few checks. One check for each way that function can break. The kind is **unit**. List every one of those ways. Do not invent a way the code does not have.
- A **page** gets a **browser** check for each way that page can break in front of someone using it. Do not add a unit check for the page.
- A **boundary** gets an **integration** check. A boundary is where two parts meet in the code the user pointed at. One check per edge. Do not add one where there is no edge.

Do not give one function a unit check and a browser check and an integration check. Do not add contract, load, speed, accessibility, golden, property, smoke, chaos, or fuzzing.

When the area holds a function and a page and a boundary, each gets the kind above. That is not a dump of every test type.

If the code can break in no way that is not already covered, dismissed, or already on the spec, say so. Do not invent a suggestion.

## The list

Show every suggestion before the first question. Number `C1`, `C2`, … Continue after the highest `C#` already used in this chat. Nothing is dropped to keep the list short.

```text
C1 — unit
What can break: <one line the code shows>
Check: <one line a stranger could run>
Where: <path>
```

The kind is `unit`, `browser`, or `integration`.

On every later turn, list every suggestion again. Mark the ones already answered `kept`, `left`, or `dismissed`. The ones not answered stay on the list. Do not remove a line to keep the list short.

## One at a time

Ask about one suggestion. Use the questions tool when it is available. The options are only:

1. **Keep**
2. **Leave**
3. **Dismiss**

Stop until the user picks. Do not write before that reply.

A batch (`C1 keep, C2 leave`) applies only the suggestions named in that batch, in order. A suggestion with no mark stays unanswered. Do not treat silence as dismiss.

### Keep

A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Follow only the handoff **From /crav1-suggest-tests-for-code** in that skill (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/SKILL.md`; plugin: sibling `skills/crav1-add-to-spec/SKILL.md`). One suggestion. Then stop that handoff.

Do not write the spec in this skill. Do not open the impact question. Do not start Specify. Do not run `/crav1-plan-from-spec`.

Plan turns that kept suggestion into a task when the user later runs plan. This command does not run plan. It does not write `plan.md` or `tasks.md`.

### Leave

Write nothing. The suggestion stays listed as left. The next run of this command offers it again when that code can still break that way.

### Dismiss

Dismiss means it is not offered again. Follow the same handoff, with the quote marked dismissed. The line is not acceptance. Plan does not turn it into a task.

The next run reads `## Dismissed test suggestions` and does not offer that check.

## After each answer

Recap that one suggestion: kept, left, or dismissed.

Then ask the next unanswered suggestion. Do not apply the next one in the same turn.

When every suggestion has an answer, stop. Repeat the full list with kept, left, or dismissed on each line.

## Stop

Do not write the tests. Do not change the code. Do not edit `plan.md`, `tasks.md`, or `verify.md`. Do not commit. Do not push. Do not open a pull request.

Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-complete-task`, `/crav1-verify-spec`, `/crav1-fix-from-verify`, `/crav1-fix-live`, or `/crav1-finalize-commit`.

When a file changed, name `/crav1-finalize-commit`. Do not run it.

Name `/crav1-plan-from-spec` only as the later step that turns a kept suggestion into a task. Do not run it.

## Hard rules

- One repo or one area. The whole system stops with no list.
- No code pointed at: stop. Do not pick an area.
- No existing spec: stop. Do not create a slug. Do not create a folder.
- Every suggestion stays listed. Nothing is dropped to keep the list short.
- One suggestion at a time: keep, leave, or dismiss.
- Dismiss means it is not offered again.
- A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. This command does not run Plan.
- Do not write the tests. Do not change the code. Do not start Specify, Plan, or Build. Do not move work into a lane.
- Later skill. Not a starter option. Asking for startup options names only the seven and does not run this command.
