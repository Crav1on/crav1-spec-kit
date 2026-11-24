# Tighten plan: issue shapes, empty queue, Reviewed line

Read by `$crav1-tighten-plan`. Moved word for word from `SKILL.md` in 1.159.0; the rules are unchanged. Since 1.159.0 `scripts/plan_check.py --vendor codex` computes the index, the counts, the batch card, the empty-queue Next line and the Reviewed line. These rules are what it computes.

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

`plan_check.py order --root <spec-folder> --vendor codex` prints the dependency waves, any loop, any `after:` that names no task, which tasks are only inferred from file order, and each task line with no verify kind or no `(spec: …)` mark. A `Branch loop:` line names branches that wait for each other, with the fixes the ready check offers (1.161.0). It is a `P#` with the `fix-loop` option and its recommended fix, applied on the batch yes like a `fix-trace`. A line that says `after PR 87 merges` and has no `(after: PR 87)` is a candidate `P#` (1.201.1). On yes, `<interpreter> -X utf8 scripts/plan_check.py after-pr --root <spec-folder> --yes --vendor codex` writes that mark on the line. Never ask the user to edit `tasks.md` by hand. Each printed problem is a candidate `P#`. Only the agent decides whether it is a real issue.

## Index

Remaining `P#` titles only. Mark the current one. Note plan vs spec. The `queue` command in `SKILL.md` prints it, with the counts first.

## Empty queue

If **no plan issues** remain, say so and print one Run next entry, its label on its own line above the command. Do not list the other cases.

- An open spec-tagged finding is a spec defect: Run next, "Fix the spec finding, which is a spec defect:" above `` `$crav1-tighten-spec <slug>` ``. A spec finding already patched, dropped or kept is settled and sends nobody back.
- An open spec-tagged finding is an open question: Run next, "Resolve the spec finding, which is an open question:" above `` `$crav1-resolve-open-questions <slug>` ``.
- None remain, and the plan names a linter or they chose to go on without one: Run next, "Check what can be built, since the plan issues are done:" above `` `$crav1-tasks-ready-to-build <slug>` `` (1.180.0: never `$crav1-build-tasks`; the ready check knows about reopened steps and held tasks). With uncommitted files, "Commit the <n> changed spec files:" above `` `$crav1-finalize-commit` `` comes first, inside Run next.
- No linter, and they have not chosen to go on: "Nothing needed now." Do not name build.

When `## Linter` says this repo has no linter or checker for the code the tasks will touch, do not name those Build commands. Stop before Build. The user decides to add the linter or to go on without one. Do not install one. When they already chose to go on without one in this turn, the Build next step applies, and the plan still says none. A plan that already says none is not a `P#` by itself.

## Reviewed line

`plan.md` may have `Reviewed: <date>, P# open: <n>` under its title, written by `$crav1-review-plan`. After each patched `P#`, and when a `P#` is dropped as not an issue, the script lowers `<n>` to the open plan `P#`s still in the items file. Keep the date. A `P#` the user leaves open stays in that file, so it stays counted. When there is no `Reviewed:` line, do not add one: only `$crav1-review-plan` records a review. This line is the only `plan.md` change this skill makes outside the picked patches.

`plan_check.py reviewed --root <spec-folder> --items <file> --write --vendor codex` makes that change and prints one line. The `open` count is the script's. Do not pass a number you counted. It does not add a line. The reviewer's first count, before any items file exists, is `plan_check.py open-count --review <file> --vendor codex`, and that `open` value is what `$crav1-review-plan` writes.

## Items file

`<file>` is JSON, one object per `P#`: `id`, `issue` (one line), `tag` (`plan` or `spec`), `status` (`open`, `patched`, `dropped`, `kept`, `skipped`), `kind` for a spec finding (`defect` or `question`), and for the batch `options` and `recommendation`. Mark the current one `"current": true`. Choosing those values is your judgement; the script does the rest. When Python cannot run, follow `references/issues.md` by hand with the same wording.

## When they pick `suggest`

Do **not** patch. Stay on this `P#`. Name the letter you would pick and why (2–4 sentences). Re-offer the same patch letters, with the suggested one first and its label ending in ` (Recommended)` (letters do not change). At most **one** alternate suggestion, then they must pick a patch letter, `ask`, `keep`, or `send-to-spec`.

## Batch size

1.195.0. A batch card holds at most 8 findings; with more, the `batch` command prints the first 8 and names the rest for the next card, paced as `crav1-tighten-spec/references/pacing.md` does. A finding whose fix adds, removes or reorders tasks (a new `T#`, a dropped task, a moved dependency) sets `changes_tasks` in the items file and never goes in a yes-to-all card; it gets its own card, one at a time.

## Prod verify (1.196.0)

Verify checks run on DEV or TEST. On prod a verify note may only read: health, version, config, or that a resource exists. A check that writes to prod (posts a message, runs a job, loads data) is its own task, marked `prod-write` in its verify note, with `owner: <person>`, the user's yes before it runs, and a line under `## Risks` in plan.md naming its T#. Run `scripts/plan_check.py lint --root <spec-folder> --vendor codex` (see `crav1-docs/reference/running-scripts.md`); it flags any other prod verify and a prod-write task missing its owner or Risks line.

Before the review findings are walked, run `lint`. Each `Prod verify:` line becomes a finding whose recommended fix moves the check to DEV/TEST and keeps only a read-only prod check; moving a prod write into its own task changes tasks, so it gets its own card.

**Per item and target (1.197.0).** The lint reads each `;` item of a verify note and flags it only when its target is prod (on prod, the PROD stage, a `-prod` resource, or a note whose environment is prod with no DEV or TEST named) and it writes. File names such as `main.prod.bicepparam`, `PROD-like` settings, `unit`, `contract` and local compile items (build, build-params, lint, what-if) are never flagged. A `(manual, prod` task whose own text drops, deletes or changes data needs `owner:` and a Risks line too. Mark the release it waits for with `(after-release: main)`; the ready check holds such a task as Waiting and never offers it as the first task. A lint line you judged false is dropped silently, never carried into the batch.

## Housekeeping with no card (1.196.0)

Housekeeping fixes are applied with no card: Trace rows for cited constraints, missing marks, merged-state wording ("until PR 71 merges" after it merged), Risks that name merged pull requests or finished claims, a stale Linter line, and the build-map refresh. Set `"housekeeping": true` on those rows in the items file; `batch` leaves them off the card and prints one line, `Applying with no card (housekeeping): P7 Trace row for the retry constraint; P14 missing mark.` Say that line, then apply them. For the Reviewed line, run `scripts/plan_check.py reviewed --root <spec-folder> --items <items file> --write --vendor codex`: housekeeping rows never count as open (1.197.0). Cards are only for intent changes: adding, removing or reordering tasks, changing a verify check, a new risk or constraint, and anything that touches prod.

## Card labels (1.196.0)

Cards follow **Walk card rules** in `crav1-docs/reference/question-cards.md`: plain option names (the `batch` command maps catalog ids such as `park-risk` or `add-regression` to words), one background bullet per item above a batch card, a short question and an `On yes:` line. A single card names the task in its own words and quotes the evidence in a bullet above it. `suggest` is offered only for a wording finding. Typed answers may still use the ids.
