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

- A named slug, title, playbook, or work-item name: `scripts/resolve_spec.py`. Exact folder first (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`, then one unique ordered token subsequence of those names (`cc 1.0` matches `cc-process-1-0`). Several matches: list them and stop. No match: say so and list the nearest slugs. Do not search the rest of the tree.
- No slug: every folder under `docs/specs/` that has `tasks.md`, skipping `_template`. A folder with `spec.md` but no `tasks.md` is listed once as `no tasks yet (run /crav1-plan-from-spec)`.

## What it reads

Per slice, read only: `spec.md` (`## Open questions` and their indented lines), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md`, and `verify.md` when it exists. Nothing else, except read-only local git for the Branches line below. Never read Azure Boards (ADO) or any network source.

**Branches (1.64.0).** When the slice has work branches (`Synced at` lines, Match `Branch:` entries, and `(branch: …)`, minus base branches and `(dropped)` entries), add the Branches line under the counts from skill `crav1-add-to-spec`, `references/branches.md` (local git only: contained, or the same change by `git cherry`). No host check here, so a squash merge can show as not merged; say `squash merges are checked by /crav1-help status`. A shared branch gets `(also in <slug>)`. **Sub-branches and reverts (1.68.0)** use `(into <spec branch>)`, and **Promotion (1.69.0)** reads `docs/environments/promotion.md`. Both are that same file, under those headings. Report only. They do not change readiness or the Done count. The choice word `pipeline runs` runs the promotion check; headless without it gives the git answer plus `Pipeline runs not checked. Add the word: pipeline runs.` When the slice has `work-item.md`, add one line: task states in Azure Boards are not read here; `/crav1-ado-sync` brings them back.

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
   - A line under `## Risks` in `plan.md` that says do not implement until resolved blocks every unticked task, `plan Risk "<short risk>" blocks the whole slice (inferred)`, only when that risk is not about a question that already has a `Blocks:` line. Any `Blocks:` line wins over that wording, including `Blocks: none`. The risk matches its question on the question's first sentence, on `(question: <first words>)`, or when the risk names the same `Blocks` tasks. A risk that uses the phrase and matches no question still blocks the slice.
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

The sort ships next to this file as `scripts/task_order.py`. When Python runs, use it for each slice: `<interpreter> <this skill folder>/scripts/task_order.py docs/specs/<slug>/tasks.md`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It prints Ready, Waits in order, Blocked, Needs tick, and Next. A recorded-merged task is under Needs tick (1.136.0). Waits in order is a real earlier task. Blocked is a cycle or an `(after:)` that names no task. Add the rule 1 to 3 results on top: a question is Waiting on a question, not Blocked. A dependent of a held task is Waiting too. The walk's `scripts/walk_progress.py readiness --root` prints `result`: `ready`, `ready-partial`, or `not-ready`.

Other skills (`/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`) use this order. The ready check's Next lines are one per ready branch (1.133.0), not the single task that unblocks the most.

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

Next: /crav1-build-walk T5 refund to the original card, because that work is on feat/orders-retry. /crav1-build-tasks builds one task without the walk.
Next: /crav1-build-walk T6 export the receipt, because that work is on feat/orders-export. /crav1-build-tasks builds one task without the walk.
Source: docs/specs/<slug>/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/<slug>/build-map.md
```

- **By branch (1.133.0).** When Python runs, `readiness --root` (skill `crav1-tighten-and-plan-ready-to-build`, `scripts/walk_progress.py`) prints `ready_lines`, `held_lines`, and `next_lines`. Print those. Do not flatten them. The branch is `scripts/build_map.py --recommend T#`, the same row as the map. Order is wave, then map order. A task is `T#` plus its short name, in the lists and on the map. One ready branch is still one group and one Next line. Without Python, use `references/build-map.md` under Ready check.
- **Result (1.132.0)** is `ready` when the tasks that are not done can start or only wait in order, `ready-partial` when some can start now and some are held, and `not-ready` when nothing can start. The walk record stays `Result: ready-partial`. A cycle, a missing task, no plan, Needs verify, or a plan-review warning still records `not-ready`.
- **Order** shows the slice's unticked tasks in dependency order, `|` between tasks of the same wave. One Order line per slice when listing all specs. The Order line keeps task ids.
- **Next** is the script's `next_lines` when the result is `ready` or `ready-partial`: `/crav1-build-walk`, and `/crav1-build-tasks` builds one task without the walk. See `run-ending.md`. Do not run it.
- Nothing is ready, and an open question blocks the first task: `Next: /crav1-resolve-open-questions <slug>, because that question blocks the first task.`
- Only Needs verify is left: `Next: /crav1-verify-build-against-spec <slug>, because the built tasks are not verified yet.`
- Nothing is left to build or verify: `Next: nothing needed now.`
- **Source** names every file it read, per slice.
- **Build map** is one line per slice, the path the script just wrote. The task list above it is unchanged.
- **verify.md behind (1.136.0).** When `verify_behind` is true, print `verify_waiting`. A verify-only change does not force `not-ready`. This command does not restamp `walk-progress.md` and does not write `verify.md`. The rule is [references/verify-behind.md](references/verify-behind.md).
- When the slice has `work-item.md`, add the Azure Boards line from **What it reads**.

## What it does not do

- No commit, no network read, no Azure Boards read, no fetch, no checkout. The only write is `build-map.md`, through the script.
- No skill run. It names the next step and stops.
- No new readiness marks. `Reviewed:`, `(after:)`, `(branch:)`, and `Blocks:` are written by the plan and question skills. This skill only reads them. It does not write `verify.md`.


## Choice words (1.69.0)

- Build map: `build-map` (show only the build map; the words after it are the scope, same as this command with no word, such as `cc 1.0`). The task list stays off. There are no `--flags`.
- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
