# Tasks ready to build

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want to know which tasks can be built now, and why the others cannot. It reads your spec folders and writes nothing. Run it any time: before Build, between tasks, or after new information changed a spec.

This is cross-cutting. It is not its own lane. It was added at Rhea's request so runners can pick the next task without guessing.

## First prompt

```text
/crav1-tasks-ready-to-build
@docs/specs/<slug>/
```

Leave out the folder to check every slice under `docs/specs/`.

## What it checks

For each task, in this order:

| Check | Done, ready, or blocked |
| --- | --- |
| Ticked in `tasks.md` | **Done** when `verify.md` lists it as verified, otherwise **Needs verify** |
| `plan.md` missing | Blocked |
| A kept-open question in `spec.md` | Blocked when its `Blocks:` line names the task (recorded). With no `Blocks:` line, it blocks the whole slice (inferred). A plan Risk that says do not implement until resolved does the same |
| Tasks it waits on | Blocked while a task in its `(after: T#)` is unticked (recorded). With no `(after: …)`, every earlier unticked task blocks it (inferred) |
| Otherwise | **Ready**. When `plan.md` has no `Reviewed:` line, it adds a warning to run `/crav1-review-plan` (inferred). When the review still has open `P#`s, it says so |

Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback). The marks are in [Readiness marks](concepts/data-layout.md#readiness-marks).

## What you see

```text
| Slice | Ready | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- |
| cancel-booking | 1 | 2 | 1 | 3 |

Ready
- cancel-booking T5: Refund to the original card. Warning: plan review unknown (inferred), run /crav1-review-plan.

Blocked
- cancel-booking T6: waits on T5 (recorded).
- cancel-booking T7: open question "Which currency for refunds?" (recorded). Asked 2026-10-10, mail to Arvid.

Needs verify
- cancel-booking T3: no verify.md row.

Done: 3

Next: /crav1-build-tasks T5 (cancel-booking)
Source: docs/specs/cancel-booking/spec.md, plan.md, tasks.md, verify.md
```

## Getting recorded reasons

The more the kit records, the fewer reasons are inferred:

- `/crav1-review-plan` writes `Reviewed: <date>, P# open: <n>` in `plan.md`, and `/crav1-tighten-plan` lowers the count.
- `/crav1-plan-from-spec` ends a task line with `(after: T1)` when the task needs an earlier one.
- `/crav1-resolve-open-questions` asks which tasks a kept-open question blocks and writes `Blocks: T#`. `/crav1-plan-from-spec` writes it for a question it parks as a risk.

## Azure Boards

It never reads Azure Boards (ADO). A task closed there but not ticked here still shows as not done. Run [`/crav1-ado-sync`](from-ado-to-tasks.md) to bring task states back.

## What does not get written

Nothing. No file, no commit, no command run.

## After

Build the task it named:

```text
/crav1-build-tasks T5
@docs/specs/<slug>/
```

Reference page: [tasks-ready-to-build](reference/skills/crav1-tasks-ready-to-build.md) · Routes: [Workflow routes](reference/workflow.md)
