# Tighten and plan until ready to build

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when a draft spec should be tightened and planned until the tasks are honestly ready to build. The command is [`/crav1-tighten-and-plan-ready-to-build`](reference/skills/crav1-tighten-and-plan-ready-to-build.md).

You can start with a playbook report, or without one. Since 1.146.0 the walk starts with one command, `<interpreter> -X utf8 scripts/walk_progress.py start --root <folder-or-slug>`, and `--playbook <file>` when you named one, as [Running a kit script](reference/running-scripts.md) says. On Windows the interpreter is `python`. That command resolves a folder or a slug and returns resume and playbook status together. Both starts go through the same steps and the same ready check. The walk runs the existing skills. It does not replace them. It is guided only. You confirm each write before it happens.

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
| Before the plan, the UI step | Only when the slice has a user-facing UI, or it is unclear (1.211.0). The walk opens `/crav1-design-ui` on its own, not as an offer, and records `- Extra: design-ui`. When no screen has its yes yet, the walk pauses at plan-from-spec and Run next names `/crav1-design-ui` and `/crav1-record-approval`. |
| 5. Plan | `/crav1-plan-from-spec` runs its UI gate first and covers only signed-off screens. It writes `plan.md` and `tasks.md`, and an `## Approval needed` item when a constraint says a named person gives a yes before something (1.141.0). The walk does not write that item itself. Before that step is recorded, questions that still have no `Blocks:` line are offered, one by one or as one batch. Since 1.145.0 that batch prints a findings table immediately before the card. The card names each question and the recommended hold. It does not say `table above` unless that table is in the reply. The card is not asked without the table. **The whole slice** writes `- Blocks: whole slice`, and that Risk line is `kept open; blocks the whole slice until resolved.` A `Blocks:` line wins over that Risk wording. |
| 6. Plan review, then tighten | `/crav1-review-plan`, then `/crav1-tighten-plan`. Since 1.202.0 the open count on `Reviewed:` is the script's `open` value from `plan_check.py open-count --review <file>`, not a count made by hand. The tighten-plan batch prints a findings table in that reply immediately before the card (1.145.0). The card names each plan finding and the recommended choice, for example `Tasks miss the 400 path (P4): add a test`. It does not say `table above` unless that table is in the reply. The card is not asked without the table. A finding that is really a spec defect is one card: run `/crav1-tighten-spec` on that finding (Recommended), or keep it as an open point and continue. On yes the walk opens that skill for the finding, then continues the plan and the ready check. It does not pause. Since 1.146.0 a close reword of a recorded finding is the same finding, and `this is new` keeps it separate. A plan finding stays in the plan tighten. |
| 7. Ready check | The walk runs `readiness --root <spec-folder> --write-map` (brief is the default since 1.156.0) and prints the script's ending, the shared walk ending also used by `/crav1-build-walk`, starting with the Run next block verbatim. Since 1.202.0 Held includes a task that only waits, via `(after:)`, on a task that is not built yet, and the reason is on that line. It rewrites `build-map.md` and does not open `/crav1-tasks-ready-to-build`. That command stays the standalone list. The walk stops here. |

A step with nothing to do says so and moves on.

Offered once, after open questions, when the spec needs them, not as fixed steps: the research helper, `/crav1-review-security`, `/crav1-model-data`, `/crav1-show-or-ask-open-questions`, and `/crav1-suggest-tests-for-code`. Security and tests stay optional. The walk does not run them unless you pick them. When one finishes, it is recorded without a second confirm.

## Progress

Beside the spec, `docs/specs/<slug>/walk-progress.md` records which steps are done, when, and the version of the spec, plan, and tasks each step covered. The ready check also records a `verify.md` version. The playbook is intake only. After apply, the playbook line is the `docs/playbooks/` path, not the file outside the project, so you can resume on another machine.

