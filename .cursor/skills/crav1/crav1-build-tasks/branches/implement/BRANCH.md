# Implement task

You implement **one** row from `tasks.md`. Then you run that row’s **verify** step. You do not take the rest of the backlog in the same turn.

## Find the work

Spec folder: user @-mention, else the most recently edited tree under `docs/specs/` excluding `_template/`.

Read `tasks.md`, `plan.md`, `spec.md`. Task row shape is this skill’s `assets/tasks.md`. Use diagrams/ADRs as constraints. Spec wins if they disagree.

**Which task:** the `T#` they named, else the first unchecked `- [ ]`. If all checked, say so and tell them to run `/crav1-verify-build-against-spec`.

If `tasks.md` is missing, stop. Next: `/crav1-plan-from-spec`.

**Branch:** before any code, follow `/crav1-create-feature-branch` (drop-in: `.cursor/skills/crav1/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`) **Build** prompt. When the task ends with `(branch: X)`, that prompt offers **X (Recommended)** first (1.64.0); on X already, go ahead. Implementation code is never written on a base branch (1.99.0): follow `crav1-create-feature-branch` `references/code-branch.md` (drop-in: `.cursor/skills/crav1/crav1-create-feature-branch/references/code-branch.md`; plugin: sibling `skills/crav1-create-feature-branch/references/code-branch.md`); on a base there is no Stay, and a task `(branch: X)` naming a base is blocked. A dirty tree still means no checkout of an existing branch. If you are on `spec/<slug>`, stop (no code) and follow that skill’s **Build on a spec-only branch**.

## Gate

Stop (no code) if:

- This `T#` depends on an open question that was parked as a risk and is still unanswered
- The task would implement a spec **non-goal**
- This workspace is only the SDD playbook (no application to change) **and** they did not explicitly ask to scaffold an app here

If two file layouts still fit, follow `plan.md` “files likely touched.” Do not invent a new architecture.

## Do the task

1. Restate `T#` in one sentence (what / verify / spec id). Stop if they object.
2. Prefer **test first** when the verify line names a check: write those named checks, then the minimum code to pass. Do not add a different list.
3. Change only files needed for this `T#`. Match existing patterns when a codebase exists.
4. If that verify is **live** (HTTP/UI against a running host), follow `crav1-verify-build-against-spec` [references/live-host.md](../../../crav1-verify-build-against-spec/references/live-host.md) (drop-in: `.cursor/skills/crav1/crav1-verify-build-against-spec/references/live-host.md`; plugin: sibling `skills/crav1-verify-build-against-spec/references/live-host.md`) **before** the evidence. Before any test command, run the local dependency preflight in `crav1-verify-build-against-spec` [references/test-dependencies.md](../../../crav1-verify-build-against-spec/references/test-dependencies.md) (drop-in: `.cursor/skills/crav1/crav1-verify-build-against-spec/references/test-dependencies.md`; plugin: sibling `skills/crav1-verify-build-against-spec/references/test-dependencies.md`). Then run the **verify** from the task line (command, test name, or a real UI path). If verify is a UI path and a browser is available, exercise it. If you cannot run it, say what you could not run — do not check the box.
5. Tests skipped for a missing local dependency are not a pass. Do not check the box unless the user chose skip for that dependency; put the dependency at the top of the recap as a blocker.
6. If verify **passes**, mark that row `[x]` in `tasks.md` (and OpenSpec `export/openspec/tasks.md` if it exists and lists the same id).
7. If verify **fails**, leave `[ ]`. Recap what failed. Do not silently start `T+1`.

## After one task

Output only:

- `T#` done or blocked
- Files changed
- Verify command and result
- Next: the one task branch of `/crav1-build-tasks` (this `T#` through verify/fix/commits), the range or all branch of `/crav1-build-tasks` (a range or all unchecked), the implement step of `/crav1-build-tasks` (next unchecked only), the message only branch of `/crav1-finalize-commit` / `/crav1-finalize-commit`, or `/crav1-verify-build-against-spec`

Do not keep going through the list unless they wrote `T2 and T3` or “continue until blocked.”

## Hard rules

- One task per turn by default.
- Do not expand v0 or “while we’re here” refactors.
- Do not edit `spec.md` to match the code. If the spec is wrong, stop and tell them `/crav1-tighten-spec`.
- Prefer fixing the task over adding features.
- When `plan.md` names a linter or checker, leave that check green. Do not install a linter. When `## Linter` says this repo has none, and the user has not chosen to go on without one, stop. Do not write code.
- Do not ask whether to run `/crav1-refresh-system-notes`.
