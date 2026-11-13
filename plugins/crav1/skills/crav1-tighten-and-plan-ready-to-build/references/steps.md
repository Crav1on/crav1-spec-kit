# Steps 2 to 6

Run these in order. When a playbook was named, the playbook question is answered before any later step, including a read-only check. Each one is the existing skill, not a copy of it. Open its file from this skill's folder, as [open-skill-file.md](../../crav1-docs/reference/open-skill-file.md) says (1.134.0). A step with nothing to do says so in one line, records `Result: nothing-to-do` with the versions it covers, and moves on. Record that one step right then. One `record` call per step. Do not record several steps in one command. Do not pass `--when`. The script stamps Done. `record` refuses more than one step.

After a step, show the progress line and get a yes before `record --yes`. The answers inside the step do not cover that line. Skip this confirm only when the step's own confirm already included this record. An extra's yes is that case. When that confirm shares one card with the step's batch, `yes (Recommended)` covers the recommendations and the progress line. Typed changes are that card's free-text answer. Do not add an `Edits` option. The rule is `crav1-docs/reference/question-cards.md`.

The new-slice route in `docs/reference/workflow.yaml` marks `/crav1-review-architecture` optional, and it also has optional `/crav1-create-feature-branch` and `/crav1-ado-sync`. This walk does not change that route. Inside the walk, architecture review always runs. The walk does not run create-feature-branch or ado-sync. They are not locked steps.

## 2. Architecture review

Open `../crav1-review-architecture/SKILL.md` (`/crav1-review-architecture`). It writes nothing. Show its issues. When it finds nothing to critique, say so and move on. Do not tighten in its place.

## 3. Tighten the spec

Open `../crav1-tighten-spec/SKILL.md` (`/crav1-tighten-spec`) as that skill walks: one issue at a time. A batch of `I#: letter` answers is that skill's own rule. Do not add a second way to patch. When it finds no issues, say so and move on.

An issue whose only work is an `Answered:` line, or that only repeats a question already under `## Open questions`, goes to step 4 with no menu. One line: `Left for /crav1-resolve-open-questions: I3, I10, I11.` More than 8 issues: that skill shows a one-line count by kind first, then one issue or a small group. One by one is always offered. Do not print the full list first.

## 4. Open questions

Open `../crav1-resolve-open-questions/SKILL.md` (`/crav1-resolve-open-questions`). When `## Open questions` has nothing left to settle, say so and move on.

Then the extras batch below, once. Do not go on to the plan first.

## After step 4, one batch of extras

Once, after `/crav1-resolve-open-questions`, when the kept-open questions are known. Not at an earlier step, and not again later. One multi-select card, as `crav1-docs/reference/question-cards.md` says. Each extra that applies is an option. List a recommended one first and end its label with ` (Recommended)`. Always include **None, go to plan**. That option runs no extra and the walk goes on to `/crav1-plan-from-spec`. At most three extras on the card, plus that option. A further extra is named in the question. When any extra applies, do not go on to the plan without that offer. When none apply, say so in one line and move on. Do not run any of them unless the user picks it. Do not tell them to type none.

Offer `/crav1-show-or-ask-open-questions` when any kept-open question is for someone else. When the user picks an extra, open its file and follow it.

Not fixed steps. Security and tests stay optional. When one of them finishes inside this walk, record it before `resume`. The record is `- Extra: review-security`, `- Extra: research`, `- Extra: model-data`, `- Extra: show-or-ask-open-questions`, or `- Extra: suggest-tests-for-code`. Pass `--yes` because the user already picked the extra. Do not ask them to run `cover`. That record leaves earlier steps done. Auto-record stays this way.

`cover --yes` is optional and is not how this walk records an extra it just ran. Use it only for a write made outside this walk, when you want the current spec, plan, and tasks counted as part of the walk without a named extra.

- Research helper, no slash command. Offer it when the spec needs a technology, a service, or a scaling choice nobody has decided. Flag the question. Do not invent a command.
- Open `../crav1-review-security/SKILL.md` (`/crav1-review-security`), when the spec touches trust, access, or personal data, or the user asks. Architecture review already names it. Still optional here.
- Open `../crav1-model-data/SKILL.md` (`/crav1-model-data`), when the spec is about stored data and no `Data model:` line names a saved model. It does not edit requirements.
- Open `../crav1-show-or-ask-open-questions/SKILL.md` (`/crav1-show-or-ask-open-questions`), when a question is for someone else.
- Open `../crav1-suggest-tests-for-code/SKILL.md` (`/crav1-suggest-tests-for-code`), when the spec names existing code and the acceptance lines do not already name the checks. A kept suggestion goes through add-to-spec, which that skill opens on yes. This walk does not write the tests.

## 5. Plan

Open `../crav1-plan-from-spec/SKILL.md` (`/crav1-plan-from-spec`). That skill writes `plan.md` and `tasks.md`, and an `## Approval needed` item when a constraint says a named person gives a yes before something (`references/write.md` in that skill, "Approval needed"). When both already match the spec and it has nothing to add, say so and move on. Do not write the plan, or that item, from this walk.

## After the plan, questions with no Blocks line

Before step 5 is recorded, run `scripts/walk_progress.py unlinked --root <spec-folder>`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It lists kept-open questions that still have no `Blocks:` line. It writes nothing.

An empty list: say so, record the plan step, and move on.