When you come back, the walk says what changed in one line: which section moved, and which steps reopen. Since 1.148.0 that is the first step that owns the changed section, not every later step. A new goal or constraint reopens tighten and the plan. It does not ask questions you already settled unless those words changed. A Match line, an In the code line, a Synced at line, or an already-answered question reopens nothing. A later step inside the walk leaves earlier steps done. An optional extra the walk itself runs, such as `/crav1-review-security`, is recorded when it finishes, and that write does not reopen earlier steps. A hand edit, or `/crav1-add-to-spec` between sessions, reopens only the steps that change affects. The spec, the plan, and the tasks stay the source of truth. The script stamps each step's done time, one step per record, right when that step finishes. The progress line is shown, and you confirm it, before it is written. When that confirm shares the open-questions card, `yes (Recommended)` covers the recommendations and the progress line, and typed changes go on that card's free-text answer (1.130.0). An extra's yes already covers its line. When two steps share a done time, the walk says so. That warning can be acknowledged once with `ack-stamps`, after a yes. The ready check records `Result: ready`, `Result: ready-partial`, or `Result: not-ready`. `ready-partial` means some tasks can start and some are held. The walk ends, the step is covered, and there is no `not-ready` mark. An older `Result: done` still reads.

## When the check is not ready

Blocked rows and Needs verify rows are named back to a step. Ready means the first task can start, the rest wait in order, and nothing else blocks. A task that only waits on an earlier real task is `waits-in-order`, not a blocker. A question-held task is `waiting`. Only a true blocker is `blocked`. A cycle, or an `(after:)` that names no task, is. The check is `readiness --root` on the spec folder. It builds the rows. A reopened walk step blocks the check too. You can jump back and rerun the skill that owns it, even for a small patch, or clear it with one line, `nothing new`, when the change does not need that step again. The walk does not edit the spec, the plan, or the tasks on that jump, and it does not write `Reviewed:`. A plan-review warning is not treated as ready. An open question that already waits on someone else, with resolve-open-questions current, is waiting, not a jump back. Who comes from the question's own "Waiting for" phrase, then the latest Pending or Asked line. With neither, the held line says `Nobody is named to answer it yet.` (1.170.0). The ending still counts a task with nobody named. Next is `/crav1-show-or-ask-open-questions` when the questions are not asked yet, or this walk when the answers arrive. When some tasks can start and some are held, the result is `ready-partial`. The walk records `Result: ready-partial` and does not write `not-ready`. Since 1.133.0 the ending groups the tasks that can start, and the held tasks, by build-map branch. A task is `T#` plus its short name. A held task names the open question and who has it, or `held, waits on T3`. Since 1.153.0 the ending has one Run next block at the top, and the bottom may keep a one-line `/crav1-build-tasks` alternative, with no `Next:` line. A later rerun, after the answers are in the spec, moves the held tasks to ready. `not-ready` remains when nothing can start.

Needs verify belongs to `/crav1-verify-build-against-spec`. That command is outside this walk. The walk names it and does not start it. It does not report ready while that row remains. Since 1.169.0 that row holds only its own task: tasks on other branches that can start keep their branch blocks, and the result is `ready-partial`. A task whose verify failed, with a short reason from its Verify cell (1.170.0), is named with `/crav1-fix-build-gaps <slug> T#`. The walk never writes `verify.md`.

Since 1.136.0 the ready check compares `tasks.md` with `verify.md`. A ticked task that `verify.md` still lists as not implemented is behind. So is an older `Next:` line that names a ticked task whose own row is not current (since 1.169.0 a Verified or Failed row is current), and a merged task that is still `Not implemented`. A merged task whose only leftover is the tick is not behind. The ending adds `Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2)` when verify is behind, and does not show that Next line. That does not make the result `not-ready`. A change to `verify.md` alone does not reopen the ready check. Spec, plan, or tasks drift still does. Only the walk's record or `clear --yes` restamps `walk-progress.md`. `/crav1-tasks-ready-to-build` only writes `build-map.md` when you run that command on its own. Since 1.146.0 the walk's ready check writes the same file with `--write-map` and does not open that skill. A spec finding no longer stops the walk before that check. The progress file records `- Jump-back:` and `Continue: plan-from-spec, review-and-tighten-plan, tasks-ready-to-build`. The same finding coming back is `- Open point:`.

