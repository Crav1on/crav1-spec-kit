# Implement task

You implement **one** row from `tasks.md`. Then you run that row’s **verify** step. You do not take the rest of the backlog in the same turn.

## Find the work

Spec folder: the user's @-mention, or the one folder `<interpreter> -X utf8 <skill crav1-tasks-ready-to-build>/scripts/resolve_spec.py "<query>" --root docs/specs` prints (`crav1-docs/reference/running-scripts.md`). Several matches: list them and stop. Do not pick the most recently edited tree.

Read `tasks.md`, `plan.md`, `spec.md`. Task row shape is this skill’s `assets/tasks.md`. Use diagrams/ADRs as constraints. Spec wins if they disagree.

**Which task:** the `T#` they named, else the first unchecked `- [ ]`. If all checked, say so and tell them to run `/crav1-verify-build-against-spec`.

If `tasks.md` is missing, stop. Next: `/crav1-plan-from-spec`.

**Branch:** before any code, follow `/crav1-create-feature-branch` (skill `crav1-create-feature-branch`, `references/task-branch.md`) **Build** prompt. Option 1 is the first line of `scripts/build_map.py docs/specs/<slug> --recommend T#` (skill `crav1-tasks-ready-to-build`); on that branch already, go ahead. Implementation code is never written on a base branch (1.99.0): follow skill `crav1-create-feature-branch`, `references/code-branch.md`; on a base there is no Stay, and a recommended name that is a base is blocked. A dirty tree still means no checkout of an existing branch. If you are on `spec/<slug>`, stop (no code) and follow that skill’s **Build on a spec-only branch**.

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
4. If that verify is **live** (HTTP/UI against a running host), follow `crav1-verify-build-against-spec` [references/live-host.md](../../../crav1-verify-build-against-spec/references/live-host.md) (skill `crav1-verify-build-against-spec`, `references/live-host.md`) **before** the evidence. Before any test command, run the local dependency preflight in `crav1-verify-build-against-spec` [references/test-dependencies.md](../../../crav1-verify-build-against-spec/references/test-dependencies.md) (skill `crav1-verify-build-against-spec`, `references/test-dependencies.md`). Then run the **verify** from the task line (command, test name, or a real UI path). If verify is a UI path and a browser is available, exercise it. If you cannot run it, say what you could not run — do not check the box.
5. Tests skipped for a missing local dependency are not a pass. Do not check the box unless the user chose skip for that dependency; put the dependency at the top of the recap as a blocker.
6. If verify **passes**, mark that row `[x]` in `tasks.md` (and OpenSpec `export/openspec/tasks.md` if it exists and lists the same id).
7. If verify **fails**, leave `[ ]`. Recap what failed. Do not silently start `T+1`.

### Host setup tasks (1.115.0)

A task marked `(host setup)` follows skill `crav1-host-setup`, `references/host-setup.md`: write the checked-in script and the manual steps from its comments, show the commands, their scope and the steps, and run `apply` only after the user's explicit yes, then `check`. A named person's yes is on record when it was said in this chat, or an `Answered:` line names it, or a matching `Approved:` line exists (same person, and the item's `Holds:` includes this task). That line does not run `apply`. The user's own yes in this run is still required, and the task stays `[ ]` until `check` prints `ok`. A yes that is not on record is not a blocker. Inside a worker, return `STATUS: needs_yes` from `references/run.md`, leave the box `[ ]`, and do not apply. When that yes is on record and the assistant's permission check refuses the live command, return `permission_refused` as skill `crav1-build-tasks`, `references/permission-block.md` says. Do not say the yes is missing, and do not work around the check. Do not edit `spec.md` and do not write `Approved:`. The same status is used for any other approval gate that needs a named person's yes. Who is the person the task, the question, or the Approval needed item names, or `not named yet`. Tick the box only when `check` prints `ok` for every setting. A worker with no person to answer never applies.

## After one task

Output only:

- `T#` done or blocked
- Files changed
- Verify command and result
- One `Next` line, the first case that applies. Do not list the others. Add the Uncommitted line when files changed and are not committed.
- `tasks.md` is missing: `Next: /crav1-plan-from-spec, because there is no task list.`
- This task is not through verify: `Next: /crav1-build-tasks <T#>, because verify is still open.`
- They named a range: `Next: /crav1-build-tasks` for that range, because that is the batch they named.
- This turn's tasks are done: `Next: /crav1-verify-build-against-spec, because this turn's tasks are done.`

Do not keep going through the list unless they wrote `T2 and T3` or “continue until blocked.”

## Hard rules

- One task per turn by default.
- Do not expand v0 or “while we’re here” refactors.
- Do not edit `spec.md` to match the code. If the spec is wrong, stop and tell them `/crav1-tighten-spec`.
- Prefer fixing the task over adding features.
- When `plan.md` names a linter or checker, leave that check green. Do not install a linter. When `## Linter` says this repo has none, and the user has not chosen to go on without one, stop. Do not write code.
- Do not ask whether to run `/crav1-refresh-system-notes`.
