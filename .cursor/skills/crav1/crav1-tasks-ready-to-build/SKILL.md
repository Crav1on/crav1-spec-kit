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

## The script owns the judgement (1.156.0)

The readiness script decides every task and prints the finished reply: the counts row, `Result:`, the shared ending (Run next first, Held, Branch runs, Loop, verify-behind and orphan Waiting lines, claim warnings), `Source:` and `Build map:`. Show that reply as-is. Do not re-derive a rule, re-sort a list, or rewrite a line. Never add your own `Next:` line. The rules it applies, with `scripts/question_blocks.py` and `scripts/task_order.py`, are in [references/rules.md](references/rules.md); read that only when the script cannot run, or to explain one result. The shared ending is `scripts/walk_ending.py --json <state>` beside this skill, described in [run-ending.md](../crav1-docs/reference/run-ending.md).

## Steps, in order

1. **Route.** The word `build-map` shows only the map; the words after it are the scope. The word `full` asks for the long form. No word: the brief reply (the default).
2. **Scope.** A named slug, title, playbook, or work-item name: `<interpreter> -X utf8 scripts/resolve_spec.py "<query>" --root docs/specs`. Exact folder first (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`, then one unique ordered token subsequence of those names (`cc 1.0` matches `cc-process-1-0`). Several matches: list them and stop. No match: say so and list the nearest slugs. Do not search the rest of the tree. No slug: every folder under `docs/specs/` that has `tasks.md`, skipping `_template`. A folder with `spec.md` but no `tasks.md` is listed once as `no tasks yet (run /crav1-plan-from-spec)`.
3. **Sync and claims.** The script fetches the specs repo and reads `claims.md` first, as [references/claims-and-sync.md](references/claims-and-sync.md) says (1.151.0). When it stops for a pull, print its reply (one Run next entry, `git pull --no-rebase`) and stop.
4. **Run it.** Per slice: `<interpreter> -X utf8 scripts/walk_progress.py readiness --root <spec-folder> --write-map --text` (skill `crav1-tighten-and-plan-ready-to-build`). Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. That rewrites `build-map.md` with `scripts/build_map.py` and prints the reply, ending `Build map: docs/specs/<slug>/build-map.md`. Print it verbatim, one slice after another when listing every slice. With `full`, run `--full` instead and add the per-task lists and the Order line from its `rows`, as [references/rules.md](references/rules.md) shows, then the same `ending`.
5. **Build map word.** With `build-map`, run `scripts/build_map.py docs/specs/<slug> --chat` and print only that summary: each wave, then that wave's Overlap lines. `--recommend T#` prints the branch to offer; the first line is the name (1.140.0). Do not hand-edit the map. Read `references/build-map.md` only when the script cannot run. Do not invent the map.
6. **Stop.** Do not run either command the reply names.

## What it reads

Per slice, only: `spec.md` (`## Open questions` and their indented lines), `plan.md` (the `Reviewed:` line and `## Risks`), `tasks.md`, `claims.md` when it exists (`In progress:` and `Claim max age:` lines), and `verify.md` when it exists. Nothing else, except read-only local git for the Branches line. Never read Azure Boards (ADO).

Read `references/work-branches.md` ("Work branches") only when the slice has work branches (`Synced at` lines, Match `Branch:` entries, or `(branch: …)`, minus base branches and `(dropped)` entries).

Read `references/sub-branches.md` ("Sub-branches and reverts") only when a branch entry has `(into <spec branch>)`, or a merged change was later undone on the base.

Read `references/promotion.md` ("Promotion") only when `docs/environments/promotion.md` exists, or the invocation has `pipeline runs`.

Read `references/work-item-line.md` ("Work item") only when the slice has `work-item.md`; the script already prints that line.

Read `references/risk-blocks.md` ("Plan risk blocks") only when a line under `## Risks` in `plan.md` says do not implement until resolved and you need to explain it. Any `Blocks:` line wins over that wording, including `Blocks: none`.

## Not-ready endings

The script prints the one `Next:` line a not-ready reply keeps. Without Python:

- Read `references/next-question.md` ("Question blocks the first task") only when nothing is ready and an open question blocks the first task.
- Read `references/next-verify.md` ("Only needs verify") only when only Needs verify is left.
- Read `references/next-nothing.md` ("Nothing left") only when nothing is left to build or verify.

Without Python at all, follow [references/rules.md](references/rules.md) and `references/build-map.md` under Ready check, and print the same shape.

## What it does not do

- No commit, no Azure Boards read, no checkout. The only network read is the script's fetch. The only write is `build-map.md`, through the script.
- No skill run. It names the next step and stops.
- No new readiness marks. `Reviewed:`, `(after:)`, `(branch:)`, and `Blocks:` are written by the plan and question skills. This skill only reads them. It does not write `verify.md`, and it does not restamp `walk-progress.md`.

## Choice words (1.69.0)

- Build map: `build-map` (show only the build map; the words after it are the scope, same as this command with no word, such as `cc 1.0`). The task list stays off. There are no `--flags`.
- Full list: `full` (1.156.0). The long form with every per-task list and the Order line. The brief reply is the default.
- Pipeline runs: `pipeline runs`. Read `references/promotion.md` ("Promotion") only when the invocation has that word. There are no `--flags`.
