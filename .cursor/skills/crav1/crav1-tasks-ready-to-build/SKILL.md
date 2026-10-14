---
name: crav1-tasks-ready-to-build
description: >-
  List the tasks that are ready to build, for one spec or all specs, and why
  the others are blocked. Ready means plan.md exists (and was reviewed),
  the task's dependencies are done, no open question blocks it, and it is
  not ticked. Reads the Reviewed line in plan.md, (after: T#) on task lines,
  Blocks: lines under spec open questions, plan Risks, tasks.md ticks, and
  verify.md. Where nothing is recorded it falls back and marks the reason
  inferred. Shows summary counts, Ready, Blocked (one reason each), Needs
  verify, a Done count, and Next: /crav1-build-tasks T#. Local only,
  never reads Azure Boards. Read-only. Can run any time.
icon: list-checks
color: green
---

# Tasks ready to build

You list which tasks can be built now and why the others cannot. You read files only. You write nothing, commit nothing, and run no other skill. Naming `/crav1-build-tasks` is not running it.

This is cross-cutting. It is not its own lane. It can run any time: before Build, between tasks, or after new information. It does not move work into Build.

It is not `/crav1-whats-known-about` (what is known about one thing) and not `/crav1-ado-sync` (which specs could become Features). It is not the batch board of `/crav1-build-tasks`.

## Scope

- A named slug (or an @-mentioned spec folder): that slice only.
- No slug: every folder under `docs/specs/` that has `tasks.md`, skipping `_template`. A folder with `spec.md` but no `tasks.md` is listed once as `no tasks yet (run /crav1-plan-from-spec)`.

## What it reads

Per slice, read only: `spec.md` (`## Open questions` and their indented lines), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md`, and `verify.md` when it exists. Nothing else. Never read Azure Boards (ADO) or any network source. When the slice has `work-item.md`, add one line: task states in Azure Boards are not read here; `/crav1-ado-sync` brings them back.

## Rules, in order

Check each task in this order and stop at the first rule that decides it. Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback, because nothing was recorded).

1. **Done or needs verify.** A ticked task (`- [x]`):
   - `verify.md` has it under **Implemented, verified**: **Done**.
   - `verify.md` is missing, or has no row for it, or lists it as failed or **Claimed done, unverified**: **Needs verify**, with what `verify.md` says or `no verify.md row`. Not counted as done.
2. **No plan.** No `plan.md`: every task is blocked, `no plan.md (recorded)`.
3. **Blocking questions.**
   - A kept-open question under `## Open questions` (no `Answered:` line) with `Blocks: T#` that names this task: blocked, `open question "<short question>" (recorded)`, plus its latest `Asked:` or `Pending:` line when there is one.
   - A kept-open question with no `Blocks:` line, or a line under `## Risks` in `plan.md` that says do not implement until resolved: blocks every unticked task in the slice, `open question "<short question>" blocks the whole slice (inferred)` or `plan Risk "<short risk>" blocks the whole slice (inferred)`.
4. **Dependencies.**
   - The task line has `(after: T1, T3)`: blocked while any of those is unticked, `waits on T1 (recorded)`. A named task that does not exist is `after: T9 names no task (recorded)`.
   - No `(after: …)`: blocked while any earlier task in `tasks.md` is unticked, `waits on T2, earlier and unticked (inferred)`.
5. **Ready.** Otherwise the task is ready.
   - `plan.md` has `Reviewed: <date>, P# open: 0`: ready.
   - `Reviewed:` with `P# open:` above 0: ready, with the warning `plan review has <n> open P# (recorded), see /crav1-tighten-plan`.
   - No `Reviewed:` line: ready, with the warning `plan review unknown (inferred), run /crav1-review-plan`.

Do not guess a dependency or a blocking link from the task text. Use only the marks above and the fallbacks.

## Output

Lead with the summary, then the lists. One line per task. Leave out an empty list.

```text
Tasks ready to build — <slug> | all specs (<n> slices)

| Slice | Ready | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- |
| <slug> | 2 | 3 | 1 | 4 |

Ready
- <slug> T5: <title>. Warning: plan review unknown (inferred), run /crav1-review-plan.

Blocked
- <slug> T6: waits on T5 (recorded).
- <slug> T7: open question "Which currency for refunds?" (recorded). Asked 2026-10-10, mail to Arvid.

Needs verify
- <slug> T3: no verify.md row.

Done: 4

Next: /crav1-build-tasks T5 (<slug>)
Source: docs/specs/<slug>/spec.md, plan.md, tasks.md, verify.md
```

- **Next** names the first ready task, in `tasks.md` order, in the first slice that has one. When nothing is ready, say what would unblock the first blocked task instead (for example `Next: answer the open question with /crav1-resolve-questions`). When only Needs verify is left, `Next: /crav1-verify-spec`.
- **Source** names every file it read, per slice.
- When the slice has `work-item.md`, add the Azure Boards line from **What it reads**.

## What it does not do

- No file write, no commit, no network read, no Azure Boards read.
- No skill run. It names the next step and stops.
- No new marks. `Reviewed:`, `(after: …)`, and `Blocks:` are written by `/crav1-review-plan`, `/crav1-tighten-plan`, `/crav1-plan-from-spec`, and `/crav1-resolve-questions`.
