# Tighten and plan until ready to build

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when a draft spec should be tightened and planned until the tasks are honestly ready to build. The command is [`/crav1-tighten-and-plan-ready-to-build`](reference/skills/crav1-tighten-and-plan-ready-to-build.md).

You can start with a playbook report, or without one. Both go through the same steps and the same ready check. The walk runs the existing skills. It does not replace them. It is guided only. You confirm each write before it happens.

Since 1.134.0 the walk opens each step skill's file and follows it. It does not start that skill as a slash command. Those skills stay command-only. The rule is [Opening another kit skill](reference/open-skill-file.md). A refusal because a skill is command-only is not a reason to stop the walk.

This is cross-cutting. It may run from any lane. It is a later skill, not a starter option. It does not start Build.

The new-slice route is unchanged. You can still run each skill on its own. On that route the architecture review is optional. Inside this walk it always runs.

## First prompt

```text
/crav1-tighten-and-plan-ready-to-build
@docs/specs/<slug>/
```

With a playbook, add the report path on the next line. You do not type brackets.

## Steps

| Step | What you see |
| --- | --- |
| 1. Playbook, only when you named one | The path may be outside the project or `docs/playbooks/<topic>.md`. This question comes first, before any later step, including a read-only check. Resume may report status. If this walk already applied that same file, you are still asked: `skip` (Recommended) or `reapply`, even when the file has not changed. Otherwise you see the changes. Nothing is written until you say yes. Apply is `/crav1-resolve-open-questions apply`. On that yes a filled playbook is copied to `docs/playbooks/<topic>.md`. The name is shown once before the first copy. A hand-edit since the last apply is shown before overwrite. Kept items are written inside that apply. |
| 2. Architecture review | Always runs. It writes nothing. If there is nothing to critique, the walk says so. |
| 3. Tighten the spec | One issue at a time, as `/crav1-tighten-spec` already walks. More than 8 issues: a one-line count first, then one issue or a small group. One by one is always offered. An open question that belongs to the next step is one line, with no menu. No issues: it says so. |
| 4. Open questions | `/crav1-resolve-open-questions`. Nothing left to settle: it says so. Then, once, the optional extras that apply, as a multi-select. **None, go to plan** is a real option and runs none of them (1.130.0). The walk does not go on to the plan without that offer when one applies. Show-or-ask is offered when a question is for someone else. |
| 5. Plan | `/crav1-plan-from-spec` writes `plan.md` and `tasks.md`, and an `## Approval needed` item when a constraint says a named person gives a yes before something (1.141.0). The walk does not write that item itself. Before that step is recorded, questions that still have no `Blocks:` line are offered, one by one or as one batch. **The whole slice** writes `- Blocks: whole slice`, and that Risk line is `kept open; blocks the whole slice until resolved.` A `Blocks:` line wins over that Risk wording. |
| 6. Plan review, then tighten | `/crav1-review-plan`, then `/crav1-tighten-plan`. A finding that is really a spec defect is one card: run `/crav1-tighten-spec` on that finding (Recommended), or keep it as an open point and continue. On yes the walk opens that skill for the finding, then continues the plan and the ready check. It does not pause. The same finding is offered once. A plan finding stays in the plan tighten. |
| 7. Ready check | `/crav1-tasks-ready-to-build`. The walk stops here. |

A step with nothing to do says so and moves on.

Offered once, after open questions, when the spec needs them, not as fixed steps: the research helper, `/crav1-review-security`, `/crav1-model-data`, `/crav1-show-or-ask-open-questions`, and `/crav1-suggest-tests-for-code`. Security and tests stay optional. The walk does not run them unless you pick them. When one finishes, it is recorded without a second confirm.

## Progress

Beside the spec, `docs/specs/<slug>/walk-progress.md` records which steps are done, when, and the version of the spec, plan, and tasks each step covered. The ready check also records a `verify.md` version. The playbook is intake only. After apply, the playbook line is the `docs/playbooks/` path, not the file outside the project, so you can resume on another machine.

When you come back, the walk says what changed. A later step inside the walk leaves earlier steps done. An optional extra the walk itself runs, such as `/crav1-review-security`, is recorded when it finishes, and that write does not reopen earlier steps. A hand edit, or `/crav1-add-to-spec` between sessions, reopens only the steps that change affects. The spec, the plan, and the tasks stay the source of truth. The script stamps each step's done time, one step per record, right when that step finishes. The progress line is shown, and you confirm it, before it is written. When that confirm shares the open-questions card, `yes (Recommended)` covers the recommendations and the progress line, and typed changes go on that card's free-text answer (1.130.0). An extra's yes already covers its line. When two steps share a done time, the walk says so. That warning can be acknowledged once with `ack-stamps`, after a yes. The ready check records `Result: ready`, `Result: ready-partial`, or `Result: not-ready`. `ready-partial` means some tasks can start and some are held. The walk ends, the step is covered, and there is no `not-ready` mark. An older `Result: done` still reads.

## When the check is not ready

