# Tasks ready to build

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want to know which tasks can be built now, and why the others cannot. Run it any time: before Build, between tasks, or after new information changed a spec. It is command-only (1.88.0): type `/crav1-tasks-ready-to-build`. Asking "which tasks are ready?" in plain words does not start it. Every run rewrites `docs/specs/<slug>/build-map.md` (1.128.0). The task list is unchanged apart from one line pointing at that file.

This is cross-cutting. It is not its own lane. It was added at Rhea's request so runners can pick the next task without guessing.

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
| A kept-open question in `spec.md` | **Waiting on a question** when its `Blocks:` line names the task (recorded). `Blocks: none` blocks no task (recorded). `Blocks: whole slice` holds every unfinished task (recorded) and the line says Holds the whole slice. With no `Blocks:` line, the question holds the `T#` ids named in its text (inferred from the text), and holds the whole slice only when no task is named and resolve-open-questions has never been recorded (1.137.0). Who comes from "Waiting for", then the latest Pending or Asked line, or not named yet. A plan Risk that says do not implement until resolved is **Blocked** when it matches no question, or matches a question with no `Blocks:` line and no inferred tasks. It matches on the question's first sentence, a `(question: <first words>)` tag, or the same Blocks tasks named in the risk. The line wins |
| An `## Approval needed` item with no matching `Approved:` line (1.141.0) | **Waiting** on that person, for the tasks on `Holds:`. Other tasks still start (`ready-partial`). A matching `Approved:` line clears the hold. The task is not ticked here |
| Tasks it waits on | **Waits in order** while a real earlier task is unticked (recorded from `(after: T#)`, or inferred from the task just before it). A cycle, or an `(after:)` that names no task, is **Blocked** |
| Otherwise | **Ready**. When `plan.md` has no `Reviewed:` line, it adds a warning to run `/crav1-review-plan` (inferred). When the review still has open `P#`s, it says so |
| Waits on a held task | **Waiting** too, reason `held, waits on T3` (1.132.0). Who is the person on the question that started the hold |

The result line is `ready`, `ready-partial`, or `not-ready` (1.132.0). `ready-partial` means some tasks can start now and some are held. `not-ready` means nothing can start. A cycle, a missing task, no plan, Needs verify, or a plan-review warning still records `not-ready`. The walk record stays `Result: ready-partial`. `/crav1-build-tasks` starts the ready tasks and refuses a held task with its reason.

Since 1.133.0 the ready tasks and the held tasks are grouped by the build-map branch, not as one flat list. The branch is the name `scripts/build_map.py --recommend` prints. Order is wave, then the map's row order. A task is shown as `T#` plus its short name, the same words as the Tasks field in `build-map.md`. A held task names the open question and who has it, or `held, waits on T3`. Each branch that can start gets its own Next line, so those branches can be started together. One branch is still one line. Since 1.143.0 that line recommends `/crav1-build-walk`, with the T number beside the short name, and names `/crav1-build-tasks` for one task without the walk.