Since 1.194.0 `/crav1-tighten-and-plan-ready-to-build` sends a spec finding to the skill that owns it. A finding about code the spec has not recorded (commits after `Synced at`, a merged pull request, `In the code` drift, new PR comments) recommends `/crav1-add-to-spec` with that pull request or branch; wording, structure, diagrams and constraints stay with `/crav1-tighten-spec`, which is also the default when it is unclear. Before the card the walk re-reads `spec.md`: a finding the spec already covers, for example when the branch's `Synced at` now shows the merge commit, gets a one-line note and no card. Typing that it is already done closes the finding only when the spec shows it; otherwise the walk says what is still missing. And when the spec's record is behind the code before the plan review, the walk asks one add-to-spec card first, and does not hand that known drift to the reviewer as a new finding.

Since 1.207.0 leftover wording (`superseded`, `still says`, `restates`) is a patch of those lines, not a full jump back to `/crav1-tighten-spec`. The card names the finding, for example `Static-IP notes (P9)`, and the background sentence is chat text before the card. Yes shows the diff and updates the notes. When only notes or question context changed and the reviewer reported no scope drift, the plan is not reviewed again. Clearing a reopened step uses that step's own card and its token. It is never folded into another step's card.

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

Since 1.173.0 a done task on the build map keeps its own commit: the merge commit in its branch's `build-progress` file, else its own row in `verify.md`. A `Date:` line or another task's row that names a newer commit never replaces it, and with no own commit the mark already on the map stays. Held and ready lines show full task names, and the open-questions entry is `Ask the open questions, which haven't been asked yet:` above `/crav1-show-or-ask-open-questions <slug>`. Every Run next entry has its label above the command; a reopened step reads `T1 waits until the reopened /crav1-tighten-plan step finishes:`, or `T1 and T2 wait until ...` for several tasks.

## After

Since 1.137.0 an edit confined to `## Open questions` does not reopen tighten-spec, plan-from-spec, the plan review, or the ready check. It reopens resolve-open-questions. That step alone leaves the result `ready-partial` when some tasks can start, with a Waiting line and a Next line for `/crav1-resolve-open-questions`. When later steps really did reopen, the result is `not-ready` and the ending starts with `Run next:` for the first of those steps, for example `/crav1-tighten-plan <slug>` when the plan was reopened for review. Do not say the tasks in `can_start` can start. The check's `because` line is the same plain reason, for example `The plan was reopened for review, so T5, T9 and T43 wait until /crav1-tighten-plan finishes.`, or the question when it holds the whole slice.

Since 1.138.0 a checkbox tick, a `(PR n)` or `(done)` note on that task line, and `(PR n)` on a Match `Branch:` line are progress. They do not reopen a step, and the walk does not ask to clear. CRLF and LF are the same text. An older `walk-progress.md` with no `Content stamp:` line still matches those edits. The next record writes `Content stamp: normalized`. A sentence change, or a renamed branch, still reopens the steps that change affects.

Since 1.139.0 a merge that conflicts only on those hash lines is settled by `scripts/walk_progress.py resolve-stamps --root <spec-folder> --yes`. `/crav1-finalize-commit` runs it. The walk does not. `Done` and `Result` stay. A real edit keeps the upstream hash.

When the check is clear, or ready-partial with tasks that can start, the ending prints `Run next:` first, before any Waiting line (1.150.0). Each command is alone in a code span and works in a new session. It names the T#s on that branch, and the slug when `docs/specs` has more than one slice. Since 1.164.0 each branch is one block: the bold branch, one plain sentence from its plan step, its open tasks, then `Run the whole branch:` and `Run only T#, the first task:`. Since 1.165.0 a `---` line stands between two branch blocks, the tasks are in walk order with `(waits on T#)` on a task that cannot start yet, and the sentence is a clean plan sentence, the step's heading, or nothing. Since 1.166.0 every branch block has a description line: up to three clean plan sentences (about 300 characters, cut only at a sentence end), else the plan note's opening clause, else the step heading, else one sentence from the open task names; and a held question that only points to a note shows the quoted question under it. Since 1.167.0 a `**Catch up first**` block leads Run next, before the branch blocks, when verify.md is behind, has a row for a T# not in tasks.md, or the specs repo is ahead of origin: one or two plain sentences, then `/crav1-verify-build-against-spec <slug>` and `git push`, each alone under its label, and those are no longer Waiting lines. Since 1.169.0 a task whose verify failed adds `Fix T#:` with `/crav1-fix-build-gaps <slug> T#` to that block, the block never replaces the branch blocks, and questions not asked yet stay a `/crav1-show-or-ask-open-questions <slug>` entry after them. Each held line is in that same reply. The walk command is only in that one block. The bottom keeps any Loop line, the Waiting lines, and the one-line alternative, with no `Next:` line (1.153.0):

