---
name: crav1-plan-from-spec
description: Turn an accepted spec into a file-level plan.md and independently testable tasks.md. When the spec is partial or In the code names paths, read that repo and branch and choose finish, add a verify test, or leave before any task is written. Use when spec.md exists and the user wants an implementation plan. Do not write application code.
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

Say which gate failed. Next command: `/crav1-tighten-spec` and/or `/crav1-resolve-questions`. Do not draft a fake plan.

**Ready with leftovers:** kept-open questions that do not block a first demo become **Risks** / “do not implement until resolved” — not silent answers.

If two architecture shapes still fit the spec (ADR still `proposed`, no constraint), ask **at most 3** multiple-choice questions, then wait. Do not pick a stack they never accepted.

## Built pieces (before any task)

Skip this section when the spec has no code behind it. No code behind it means match status `not in the code`, or the spec never claims existing code (no partial status, no status `done`, no `## In the code`, and it already has Problem, Goals, or Acceptance criteria).

When the spec is partial, or `## In the code` names paths, do this before any task is written.

Use the same repo and branch test as `/crav1-tighten-spec`. The repo is the Match repo line, a `Synced at` line, or another line in `spec.md` that names it. The branch is the branch on that line. Do not take them from the open checkout. Do not take a branch from `docs/system/repos.md` when the spec does not name it.

If the open checkout is a different repo or a different branch, stop and name the right ones. Do not read the open tree. Do not treat a stub as the code. A stub is a placeholder, for example a `.gitkeep` on `main`. If the paths on the named branch are only a stub, stop and say so.

If the spec names no branch, stop and ask which branch has the code. Do not assume `main`. Do not assume the open checkout. When that repo lists branches, the options are those branches. Do not pick one. After the user answers, that branch is the read. Do not write the branch onto the spec. That yes or no belongs to `/crav1-tighten-spec`. This skill leaves `spec.md` alone.

If the spec is too thin for that read (partial, status `done`, or `## In the code` without a repo or without paths), stop. Name `/crav1-code-into-specs` when a change already landed on an existing spec. Name `/crav1-match-to-specs` when the slice was never matched. Do not guess. Do not write a task.

Read the committed files on that branch. An uncommitted edit is not the fact. List every built piece. Do not drop one to keep the list short.

- A piece that already matches v0 is not a choice. Mark it already there. Give it no rebuild task.
- A piece the code only partly has, where v0 wants the rest, is a choice.
- A disagreement is its own line, before any task exists. Quote what the spec says and what the code does. The spec says one environment and the code enables another is one such line. It is not a match. Do not fold it into another piece.

Each choice says what it means and what it will do. These three are the only choices. Use the questions tool when it is available.

- **A. Finish the gap.** The code is partly there and v0 wants the rest. Write a task for that gap only. Do not rebuild what already matches.
- **B. Add a verify test.** The code stays as it is. Write a task for a test that checks what is already there. Do not change the feature.
- **C. Leave it.** No task. The plan gets one line saying this piece was left as committed. A later run does not turn it into work unless the user says so.

The user can answer one line or a batch (`auth A, export C`). An unanswered line stays open. Do not write a task until the choices that are open have an answer. A piece marked already there does not wait.

A later run reads `## Left as committed` when that heading is already in `plan.md`. It does not offer those pieces again unless the user says so in this turn.

On the trace, `already there` and `left as committed` are not missing tasks. A finish-the-gap task maps only the gap. An add-a-verify-test task maps a test of what is already there and does not change the feature.

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
- **Risks** — including kept-open questions
- **Out of scope** — spec non-goals; do not plan them
- **Left as committed** — only when the user left a piece. One line per piece: `Left as committed: <piece>.` Omit the heading when nothing was left.

Stay inside v0. File-level, not class-by-class essays. No new product behavior. A piece marked already there is named in the trace as `already there` and has no rebuild task. A left piece is the line above and has no task.

### tasks.md

Read this skill’s [references/checks.md](references/checks.md) before writing tasks (drop-in: `.claude/skills/crav1-plan-from-spec/references/checks.md`; plugin: this skill’s `references/checks.md`). Name the checks there. Do not write test code.

Independently testable slices. Bad: “add authentication.” Good: “POST `/register` rejects invalid email (verify: unit — empty email is rejected; unit — malformed email is rejected) (spec: invalid email).”

```markdown
# Tasks

- [ ] T1: <what> (verify: <kind> — <named check>) (spec: <REQ or acceptance>)
```

Rules:

- Each task maps to at least one spec acceptance line, REQ, or kept security check
- Every v0 acceptance line maps to at least one task (or an explicit “covered by T#”), or the trace says `already there` or `left as committed`
- Every kept security check (`docs/system/security.md` or a Security section on the spec) maps to a task, or the trace says which task already covers it
- Each verify note names the kind and the checks, per `references/checks.md`
- Order so each task can be verified before the next depends on it
- No task is “and also the rest of the app”

## After writing

Output only:

- Paths written
- Task count and any acceptance line with no task, not marked `already there`, and not `left as committed` (must be none, or the plan failed)
- Each built piece: already there, finish the gap, add a verify test, or left as committed
- The branch read, when **Built pieces** ran
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
- Do not write a rebuild task for a piece that already matches v0. Do not write a task for a piece the user left. A later run does not turn that piece into work unless the user says so.
- Finish the gap, add a verify test, and leave it are choices in this skill, before any task exists. A disagreement is its own line with those same three choices.
- Do not treat the host plan UI (Cursor Plan Mode or Claude Code plan mode) as a substitute for writing `plan.md` and `tasks.md` unless they said they only want the UI plan and not files. The skill still writes both files.