Lists inside a branch follow the map. The wider task graph is still **dependency order** (1.103.0): tasks with nothing to wait on first, then the tasks they unblock, wave by wave, lowest number first inside a wave. For a slice where T7 waits on T2, T3 and T6 on T7, T4 on T3 and T7, and T5 on T4, the order is T1 → T2 → T7 → T3 | T6 → T4 → T5. `/crav1-build-tasks`, `/crav1-build-features` and `/crav1-verify-build-against-spec` use that order.

Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback). The marks are in [Readiness marks](concepts/data-layout.md#readiness-marks).

## What you see

```text
| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- | --- | --- |
| cancel-booking | 1 | 1 | 1 | 0 | 1 | 3 |

Ready now
- `feat/orders-retry` (wave 1): T5 refund to the original card

Held
- `feat/orders-currency` (wave 1): T7 choose the currency — open question "Which currency for refunds?" Waiting for the partner.

Waits in order (dependency order)
- T6 send the mail: waits on T5 (recorded).

Needs verify
- T3 short name: no verify.md row.

Done: 3

Next: /crav1-build-walk T5 refund to the original card, because that work is on feat/orders-retry. /crav1-build-tasks builds one task without the walk.
Source: docs/specs/cancel-booking/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/cancel-booking/build-map.md
```

## Getting recorded reasons

The more the kit records, the fewer reasons are inferred:

- `/crav1-review-plan` writes `Reviewed: <date>, P# open: <n>` in `plan.md`, and `/crav1-tighten-plan` lowers the count.
- `/crav1-plan-from-spec` ends a task line with `(after: T1)` when the task needs an earlier one.
- `/crav1-resolve-open-questions` asks which tasks a kept-open question blocks and writes `Blocks: T#`. **None** writes `Blocks: none`. **The whole slice** writes `Blocks: whole slice`. `/crav1-plan-from-spec` writes `Blocks: T#` or `Blocks: none` for a question it parks as a risk.

## Azure Boards

It never reads Azure Boards (ADO). A task closed there but not ticked here still shows as not done. Run [`/crav1-ado-sync`](from-ado-sync-pull-tasks.md) to bring task states back.

## The build map (1.128.0)

The file `docs/specs/<slug>/build-map.md` is how the work will be built, by branch. One branch per numbered step in the plan, unless the task line names its own. A task can name another branch with `(map: feat/cancel-refund)`. `(branch: feat/orders-retry)` does the same when no `(map:)` is set. Since 1.140.0 a `feat/…` name in the sentence, or `committed later on feat/orders-cicd`, does the same when neither mark is set. `from develop` after that name is the base. The plan step's `feat/<slug>-<words>` name is only the fallback. Two tasks on one step can use different branches. `(step: 1)` links a task to a step when the step text does not. No steps means one branch per task, and the file says so. `scripts/build_map.py --recommend T1` prints the branch on the first line and does not write the file. A merged branch, or a branch deleted locally and on the remote, is not that line.

Branches sit in waves. Wave 1 can start from a dependency point of view. Later waves open after those merge. The heading always says how many can start now, including one branch: `1 branch, 1 can start now`. The flowchart puts each wave side by side. An overlap note under a wave names two branches that share a requirement or a path. It does not change what is ready. Each branch row has six things: the branch name, one line on what it delivers, a short name for each task, which branches it waits for, any open question and who has the answer, and whether it is ready now. The short name is the work-item title when `work-item.md` has `task: T1 Turn off pipelines 7 and 24`, otherwise the task text up to the first parenthesis, `, in `, or the end of the sentence. When the task text names a different branch, the row adds `Task text names feat/orders-cicd; built on feat/orders-retry`. When the row is the branch on the task line and the plan step's name differs, the row adds `Plan step names feat/orders-one-commit-cleanup-main; built on feat/orders-host-setup-scripts` (1.140.0). Task ids are not in the file. The chat stays short. The word `build-map` prints the path, each wave's count, and that wave's overlap notes, one line per pair. The ready-check list stays the one pointer line.

A ticked task stays in its wave (1.132.0). The row strikes the short name through and marks it done, with the pull request link, or the branch or commit when there is no pull request: `~~Persist the decision~~ ✓ done ([PR 12](https://github.com/contoso/orders-api/pull/12))`. The heading counts done tasks apart from the branches that can start (`1 branch, 1 can start now, 1 done`). A wave whose every task is done is wrapped in a details block, `Wave 1 done (2 tasks)`. The rows stay in the file.

The script writes the file. This command does not commit it. Commit it with the spec when you are ready.

## When verify.md is behind (1.136.0)

The check reads `verify.md` and does not write it. A task stays done for later tasks when it is ticked, or when its pull request is recorded merged: `(PR n)` and the word merged on the task line, or on the Match `Branch:` line for that task's branch. The check adds a Waiting line when a ticked task is still `Not implemented`, when `Next:` names a ticked task, or when a merged task is still `Not implemented`. A merged row whose status is **Implemented, verified, tick pending** is not behind. The checkbox is the only leftover. `task_order.py` lists that task under Needs tick, not under Ready. A verify-only change does not force `not-ready`. This command only writes `build-map.md`. Only the walk's record or `clear --yes` restamps `walk-progress.md`.

When verify is behind, the check adds:

```text
Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2, T45)
```

It does not show that `Next:` line from `verify.md`. `/crav1-tasks-ready-to-build` still rewrites only `build-map.md`.

## What does not get written

No commit, and no other file. The build map is the one file this command writes. `verify.md` stays with `/crav1-verify-build-against-spec`.

## After

The Next line recommends the build walk, with the T number beside the short name. `/crav1-build-tasks` builds one task without the walk:

```text
/crav1-build-walk T5 refund to the original card
@docs/specs/<slug>/
```

Reference page: [tasks-ready-to-build](reference/skills/crav1-tasks-ready-to-build.md) · Routes: [Workflow routes](reference/workflow.md)

The run ends as [How a run ends](reference/run-ending.md) says: one `Next:` line per ready branch, `Waiting:` only when a step is blocked, and `Uncommitted:` when files changed and are not committed.
