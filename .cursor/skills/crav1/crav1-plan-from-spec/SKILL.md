---
name: crav1-plan-from-spec
description: Turn an accepted spec into a file-level plan.md and independently testable tasks.md. Use when spec.md exists and the user wants an implementation plan. Do not write application code.
disable-model-invocation: true
icon: git-branch
color: green
---

# Plan from spec

You turn a spec into a **reviewable implementation plan and task list**. You do not implement. You do not expand v0. You do not reopen rejected ADRs or non-goals.

Read this skill’s `assets/plan.md` and `assets/tasks.md` for shape (same files as `docs/specs/_template/`). If a real codebase exists, search it before naming files.

## Find the spec

Use the spec the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug.

Read `spec.md`, plus `diagrams.md`, `adr/`, `export/` if present. Treat `spec.md` as source of truth. Exports and diagrams must not add behavior; if they contradict the spec, stop and tell them to `/crav1-tighten-spec` or `/crav1-export-spec`.

## Gate (no files yet)

**Not ready** — stop and send them back — if any of these is true:

- No primary user, no v0 vs later, or no non-goals
- Missing happy/fail/**empty** path
- Acceptance lines that are not yes/no
- Open questions that **block the demo** (auth model, source of truth, “what is v0”) with no keep-open-and-plan-around path

Say which gate failed. Next command: `/crav1-tighten-spec` and/or `/crav1-resolve-questions`. Do not draft a fake plan.

**Ready with leftovers:** kept-open questions that do not block a first demo become **Risks** / “do not implement until resolved” — not silent answers.

If two architecture shapes still fit the spec (ADR still `proposed`, no constraint), ask **at most 3** multiple-choice questions, then wait. Do not pick a stack they never accepted.

## Write (after the gate)

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
- **Risks** — including kept-open questions
- **Out of scope** — spec non-goals; do not plan them

Stay inside v0. File-level, not class-by-class essays. No new product behavior.

### tasks.md

Read this skill’s [references/checks.md](references/checks.md) before writing tasks (drop-in: `.cursor/skills/crav1/crav1-plan-from-spec/references/checks.md`; plugin: this skill’s `references/checks.md`). Name the checks there. Do not write test code.

Independently testable slices. Bad: “add authentication.” Good: “POST `/register` rejects invalid email (verify: unit — empty email is rejected; unit — malformed email is rejected) (spec: invalid email).”

```markdown
# Tasks

- [ ] T1: <what> (verify: <kind> — <named check>) (spec: <REQ or acceptance>)
```

Rules:

- Each task maps to at least one spec acceptance line, REQ, or kept security check
- Every v0 acceptance line maps to at least one task (or an explicit “covered by T#”)
- Every kept security check (`docs/system/security.md` or a Security section on the spec) maps to a task, or the trace says which task already covers it
- Each verify note names the kind and the checks, per `references/checks.md`
- Order so each task can be verified before the next depends on it
- No task is “and also the rest of the app”

## After writing

Output only:

- Paths written
- Task count and any acceptance line with no task (must be none, or you failed)
- Any verify note with no kind, and any kept security check with no task (must be none, or you failed)
- Kept-open questions parked as risks
- These notes name the checks. `/crav1-verify-spec` is the gate that says they passed. Do not run it here.
- The linter line: the tool and command, or that this repo has none for the code these tasks will touch.
- Next, when the plan names a linter: `/crav1-review-plan` (optional but useful), then `/crav1-tighten-plan` for plan `P#`s. Build is expected to leave that named check green.
- Next, when the plan says there is no linter: stop before Build. Say that. The user decides to add the linter or to go on without one. Do not install one. Do not name `/crav1-implement-task`, `/crav1-complete-task`, `/crav1-complete-tasks`, or `/crav1-complete-features` until they choose. `/crav1-review-plan` and `/crav1-tighten-plan` stay available. They are not Build. When they choose to go on without one, the Build next step applies, and the plan still says none.
- If this branch is `spec/<slug>` (specify-only): `/crav1-finalize-commit` (no push), then **they** open a PR when they want this spec on the default branch. Do **not** implement here. After it is on default: `/crav1-feature-branch` → `feat/<slug>`, then a **new chat** for `/crav1-implement-task` or `/crav1-complete-task`. That implement chat waits until the plan names a linter, or they chose to go on without one.
- If this branch is `feat/<slug>` (or they stayed on one branch), and the plan names a linter or they chose to go on without one: **new chat**, `/crav1-implement-task` (or `/crav1-complete-task`) with `plan.md`, `tasks.md`, and `spec.md` attached.

Do not start coding in this chat.

## Hard rules

- **Refuse application code** — no feature files, no refactors, no “quick scaffold.” If they ask to build, tell them to start a new chat with the plan attached.
- Prefer existing repo patterns when a codebase exists.
- Do not invent endpoints, entities, screens, or a performance goal the spec does not require.
- Do not write test code. Smoke after deploy, chaos, and fuzzing for its own sake stay out.
- Do not run `/crav1-security-review`. Map kept checks that are already written.
- A kept suggestion from `/crav1-suggest-tests-for-code` that is already an acceptance line maps to a task. A line under `## Dismissed test suggestions` is not a task. Do not run `/crav1-suggest-tests-for-code`.
- Do not run `/crav1-review-pr`. Specify does not name the linter. Do not install a linter.
- Do not name Build when `## Linter` says this repo has no linter or checker for the code these tasks will touch, until the user chooses to go on without one.
- Do not treat the host plan UI (Cursor Plan Mode or Claude Code plan mode) as a substitute for writing `plan.md` and `tasks.md` unless they said they only want the UI plan and not files. The skill still writes both files.
