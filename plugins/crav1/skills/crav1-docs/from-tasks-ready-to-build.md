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
| A kept-open question in `spec.md` | **Waiting on a question** when its `Blocks:` line names the task (recorded). `Blocks: none` blocks no task (recorded). With no `Blocks:` line, the question holds the whole slice (inferred). Who comes from "Waiting for", then the latest Pending or Asked line, or not named yet. A plan Risk that says do not implement until resolved is **Blocked** when it matches no question, or matches a question with no `Blocks:` line. It matches on the question's first sentence, a `(question: <first words>)` tag, or the same Blocks tasks named in the risk. The line wins |
| Tasks it waits on | **Waits in order** while a real earlier task is unticked (recorded from `(after: T#)`, or inferred from the task just before it). A cycle, or an `(after:)` that names no task, is **Blocked** |
| Otherwise | **Ready**. When `plan.md` has no `Reviewed:` line, it adds a warning to run `/crav1-review-plan` (inferred). When the review still has open `P#`s, it says so |

Lists are in **dependency order** (1.103.0), not task number: tasks with nothing to wait on first, then the tasks they unblock, wave by wave, lowest number first inside a wave. For a slice where T7 waits on T2, T3 and T6 on T7, T4 on T3 and T7, and T5 on T4, the order is T1 → T2 → T7 → T3 | T6 → T4 → T5. **Next** is the ready task that unblocks the most other tasks. `/crav1-build-tasks`, `/crav1-build-features` and `/crav1-verify-build-against-spec` use the same order.

Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback). The marks are in [Readiness marks](concepts/data-layout.md#readiness-marks).

## What you see

```text
| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- | --- | --- |
| cancel-booking | 1 | 1 | 1 | 0 | 1 | 3 |

Ready (dependency order)
- cancel-booking T5: Refund to the original card. Warning: plan review unknown (inferred), run /crav1-review-plan.

Waiting on a question
- cancel-booking T7: open question "Which currency for refunds?" (recorded). Waiting for the partner.

Waits in order (dependency order)
- cancel-booking T6: waits on T5 (recorded).

Needs verify
- cancel-booking T3: no verify.md row.

Done: 3

Next: /crav1-build-tasks T5 (cancel-booking), because that task unblocks the most others.
Source: docs/specs/cancel-booking/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/cancel-booking/build-map.md
```

## Getting recorded reasons

The more the kit records, the fewer reasons are inferred:

- `/crav1-review-plan` writes `Reviewed: <date>, P# open: <n>` in `plan.md`, and `/crav1-tighten-plan` lowers the count.
- `/crav1-plan-from-spec` ends a task line with `(after: T1)` when the task needs an earlier one.
- `/crav1-resolve-open-questions` asks which tasks a kept-open question blocks and writes `Blocks: T#`. **None** writes `Blocks: none`. **The whole slice** leaves no line. `/crav1-plan-from-spec` writes `Blocks: T#` or `Blocks: none` for a question it parks as a risk.

## Azure Boards

It never reads Azure Boards (ADO). A task closed there but not ticked here still shows as not done. Run [`/crav1-ado-sync`](from-ado-sync-pull-tasks.md) to bring task states back.

## The build map (1.128.0)

The file `docs/specs/<slug>/build-map.md` is how the work will be built, by branch. One branch per numbered step in the plan. A task can name another branch with `(map: feat/cancel-refund)`. `(branch: feat/orders-retry)` does the same when no `(map:)` is set. `(step: 1)` links a task to a step when the step text does not. No steps means one branch per task, and the file says so. Since 1.129.0 that row branch is what `/crav1-build-tasks` offers. `scripts/build_map.py --recommend T1` prints it.

Branches sit in waves. Wave 1 can start from a dependency point of view. Later waves open after those merge. The heading always says how many can start now, including one branch: `1 branch, 1 can start now`. The flowchart puts each wave side by side. An overlap note under a wave names two branches that share a requirement or a path. It does not change what is ready. Each branch row has six things: the branch name, one line on what it delivers, a short name for each task, which branches it waits for, any open question and who has the answer, and whether it is ready now. The short name is the work-item title when `work-item.md` has `task: T1 Turn off pipelines 7 and 24`, otherwise the task text up to the first parenthesis, `, in `, or the end of the sentence. When the task text names a different branch, the row adds `Task text names feat/orders-cicd; built on feat/orders-retry`. Task ids are not in the file. The chat stays short. The word `build-map` prints the path, each wave's count, and that wave's overlap notes, one line per pair. The ready-check list stays the one pointer line.

The script writes the file. This command does not commit it. Commit it with the spec when you are ready.

## What does not get written

No commit, and no other file. The build map is the one file this command writes.

## After

Build the task it named:

```text
/crav1-build-tasks T5
@docs/specs/<slug>/
```

Reference page: [tasks-ready-to-build](reference/skills/crav1-tasks-ready-to-build.md) · Routes: [Workflow routes](reference/workflow.md)

The run ends as [How a run ends](reference/run-ending.md) says: one `Next:` line, `Waiting:` only when a step is blocked, and `Uncommitted:` when files changed and are not committed.
