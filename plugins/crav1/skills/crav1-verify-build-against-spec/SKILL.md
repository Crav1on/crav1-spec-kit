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

User @-mention, else the most recently edited tree under `docs/specs/` excluding `_template/`.

Read `spec.md` acceptance (and EARS/BDD export if present — spec.md still wins). Read `tasks.md` if it exists. Skim tests and the files `plan.md` said would be touched.

## Classify each task (before writing)

For every `T#` in `tasks.md`, in dependency order (`/crav1-tasks-ready-to-build` **Dependency order**, its `scripts/task_order.py` when Python runs), so a task is checked after the tasks it waits on. List tasks in that order in the Tasks overview and the TL;DR id lists, under the heading `Tasks — overview (dependency order)`.

A task downstream of an **Implemented, verify failed** task (it waits on it, directly or through other tasks) keeps its own status, and its Verify cell starts with `depends on T7 (failed)`. When it failed too, its gap names T7 as the first thing to fix. `task_order.py <tasks.md> --failed T7` lists them.

| Status | Meaning |
| --- | --- |
| **Implemented, verified** | Row is `[x]` **and** its verify evidence ran and passed |
| **Implemented, verify failed** | `[x]` or code exists for this `T#`, but verify ran and failed |
| **Not implemented** | Still `- [ ]` (or no code for this `T#`) |
| **Claimed done, unverified** | `[x]` but evidence could not be run (no command, no browser). Also a ticked task whose `(branch: X)` is not the checkout: **Claimed done, unverified (on X, not checked out)** |

## Branches (1.64.0)

When the spec has work branches (its `Synced at` lines, Match `Branch:` list and task `(branch: …)` parts, minus base branches and `(dropped)` entries), work out the Branches line as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says: per repo, merged into its into branch or not, own commits since the fork point, `merged, branch deleted`, `branch rewritten since last read`, `unknown (branch gone)`, `(also in <slug>)` for a branch other specs list too, and the age of each remote copy. Use refs on disk; never fetch, never check out. Host checks only for GitHub (`gh`) and Azure DevOps (`az`) when already signed in. Report only: never change `Status:` or any spec line because of it.

**Sub-branches and reverts (1.68.0).** As that file says under **Spec branch and sub-branches** and **Reverted**: sub-branches (entries with `(into <spec branch>)`) are left out of the Branches count and get `Sub-branches: <n> of <m> merged into <spec branch>.`, plus `left behind: <branch> (not in <spec branch>)` for one that never merged after the spec branch reached the base; done counts top-level branches only. A merged branch whose change was later undone on the base shows `<branch>: merged, reverted on <base> (<revert sha>)`. Both are report only and never block done. In verify.md they go with the Branches line in the TL;DR. "Demoable; they can ship / PR" needs every top-level branch merged, not every sub-branch.

**Promotion (1.69.0).** When the spec repo has `docs/environments/promotion.md`, add the `Promotion:` line after the Branches line, as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Promotion**: per repo, the furthest environment reached and each later one not yet reached, as `on the branch that deploys to <env> (<branch>)` or `not yet on the branch that deploys to <env> (<branch>)`, release patterns as `on release/<x> (deploys to <env>)`, tag lines as `in tag <tag> (deploys to <env>)` or `not yet tagged`, the chain at the end, `Unclear:` for an unknown word with no `(after …)`, and `<branch>: not back on <base>` for a release fix. Branch reach, never `deployed to`. When a pipeline-sourced line is behind it, end with **Also check the latest pipeline runs?** (**Check pipeline runs** / **No, keep the git answer**); the choice word `pipeline runs` runs the check without asking; headless without it gives the git answer plus `Pipeline runs not checked. Add the word: pipeline runs.` Azure DevOps only, read-only; `az has no login` keeps the git answer. Report only: done stays merged into the base. In verify.md the Promotion line goes in the TL;DR under the Branches line.

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
4. Map `tasks.md` rows: checked but failing verify → **Implemented, verify failed**; unchecked → **Not implemented**.

## Write `docs/specs/<slug>/verify.md`

Follow this skill’s `assets/verify.md` **section order**. Do not put the long acceptance table first.

1. **TL;DR** — counts + id lists, then the Branches line when the spec has work branches. Then one line: next command (`/crav1-fix-build-gaps` if failed/unverified/`G#` remain, else `/crav1-build-tasks` or ship).
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
4. Next:
   - Inner-loop (**verify failed**, **claimed done, unverified**, wiring **`G#`**) → `/crav1-fix-build-gaps` (omit Gap to walk them in order)
   - **Not implemented** → `/crav1-build-tasks T#`
   - acceptance with no task → `/crav1-plan-from-spec` or `/crav1-tighten-spec` if the line should die
   - all **Implemented, verified**, no missing acceptance, and every work branch merged → spec is demoable; they can ship / PR
   - all verified but some work branches not merged → `built and verified, not merged yet: <branches>`, next `/crav1-open-pr` or `/crav1-merge-pr`

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

- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
