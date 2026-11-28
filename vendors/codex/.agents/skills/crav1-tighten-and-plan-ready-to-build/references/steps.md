# Steps 2 to 6

**Merged since sync (1.194.0).** At the walk start, after the specs-repo sync and before step 1, run `scripts/merged_since_sync.py check --spec <spec.md> --code-repo <code checkout> --base <Merges into>` in `crav1-add-to-spec` (the one shared check), as `crav1-docs/reference/running-scripts.md` says. It fetches origin once first (1.196.0; `--no-fetch` skips it), prefers `origin/<branch>` over a stale local branch, catches a tip that is already merged, and compares each branch in the spec's `Synced at:` lines with that branch's base, found per branch (1.195.0): `--base`, which callers pass as the repo's `Merges into` branch from `docs/system/repos.md` when it names one (leave `--base` out otherwise), then that `Merges into` column, then the base branch's own `Synced at` line, then `origin/develop`, then the default branch and writes nothing. When `offer` is `take-in`, ask its one yes card with its `question` and two `options`. On yes, Open `../crav1-add-to-spec/SKILL.md` for its `command` and follow the PR or branch step inline with that skill's own confirms, then run its `after_yes` (`merged_since_sync.py stamp ... --yes`) to move `Synced at` to the merge. On `not now`, write nothing. Either way the walk continues with its steps. With no card (`not-merged`, `already-synced` or `skipped`), say nothing.

**Code drift at the start (1.195.0).** In the same place, right after that check, run `scripts/walk_progress.py code-drift --root <spec-folder> --code-repo <code checkout> --base <Merges into> --vendor codex` (leave `--base` out when `repos.md` names none). It counts only commits the spec has not recorded: commits already named in the spec or in a note's `commits:` list, and base merge-ins, are left out and reported as `already_recorded` and `base_merge_ins` next to `count`. When `offer` is `add-to-spec`, ask its card now, as **Spec behind the code first** below says. When anything stale was seen here (`take-in`, `behind`, or a stale research mark), pass `--stale-seen` to every `readiness` run of this walk, so a reopen card recommends rerun.

**Tickable at the start (1.196.0).** Right after the code checks, run `scripts/walk_progress.py tickable --root <spec-folder> --write --vendor codex`. This tick is owned by `$crav1-tighten-spec`'s rule. It has no card for clear evidence (a verify row passing on the base, evidence files named): it ticks the acceptance item and, when a later open task touches the evidence files, ticks now and adds a recheck line to that task's verify note. Say its one `line`. Its `cards` go to the tighten-spec step as issues: only a failing row, or a passing row with no evidence (1.197.0). An untested or pending row is left open with no question; say its `waiting_line` when there is one.

**Finished claims (1.196.0).** Also at the walk start, run `scripts/claims.py prune --root <spec-folder> --code-repo <code checkout> --base <Merges into>` in `crav1-build-walk`. No card: it clears claims whose tasks are all ticked or whose branch is merged into `origin/<base>`, and prints one summary line such as `Cleared 2 finished claims: T5 (PR 71), T8 (ticked).` Say that line; say nothing when there is none. Unfinished claims stay, with their age warning; a finished claim never warns. Never write a line saying claims or claimed tasks were kept or stay unchanged.

**Signed-off UI screens at the start (1.211.0).** When the slice has `ui/`, also run `../crav1-design-ui/scripts/ui_screens.py status --root <spec-folder>` (skill `crav1-design-ui`). No card. It compares each screen with its item's `Screen:` mark. For each screen whose state is `changed`, say one line with its `why`: that signed-off screen had a material change since its yes. A `minor` change says nothing; the yes stays.

Run these in order. When a playbook was named, the playbook question is answered before any later step, including a read-only check. Each one is the existing skill, not a copy of it. Open its file from this skill's folder, as [open-skill-file.md](../../crav1-docs/reference/open-skill-file.md) says (1.134.0). A step with nothing to do says so in one line, records `Result: nothing-to-do` with the versions it covers, and moves on. Record that one step right then. One `record` call per step. Do not record several steps in one command. Do not pass `--when`. The script stamps Done. `record` refuses more than one step.