A list: offer to set them before the plan review. Options: `one batch` (Recommended), `one by one`. `one batch` is a batch card. Follow **Batch of several items** in `crav1-docs/reference/question-cards.md` before this card. Print the findings table in this reply, then ask. The card names each item and its recommendation, for example `P4 tasks miss the 400 path: A add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table. For each question, the choices are the unticked tasks it blocks (`Blocks: T2, T4`), **None** (`Blocks: none`, and a short reason in parentheses when they give one, such as `later phase`), or **The whole slice** (`- Blocks: whole slice`). One yes writes only those lines. A task list also sets that question's Risk line to `kept open; blocks T2, T4 until resolved.` None replaces "do not implement until resolved" on that question's Risk line with `kept open; does not block the current tasks.` The whole slice writes `- Blocks: whole slice` and sets that Risk line to `kept open; blocks the whole slice until resolved.` A `Blocks:` line wins over that Risk wording, so the line does not keep "do not implement until resolved". Do not start the plan review until this offer is answered. Then record the plan step, so the spec version includes these lines.

## 6. Review the plan, then tighten it

Open `../crav1-review-plan/SKILL.md` (`/crav1-review-plan`), then Open `../crav1-tighten-plan/SKILL.md` (`/crav1-tighten-plan`), in that order. Review writes the `Reviewed:` line and does not edit the plan otherwise. Tighten walks plan issues and does not edit `spec.md`. Its batch card follows **Batch of several items** in `crav1-docs/reference/question-cards.md` (1.145.0). Print the findings table in this reply, then ask. The card names each item and its recommendation, for example `P4 tasks miss the 400 path: A add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table. When either has nothing to do, say so. Record one progress step, `review-and-tighten-plan`, only after both have finished or both had nothing to do.

## Spec finding during plan review (1.135.0)

A finding from the plan review that is tagged **spec** is a spec defect. Inside this walk it is not a pause. A plan-tagged finding stays in `/crav1-tighten-plan`, as that skill already walks it. Do not pass a plan finding to `spec-finding`.

Run `scripts/walk_progress.py spec-finding --root <spec-folder> --id P2 --text "<the finding>"`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. With no `--choice` it writes nothing. `--tag plan` is not a jump back.

When `offer` is `jump-back`, ask one question card, as `crav1-docs/reference/question-cards.md` says. Use the script's `options`, in that order. The recommended label is `run /crav1-tighten-spec on just that finding now (Recommended)`. The other label is `keep it as an open point and continue`. Do not add a third option.

On the recommended yes, run the same command with `--choice tighten-spec --yes`. Then Open `../crav1-tighten-spec/SKILL.md` (`/crav1-tighten-spec`) and follow it for that finding only, with that skill's own confirms. Do not start it as a slash command. The rule is [open-skill-file.md](../../crav1-docs/reference/open-skill-file.md) (1.134.0). After that skill finishes, continue this walk. Open `../crav1-plan-from-spec/SKILL.md` for the parts that finding changed, then Open `../crav1-review-plan/SKILL.md` and Open `../crav1-tighten-plan/SKILL.md`, then the ready check. Do not pause.

On the other option, run `spec-finding` with `--choice open-point --yes` and continue `/crav1-tighten-plan`, then the ready check. Do not reopen the spec for that finding.

The same finding is the same words. The script stores `Key:`. It is offered once. When `already_jumped` is true, do not ask again. Pass `--yes` so the open point is recorded, then continue review-and-tighten-plan and the ready check. A second `tighten-spec` choice is refused.

`walk-progress.md` records the jump-back step. Do not hand-edit it.

```text
- Jump-back: P2
  Done: 2026-11-11T20:30:00+00:00
  Finding: the plan requires a named person's yes to stop a prod function app
  Result: jumped
  Open: ../crav1-tighten-spec/SKILL.md
  Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build
  Key: 6a034c36ad9e

- Open point: P2
  Done: 2026-11-11T20:30:00+00:00
  Finding: the plan requires a named person's yes to stop a prod function app
  Result: open-point
  Continue: review-and-tighten-plan, tasks-ready-to-build
  Key: 6a034c36ad9e
```

`Result: jumped` is only on `- Jump-back:`. `Result: open-point` is only on `- Open point:`. This walk does not edit `spec.md` on the jump. The skill that owns the spec does, after its own yes. The walk does not write `Reviewed:`. This walk never writes `verify.md`.

## Jump back

A jump back opens the file of the skill that owns the step, even for a small patch, and follows it. The walk does not edit `spec.md`, `plan.md`, or `tasks.md` on a jump back, and it does not write `Reviewed:`. Open `../crav1-review-plan/SKILL.md` (`/crav1-review-plan`) for that line. Open `../crav1-plan-from-spec/SKILL.md` (`/crav1-plan-from-spec`) for the plan and the tasks. Open `../crav1-tighten-plan/SKILL.md` (`/crav1-tighten-plan`) for plan issues. Open `../crav1-resolve-open-questions/SKILL.md` (`/crav1-resolve-open-questions`) for questions. Do not record a step `done` after editing those files yourself. Do not record `nothing-to-do` for a step you did not run.

When a reopened step truly has nothing new, run `clear --step <id> --yes`. Do not record `nothing-to-do` over it. A `nothing-to-do` record keeps an earlier `done` Result. A progress-only edit is not a reopen. Do not ask to clear it. The rule is [progress.md](progress.md) (1.138.0).
