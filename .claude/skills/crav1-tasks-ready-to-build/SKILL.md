---
name: crav1-tasks-ready-to-build
description: >-
  Use when the user asks which tasks are ready to build, for one spec or all,
  and why others are blocked, or asks for the build map. Lists ready and
  blocked tasks in dependency order and refreshes each slice's build map.
disable-model-invocation: true
icon: list-checks
color: green
---

# Tasks ready to build

You list which tasks can be built now and why the others cannot. The only file you write is `docs/specs/<slug>/build-map.md`, through the script. You commit nothing and run no other skill. Naming `/crav1-build-tasks` is not running it.

This is cross-cutting. It is not its own lane. It can run any time: before Build, between tasks, or after new information. It does not move work into Build.

It is not `/crav1-what-do-we-know-about-this` (what is known about one thing) and not `/crav1-ado-sync` (which specs could become Features). It is not the batch board of `/crav1-build-tasks`.

## Build map (1.128.0)

Route first. The word `build-map` shows only the map. The words after it are the scope, the same scope as this command with no word (a slug such as `cc 1.0`, an `@` folder, or every slice). No word keeps the task list.

Every run, rebuild `docs/specs/<slug>/build-map.md` with `scripts/build_map.py`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not hand-edit it. With no flag, it prints only the one-line path. The task list gains that line. With the word, run `--chat` and print only that summary: each wave, then that wave's Overlap lines. `--recommend T#` prints the branch to offer. The first line is the name (1.140.0). Read `references/build-map.md` only when the script cannot run. Do not invent the map.

## Scope

