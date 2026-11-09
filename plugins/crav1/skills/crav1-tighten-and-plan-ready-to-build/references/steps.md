# Steps 2 to 6

Run these in order. Each one is the existing skill, not a copy of it. A step with nothing to do says so in one line, records `Result: nothing-to-do` with the versions it covers, and moves on.

The new-slice route in `docs/reference/workflow.yaml` marks `/crav1-review-architecture` optional, and it also has optional `/crav1-create-feature-branch` and `/crav1-ado-sync`. This walk does not change that route. Inside the walk, architecture review always runs. The walk does not run create-feature-branch or ado-sync. They are not locked steps.

## 2. Architecture review

Always run `/crav1-review-architecture`. It writes nothing. Show its issues. When it finds nothing to critique, say so and move on. Do not tighten in its place.

## 3. Tighten the spec

Run `/crav1-tighten-spec` as that skill walks: one issue at a time. A batch of `I#: letter` answers is that skill's own rule. Do not add a second way to patch. When it finds no issues, say so and move on.

## 4. Open questions

Run `/crav1-resolve-open-questions`. When `## Open questions` has nothing left to settle, say so and move on.

When a kept-open question needs someone else to answer, offer `/crav1-show-or-ask-open-questions` in the optional batch below. Do not run it unless the user says yes.

## 5. Plan

Run `/crav1-plan-from-spec`. That skill writes `plan.md` and `tasks.md`. When both already match the spec and it has nothing to add, say so and move on. Do not write the plan from this walk.

## 6. Review the plan, then tighten it

Run `/crav1-review-plan`, then `/crav1-tighten-plan`, in that order. Review writes the `Reviewed:` line and does not edit the plan otherwise. Tighten walks plan issues and does not edit `spec.md`. When either has nothing to do, say so. Record one progress step, `review-and-tighten-plan`, only after both have finished or both had nothing to do.

## Offered only when the spec needs them

Not fixed steps. Security and tests stay optional. Offer the ones that apply in one batch, at most four options, a fifth under Other. List a recommended one first and end its label with ` (Recommended)`. Do not run any of them unless the user picks it. After one of them writes, run `resume` and reopen only the steps it affected.

- Research helper, no slash command. Offer it when the spec needs a technology, a service, or a scaling choice nobody has decided. Flag the question. Do not invent a command.
- `/crav1-review-security`, when the spec touches trust, access, or personal data, or the user asks. Architecture review already names it. Still optional here.
- `/crav1-model-data`, when the spec is about stored data and no `Data model:` line names a saved model. It does not edit requirements.
- `/crav1-show-or-ask-open-questions`, when a question is for someone else.
- `/crav1-suggest-tests-for-code`, when the spec names existing code and the acceptance lines do not already name the checks. A kept suggestion goes through `/crav1-add-to-spec`, which that skill runs on yes. This walk does not write the tests.
