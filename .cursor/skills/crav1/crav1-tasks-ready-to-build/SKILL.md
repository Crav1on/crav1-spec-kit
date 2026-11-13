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

Every run, rebuild `docs/specs/<slug>/build-map.md` with `scripts/build_map.py`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not hand-edit it. The task list gains one line: `Build map: docs/specs/<slug>/build-map.md`. With the word, run `--chat` and print only that summary: each wave, then that wave's Overlap lines. `--recommend T#` prints the branch to offer. The first line is the name (1.140.0). Read `references/build-map.md` only when the script cannot run. Do not invent the map.

## Scope

- A named slug, title, playbook, or work-item name: `<interpreter> -X utf8 scripts/resolve_spec.py "<query>" --root docs/specs`. Exact folder first (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`, then one unique ordered token subsequence of those names (`cc 1.0` matches `cc-process-1-0`). Several matches: list them and stop. No match: say so and list the nearest slugs. Do not search the rest of the tree.
- No slug: every folder under `docs/specs/` that has `tasks.md`, skipping `_template`. A folder with `spec.md` but no `tasks.md` is listed once as `no tasks yet (run /crav1-plan-from-spec)`.

## What it reads

Per slice, read only: `spec.md` (`## Open questions` and their indented lines), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md`, and `verify.md` when it exists. Nothing else, except read-only local git for the Branches line below. Never read Azure Boards (ADO) or any network source.

When the slice has work branches (`Synced at` lines, Match `Branch:` entries, and `(branch: …)`, minus base branches and `(dropped)` entries), read `references/slice-branches.md` (1.64.0). Do not open it when the slice has none.

When the spec repo has `docs/environments/promotion.md`, read `references/promotion.md` (1.69.0). Do not open it otherwise.

When the slice has `work-item.md`, read `references/work-item-line.md`. Do not open it otherwise.

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
   - Any `Blocks:` line wins over a plan Risk, including `Blocks: none`. When a line under `## Risks` says do not implement until resolved, read [references/plan-risk.md](references/plan-risk.md). Do not open it when no risk says that.
4. **Dependencies.**
   - The task line has `(after: T1, T3)`: waits in order while any of those is unticked, `waits on T1 (recorded)`. A named task that does not exist is blocked, `after: T9 names no task (recorded)`.
   - No `(after: …)`: the task waits in order on the task just before it in `tasks.md` (the first task waits on nothing). Waits in order while that one is unticked, `waits on T2 (inferred)`.
   - When tasks wait on each other in a loop, read [references/cycle.md](references/cycle.md). Do not open it when the waits do not loop.
   - **Held dependents (1.132.0).** A task that waits on a held task is held too. The reason is `held, waits on T3 (recorded)` or `(inferred)`. It stays under Waiting. It is not Waits in order. Who is the person on the question or the Approval needed item. See [references/approval-holds.md](references/approval-holds.md).
5. **Ready.** Otherwise the task is ready.
   - `plan.md` has `Reviewed: <date>, P# open: 0`: ready.
   - `Reviewed:` with `P# open:` above 0: ready, with the warning `plan review has <n> open P# (recorded), see /crav1-tighten-plan`.
   - No `Reviewed:` line: ready, with the warning `plan review unknown (inferred), run /crav1-review-plan`.

Do not guess a dependency or a blocking link from the task text. Use only the marks above and the fallbacks.

When Python runs, rule 3 may use `scripts/question_blocks.py` beside this skill, and `scripts/approval_needed.py` (skill `crav1-record-approval`) for `## Approval needed`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Use its result. It does not write. Marks are in [references/question-holds.md](references/question-holds.md) and [references/approval-holds.md](references/approval-holds.md).

## Dependency order (1.103.0)

Every task list is in **dependency order**, not task-number order. Each task gets a wave: 0 when it waits on nothing, otherwise one more than the latest wave of the tasks it waits on. List wave by wave, lowest number first inside a wave; tasks in one wave can be built in either order. Tasks on a cycle go last.

The sort ships next to this file as `scripts/task_order.py`. When Python runs, use it for each slice: `<interpreter> <this skill folder>/scripts/task_order.py docs/specs/<slug>/tasks.md`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It prints Ready, Waits in order, Blocked, Needs tick, and Next. A recorded-merged task is under Needs tick (1.136.0). Waits in order is a real earlier task. Blocked is a cycle or an `(after:)` that names no task. Add the rule 1 to 3 results on top: a question is Waiting on a question, not Blocked. A dependent of a held task is Waiting too. The walk's `scripts/walk_progress.py readiness --root <spec-folder>` prints `result`: `ready`, `ready-partial`, or `not-ready`.

Other skills (`/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`) use this order. The ready check's Next lines are one per ready branch (1.133.0), not the single task that unblocks the most.

## Output

When you print the task list, read `references/task-list.md`. The word `build-map` does not open it. Next follows [run-ending.md](../crav1-docs/reference/run-ending.md).

When the result is not `ready` and not `ready-partial`, or nothing can start, read `references/other-next.md`. Do not open it for a `ready` or `ready-partial` result.

**verify.md behind (1.136.0).** When `verify_behind` is true, read `references/verify-behind.md`. This command does not write `verify.md`. Do not open that file otherwise.

## What it does not do

- No commit, no network read, no Azure Boards read, no fetch, no checkout. The only write is `build-map.md`, through the script.
- No skill run. It names the next step and stops.
- No new readiness marks. `Reviewed:`, `(after:)`, `(branch:)`, and `Blocks:` are written by the plan and question skills. This skill only reads them. It does not write `verify.md`.


## Choice words (1.69.0)

- Build map: `build-map` (show only the build map; the words after it are the scope, same as this command with no word, such as `cc 1.0`). The task list stays off. There are no `--flags`.
- Pipeline runs: `pipeline runs`. The meaning is in `references/promotion.md`, read only when `docs/environments/promotion.md` exists. There are no `--flags`.
