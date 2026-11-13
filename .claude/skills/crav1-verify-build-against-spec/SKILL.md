---
name: crav1-verify-build-against-spec
description: >-
  Use after implementation or when the user wants proof against spec.md. Maps
  every v0 acceptance line to tests or UI checks and reports pass, fail, or
  missing, with a TL;DR of implemented tasks. Does not add features.
disable-model-invocation: true
icon: beaker
color: orange
---

# Verify spec

You prove the **running system** (or current tree) against `spec.md`. You do not add features. You do not “fix” the spec to match the code.

Lead with a **TL;DR**: which tasks are implemented and verified, which are not. Same facts as today — **overview first, details below**.

## Find the spec

The spec folder is the user's @-mention, or the one folder `<interpreter> -X utf8 <skill crav1-tasks-ready-to-build>/scripts/resolve_spec.py "<query>" --root docs/specs` prints, as `crav1-docs/reference/running-scripts.md` says. Exact folder first, then hyphen and space forms (`orders 1.0` matches `orders-1-0`), then one unique playbook basename, spec title, or work-item name in `spec.md`, then one unique ordered token subsequence of those names (`cc 1.0` matches `cc-process-1-0`). Several matches: list them and stop. No match: say so and list the nearest slugs. Do not pick the most recently edited tree. Do not search the rest of the tree. No name: ask which slug.

Read `spec.md` acceptance (and EARS/BDD export if present — spec.md still wins). Read `tasks.md` if it exists. Skim tests and the files `plan.md` said would be touched.

## Classify each task (before writing)

For every `T#` in `tasks.md`, in dependency order (`/crav1-tasks-ready-to-build` **Dependency order**, its `scripts/task_order.py` when Python runs; pick the interpreter as `crav1-docs/reference/running-scripts.md` says), so a task is checked after the tasks it waits on. List tasks in that order in the Tasks overview and the TL;DR id lists, under the heading `Tasks — overview (dependency order)`.

A task downstream of an **Implemented, verify failed** task (it waits on it, directly or through other tasks) keeps its own status, and its Verify cell starts with `depends on T7 (failed)`. When it failed too, its gap names T7 as the first thing to fix. `task_order.py <tasks.md> --failed T7` lists them.

| Status | Meaning |
| --- | --- |
| **Implemented, verified** | Row is `[x]` **and** its verify evidence ran and passed |
| **Implemented, verified, tick pending** | Evidence passed, the row is still `[ ]`, and the pull request is recorded merged (`(PR n)` and the word `merged` on the task line, or on the Match `Branch:` line for its `(branch:)` or `(map:)`). Not **Not implemented**. The open checkbox is a Gap |
| **Implemented, verify failed** | `[x]` or code exists for this `T#`, but verify ran and failed |
| **Not implemented** | Still `- [ ]`, and it is not tick pending (or no code for this `T#`) |
| **Claimed done, unverified** | `[x]` but evidence could not be run (no command, no browser). Also a ticked task whose `(branch: X)` is not the checkout: **Claimed done, unverified (on X, not checked out)** |

Read `references/tick-pending.md` ("Tick pending") only when evidence passed, the row is still `[ ]`, and the pull request is recorded merged.

Read `references/host-setup-task.md` ("Host setup tasks") only when a task is marked `(host setup)` (1.115.0, skill `crav1-host-setup`).

## Branches (1.64.0)

Read `references/work-branches.md` ("Work branches") only when the spec has work branches (its `Synced at` lines, Match `Branch:` list, or task `(branch: …)` parts, minus base branches and `(dropped)` entries).

Read `references/sub-branches.md` ("Sub-branches and reverts") only when a branch entry has `(into <spec branch>)`, or a merged change was later undone on the base.

Read `references/promotion.md` ("Promotion") only when the spec repo has `docs/environments/promotion.md`, or the invocation has `pipeline runs`.

Acceptance lines with **no** `T#` stay in the detail matrix as **missing** coverage — also list their ids in the TL;DR.

## Results (unchanged meanings)

- **pass** — evidence ran and matched the acceptance line
- **fail** — evidence ran and contradicted it
- **untested** — could not run (no command, no browser)
- **missing** — no test, no task, no UI path covers it

