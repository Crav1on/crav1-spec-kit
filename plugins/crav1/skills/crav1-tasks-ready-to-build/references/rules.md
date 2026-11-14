# Readiness rules (moved from SKILL.md in 1.156.0)

`scripts/walk_progress.py readiness --root <spec-folder>` (skill `crav1-tighten-and-plan-ready-to-build`) applies these rules and prints the reply. Read this file only when the script cannot run, or to explain one result. Do not re-derive a result the script printed.

## Rules, in order

Check each task in this order and stop at the first rule that decides it. Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback, because nothing was recorded).

1. **Done or needs verify.** A ticked task (`- [x]`):
   - `verify.md` has it under **Implemented, verified**: **Done**.
   - `verify.md` is missing, or has no row for it, or lists it as failed or **Claimed done, unverified**: **Needs verify**, with what `verify.md` says or `no verify.md row`. Not counted as done.
2. **No plan.** No `plan.md`: every task is blocked, `no plan.md (recorded)`.
3. **Blocking questions (1.125.0).**
   - A kept-open question under `## Open questions` (no `Answered:` line) with `Blocks: T#` that names this task: waiting on a question, `open question "<short question>" (recorded)`. Who comes first from the question's own "Waiting for <who>" phrase, then the latest `Pending:` or `Asked:` line. When neither names anyone, say not named yet.
   - `Blocks: none`, optionally `Blocks: none (later phase)`: this question blocks no task (recorded).
   - No `Blocks:` line (1.137.0): [question-holds.md](question-holds.md). A `T#` in the text that exists in `tasks.md` is the hold, noted inferred from the text. The whole slice is held only when no task is named and resolve-open-questions has never been recorded.
   - A line under `## Risks` in `plan.md` that says do not implement until resolved: [risk-blocks.md](risk-blocks.md). Any `Blocks:` line wins over that wording, including `Blocks: none`.
4. **Dependencies.**
   - The task line has `(after: T1, T3)`: waits in order while any of those is unticked, `waits on T1 (recorded)`. A named task that does not exist is blocked, `after: T9 names no task (recorded)`.
   - No `(after: …)`: the task waits in order on the task just before it in `tasks.md` (the first task waits on nothing). Waits in order while that one is unticked, `waits on T2 (inferred)`.
   - Tasks that wait on each other in a loop are blocked, `cycle T3 → T7 → T3 (recorded)`. Fix the `(after: …)` marks with `/crav1-tighten-plan`.
   - **Held dependents (1.132.0).** A task that waits on a held task is held too. The reason is `held, waits on T3 (recorded)` or `(inferred)`. It stays under Waiting. It is not Waits in order. Who is the person on the question or the Approval needed item. See [approval-holds.md](approval-holds.md).
5. **Ready.** Otherwise the task is ready.
   - `plan.md` has `Reviewed: <date>, P# open: 0`: ready.
   - `Reviewed:` with `P# open:` above 0: ready, with the warning `plan review has <n> open P# (recorded), see /crav1-tighten-plan`.
   - No `Reviewed:` line: ready, with the warning `plan review unknown (inferred), run /crav1-review-plan`.

Do not guess a dependency or a blocking link from the task text. Use only the marks above and the fallbacks.

Rule 3 uses `scripts/question_blocks.py` beside this skill, and `scripts/approval_needed.py` (skill `crav1-record-approval`) for `## Approval needed`. Marks are in [question-holds.md](question-holds.md) and [approval-holds.md](approval-holds.md).

## Dependency order (1.103.0)

Every task list is in **dependency order**, not task-number order. Each task gets a wave: 0 when it waits on nothing, otherwise one more than the latest wave of the tasks it waits on. List wave by wave, lowest number first inside a wave; tasks in one wave can be built in either order. Tasks on a cycle go last. A recorded-merged task is under Needs tick (1.136.0). Waits in order is a real earlier task. Blocked is a cycle, an `(after:)` that names no task, or a branch in a `Loop:` line (1.154.0). A question hold, and a dependent of a held task, stay under Waiting.

Other skills (`/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`) use this order. Run next is one entry per ready branch (1.133.0), not the single task that unblocks the most.

## What the reply holds

The brief reply is the default (1.156.0): the header, the counts row, `Result:`, the shared ending, `Source:` and `Build map:`. The long form adds the per-task lists and the Order line, only when the user asks for the full list (`full`).

```text
Tasks ready to build — <slug>

| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- | --- | --- |
| <slug> | 1 | 1 | 1 | 1 | 1 | 4 |

Result: ready-partial

Run next:

`/crav1-build-walk T5`
branch feat/orders-retry, T5 refund to the original card

`/crav1-build-walk T6`
branch feat/orders-export, T6 export the receipt

Held:
- `feat/orders-currency` (wave 1): T7 choose the currency — open question "Which currency for refunds?" Waiting for the partner.

/crav1-build-tasks builds one task without the walk.

Source: docs/specs/<slug>/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/<slug>/build-map.md
```

The long form (`full`) inserts these lists after `Result:`, one line per task, leaving out an empty list:

```text
Ready now
- `feat/orders-retry` (wave 1): T5 refund to the original card
Waits in order (dependency order)
- T9 send the mail: waits on T5 (recorded).
Blocked (dependency order)
- T10 cycle T10 → T11 → T10 (recorded).
Needs verify
- T3 short name: no verify.md row.
Done: 4
Order: T5 → T9 → T7 → T8
```

- **By branch (1.133.0).** The branch is `scripts/build_map.py docs/specs/<slug> --recommend T#`, the same row as the map. Order is wave, then map order. A task is `T#` plus its short name. Run next entries and the `Branch runs:` block (1.155.0) are in [build-map.md](build-map.md).
- **Result (1.132.0)** is `ready` when the tasks that are not done can start or only wait in order, `ready-partial` when some can start now and some are held, and `not-ready` when nothing can start. The walk record stays `Result: ready-partial`. A cycle, a missing task, no plan, Needs verify, or a plan-review warning still records `not-ready`.
- **Order** shows the slice's unticked tasks in dependency order, `|` between tasks of the same wave. One Order line per slice when listing all specs. The Order line keeps task ids.
- **Run next (1.153.0)** is the script's ending block, first. The walk command appears only there. The bottom may keep Waiting lines and one `/crav1-build-tasks` alternative. See `run-ending.md`.
- **Source** names every file it read, per slice. **Build map** is one line per slice, the path the script just wrote.
- **verify.md behind (1.136.0).** When `verify_behind` is true, the ending prints `verify_waiting`. A verify.md row for a T# not in tasks.md is one Waiting line; fix it with `/crav1-verify-build-against-spec` or tighten, and do not edit `verify.md`. A verify-only change does not force `not-ready`. The rule is [verify-behind.md](verify-behind.md).
