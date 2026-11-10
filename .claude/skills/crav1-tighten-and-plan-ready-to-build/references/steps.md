# Steps 2 to 6

Run these in order. When a playbook was named, the playbook question is answered before any later step, including a read-only check. Each one is the existing skill, not a copy of it. A step with nothing to do says so in one line, records `Result: nothing-to-do` with the versions it covers, and moves on. Record that one step right then. One `record` call per step. Do not record several steps in one command. Do not pass `--when`. The script stamps Done. `record` refuses more than one step.

After a step, show the progress line and get a yes before `record --yes`. The answers inside the step do not cover that line. Skip this confirm only when the step's own confirm already included this record. An extra's yes is that case.

The new-slice route in `docs/reference/workflow.yaml` marks `/crav1-review-architecture` optional, and it also has optional `/crav1-create-feature-branch` and `/crav1-ado-sync`. This walk does not change that route. Inside the walk, architecture review always runs. The walk does not run create-feature-branch or ado-sync. They are not locked steps.

## 2. Architecture review

Always run `/crav1-review-architecture`. It writes nothing. Show its issues. When it finds nothing to critique, say so and move on. Do not tighten in its place.

## 3. Tighten the spec

Run `/crav1-tighten-spec` as that skill walks: one issue at a time. A batch of `I#: letter` answers is that skill's own rule. Do not add a second way to patch. When it finds no issues, say so and move on.

An issue whose only work is an `Answered:` line, or that only repeats a question already under `## Open questions`, goes to step 4 with no menu. One line: `Left for /crav1-resolve-open-questions: I3, I10, I11.` More than 8 issues: that skill shows a one-line count by kind first, then one issue or a small group. One by one is always offered. Do not print the full list first.

## 4. Open questions

Run `/crav1-resolve-open-questions`. When `## Open questions` has nothing left to settle, say so and move on.

Then the extras batch below, once. Do not go on to the plan first.

## After step 4, one batch of extras

Once, after `/crav1-resolve-open-questions`, when the kept-open questions are known. Not at an earlier step, and not again later. Offer the ones that apply, in one batch, at most four options, a fifth under Other. List a recommended one first and end its label with ` (Recommended)`. When any extra applies, do not go on to the plan without that offer. When none apply, say so in one line and move on. Do not run any of them unless the user picks it.

Offer `/crav1-show-or-ask-open-questions` when any kept-open question is for someone else.

Not fixed steps. Security and tests stay optional. When one of them finishes inside this walk, record it before `resume`. The record is `- Extra: review-security`, `- Extra: research`, `- Extra: model-data`, `- Extra: show-or-ask-open-questions`, or `- Extra: suggest-tests-for-code`. Pass `--yes` because the user already picked the extra. Do not ask them to run `cover`. That record leaves earlier steps done. Auto-record stays this way.

`cover --yes` is optional and is not how this walk records an extra it just ran. Use it only for a write made outside this walk, when you want the current spec, plan, and tasks counted as part of the walk without a named extra.

- Research helper, no slash command. Offer it when the spec needs a technology, a service, or a scaling choice nobody has decided. Flag the question. Do not invent a command.
- `/crav1-review-security`, when the spec touches trust, access, or personal data, or the user asks. Architecture review already names it. Still optional here.
- `/crav1-model-data`, when the spec is about stored data and no `Data model:` line names a saved model. It does not edit requirements.
- `/crav1-show-or-ask-open-questions`, when a question is for someone else.
- `/crav1-suggest-tests-for-code`, when the spec names existing code and the acceptance lines do not already name the checks. A kept suggestion goes through `/crav1-add-to-spec`, which that skill runs on yes. This walk does not write the tests.

## 5. Plan

Run `/crav1-plan-from-spec`. That skill writes `plan.md` and `tasks.md`. When both already match the spec and it has nothing to add, say so and move on. Do not write the plan from this walk.

## After the plan, questions with no Blocks line

Before step 5 is recorded, run `scripts/walk_progress.py unlinked --root <spec-folder>`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It lists kept-open questions that still have no `Blocks:` line. It writes nothing.

An empty list: say so, record the plan step, and move on.

A list: offer to set them before the plan review. Options: `one batch` (Recommended), `one by one`. For each question, the choices are the unticked tasks it blocks (`Blocks: T2, T4`), **None** (`Blocks: none`, and a short reason in parentheses when they give one, such as `later phase`), or **The whole slice** (no line). One yes writes only those lines. A task list also sets that question's Risk line to `kept open; blocks T2, T4 until resolved.` None replaces "do not implement until resolved" on that question's Risk line with `kept open; does not block the current tasks.` The whole slice leaves no line, keeps "do not implement until resolved", and still blocks every current task. Do not start the plan review until this offer is answered. Then record the plan step, so the spec version includes these lines.

## 6. Review the plan, then tighten it

Run `/crav1-review-plan`, then `/crav1-tighten-plan`, in that order. Review writes the `Reviewed:` line and does not edit the plan otherwise. Tighten walks plan issues and does not edit `spec.md`. When either has nothing to do, say so. Record one progress step, `review-and-tighten-plan`, only after both have finished or both had nothing to do.

## Jump back

A jump back reruns the skill that owns the step, even for a small patch. The walk does not edit `spec.md`, `plan.md`, or `tasks.md` on a jump back, and it does not write `Reviewed:`. `/crav1-review-plan` writes that line. `/crav1-plan-from-spec` writes the plan and the tasks. `/crav1-tighten-plan` walks plan issues. `/crav1-resolve-open-questions` settles questions. Do not record a step `done` after editing those files yourself. Do not record `nothing-to-do` for a step you did not run.

When a reopened step truly has nothing new, run `clear --step <id> --yes`. Do not record `nothing-to-do` over it. A `nothing-to-do` record keeps an earlier `done` Result.