**Inside the walk (1.196.0).**

- A locked skill the walk opens prints no Run next and no `Uncommitted:` line; only the walk's own last reply ends the run.
- After a spec jump-back, follow its `continue` list: rerun plan-from-spec for the lines the jump patched, then review and tighten the plan, then the ready check. Do not fold the plan follow-up into a tighten-plan finding.
- Run the plan reviewer in the foreground; the walk cannot go on without it, so no wake-up timer.
- Quote every free-text argument, `--text "…"` and `--topic "…"`, so PowerShell passes it as one value. When `spec-finding` returns `kind-conflict`, ask its card: merged work that is not marked merged counts as code drift.

**The save rides on the step's last yes (1.196.0).** A step's record is not its own card. The step's last card says it in its result-on-yes line, for example `Yes applies the eight fixes and saves the plan review as done.`, and that yes runs `record --yes` too. Only a step that asked no card at all gets the save card below, and only once: when the next step has a card, fold it into that card's result line instead (`… and saves the architecture review as done.`). The ready check never gets a save card (1.197.0): it is a read-only result, so record it with `record --yes` right after printing its reply, with no card. Plan-from-spec housekeeping (Risks wording refreshes, Trace evidence shas, header read lines) is applied with no card and one summary line, as in tighten-plan.

The fallback save card says in plain words what will be recorded. The card does not quote the progress line, `walk-progress.md`, `Done`, `Result`, or step ids:

Card: Save the architecture review as done?
- **Save it (Recommended)** (`yes`): the walk notes the architecture review as done, so a later run does not ask again. Why: the review just ran with nothing to change.
- **Not now** (`stop`): save nothing, and the walk asks again next time.

 The answers inside the step do not cover that line. Skip this confirm only when the step's own confirm already included this record. An extra's yes is that case. When that confirm shares one card with the step's batch, `yes (Recommended)` covers the recommendations and the progress line. Typed changes are that card's free-text answer. Do not add an `Edits` option. The rule is `crav1-docs/reference/question-cards.md`.

The new-slice route in `docs/reference/workflow.yaml` marks `$crav1-review-architecture` optional, and it also has optional `$crav1-create-feature-branch` and `$crav1-ado-sync`. This walk does not change that route. Inside the walk, architecture review always runs. The walk does not run create-feature-branch or ado-sync. They are not locked steps.

## 2. Architecture review

Open `../crav1-review-architecture/SKILL.md` (`$crav1-review-architecture`). It writes nothing. Show its issues. When it finds nothing to critique, say so and move on. Do not tighten in its place.

## 3. Tighten the spec

Open `../crav1-tighten-spec/SKILL.md` (`$crav1-tighten-spec`) as that skill walks: one issue at a time. A batch of `I#: letter` answers is that skill's own rule. Do not add a second way to patch. When it finds no issues, say so and move on.

An issue whose only work is an `Answered:` line, or that only repeats a question already under `## Open questions`, goes to step 4 with no menu. One line: `Left for $crav1-resolve-open-questions: I3, I10, I11.` More than 8 issues: that skill shows a one-line count by kind first, then one issue or a small group. One by one is always offered. Do not print the full list first.

## 4. Open questions

Open `../crav1-resolve-open-questions/SKILL.md` (`$crav1-resolve-open-questions`). When `## Open questions` has nothing left to settle, say so and move on.

Then the extras batch below, once. Do not go on to the plan first.

## After step 4, one batch of extras

Once, after `$crav1-resolve-open-questions`, when the kept-open questions are known. Not at an earlier step, and not again later. One multi-select card, as `crav1-docs/reference/question-cards.md` says. Each extra that applies is an option. List a recommended one first and end its label with ` (Recommended)`. Always include **None, go to plan**. That option runs no extra and the walk goes on to `$crav1-plan-from-spec`. At most three extras on the card, plus that option. A further extra is named in the question. When any extra applies, do not go on to the plan without that offer. When none apply, say so in one line and move on. Do not run any of them unless the user picks it. Do not tell them to type none.

