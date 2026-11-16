# Tasks ready to build

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want to know which tasks can be built now, and why the others cannot. Run it any time: before Build, between tasks, or after new information changed a spec. It is command-only (1.88.0): type `/crav1-tasks-ready-to-build`. Asking "which tasks are ready?" in plain words does not start it. Every run rewrites `docs/specs/<slug>/build-map.md` (1.128.0). The task list is unchanged apart from one line pointing at that file.

This is cross-cutting. It is not its own lane. It was added at Rhea's request so runners can pick the next task without guessing. Since 1.144.0 a named spec is `<interpreter> -X utf8 scripts/resolve_spec.py "<query>" --root docs/specs`, and `--recommend` names `docs/specs/<slug>`. The interpreter is [Running a kit script](reference/running-scripts.md).

## First prompt

```text
/crav1-tasks-ready-to-build
@docs/specs/<slug>/
```

Leave out the folder to check every slice under `docs/specs/`.

To see only the build map, put the word first. The rest is the same scope, including a slice such as `cc 1.0`:

```text
/crav1-tasks-ready-to-build build-map cc 1.0
```

## What it checks

For each task, in this order:

| Check | Where it lands |
| --- | --- |
| Ticked in `tasks.md` | **Done** when `verify.md` lists it as verified, otherwise **Needs verify** |
| `plan.md` missing | Blocked |
| A kept-open question in `spec.md` | **Waiting on a question** when its `Blocks:` line names the task (recorded). `Blocks: none` blocks no task (recorded). `Blocks: whole slice` holds every unfinished task (recorded) and the line says Holds the whole slice. With no `Blocks:` line, the question holds the `T#` ids named in its text (inferred from the text), and holds the whole slice only when no task is named and resolve-open-questions has never been recorded (1.137.0). Who comes from "Waiting for", then the latest Pending or Asked line; with neither, the line says Nobody is named to answer it yet (1.170.0). A plan Risk that says do not implement until resolved is **Blocked** when it matches no question, or matches a question with no `Blocks:` line and no inferred tasks. It matches on the question's first sentence, a `(question: <first words>)` tag, or the same Blocks tasks named in the risk. The line wins |
| An `## Approval needed` item with no matching `Approved:` line (1.141.0) | **Waiting** on that person, for the tasks on `Holds:`. Other tasks still start (`ready-partial`). A matching `Approved:` line clears the hold. The task is not ticked here |
| Tasks it waits on | **Waits in order** while a real earlier task is unticked (recorded from `(after: T#)`, or inferred from the task just before it). A cycle, or an `(after:)` that names no task, is **Blocked**. A task on a branch caught in a loop is **Blocked** in the counts and the map, with a `Loop:` line (1.154.0) |
| Otherwise | **Ready**. When `plan.md` has no `Reviewed:` line, it adds a warning to run `/crav1-review-plan` (inferred). When the review still has open `P#`s, it says so |
| Waits on a held task | **Waiting** too, reason `held, waits on T3` (1.132.0). Who is the person on the question that started the hold |

The result line is `ready`, `ready-partial`, or `not-ready` (1.132.0). `ready-partial` means some tasks can start now and some are held. `not-ready` means nothing can start. A cycle, a missing task, no plan, Needs verify, or a plan-review warning still records `not-ready`. The walk record stays `Result: ready-partial`. `/crav1-build-tasks` starts the ready tasks and refuses a held task with its reason.

Since 1.133.0 the ready tasks and the held tasks are grouped by the build-map branch, not as one flat list. The branch is the name `scripts/build_map.py docs/specs/<slug> --recommend T#` prints. Order is wave, then the map's row order. A task is shown as `T#` plus its short name, the same words as the Tasks field in `build-map.md`. A held task names the open question and who has it, or `held, waits on T3`. Each branch that can start gets its own entry in the one Run next block at the top, so those branches can be started together. One branch is still one entry. The walk command appears only there. The bottom keeps Waiting lines and the one line `/crav1-build-tasks builds one task without the walk.`, with no `Next:` line (1.153.0).