- A named slug, title, playbook, or work-item name: `<interpreter> -X utf8 scripts/resolve_spec.py "<query>" --root docs/specs`. Exact folder first (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`, then one unique ordered token subsequence of those names (`cc 1.0` matches `cc-process-1-0`). Several matches: list them and stop. No match: say so and list the nearest slugs. Do not search the rest of the tree.
- No slug: every folder under `docs/specs/` that has `tasks.md`, skipping `_template`. A folder with `spec.md` but no `tasks.md` is listed once as `no tasks yet (run /crav1-plan-from-spec)`.

## What it reads

Before reading a slice, fetch the specs repo and read `claims.md` when it exists, as [references/claims-and-sync.md](references/claims-and-sync.md) says (1.151.0). Then, per slice, read only: `spec.md` (`## Open questions` and their indented lines), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md`, `claims.md` when it exists (`In progress:` and `Claim max age:` lines), and `verify.md` when it exists. Nothing else, except read-only local git for the Branches line below. Never read Azure Boards (ADO).

Read `references/work-branches.md` ("Work branches") only when the slice has work branches (`Synced at` lines, Match `Branch:` entries, or `(branch: …)`, minus base branches and `(dropped)` entries).

Read `references/sub-branches.md` ("Sub-branches and reverts") only when a branch entry has `(into <spec branch>)`, or a merged change was later undone on the base.

Read `references/promotion.md` ("Promotion") only when `docs/environments/promotion.md` exists, or the invocation has `pipeline runs`.

Read `references/work-item-line.md` ("Work item") only when the slice has `work-item.md`.

## Rules, in order

Check each task in this order and stop at the first rule that decides it. Every reason says **recorded** (from a mark in a file) or **inferred** (a fallback, because nothing was recorded).

1. **Done or needs verify.** A ticked task (`- [x]`):
   - `verify.md` has it under **Implemented, verified**: **Done**.
   - `verify.md` is missing, or has no row for it, or lists it as failed or **Claimed done, unverified**: **Needs verify**, with what `verify.md` says or `no verify.md row`. Not counted as done.
2. **No plan.** No `plan.md`: every task is blocked, `no plan.md (recorded)`.
3. **Blocking questions (1.125.0).**
   - A kept-open question under `## Open questions` (no `Answered:` line) with `Blocks: T#` that names this task: waiting on a question, `open question "<short question>" (recorded)`. Who comes first from the question's own "Waiting for <who>" phrase, then the latest `Pending:` or `Asked:` line. When neither names anyone, say not named yet.
   - `Blocks: none`, optionally `Blocks: none (later phase)`: this question blocks no task (recorded).
   - No `Blocks:` line (1.137.0): [references/question-holds.md](references/question-holds.md). A `T#` in the text that exists in `tasks.md` is the hold, noted inferred from the text. The whole slice is held only when no task is named and resolve-open-questions has never been recorded.
   - Read `references/risk-blocks.md` ("Plan risk blocks") only when a line under `## Risks` in `plan.md` says do not implement until resolved. Any `Blocks:` line wins over that wording, including `Blocks: none`.
4. **Dependencies.**
   - The task line has `(after: T1, T3)`: waits in order while any of those is unticked, `waits on T1 (recorded)`. A named task that does not exist is blocked, `after: T9 names no task (recorded)`.
   - No `(after: …)`: the task waits in order on the task just before it in `tasks.md` (the first task waits on nothing). Waits in order while that one is unticked, `waits on T2 (inferred)`.
   - Tasks that wait on each other in a loop are blocked, `cycle T3 → T7 → T3 (recorded)`. Fix the `(after: …)` marks with `/crav1-tighten-plan`.
   - **Held dependents (1.132.0).** A task that waits on a held task is held too. The reason is `held, waits on T3 (recorded)` or `(inferred)`. It stays under Waiting. It is not Waits in order. Who is the person on the question or the Approval needed item. See [references/approval-holds.md](references/approval-holds.md).
5. **Ready.** Otherwise the task is ready.
   - `plan.md` has `Reviewed: <date>, P# open: 0`: ready.
   - `Reviewed:` with `P# open:` above 0: ready, with the warning `plan review has <n> open P# (recorded), see /crav1-tighten-plan`.
   - No `Reviewed:` line: ready, with the warning `plan review unknown (inferred), run /crav1-review-plan`.

Do not guess a dependency or a blocking link from the task text. Use only the marks above and the fallbacks.

When Python runs, rule 3 may use `scripts/question_blocks.py` beside this skill, and `scripts/approval_needed.py` (skill `crav1-record-approval`) for `## Approval needed`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Use its result. It does not write. Marks are in [references/question-holds.md](references/question-holds.md) and [references/approval-holds.md](references/approval-holds.md).

## Dependency order (1.103.0)

Every task list is in **dependency order**, not task-number order. Each task gets a wave: 0 when it waits on nothing, otherwise one more than the latest wave of the tasks it waits on. List wave by wave, lowest number first inside a wave; tasks in one wave can be built in either order. Tasks on a cycle go last.

When Python runs, run the walk's `scripts/walk_progress.py readiness --root <spec-folder> --brief --write-map` (skill `crav1-tighten-and-plan-ready-to-build`). Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Print that output. Start the ending with the script's `Run next` block, verbatim. Never write a `Next:` line of your own. `scripts/task_order.py` is only needed with `--full`. A recorded-merged task is under Needs tick (1.136.0). Waits in order is a real earlier task. Blocked is a cycle or an `(after:)` that names no task. A question hold, and a dependent of a held task, stay under Waiting.

Other skills (`/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`) use this order. Run next is one entry per ready branch (1.133.0), not the single task that unblocks the most.

## Output

Lead with the summary, then the lists. One line per task. Leave out an empty list.

```text
Tasks ready to build — <slug> | all specs (<n> slices)

| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- | --- | --- |
| <slug> | 1 | 1 | 1 | 1 | 1 | 4 |

Result: ready-partial

Ready now
- `feat/orders-retry` (wave 1): T5 refund to the original card
- `feat/orders-export` (wave 1): T6 export the receipt

Held
- `feat/orders-currency` (wave 1): T7 choose the currency — open question "Which currency for refunds?" Waiting for the partner.
- `feat/orders-archive` (wave 2): T8 archive the receipt — held, waits on T7

Waits in order (dependency order)
- T9 send the mail: waits on T5 (recorded).

Blocked (dependency order)
- T10 cycle T10 → T11 → T10 (recorded).

Needs verify
- T3 short name: no verify.md row.

Done: 4
Order: T5 → T9 → T7 → T8

Run next:

`/crav1-build-walk T5`
branch feat/orders-retry, T5 refund to the original card

`/crav1-build-walk T6`
branch feat/orders-export, T6 export the receipt

/crav1-build-tasks builds one task without the walk.
Source: docs/specs/<slug>/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/<slug>/build-map.md
```

- **By branch (1.133.0).** When Python runs, print the brief `ending` from `readiness --root <spec-folder> --brief --write-map`. Do not flatten it, and do not add a `Next:` line. The branch is `scripts/build_map.py docs/specs/<slug> --recommend T#`, the same row as the map. Order is wave, then map order. A task is `T#` plus its short name. One ready branch is still one Run next entry. Without Python, use `references/build-map.md` under Ready check.
- **Result (1.132.0)** is `ready` when the tasks that are not done can start or only wait in order, `ready-partial` when some can start now and some are held, and `not-ready` when nothing can start. The walk record stays `Result: ready-partial`. A cycle, a missing task, no plan, Needs verify, or a plan-review warning still records `not-ready`.
- **Order** shows the slice's unticked tasks in dependency order, `|` between tasks of the same wave. One Order line per slice when listing all specs. The Order line keeps task ids.
- **Run next (1.153.0)** is the script's ending block, printed verbatim at the start. The walk command appears only there. The bottom may keep Waiting lines and one `/crav1-build-tasks` alternative. Never write a `Next:` line of your own. See `run-ending.md`. Do not run either command.
- Read `references/next-question.md` ("Question blocks the first task") only when nothing is ready and an open question blocks the first task.
- Read `references/next-verify.md` ("Only needs verify") only when only Needs verify is left.
- Read `references/next-nothing.md` ("Nothing left") only when nothing is left to build or verify.
- **Source** names every file it read, per slice.
- **Build map** is one line per slice, the path the script just wrote. The task list above it is unchanged.
- **verify.md behind (1.136.0).** When `verify_behind` is true, print `verify_waiting`. A verify.md row for a T# not in tasks.md is one Waiting line; fix it with `/crav1-verify-build-against-spec` or tighten, and do not edit `verify.md`. A verify-only change does not force `not-ready`. This command does not restamp `walk-progress.md` and does not write `verify.md`. The rule is [references/verify-behind.md](references/verify-behind.md).
- When the slice has `work-item.md`, add the Azure Boards line from **What it reads**.

## What it does not do

- No commit, no network read, no Azure Boards read, no fetch, no checkout. The only write is `build-map.md`, through the script.
- No skill run. It names the next step and stops.
- No new readiness marks. `Reviewed:`, `(after:)`, `(branch:)`, and `Blocks:` are written by the plan and question skills. This skill only reads them. It does not write `verify.md`.


## Choice words (1.69.0)

- Build map: `build-map` (show only the build map; the words after it are the scope, same as this command with no word, such as `cc 1.0`). The task list stays off. There are no `--flags`.
- Pipeline runs: `pipeline runs`. Read `references/promotion.md` ("Promotion") only when the invocation has that word. There are no `--flags`.