Offer `$crav1-show-or-ask-open-questions` when any kept-open question is for someone else. When the user picks an extra, open its file and follow it.

Not fixed steps. Security and tests stay optional. When one of them finishes inside this walk, record it before `resume`. The record is `- Extra: review-security`, `- Extra: research`, `- Extra: model-data`, `- Extra: show-or-ask-open-questions`, or `- Extra: suggest-tests-for-code`. Pass `--yes` because the user already picked the extra. Do not ask them to run `cover`. That record leaves earlier steps done. Auto-record stays this way.

`cover --yes` is optional and is not how this walk records an extra it just ran. Use it only for a write made outside this walk, when you want the current spec, plan, and tasks counted as part of the walk without a named extra.

- Research helper, no slash command. Offer it when the spec needs a technology, a service, or a scaling choice nobody has decided. Flag the question. Do not invent a command.
- Open `../crav1-review-security/SKILL.md` (`$crav1-review-security`), when the spec touches trust, access, or personal data, or the user asks. Architecture review already names it. Still optional here.
- Open `../crav1-model-data/SKILL.md` (`$crav1-model-data`), when the spec is about stored data and no `Data model:` line names a saved model. It does not edit requirements.
- Offer `$crav1-design-architecture` (1.181.0) when the spec needs an architecture change nobody has decided: systems, environments, hosting, data flows, integrations or deployment. It works on its own design branch, so the walk names it and does not open it. Planning that depends on the design waits until that design branch is merged.
- Open `../crav1-show-or-ask-open-questions/SKILL.md` (`$crav1-show-or-ask-open-questions`), when a question is for someone else.
- Open `../crav1-suggest-tests-for-code/SKILL.md` (`$crav1-suggest-tests-for-code`), when the spec names existing code and the acceptance lines do not already name the checks. A kept suggestion goes through add-to-spec, which that skill opens on yes. This walk does not write the tests.

## Before the plan, the UI step (1.211.0)

Not an extra and not offered. After the extras batch, run `<interpreter> -X utf8 ../crav1-design-ui/scripts/ui_screens.py status --root <spec-folder>` (skill `crav1-design-ui`). It writes nothing.

- `ui` is `no` (no UI words, or a `UI: none` line in `spec.md`): say nothing and go on to the plan.
- `ui` is `unclear`, or `yes` with a screen whose state is `new`, `changed` or `waiting`, or the user asks to change a screen: Open `../crav1-design-ui/SKILL.md` (`$crav1-design-ui`) and follow it inside the walk, with its own cards and its one closing yes. Inside the walk it prints no Run next. When it finishes, record `- Extra: design-ui` with `--yes`, as the extras are recorded.
- A screen whose state is `changed` is a signed-off screen with a material change since its yes. Say its `why` once, at this point and at the walk start: `Orders list (S1) was signed off; the states changed since, so its yes is cleared on the next UI step.`

The plan step's UI gate then decides. When it prints Run next (no screen signed off yet), the walk pauses: say `Paused at plan-from-spec.` and print that Run next as-is. It names `$crav1-design-ui` and `$crav1-record-approval`. The walk never writes `Approved:`.

## 5. Plan

Open `../crav1-plan-from-spec/SKILL.md` (`$crav1-plan-from-spec`). Its UI gate runs first and the plan covers only signed-off screens. That skill writes `plan.md` and `tasks.md`, and an `## Approval needed` item when a constraint says a named person gives a yes before something (`references/write.md` in that skill, "Approval needed"). When both already match the spec and it has nothing to add, say so and move on. Do not write the plan, or that item, from this walk.

## After the plan, questions with no Blocks line

Before step 5 is recorded, run `scripts/walk_progress.py unlinked --root <spec-folder> --vendor codex`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It lists kept-open questions that still have no `Blocks:` line. It writes nothing.

