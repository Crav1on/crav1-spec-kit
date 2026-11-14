# Tighten plan: issue shapes, empty queue, Reviewed line

Read by `/crav1-tighten-plan`. Moved word for word from `SKILL.md` in 1.159.0; the rules are unchanged. Since 1.159.0 `scripts/plan_check.py` computes the index, the counts, the batch card, the empty-queue Next line and the Reviewed line. These rules are what it computes.

## Typical plan shapes

Typical **plan** shapes:

- `T#` too big to verify alone (“add authentication”)
- Missing `verify:` kind, missing named checks, or missing `(spec: …)`
- An algorithm with one happy check and no corner cases
- Behavior that already works, with no regression check
- Two parts meet, with no integration test for that edge
- A kept security check with no task and no “covered by T#”
- Load or speed goal the spec did not state
- Smoke after deploy, chaos, or fuzzing for its own sake, or test code in the plan
- Task or approach step invents behavior the spec does not require
- Acceptance / REQ with no task (or task with no spec line). Compare by meaning first: a reworded line a task already covers is a `fix-trace`, not a new task.
- Files likely touched wrong, missing, or not `(proposed)` when there is no repo
- `## Linter` missing, or it never says whether this repo has a linter or checker for the code the tasks will touch
- Plan treats a kept-open spec question as decided

**Spec** tag: the plan is fine or cannot be honest until `spec.md` changes. Do not “fix” that by writing product behavior into the plan.

Skip nitpicks. Merge duplicates. Prefer fewer sharp issues.

## Ordering findings (1.159.0)

`plan_check.py order --root <spec-folder>` prints the dependency waves, any loop, any `after:` that names no task, which tasks are only inferred from file order, and each task line with no verify kind or no `(spec: …)` mark. Each printed problem is a candidate `P#`. Only the agent decides whether it is a real issue.

## Index

Remaining `P#` titles only. Mark the current one. Note plan vs spec. The `queue` command in `SKILL.md` prints it, with the counts first.

## Empty queue

If **no plan issues** remain, say so and print one `Next` line. Do not list the other cases.

- A spec-tagged finding is a spec defect: `Next: /crav1-tighten-spec, because that finding is a spec defect.`
- A spec-tagged finding is an open question: `Next: /crav1-resolve-open-questions, because that finding is an open question.`
- None remain, and the plan names a linter or they chose to go on without one: `Next: /crav1-build-tasks, because the plan issues are done.` A new chat, with `plan.md`, `tasks.md`, and `spec.md` attached.
- No linter, and they have not chosen to go on: `Next: nothing needed now.` Do not name build.

When `## Linter` says this repo has no linter or checker for the code the tasks will touch, do not name those Build commands. Stop before Build. The user decides to add the linter or to go on without one. Do not install one. When they already chose to go on without one in this turn, the Build next step applies, and the plan still says none. A plan that already says none is not a `P#` by itself.

## Reviewed line

`plan.md` may have `Reviewed: <date>, P# open: <n>` under its title, written by `/crav1-review-plan`. After each patched `P#`, and when a `P#` is dropped as not an issue, lower `<n>` to the number of reviewer `P#`s still open. Keep the date. A `P#` the user leaves open stays counted. When there is no `Reviewed:` line, do not add one: only `/crav1-review-plan` records a review. This line is the only `plan.md` change this skill makes outside the picked patches.

`plan_check.py reviewed --root <spec-folder> --open <n> --write` makes that change and prints one line. It never adds a line.

## Items file

`<file>` is JSON, one object per `P#`: `id`, `issue` (one line), `tag` (`plan` or `spec`), `status` (`open`, `patched`, `dropped`, `kept`, `skipped`), `kind` for a spec finding (`defect` or `question`), and for the batch `options` and `recommendation`. Mark the current one `"current": true`. Choosing those values is your judgement; the script does the rest. When Python cannot run, follow `references/issues.md` by hand with the same wording.

## When they pick `suggest`

Do **not** patch. Stay on this `P#`. Name the letter you would pick and why (2–4 sentences). Re-offer the same patch letters, with the suggested one first and its label ending in ` (Recommended)` (letters do not change). At most **one** alternate suggestion, then they must pick a patch letter, `ask`, `keep`, or `send-to-spec`.
