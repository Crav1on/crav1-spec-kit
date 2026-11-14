---
name: crav1-plan-from-spec
description: >-
  Use when spec.md is accepted and the user wants an implementation plan.
  Writes a file-level plan.md and independently testable tasks.md, reading the
  code first when the slice is partial. Names the linter check. Does not write
  application code.
disable-model-invocation: true
icon: git-branch
color: green
---

# Plan from spec

You turn a spec into a **reviewable implementation plan and task list**. You do not implement. You do not expand v0. You do not reopen rejected ADRs or non-goals.

Read this skill’s `assets/plan.md` and `assets/tasks.md` for shape (same files as `docs/specs/_template/`). When the spec is partial or `## In the code` names paths, read that committed code in **Built pieces** before naming files or writing a task. When the spec has no code behind it, search the open repo before naming files.

## Find the spec

Use the spec the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug.

Read `spec.md`, plus `diagrams.md`, `adr/`, `export/` if present. Treat `spec.md` as source of truth. Exports and diagrams must not add behavior; if they contradict the spec, stop and tell them to `/crav1-tighten-spec` or `/crav1-export-spec`.

## Gate (no files yet)

**Not ready** — stop and send them back — if any of these is true:

- No primary user, no v0 vs later, or no non-goals
- Missing happy/fail/**empty** path
- Acceptance lines that are not yes/no
- Open questions that **block the demo** (auth model, source of truth, “what is v0”) with no keep-open-and-plan-around path

Say which gate failed. Next command: `/crav1-tighten-spec` and/or `/crav1-resolve-open-questions`. Do not draft a fake plan.

**Ready with leftovers (1.87.0, 1.125.0):** each kept-open question that does not block a first demo becomes its own entry under **Risks** in `plan.md`. Do not ask whether to park it, keep it, or answer it, and do not answer it silently. Answering stays with `/crav1-resolve-open-questions`. The `Blocks:` line and the risk wording are in `references/write.md` ("Blocks lines"). When you cannot tell whether a leftover is current work or later, that section's one short batch is the ask.

Stale research does not fail this gate. A `Stale since` line under `## Research findings`, or a stale block on a note that section links to, is listed under Risks. Follow the readers section of skill `crav1-add-to-spec`, `references/research-stale.md`. Do not block the plan. Do not clear the mark. Do not treat the stale research as current.

If two architecture shapes still fit the spec (ADR still `proposed`, no constraint), ask **at most 3** multiple-choice questions, then wait. Do not pick a stack they never accepted.

## Built pieces (before any task)

Read `references/built-pieces.md` ("Built pieces (before any task)") only when any acceptance line may already be built (code exists for the slug).

## Write (after the gate)

When **Built pieces** left a choice unanswered, stop. Do not write files yet.

Write only `docs/specs/<slug>/plan.md` and `docs/specs/<slug>/tasks.md`.

If `export/openspec/design.md` or `export/openspec/tasks.md` already exist, update them to **match** these files (same tasks, no extra scope). Do not create a full OpenSpec tree unless they asked `/crav1-export-spec` Format: OpenSpec.

### plan.md

Use the template in this skill’s `assets/plan.md`. Fill each section as `references/write.md` ("plan.md") says: Constraints, Approach, Files likely touched, Linter (**Linter, before Build** in `references/checks.md`; Specify does not name the linter), the Trace table, Risks, Out of scope, and Left as committed.

Stay inside v0. File-level, not class-by-class essays. No new product behavior. A piece marked already there is named in the trace as `already there` and has no rebuild task. A left piece has no task.

### Host setup tasks (1.115.0)

A host setting with no repo file is its own `(host setup)` task. Read `references/write.md` ("Host setup tasks") and skill `crav1-host-setup`, `references/host-setup.md`.

### Blocks lines

The one exception to leaving `spec.md` alone: a `Blocks:` line under a kept-open question, `Blocks: T#` or `Blocks: none`, and an `## Approval needed` item from a constraint. Read `references/write.md` ("Blocks lines" and "Approval needed"). The recap lists each `Blocks:` line and each approval item.

### tasks.md

Read `references/write.md` ("tasks.md") and [references/checks.md](references/checks.md) before writing tasks: the line format, `(after: …)`, `(branch: …)`, and the mapping rules. Do not write test code. Then run `<interpreter> -X utf8 scripts/plan_check.py order --root <spec-folder>` and fix any loop or `after:` that names no task before the recap.

## Claimed tasks (1.151.0)

A task listed in `docs/specs/<slug>/claims.md` as `In progress:` is left unchanged: no renumber, reorder, rewrite, or removal. Other tasks may change. After writing `tasks.md`, run `<interpreter> -X utf8 scripts/claims.py preserve --before <old tasks.md> --after docs/specs/<slug>/tasks.md --root <spec-folder> --write`, as `crav1-docs/reference/running-scripts.md` says, and say once which claimed tasks were kept.

## After writing

Print the recap with one command, as `crav1-docs/reference/running-scripts.md` says, and show its stdout as-is. Never add, drop, or rewrite a line, and never write a second `Next` line:

`<interpreter> -X utf8 scripts/plan_check.py recap --root <spec-folder> --branch <current branch> --facts <file>`

It computes every line [references/recap.md](references/recap.md) lists, including the dependency waves and the one `Next` line that `crav1-docs/reference/run-ending.md` asks for (1.159.0). Add `--uncommitted <n>` when files changed and are not committed. `<file>` is JSON with what only you know: `built_pieces` (a list of `{piece, choice}`), `branch_read` when **Built pieces** ran, and `security_unmapped` (kept security checks with no task). A line it prints that must be none, and is not, means the plan failed: fix `plan.md` or `tasks.md` and run it again. When Python cannot run, follow that reference by hand.

Do not start coding in this chat.

## Parked and retired specs (1.60.0)

Read `references/parked.md` ("Parked and retired specs (1.60.0)") only when the spec is parked or retired.

## Hard rules

- **Refuse application code** — no feature files, no refactors, no “quick scaffold.” If they ask to build, tell them to start a new chat with the plan attached.
- Prefer existing repo patterns when a codebase exists.
- Do not invent endpoints, entities, screens, or a performance goal the spec does not require.
- Smoke after deploy, chaos, and fuzzing for its own sake stay out.
- Do not run `/crav1-review-security`. Map kept checks that are already written.
- A kept suggestion from `/crav1-suggest-tests-for-code` that is already an acceptance line maps to a task. A line under `## Dismissed test suggestions` is not a task. Do not run `/crav1-suggest-tests-for-code`.
- Do not run `/crav1-review-pr`. Specify does not name the linter.
- A later run does not turn an already-there or left piece into work unless the user says so.
- Finish the gap, add a verify test, and leave it are choices in this skill, before any task exists. A disagreement is its own line with those same three choices.
- Do not treat the host plan UI (Cursor Plan Mode or Claude Code plan mode) as a substitute for writing `plan.md` and `tasks.md` unless they said they only want the UI plan and not files. The skill still writes both files.