Blocked rows and Needs verify rows are named back to a step. Ready means the first task can start, the rest wait in order, and nothing else blocks. A task that only waits on an earlier real task is `waits-in-order`, not a blocker. A question-held task is `waiting`. Only a true blocker is `blocked`. A cycle, or an `(after:)` that names no task, is. The check is `readiness --root` on the spec folder. It builds the rows. A reopened walk step blocks the check too. You can jump back and rerun the skill that owns it, even for a small patch, or clear it with one line, `nothing new`, when the change does not need that step again. The walk does not edit the spec, the plan, or the tasks on that jump, and it does not write `Reviewed:`. A plan-review warning is not treated as ready. An open question that already waits on someone else, with resolve-open-questions current, is waiting, not a jump back. Who comes from the question's own "Waiting for" phrase, then the latest Pending or Asked line, or "not named yet". The ending still counts a task whose person is not named yet. Next is `/crav1-show-or-ask-open-questions` when the questions are not asked yet, or this walk when the answers arrive. When some tasks can start and some are held, the result is `ready-partial`. The walk records `Result: ready-partial` and does not write `not-ready`. Since 1.133.0 the ending groups the tasks that can start, and the held tasks, by build-map branch. A task is `T#` plus its short name. A held task names the open question and who has it, or `held, waits on T3`. Next is one `/crav1-build-tasks` line per ready branch. A later rerun, after the answers are in the spec, moves the held tasks to ready. `not-ready` remains when nothing can start.

Needs verify belongs to `/crav1-verify-build-against-spec`. That command is outside this walk. The walk names it and does not start it. It does not report ready while that row remains. The walk never writes `verify.md`.

Since 1.136.0 the ready check compares `tasks.md` with `verify.md`. A ticked task that `verify.md` still lists as not implemented is behind. So is a `Next:` line that names a ticked task, and a merged task that is still `Not implemented`. A merged task whose only leftover is the tick is not behind. The ending adds `Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2)` when verify is behind, and does not show that Next line. That does not make the result `not-ready`. A change to `verify.md` alone does not reopen the ready check. Spec, plan, or tasks drift still does. Only the walk's record or `clear --yes` restamps `walk-progress.md`. `/crav1-tasks-ready-to-build` only writes `build-map.md`. The ready check still rewrites that file. A spec finding no longer stops the walk before that check. The progress file records `- Jump-back:` and `Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build`. The same finding coming back is `- Open point:`.

## What gets written

- `docs/specs/<slug>/walk-progress.md`, after a yes. The playbook line names `docs/playbooks/<topic>.md`.
- Spec, plan, and task edits only inside the skill that owns them, after that skill's own yes. A jump back reruns that skill. The walk does not patch those files itself, and it does not write `Reviewed:`.
- Playbook answers only through `/crav1-resolve-open-questions apply`, on yes.
- `docs/playbooks/<topic>.md` when that apply copies a filled playbook. Specs it changed link that file.

Not written: application code. `Answer:` and `Change:` lines in the playbook are not edited. A draft with no filled answer is not copied. Nothing is git-committed.

## Already applied, then new information

You already applied a playbook. Then new information landed in the specs, for example from a mail import. Do not re-walk the playbook. Its answers are already in the specs. New facts from mail are open questions or conflicts in the specs. Settle those with `/crav1-resolve-open-questions`.

Recommended path: run the walk again and name that playbook.

```text
/crav1-tighten-and-plan-ready-to-build
@docs/specs/<slug>/

<the playbook file>
```

Step 1 offers `skip` (Recommended) or `reapply`. `reapply` also writes the `docs/playbooks/` copy when that file is missing, for example a playbook applied before 1.120.0. The open-questions step picks up what the mail added. The walk continues to the ready check.

Without the walk: run `/crav1-resolve-open-questions` for the new questions. Reapply the playbook only when you need the `docs/playbooks/` copy.

Make a fresh `report-playbook-full` only when the new information changes the playbook's own decisions, for example the merge order or a reversed choice. That report reads the current specs.

A playbook applied before 1.120.0: reapply the same file. That creates the `docs/playbooks/` copy. Spec answers already present stay as they are.

## After

Since 1.137.0 an edit confined to `## Open questions` does not reopen tighten-spec, plan-from-spec, the plan review, or the ready check. It reopens resolve-open-questions. That step alone leaves the result `ready-partial` when some tasks can start, with a Waiting line and a Next line for `/crav1-resolve-open-questions`. When later steps really did reopen, Next names them: `Next: rerun or clear <steps>.` The result of that real change is `not-ready`. Do not say the tasks in `can_start` can start. The check's `because` line names the reopened steps, or the question when it holds the whole slice.

Since 1.138.0 a checkbox tick, a `(PR n)` or `(done)` note on that task line, and `(PR n)` on a Match `Branch:` line are progress. They do not reopen a step, and the walk does not ask to clear. CRLF and LF are the same text. An older `walk-progress.md` with no `Content stamp:` line still matches those edits. The next record writes `Content stamp: normalized`. A sentence change, or a renamed branch, still reopens the steps that change affects.

Since 1.139.0 a merge that conflicts only on those hash lines is settled by `scripts/walk_progress.py resolve-stamps`. `/crav1-finalize-commit` runs it. The walk does not. `Done` and `Result` stay. A real edit keeps the upstream hash.

When the check is clear, or ready-partial with tasks that can start, the ending recommends the build walk. One line per ready branch, with the T number beside the short name:

```text
Next: /crav1-build-walk T1 Record the decision, because that work is on feat/orders-api-record. /crav1-build-tasks builds one task without the walk.
```

`/crav1-build-tasks` is the alternative for one task without the walk. This walk does not run `/crav1-build-tasks` or `/crav1-build-walk`. A not-ready result does not recommend the walk. When the progress file is not committed: `Uncommitted: 1 file; commit with /crav1-finalize-commit when ready.` See [How a run ends](reference/run-ending.md).

Reference page: [tighten and plan, ready to build](reference/skills/crav1-tighten-and-plan-ready-to-build.md)