**Evidence** must be something a stranger could rerun. “Looks fine” is not evidence.

Then:

1. If any acceptance or task verify is **live** (running Aspire/compose/dev host, published URL, browser against localhost), follow this skill’s [references/live-host.md](references/live-host.md) **before** that evidence. Record refresh/health in **Commands run**.
2. Before any test command, run the local dependency preflight in this skill's [references/test-dependencies.md](references/test-dependencies.md): detect what the tests need (Azurite, a database container, an emulator), check each is running, and ask start, skip, or stop for one that is not. Then run the documented test/lint commands from `AGENTS.md` or the repo README when they exist. Record the command and outcome. A test skipped for a missing dependency blocks **Implemented, verified** unless the user chose skip; that task is **Claimed done, unverified**, and the missing dependency goes at the top of the report as a blocker.
3. For UI acceptance, use the browser if available; otherwise mark **untested** and say why.
4. Map `tasks.md` rows: checked but failing verify → **Implemented, verify failed**; evidence passed, row still `[ ]`, pull request recorded merged → **Implemented, verified, tick pending**; other unchecked → **Not implemented**.

## Write `docs/specs/<slug>/verify.md`

Follow this skill’s `assets/verify.md` **section order**. Do not put the long acceptance table first.

1. **TL;DR** — counts + id lists, including tick pending, then the Branches line when the spec has work branches. Next skips tasks the ready check counts as done and names the first task that can start, one line per ready branch. A tick-pending Gap does not by itself make Next `/crav1-fix-build-gaps`.
2. **Tasks — overview** — one short table: `T#` | title | status | verify result, in dependency order (above).
3. **Acceptance — details** — the full A# matrix (quote, evidence, result).
4. **Commands run**
5. **Gaps** (`G1`, `G2`, …)

Do not rewrite `spec.md`.

## After the report (chat)

Same order as the file. Do **not** open with the full acceptance matrix.

1. Path to `verify.md`
2. **TL;DR** (copy the id lists and the Branches line; they should be scannable in a few seconds)
3. Point at the Tasks overview in the file
4. One `Next` line, the first case that applies, as `crav1-docs/reference/run-ending.md` says. Do not list the other cases. Do not run it. Add the Uncommitted line when `verify.md` changed and is not committed. Read only the file for that case:
   - Read `references/next-fix.md` ("Fix the gaps") only when inner-loop ids remain (verify failed, claimed done unverified, or a wiring `G#`). A tick-pending Gap is not an inner-loop id.
   - Read `references/next-build.md` ("Build what is left") only when only not-implemented tasks remain.
   - Read `references/next-plan.md` ("Acceptance with no task") only when an acceptance line has no task and should stay.
   - Read `references/next-tighten.md` ("Acceptance that should not stay") only when an acceptance line should die.
   - Read `references/next-open-pr.md` ("Open a pull request") only when all are verified and a work branch is not merged. A branch with `(PR <n>)` names it: `/crav1-open-pr` to push to PR <n> and update its description or comment.
   - Read `references/next-done.md` ("Nothing needed") only when all are verified and every work branch is merged.

Read `references/next-walk.md` ("Walk owns the next line") only when `/crav1-build-walk` opened this skill. Do not print the case line then.

Do not start implementing in this turn unless they already named a `T#` to fix.

## Hard rules

- Do not invent new acceptance. Do not expand v0.
- Do not mark pass without a command, test name, or exercised UI path.
- Do not mark verified when tests skipped for a missing local dependency, unless the user chose skip. Then record those tests under **Skipped tests**.
- If the code is right and the spec is wrong, say so and send `/crav1-tighten-spec` — do not silently edit the spec.
- If this workspace has no application to run, report **untested** / **claimed done, unverified** with that reason; do not scaffold an app to get a green matrix.
- Do not bury task implementation status inside the acceptance table. Overview is task-first; details are acceptance-first.
- Do not run `/crav1-review-pr`. Do not run `/crav1-fix-bug`. A bug on work that is already shipping is that command. This skill does not start it.


## Choice words (1.69.0)

- Pipeline runs: `pipeline runs`. Read `references/promotion.md` ("Promotion") only when the invocation has that word. There are no `--flags`.