```text
Run next:

**feat/orders-api-record**
Record each decision with who made it and when.
2 open tasks:
- T1 Record the decision
- T2 Store the card

Run the whole branch:
`/crav1-build-walk orders-api feat/orders-api-record`
Run only T1, the first task:
`/crav1-build-walk orders-api T1`

/crav1-build-tasks builds one task without the walk.
```

Since 1.155.0 the whole-branch entry is offered only when that branch has two or more open tasks. `walk-progress.md` also holds one `- Branch run:` status line per whole-branch run of `/crav1-build-walk`, under `## Branch runs`, linking to that branch's `build-progress` log. Recording a step keeps those lines, `resume` returns them as `branch_runs`, and the ready check prints the unmerged ones under `Branch runs:`. A conflict that is only those lines is settled by `resolve-stamps`, newest line per branch.

When two branches wait for each other, the ending and `build-map.md` both carry one Loop line (1.154.0), for example `Loop: feat/orders-x and feat/orders-y wait for each other: T14 on feat/orders-x waits for T13 on feat/orders-y, and T13 on feat/orders-y waits for T12 on feat/orders-x.` Since 1.161.0 the kit offers the fix under that line instead of asking for a hand edit: for example `Recommended fix (say `fix-loop`): T14 and T15 are on feat/orders-x, but they wait for T13 on feat/orders-y, which itself waits for feat/orders-x to merge, so the two branches wait for each other. Build T14 and T15 on feat/orders-y instead, right after T13. The tasks stay the same; only the branch and pull request they go into change. Then feat/orders-x holds T9-T12 and merges first, and feat/orders-y runs T13, T14, T15, T16.` Say `fix-loop`, or `fix-loop <n>` for an alternative, confirm the card, and the kit writes the `(map:)` marks, rebuilds the map and shows the loop is gone. Those branches count as Blocked in both. Other branches keep their wave and state.

`/crav1-build-tasks` is the alternative for one task without the walk. This walk does not run `/crav1-build-tasks` or `/crav1-build-walk`. A not-ready result does not recommend the walk; its ending starts with `Run next:` for the first real next step (1.163.0), for example `/crav1-tighten-plan <slug>` when the plan was reopened for review. When the ready check's own record is the only stale step, the reply says once that the earlier record is replaced, and the result comes from the tasks. Another reopened step still blocks. When the progress file is not committed: `Uncommitted: 1 file; commit with /crav1-finalize-commit when ready.` See [How a run ends](reference/run-ending.md).

## Claims and a fresh copy (1.151.0)

The walk fetches the specs repo before it reads. If that copy is behind origin, it stops and Run next is `git pull --no-rebase`. A task with an `In progress:` line in `docs/specs/<slug>/claims.md` is left unchanged: no renumber, reorder, rewrite, or removal. The walk says once which claimed tasks were kept. The ready check holds those tasks as `in progress by <user> since <date>` and does not offer them in Run next.

Reference page: [tighten and plan, ready to build](reference/skills/crav1-tighten-and-plan-ready-to-build.md)

Since 1.164.0 `start` and `resume` name the one reference the next step needs in `read`, and the walk opens only that file. Its cards follow the card wording rule in [Question cards](reference/question-cards.md): a reopened step asks `Skip redoing the plan review?` after one plain sentence, and the record card asks `Save the ready check as done?` without quoting the progress line.

Since 1.171.0 the ready check asks its record card before it prints the ending, so its last reply starts with Run next. When only the time or the verify version would change, it skips the record and says `Record unchanged.`, and `walk-progress.md` stays clean. A task whose build walk is pushed and waits on a merge is waiting, not offered, and your own claim reads `T5 is yours; the walk resumes it.` A branch description is never a note about how the branch was cut, and never a sentence about a task that is already done.