An empty list: say so, record the plan step, and move on.

A list: offer to set them before the plan review. One card:

Card: Set which tasks each kept-open question holds, before the plan review?
- **All in one batch (Recommended)** (`one batch`): one card lists every question with the tasks it should hold, and one yes writes them. Why: it is one answer instead of many.
- **One by one** (`one by one`): ask each question on its own card.

`one batch` is a batch card. Follow **Batch of several items** in `crav1-docs/reference/question-cards.md` before this card. Print the findings table in this reply, then ask. The card names each item and its recommendation, for example `Tasks miss the 400 path (P4): add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table. For each question, the choices are the unticked tasks it blocks (`Blocks: T2, T4`), **None** (`Blocks: none`, and a short reason in parentheses when they give one, such as `later phase`), or **The whole slice** (`- Blocks: whole slice`). One yes writes only those lines. A task list also sets that question's Risk line to `kept open; blocks T2, T4 until resolved.` None replaces "do not implement until resolved" on that question's Risk line with `kept open; does not block the current tasks.` The whole slice writes `- Blocks: whole slice` and sets that Risk line to `kept open; blocks the whole slice until resolved.` A `Blocks:` line wins over that Risk wording, so the line does not keep "do not implement until resolved". Do not start the plan review until this offer is answered. Then record the plan step, so the spec version includes these lines.

## 6. Review the plan, then tighten it

**Spec behind the code first (1.194.0).** Before the plan review, when the spec names code (`Synced at:` lines), run `scripts/walk_progress.py code-drift --root <spec-folder> --code-repo <code checkout> --base <Merges into> --vendor codex` again as a recheck (1.195.0: the main run is at the walk start; here it is a no-op when nothing moved since) (add `--pr <n> --merged <sha>` when this walk already saw a pull request merged). Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It fetches origin once first (1.196.0; `--no-fetch` skips it), prefers `origin/<branch>` over a stale local branch, and writes nothing. When `offer` is `add-to-spec`, put its `background` sentence before one question card with its two `options`, in that order. On the recommended yes, Open `../crav1-add-to-spec/SKILL.md` for its `command` and follow it with that skill's own confirms (do not start it as a slash command), then Open `../crav1-plan-from-spec/SKILL.md` for the parts it changed, then start the review. On `review the plan as it is`, start the review. Either way, pass the script's `reviewer_note` to the reviewer as known context, not as a finding to check, and never list that drift as a new item for the reviewer to echo. When `behind` is false, say nothing and start the review.

**Review packet (1.197.0).** Before the review, run `scripts/walk_progress.py review-packet --root <spec-folder> --vendor codex` (add `--since <commit>` from the last recorded plan review when there is one), as `crav1-docs/reference/running-scripts.md` says. It writes the reviewer's input outside the repo: the changed tasks (or the open ones), their spec sections by line range, and the plan's Risks and Linter, and says `quick` for a small delta. Say its `line`. Pass the packet's `path` and mode to the reviewer, in the foreground; it never reads `spec.md` whole.

Open `../crav1-review-plan/SKILL.md` (`$crav1-review-plan`), then Open `../crav1-tighten-plan/SKILL.md` (`$crav1-tighten-plan`), in that order. Review writes the `Reviewed:` line and does not edit the plan otherwise. The open count on that line is the `open` value from `<interpreter> -X utf8 ../crav1-plan-from-spec/scripts/plan_check.py open-count --review <file> --vendor codex` (the reviewer's reply). Use that value. Do not count the `P#` lines yourself. Later, `reviewed --items <file>` recomputes it from the items file the same way. Tighten walks plan issues and does not edit `spec.md`. Its batch card follows **Batch of several items** in `crav1-docs/reference/question-cards.md` (1.145.0). Print the findings table in this reply, then ask. The card names each item and its recommendation, for example `Tasks miss the 400 path (P4): add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table. When either has nothing to do, say so. Record one progress step, `review-and-tighten-plan`, only after both have finished or both had nothing to do.

