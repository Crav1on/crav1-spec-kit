---
name: crav1-tasks-ready-to-build
description: >-
  Use when the user asks which tasks are ready to build, for one spec or all,
  and why others are blocked. Lists Ready, Blocked, Needs verify and Done in
  dependency order and names the next task. Local and read-only.
disable-model-invocation: true
icon: list-checks
color: green
---

# Tasks ready to build

You list which tasks can be built now and why the others cannot. You read files only. You write nothing, commit nothing, and run no other skill. Naming `/crav1-build-tasks` is not running it.

This is cross-cutting. It is not its own lane. It can run any time: before Build, between tasks, or after new information. It does not move work into Build.

It is not `/crav1-what-do-we-know-about-this` (what is known about one thing) and not `/crav1-ado-sync` (which specs could become Features). It is not the batch board of `/crav1-build-tasks`.

## Scope

- A named slug (or an @-mentioned spec folder): that slice only.
- No slug: every folder under `docs/specs/` that has `tasks.md`, skipping `_template`. A folder with `spec.md` but no `tasks.md` is listed once as `no tasks yet (run /crav1-plan-from-spec)`.

## What it reads

Per slice, read only: `spec.md` (`## Open questions` and their indented lines), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md`, and `verify.md` when it exists. Nothing else, except read-only local git for the Branches line below. Never read Azure Boards (ADO) or any network source.

**Branches (1.64.0).** When the slice has work branches (its `Synced at` lines, Match `Branch:` list and task `(branch: …)` parts, minus base branches and `(dropped)` entries), add one Branches line under the counts, from `crav1-add-to-spec` `references/branches.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`), using only the local git tests (contained, or the same change by `git cherry`) on the refs on disk. No host check here, so a squash merge can show as not merged; say `squash merges are checked by /crav1-help status` when a branch is not merged. A branch other slices also list gets `(also in <slug>)`. It doesn't change readiness or the Done count. **Sub-branches and reverts (1.68.0).** As that file says under **Spec branch and sub-branches** and **Reverted**: sub-branches (entries with `(into <spec branch>)`) are left out of the Branches count and get `Sub-branches: <n> of <m> merged into <spec branch>.`, plus `left behind: <branch> (not in <spec branch>)` for one that never merged after the spec branch reached the base; done counts top-level branches only. A merged branch whose change was later undone on the base shows `<branch>: merged, reverted on <base> (<revert sha>)`. They use the same local git tests and are report only and never block done. **Promotion (1.69.0).** When the spec repo has `docs/environments/promotion.md`, add the `Promotion:` line after the Branches line, as `crav1-add-to-spec` `references/branches.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Promotion**: per repo, the furthest environment reached and each later one not yet reached, as `on the branch that deploys to <env> (<branch>)` or `not yet on the branch that deploys to <env> (<branch>)`, release patterns as `on release/<x> (deploys to <env>)`, tag lines as `in tag <tag> (deploys to <env>)` or `not yet tagged`, the chain at the end, `Unclear:` for an unknown word with no `(after …)`, and `<branch>: not back on <base>` for a release fix. Branch reach, never `deployed to`. When a pipeline-sourced line is behind it, end with **Also check the latest pipeline runs?** (**Check pipeline runs** / **No, keep the git answer**); the choice word `pipeline runs` runs the check without asking; headless without it gives the git answer plus `Pipeline runs not checked. Add the word: pipeline runs.` Azure DevOps only, read-only; `az has no login` keeps the git answer. Report only: done stays merged into the base. When the slice has `work-item.md`, add one line: task states in Azure Boards are not read here; `/crav1-ado-sync` brings them back.

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
   - No `(after: …)`: the task waits on the task just before it in `tasks.md` (the first task waits on nothing). Blocked while that one is unticked, `waits on T2 (inferred)`.
   - Tasks that wait on each other in a loop are blocked, `cycle T3 → T7 → T3 (recorded)`. Fix the `(after: …)` marks with `/crav1-tighten-plan`.
5. **Ready.** Otherwise the task is ready.
   - `plan.md` has `Reviewed: <date>, P# open: 0`: ready.
   - `Reviewed:` with `P# open:` above 0: ready, with the warning `plan review has <n> open P# (recorded), see /crav1-tighten-plan`.
   - No `Reviewed:` line: ready, with the warning `plan review unknown (inferred), run /crav1-review-plan`.

Do not guess a dependency or a blocking link from the task text. Use only the marks above and the fallbacks.

## Dependency order (1.103.0)

Every task list is in **dependency order**, not task-number order. Each task gets a wave: 0 when it waits on nothing, otherwise one more than the latest wave of the tasks it waits on. List wave by wave, lowest number first inside a wave; tasks in one wave can be built in either order. Tasks on a cycle go last. For the slice in the example below (T7 after T2, T3 and T6 after T7, T4 after T3 and T7, T5 after T4) the order is T1 → T2 → T7 → T3 | T6 → T4 → T5.

The sort ships next to this file as `scripts/task_order.py`. When Python runs, use it for each slice: `python3 <this skill folder>/scripts/task_order.py docs/specs/<slug>/tasks.md` prints Ready, Blocked, the Order line and Next, with the reasons for rule 4. Add the rule 1 to 3 results on top. Without Python, apply the same rule by hand.

Other skills (`/crav1-build-tasks`, `/crav1-build-features`, `/crav1-verify-build-against-spec`) use this order and this Next rule.

## Output

Lead with the summary, then the lists. One line per task. Leave out an empty list.

```text
Tasks ready to build — <slug> | all specs (<n> slices)

| Slice | Ready | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- |
| <slug> | 2 | 3 | 1 | 4 |

Ready (dependency order)
- <slug> T5: <title> (branch: feat/orders-retry). Warning: plan review unknown (inferred), run /crav1-review-plan.

Blocked (dependency order)
- <slug> T6: waits on T5 (recorded).
- <slug> T7: open question "Which currency for refunds?" (recorded). Asked 2026-10-10, mail to Dana.

Needs verify
- <slug> T3: no verify.md row.

Done: 4
Order: T5 → T6 → T7
Branches: 1 of 3 merged into develop. Not merged: feat/orders-retry (2 commits), feature/orders-export (3 commits).

Next: /crav1-build-tasks T5 (<slug>)
Source: docs/specs/<slug>/spec.md, plan.md, tasks.md, verify.md
```

- **Order** shows the slice's unticked tasks in dependency order, `|` between tasks of the same wave. One Order line per slice when listing all specs.
- **Next** names the ready task that unblocks the most other unticked tasks (every task downstream of it), lowest number on a tie, in the first slice that has one. When nothing is ready, say what would unblock the first blocked task instead (for example `Next: answer the open question with /crav1-resolve-open-questions`). When only Needs verify is left, `Next: /crav1-verify-build-against-spec`.
- A ready task with `(branch: …)` shows that branch beside it.
- **Source** names every file it read, per slice.
- When the slice has `work-item.md`, add the Azure Boards line from **What it reads**.

## What it does not do

- No file write, no commit, no network read, no Azure Boards read, no fetch, no checkout.
- No skill run. It names the next step and stops.
- No new marks. `Reviewed:`, `(after: …)`, `(branch: …)`, and `Blocks:` are written by `/crav1-review-plan`, `/crav1-tighten-plan`, `/crav1-plan-from-spec`, and `/crav1-resolve-open-questions`.


## Choice words (1.69.0)

- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