Since 1.195.0 the walk checks the code at the start: the shared merged-since-sync check finds each branch's base per branch (the repo's `Merges into` from `repos.md`, a base `Synced at` line, then `develop`, then the default branch), and the code-drift check runs right after it, counting only commits the spec and notes have not recorded (it reports the new count, the already-recorded count and base merge-ins). The run before the plan review is only a recheck. When anything stale was seen, reopen cards recommend rerun, never nothing new. `/crav1-tighten-plan` puts at most 8 findings on one batch card, and a finding that adds, removes or reorders tasks always gets its own card. `/crav1-tighten-spec` recommends ask or keep for a "whether" finding no source decides, never recommends a patch that contradicts a quoted source line, and ticks a spec acceptance box only through `tick-from-verify`, which quotes the passing verify row.

## Start checks and fewer cards (1.196.0)

The walk fetches origin once at the start and compares against `origin/develop`, so a branch tip that is already merged shows as merged, not as drift. In the same start it clears finished claims and ticks acceptance items whose verify row passes with evidence, in one line such as `Ticked 2 acceptance items from verify: item 1 (A1), item 2 (A2, recheck on T3).` When an open task touches the evidence, the item is ticked and that task's verify note gets a recheck line.

Fewer cards: housekeeping fixes in the plan apply with one summary line, a reopen that only came from a fact the walk just recorded gets no card, and the save rides on the step's last yes. Batch cards show one bullet per item above a short question and an `On yes:` line, in plain words with no letters or internal names. Verify runs on DEV or TEST; a check on prod is read-only, and a check that writes to prod is its own task with an owner, your yes and a Risks line.

## Release gates, quieter cards and a scoped review (1.197.0)

The prod lint reads each verify item and its target, so a local Bicep compile of `main.prod.bicepparam`, a unit test with PROD-like settings or a read-only check on prod is not flagged. A manual prod task that drops or changes data needs an owner and a Risks line, and the ready check holds it until its release, for example `T52 waits for the first release to main and a prod yes`, so it is never offered as the first task. Untested acceptance items stay open with no question. Batch cards keep option text as written, and the question is only the short `Card:` line.

Before the plan review, the walk writes a review packet with the changed tasks, their spec sections and the plan's Risks, and `/crav1-review-plan` runs in the foreground on that packet instead of reading the whole spec. A small change gets a quick review.

## 1.198.0 changes

The `/crav1-tighten-and-plan-ready-to-build` ready check names the hard hit when it says not-ready while tasks can start, says `T30 is yours and waits for PR 85's merge.` for your own pushed task, names who the answers come from in `Resume the walk when the answers from person A arrive:`, shows a repeated question once (`same question as T26`), records a result that only reflects waits without a card (`Recorded: not-ready (was ready-partial).`), and labels a lone build-map change `Commit the updated build map:`. The walk start says `Kit update available: <installed> -> <latest>` when a newer release is out.

## 1.199.0 changes

`walk_progress.py code-drift --root <spec folder> --code-repo <checkout>` also reports commits merged in from the base that touch this slice's files and come from a branch the spec does not list, so they are offered for add-to-spec instead of counted as merged in. In the ready check, your own task that is pushed and waits for its pull request (for example `T30 is yours and waits for PR 85's merge.`) is waiting, not a blocker, so the other ready tasks still go into Run next; a real `Not ready: …` line comes right after Run next, before Held, and a merge wait names its PR, `Waiting: PR 85 to merge, then T28, T37 and T39 are ticked.`

## 1.209.0 changes

A finding recorded before topics existed has an empty topic. The next `start` derives one from the finding text, the same way a new finding gets a topic, writes it back, and the reply says that one line, `Filled finding topics: Static-IP notes (P9).` A later start does not say it again. The ready check in this walk quotes a held task's own `Q` or `question` line, keeps a waits-on list as T numbers, and names the `Ask` or `owner` on the question.

## 1.211.0 changes

At the walk start, each signed-off screen with a material change since its yes gets one line, for example `Orders list (S1) was signed off; the states changed since, so its yes is cleared on the next UI step.` See [Design the UI](from-design-ui.md).