## Spec finding during plan review (1.135.0)

A finding from the plan review that is tagged **spec** is a spec defect. Inside this walk it is not a pause. A plan-tagged finding stays in `$crav1-tighten-plan`, as that skill already walks it. Do not pass a plan finding to `spec-finding`.

Run `scripts/walk_progress.py spec-finding --root <spec-folder> --id P2 --text "<the finding>" --vendor codex`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. With no `--choice` it writes nothing. `--tag plan` is not a jump back.

**Which skill owns it (1.194.0).** Pass `--kind code-drift` for a finding about code the spec has not recorded: unrecorded commits, a merged pull request, `Synced at` or `## In the code` drift, or new PR comments, with `--pr <n>` or `--branch <branch>`. Pass `--kind spec-text` for wording, structure, a diagram or a constraint. With no kind the script reads the words; when unclear it stays with `$crav1-tighten-spec`. The script's `owner`, `command` and `path` name the skill; never recommend `$crav1-tighten-spec` for a code finding.

**Already fixed (1.194.0).** Before any card the script re-reads `spec.md` and its `Synced at:` lines. Pass `--expect "<words the fix leaves>"` when you know them, and `--code-repo <checkout>` so a `Synced at` commit after the merge commit counts. When `offer` is `already-fixed` there is no card: say its `note` in one line and record it with `--choice already-done --yes`. When the user types that it is already done, run the same command with `--choice already-done`: the finding closes only when the spec shows it (`recorded` is `already-fixed`, with `--yes`). Otherwise the script returns the card again with `still_missing`; say what is still missing in one line and ask the card.

When `offer` is `jump-back`, ask one question card, as `crav1-docs/reference/question-cards.md` says. Show the script's `background` as chat text before the card. The card header is the script's `header`, the plain name and the code, for example `Approver (P2)`, never the bare code. Use the script's `options`, in that order, each with its `text` saying what happens. The recommended label is `Fix it in the spec first (Recommended)`, or `Record the code in the spec first (Recommended)` when `owner` is `add-to-spec` (plain labels, 1.196.0; the command is in the option's text). The other label is `Keep it as an open point and go on`. When the script returns a `result` line, put it under the question. When it does not, the option already says what happens, so do not add an On yes line. Do not add a third option.

**Stale wording (1.207.0).** Pass `--kind stale-wording` when the finding is leftover wording after a decision: `superseded`, `still says`, `restates`, `Possible answer`, `stands until`, or `not a settlement`. With no `--kind` the script detects those words. `still says` stays code drift when the line is also a merge or a `Synced at` miss. A finding about an open question's wording has `owner` `resolve-open-questions`. When `offer` is `stale-wording`, this is not a jump back and the full skill does not run. Show the script's `background` as chat text, then one card. The header is the script's `header`, for example `Static-IP notes (P9)`. The question is the script's `question`, for example `Update the old static-IP notes (P9) now?`. The options are `Update the wording now (Recommended)` and `Keep it as an open point`. There is no second On yes line. On yes, run `../crav1-add-to-spec/scripts/stale_state_lines.py --spec <spec.md>` for the old words, show its `diff`, and ask its batch card. On that yes, run it with `--yes`. Do not Open the full owning skill. Then run `spec-finding` with `--choice update --yes`. When the patch touched only notes or question context and the reviewer reported no scope drift, add `--notes-only --no-scope-drift`. The script returns `cover` for `plan-from-spec` and `review-and-tighten-plan`. Pass those to `readiness --covered` so the plan is not reviewed again. On the other option, run `--choice open-point --yes` and go on. A second sighting of a patched finding is not asked again.