Lists inside a branch follow the map. The wider task graph is still **dependency order** (1.103.0): tasks with nothing to wait on first, then the tasks they unblock, wave by wave, lowest number first inside a wave. For a slice where T7 waits on T2, T3 and T6 on T7, T4 on T3 and T7, and T5 on T4, the order is T1 → T2 → T7 → T3 | T6 → T4 → T5. `/crav1-build-tasks`, `/crav1-build-features` and `/crav1-verify-build-against-spec` use that order.

Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback). The marks are in [Readiness marks](concepts/data-layout.md#readiness-marks).

## What you see

Since 1.156.0 the script prints the whole reply and the assistant gives it once as the answer, as-is, with at most one short lead sentence and without first pasting the raw tool output: `walk_progress.py readiness --root <spec-folder> --write-map --text`. Since 1.163.0 a not-ready ending starts with `Run next:` naming the first real next step. The brief reply is the default: the counts row, the result, the shared ending, the sources and the build map.

```text
Tasks ready to build — cancel-booking

| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- | --- | --- |
| cancel-booking | 1 | 1 | 1 | 0 | 1 | 3 |

Result: ready-partial

Run next:

**feat/orders-retry**
Retry a failed refund to the original card.
2 open tasks:
- T5 refund to the original card
- T6 send the mail

Run the whole branch:
`/crav1-build-walk feat/orders-retry`
Run only T5, the first task:
`/crav1-build-walk T5`

Held:
- `feat/orders-currency` (wave 1): T7 choose the currency — open question "Which currency for refunds?" Waiting for the partner.

/crav1-build-tasks builds one task without the walk.

Source: docs/specs/cancel-booking/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/cancel-booking/build-map.md
```

Say `full` (`/crav1-tasks-ready-to-build full cancel-booking`) for the long form. It adds the per-task lists after the result line:

```text
Ready now
- `feat/orders-retry` (wave 1): T5 refund to the original card

Waits in order (dependency order)
- T6 send the mail: waits on T5 (recorded).

Needs verify
- T3 short name: no verify.md row.

Done: 3
```

The ending is shared (1.156.0). `/crav1-tasks-ready-to-build`, the tighten-and-plan ready check and `/crav1-build-walk` build it with one shared `walk_ending` script, so for the same ready branches the Run next entries are the same words in all three. `/crav1-build-tasks` reads the full readiness JSON (`--full`) to start the ready tasks. See [How a run ends](reference/run-ending.md#the-shared-walk-ending-11560).

Since 1.165.0 a `---` line, with a blank line on each side, stands between two branch blocks so they never run together in a Markdown viewer. The open tasks are listed in the order the walk runs them. A listed task that cannot start yet says why on its line, for example `- T8 Take in develop (waits on T5)`, and when the first listed task cannot start the label is `Run only T#, the first task that can start:`. The plain sentence is used only when the plan step's first sentence is clean: it ends with a full stop, has no colon list, and does not open with a person (`Person A builds ...`). Otherwise the step's heading in plain words is used, or the line is left out. A long line, a sentence or a held question, is cut at a clause end or a word, never on a dangling word such as `the`, and a held question that opens with a heading such as `Client certificate.` shows the question itself. Since 1.164.0 each ready branch is one block with its open tasks listed, `Run the whole branch:` first and `Run only T#, the first task:` second, each command alone on its own line under its label; the reply also ends with `Zoom the map in your browser:` and `/crav1-tasks-ready-to-build <slug> open-map`. Before that, since 1.155.0 each ready branch offered its next task, and, when the branch has two or more open tasks, the whole branch as a second entry, built in one run by `/crav1-build-walk <slug> <branch>`. A branch with one open task gets only the T# entry. When a whole-branch run is going, or stopped, the ending also has a `Branch runs:` block from the `- Branch run:` status lines in `walk-progress.md`, for example `- feat/orders-retry: running, T5 done, next T6 (log: build-progress/feat--orders-retry.md)`. A merged run is left out.

Since 1.166.0 every branch block has a description line between the bold branch and `<n> open tasks:`. In order: up to three clean sentences from the plan step (each ends with a full stop, has no colon list, no person leading it and no file or path), about 300 characters at most and cut only at a sentence end, never mid-sentence; else the plan note trimmed to its opening clause, the words before the first `:` or ` — `, with a person lead such as `Person A builds PR 73:` dropped, for example `The orders CI/CD branch, cut from develop after billing-ops.`; else the step's heading in plain words; else one sentence from the open task names, a shared prefix once, for example `Orders CI/CD: infra Bicep, cd pipeline, ci lint and tests, and deploy README.`, about 160 characters. The line is left out only when the branch has no plan step and no usable task name, and a person's name never shows. A held question that ends with `:` or only points to a note, such as `The note docs/notes/x.md, in Open questions, question 5, says:`, shows the quoted question that follows: the `>` blockquote under the bullet, else the text in quotes after the colon, else the first sentence ending in `?`.

## Getting recorded reasons

The more the kit records, the fewer reasons are inferred:

- `/crav1-review-plan` writes `Reviewed: <date>, P# open: <n>` in `plan.md`, and `/crav1-tighten-plan` lowers the count.
- `/crav1-plan-from-spec` ends a task line with `(after: T1)` when the task needs an earlier one.
- `/crav1-resolve-open-questions` asks which tasks a kept-open question blocks and writes `Blocks: T#`. **None** writes `Blocks: none`. **The whole slice** writes `Blocks: whole slice`. `/crav1-plan-from-spec` writes `Blocks: T#` or `Blocks: none` for a question it parks as a risk.

## Azure Boards

It never reads Azure Boards (ADO). A task closed there but not ticked here still shows as not done. Run [`/crav1-ado-sync`](from-ado-sync-pull-tasks.md) to bring task states back.

## The build map (1.128.0)

The file `docs/specs/<slug>/build-map.md` is how the work will be built, by branch. One branch per numbered step in the plan, unless the task line names its own. A task can name another branch with `(map: feat/cancel-refund)`. `(branch: feat/orders-retry)` does the same when no `(map:)` is set. Since 1.140.0 a `feat/…` name in the sentence, or `committed later on feat/orders-cicd`, does the same when neither mark is set. `from develop` after that name is the base. The plan step's `feat/<slug>-<words>` name is only the fallback. Two tasks on one step can use different branches. `(step: 1)` links a task to a step when the step text does not. No steps means one branch per task, and the file says so. `scripts/build_map.py docs/specs/<slug> --recommend T1` prints the branch on the first line and does not write the file. A merged branch, or a branch deleted locally and on the remote, is not that line. A branch that is only on origin, or is the head of an open pull request, is that line, and the build checks it out without asking (1.160.0).

Branches sit in waves. Wave 1 can start from a dependency point of view. Later waves open after those merge. The heading always says how many can start now, including one branch: `1 branch, 1 can start now`. The flowchart puts each wave side by side. An overlap note under a wave names two branches that share a requirement or a path. It does not change what is ready. Each branch row has six things: the branch name, one line on what it delivers, a short name for each task, which branches it waits for, any open question and who has the answer, and whether it is ready now. The short name is the work-item title when `work-item.md` has `task: T1 Turn off pipelines 7 and 24`, otherwise the task text up to the first parenthesis, `, in `, or the end of the sentence. When the task text names a different branch, the row adds `Task text names feat/orders-cicd; built on feat/orders-retry`. When the row is the branch on the task line and the plan step's name differs, the row adds `Plan step names feat/orders-one-commit-cleanup-main; built on feat/orders-host-setup-scripts` (1.140.0). Task ids are not in the file. Branches that wait for each other are a loop (1.154.0). The file and the ready-check ending print one line for it, for example `Loop: feat/orders-x and feat/orders-y wait for each other: T14 on feat/orders-x waits for T13 on feat/orders-y, and T13 on feat/orders-y waits for T12 on feat/orders-x.` Since 1.161.0 the kit offers the fix under that line instead of asking for a hand edit: for example `Recommended fix (say `fix-loop`): T14 and T15 are on feat/orders-x, but they wait for T13 on feat/orders-y, which itself waits for feat/orders-x to merge, so the two branches wait for each other. Build T14 and T15 on feat/orders-y instead, right after T13. The tasks stay the same; only the branch and pull request they go into change. Then feat/orders-x holds T9-T12 and merges first, and feat/orders-y runs T13, T14, T15, T16.` Say `fix-loop`, or `fix-loop <n>` for an alternative, confirm the card, and the kit writes the `(map:)` marks, rebuilds the map and shows the loop is gone. Those branches are listed under Blocked, in an `In a loop` group of the flowchart. A branch that only waits for a loop keeps its own wave and state. A branch is always in a later wave than each branch it waits for, unless both are in the same loop. A held line shows the wave, or `in a loop`, never `(blocked)`. The chat stays short. The word `build-map` prints the path, each wave's count, and that wave's overlap notes, one line per pair. The ready-check list stays the one pointer line.

A ticked task stays in its wave (1.132.0). The row strikes the short name through and marks it done, with the pull request link, or the branch or commit when there is no pull request: `~~Persist the decision~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))`. The heading counts done tasks apart from the branches that can start (`1 branch, 1 can start now, 1 done`). A wave whose every task is done is wrapped in a details block, `Wave 1 done (2 tasks)`. The rows stay in the file.

The script writes the file. This command does not commit it. Commit it with the spec when you are ready.

## Zoom the map, or send it (1.162.0)

A wide map shrinks to fit the Markdown preview. Say `open-map` to see the whole `build-map.md` as a page in your browser:

`/crav1-tasks-ready-to-build orders-api open-map`

The page shows the same text, lists and wave lists, which still fold. The diagram sits in place with zoom on the mouse wheel, drag to pan, and `-`, `+`, `Fit`, `100%` and `Fullscreen` buttons. The text stays in a readable column, and the diagram pane uses the full width of the window. It works offline: the kit ships Mermaid and marked in `crav1-tasks-ready-to-build/scripts/vendor/`.

To show the map to someone, say `export-map`:

`/crav1-tasks-ready-to-build orders-api export-map`

That writes one file, for example `orders-api-build-map-2026-11-15.html`, to your Downloads folder, never into the specs repo. It is about 2.6 MB and opens with a double-click in any browser, offline, with nothing to install. It is a snapshot of the map and holds everything the map shows, so export again after the plan changes and send it only to people who may see the plan.

A done branch says `Waited for:` instead of `Waits for:`, since nothing waits any more. The line under the map's heading names both commands.

## When verify.md is behind (1.136.0)

The check reads `verify.md` and does not write it. A task stays done for later tasks when it is ticked, or when its pull request is recorded merged: `(PR n)` and the word merged on the task line, or on the Match `Branch:` line for that task's branch. The check adds a Waiting line when a ticked task is still `Not implemented`, when an older `Next:` line names a ticked task whose own row is not current, or when a merged task is still `Not implemented`. Since 1.169.0 a Verified or Failed row is current, so a fresh verify is never behind, and verify no longer writes a `Next:` line. A merged row whose status is **Implemented, verified, tick pending** is not behind. The checkbox is the only leftover. `task_order.py` lists that task under Needs tick, not under Ready. A verify-only change does not force `not-ready`. This command only writes `build-map.md`. Only the walk's record or `clear --yes` restamps `walk-progress.md`.

Since 1.169.0 a built task whose verify failed is in the Catch up first block as `T6 failed verify: <reason>.`, with `Fix T6:` and `/crav1-fix-build-gaps <slug> T6`, not sent back to verify. Needs verify holds only its own task. Ready branches keep their blocks after the catch-up block and the `---` line, and the result is ready-partial. Questions that are not asked yet stay a `/crav1-show-or-ask-open-questions <slug>` entry after the branch blocks.

Since 1.170.0 the reason is short: the Verify cell's opening sentence, plus the sentence that names the cause (`... made the asserts stale.`, `... because ...`) when it fits, about 200 characters, cut only at a sentence end. Leading run detail such as `fail at PR 7's tip abc1234: pipeline 6 run 251, 110 failed, 173 passed.` gives way to the next sentence. The full cell stays in `verify.md`, and `/crav1-fix-build-gaps` reads it there. Since 1.170.0 a hold with nobody named says so plainly: `Nobody is named to answer it yet.` for a question, `Nobody is named to give it yet.` for an approval, and `nobody named for 1` on the Waiting line, never `Waiting for not named yet`.

Since 1.167.0 what you can fix now with one command is not a Waiting line any more. It leads Run next as a `**Catch up first**` block, before the branch blocks and in the same layout: verify.md behind tasks.md, a verify.md row for a T# that is not in tasks.md, and a specs repo ahead of origin. `/crav1-verify-build-against-spec` checks the behind tasks and drops a row for a T# that tasks.md does not have, so the two share one command. The block is left out when nothing is behind, and Waiting keeps only what waits on a person or a merge:

```text
Run next:

**Catch up first**
verify.md is behind for T2 and T45, and it has a row for T44, which is not in tasks.md.

Check T2 and T45 against the spec and remove the T44 row:
`/crav1-verify-build-against-spec orders-api`
Push the specs repo, which is 2 commits ahead of origin:
`git push`

---

**feat/orders-api-record**
...
```

With only the orphan row the label is `Remove the T44 row (it is in verify.md but not in tasks.md):`. Before 1.167.0 the check printed `Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2, T45)` near the bottom.

It does not show that `Next:` line from `verify.md`. `/crav1-tasks-ready-to-build` still rewrites only `build-map.md`.

## What does not get written

No commit, and no other file. The build map is the one file this command writes. `verify.md` stays with `/crav1-verify-build-against-spec`.

Since 1.149.0, `/crav1-tasks-ready-to-build` keeps the task rules in its skill file and reads a references file only when that case applies: work branches, a sub-branch, promotion, a work item, a plan risk that blocks the slice, or a next line that is not the ready list.

Since 1.173.0 a done task on the build map keeps its own commit: the merge commit in its branch's `build-progress` file, else its own row in `verify.md`. A `Date:` line or another task's row that names a newer commit never replaces it, and with no own commit the mark already on the map stays. Held and ready lines show full task names, and the open-questions entry is `Ask the open questions, which haven't been asked yet:` above `/crav1-show-or-ask-open-questions <slug>`.

Since 1.175.0 the ready check offers `Continue the build walk on <branch>:` only for your own walk: the walk's claim user in `claims.md` (else the `Run yes:` name in its `build-progress` file) must match `git config user.name`, the same check that makes a claim yours. `Owner: self` in the progress file means whoever ran that walk, so it is never trusted alone. Someone else's walk is a Waiting line instead, `Waiting: T9 to T12 are person B's, built, and wait for PR 82 to merge.`, or `Waiting: T9 to T12 are in progress by person B.` when the pull request is not known. A claimed task that is already built on a branch that is not merged reads `built by <name>, waits for PR <n> to merge` in the Held list, the status and `build-map.md`, not `in progress by <name> since <date>`. A reopened step's entry says why in one plain sentence, which names the changed spec sections or files and the tasks that wait, above an action label, `Finish the reopened /crav1-tighten-spec step:`. A build walk's own files (claims.md, walk-progress.md, build-progress, verify.md and task ticks) never reopen a step. The Catch up first push entry says how far ahead once, in its label `Push the specs repo, which is 2 commits ahead of origin:`, with no sentence repeating it.

Since 1.174.0 a done task's commit is the merge commit from its branch's `merge-pr` step, not the later commit that ticked it. A branch whose tasks are built and whose pull request is open reads `built, waits for PR <n> to merge`, never waiting on its own tasks, and the `Delivers:` and `Tasks:` lines show full names. An unfinished branch walk is the first Run next entry, `Continue the build walk on <branch>:` above `/crav1-build-walk <slug> <branch>`.

## After

The Next line recommends the build walk, with the T number beside the short name. `/crav1-build-tasks` builds one task without the walk:

```text
/crav1-build-walk T5 refund to the original card
@docs/specs/<slug>/
```

## Claims and a fresh copy (1.151.0)

The ready check fetches the specs repo before it reads. If that copy is behind origin, it stops and Run next is `git pull --no-rebase`. A task with an `In progress:` line in `docs/specs/<slug>/claims.md` is held `in progress by <user> since <date>` and is not offered in Run next.

Since 1.177.1 a pull request in the `Merge these PRs, in this order:` list gets no Waiting line of its own. When none of the listed pull requests is yours, Run next leads with `Ask the PR owners to merge, in this order:` and one line per owner. A merge-list line that says `owner not recorded` means neither the kit's records nor the pull request's host named who opened it; the skill asks you once and records your answer with `pr_common.py author`, so you never edit a spec file.

Reference page: [tasks-ready-to-build](reference/skills/crav1-tasks-ready-to-build.md) · Routes: [Workflow routes](reference/workflow.md)

The run ends as [How a run ends](reference/run-ending.md) says: one Run next block with one entry per ready branch, `Waiting:` only when a step is blocked, and `Uncommitted:` when files changed and are not committed.
