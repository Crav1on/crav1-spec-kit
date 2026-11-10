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

Write only:

```text
docs/specs/<slug>/plan.md
docs/specs/<slug>/tasks.md
```

If `export/openspec/design.md` or `export/openspec/tasks.md` already exist, update them to **match** these files (same tasks, no extra scope). Do not create a full OpenSpec tree unless they asked `/crav1-export-spec` Format: OpenSpec.

### plan.md

Use the template in this skill’s `assets/plan.md`. Fill:

- **Constraints** — from spec constraints + accepted ADRs only
- **Approach** — ordered steps for v0; reference diagrams
- **Files likely touched** — real paths if a repo exists; otherwise proposed paths consistent with the spec, marked `(proposed)`
- **Linter** — whether this repo has a linter or checker for the code those files will hold. See **Linter, before Build** in `references/checks.md`. Specify does not name the linter
- **Requirements trace** — table: acceptance / REQ id → task ids
- **Risks** — one entry per kept-open question, as **Blocks lines** in `references/write.md` says, and each stale research finding. One line per mark: the stale line, and the note path when there is one. Stale research does not block the plan. Do not clear the mark.
- **Out of scope** — spec non-goals; do not plan them
- **Left as committed** — only when the user left a piece; see `references/write.md` ("Left as committed").

Stay inside v0. File-level, not class-by-class essays. No new product behavior. A piece marked already there is named in the trace as `already there` and has no rebuild task. A left piece has no task.

### Host setup tasks (1.115.0)

A requirement that is a host setting with no file in the repo (a branch policy or required build, required reviewers, an environment approval, a variable group, a service connection) gets its own task marked `(host setup)`. Its verify is the script's `check` part reading the live setting, for example `infra/ado/develop-build-policy.sh check prints ok`. Pipeline YAML, templates and infrastructure as code stay ordinary code tasks. Read skill `crav1-host-setup`, `references/host-setup.md` for the split. A secret is a manual task: the plan names what to create and where, never a value.

### Blocks lines

The one exception to leaving `spec.md` alone: a `Blocks:` line under a kept-open question, `Blocks: T#` or `Blocks: none`. Read `references/write.md` ("Blocks lines") when any question stays open. List each `Blocks:` line in the recap.

### tasks.md

Read `references/write.md` ("tasks.md") and [references/checks.md](references/checks.md) before writing tasks: the line format, `(after: …)`, `(branch: …)`, and the mapping rules. Do not write test code.

## After writing

Output only:

- Paths written
- Task count and any acceptance line with no task, not marked `already there`, and not `left as committed` (must be none, or the plan failed)
- Each built piece: already there, finish the gap, add a verify test, or left as committed
- The branch read, when **Built pieces** ran
- Any verify note with no kind, and any kept security check with no task (must be none, or you failed)
- Kept-open questions parked as risks, one line each. The current-or-later batch is the only ask, and only when a leftover is unclear.
- Each stale research finding listed under Risks, or that none was marked stale
- These notes name the checks. `/crav1-verify-build-against-spec` is the gate that says they passed. Do not run it here.
- The linter line: the tool and command, or that this repo has none for the code these tasks will touch.
- One `Next` line, as `crav1-docs/reference/run-ending.md` says. Do not run it. Add the Uncommitted line when a file changed and is not committed. Do not name tighten-plan or build in this ending.
- This branch is `spec/<slug>`: `Next: /crav1-open-pr, because this specify-only branch is not on the default branch yet.` Do not implement here.
- Any other branch: `Next: /crav1-review-plan, because the plan is written and not reviewed.` When the plan says there is no linter, say build is not named until they add one or choose to go on without one. Do not install one.

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