On the recommended yes, run the same command with `--choice <owner> --yes` (`tighten-spec` or `add-to-spec`). Then Open the script's `path` (`../crav1-tighten-spec/SKILL.md`, or `../crav1-add-to-spec/SKILL.md` for its `command`) and follow it for that finding only, with that skill's own confirms. Do not start it as a slash command. The rule is [open-skill-file.md](../../crav1-docs/reference/open-skill-file.md) (1.134.0). After that skill finishes, continue this walk. Open `../crav1-plan-from-spec/SKILL.md` for the parts that finding changed, then Open `../crav1-review-plan/SKILL.md` and Open `../crav1-tighten-plan/SKILL.md`, then the ready check. Do not pause.

On the other option, run `spec-finding` with `--choice open-point --yes` and continue `$crav1-tighten-plan`, then the ready check. Do not reopen the spec for that finding.

The same finding is the first-seen `Key:`, or an `Alias:` of a later wording (1.146.0). Exact words are not asked again. When `offer` is `same-or-new`, ask that card. Use the script's `options`, each with its `text`. When one finding matches, the recommended label is `same recorded finding (Recommended)` and the other label is `this is new`. On same, run `spec-finding` with `--choice same --yes`. On this is new, run it again with `--new`, then the jump-back card. When more than one finding is close, the recommended label is `this is new (Recommended)`. Do not merge them. Pass `--match-key` only when they pick one. An explicit `--topic approver` with the same P# is that stable id. A different topic does not match. Pass `--topic` when the finding has a short name. An old file with only `Key:` still matches those words. When `already_jumped` is true, do not ask again. Pass `--yes` so the open point is recorded, then continue review-and-tighten-plan and the ready check. A second `tighten-spec` choice is refused.

`walk-progress.md` records the jump-back step. Do not hand-edit it.

```text
- Jump-back: P2
  Done: 2026-11-11T20:30:00+00:00
  Finding: the plan requires a named person's yes to stop a prod function app
  Result: jumped
  Open: ../crav1-tighten-spec/SKILL.md
  Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build
  Key: 6a034c36ad9e
  Topic: approver
  Alias: b7c8d9e0f1a2

- Open point: P2
  Done: 2026-11-11T20:30:00+00:00
  Finding: the plan requires a named person's yes to stop a prod function app
  Result: open-point
  Continue: review-and-tighten-plan, tasks-ready-to-build
  Key: 6a034c36ad9e
```

`Result: jumped` is only on `- Jump-back:`. `Result: open-point` is only on `- Open point:`. This walk does not edit `spec.md` on the jump. The skill that owns the spec does, after its own yes. The walk does not write `Reviewed:`. This walk never writes `verify.md`.

## Jump back

A jump back opens the file of the skill that owns the step, even for a small patch, and follows it. Stale wording is not that jump: it patches the leftover lines through `stale_state_lines.py --spec <spec.md>` and does not Open the full skill. The walk does not edit `spec.md`, `plan.md`, or `tasks.md` on a jump back, and it does not write `Reviewed:`. Open `../crav1-review-plan/SKILL.md` (`$crav1-review-plan`) for that line. Open `../crav1-plan-from-spec/SKILL.md` (`$crav1-plan-from-spec`) for the plan and the tasks. Open `../crav1-tighten-plan/SKILL.md` (`$crav1-tighten-plan`) for plan issues. Open `../crav1-resolve-open-questions/SKILL.md` (`$crav1-resolve-open-questions`) for questions. Do not record a step `done` after editing those files yourself. Do not record `nothing-to-do` for a step you did not run.

When a reopened step truly has nothing new, ask that step's own reopen card first. A reopen clear is never folded into another step's card. Then run `clear --step <id> --card <token> --yes`, where `<token>` is that card's `card` field (or the matching `auto_clear_cards` entry when readiness listed the step under `auto_clear`). Without that token the script refuses with `ask the reopen card first`. Do not record `nothing-to-do` over it. A `nothing-to-do` record keeps an earlier `done` Result. A progress-only edit is not a reopen. Do not ask to clear it. The rule is [progress.md](progress.md) (1.138.0). Since 1.148.0 say `reopen_line` once and redo only those steps. When resolve-open-questions reopens, ask only `changed_questions`. The map is [section-reopen.md](section-reopen.md).
