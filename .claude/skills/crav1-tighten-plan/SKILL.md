---
name: crav1-tighten-plan
description: >-
  Use to walk plan.md and tasks.md issues one by one, including /crav1-review-
  plan P#s. Offers resolutions and patches only plan and tasks after a pick.
  Spec findings go to /crav1-tighten-spec. Does not edit spec.md or write
  code.
disable-model-invocation: true
icon: list
color: orange
---

# Tighten plan

You refine **`plan.md` and `tasks.md`** one issue at a time. `spec.md` is the source of truth. You do **not** edit the spec. You do **not** answer new product questions.

Do **not** offer a single menu (“fix the whole review”). That hides per-finding decisions.

**Do not patch until the user picks a resolution for the current issue** (or a batch of `P#: letter` answers). `suggest` is not a patch. `send-to-spec` is not a plan patch.


## Find the spec folder

Use the folder the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug. Expected headings: this skill’s `assets/plan.md` and `assets/tasks.md`.

Need `spec.md`, `plan.md`, and `tasks.md`. If plan/tasks are missing, stop (`/crav1-plan-from-spec`).

Read those three. Note `diagrams.md` / `adr/` / `export/openspec/` if present. Read `docs/system/security.md` and a Security section on the spec when those exist. Check rules: `crav1-plan-from-spec` [references/checks.md](../crav1-plan-from-spec/references/checks.md) (skill `crav1-plan-from-spec`, `references/checks.md`).

Also read the latest **crav1-plan-reviewer-agent** / `/crav1-review-plan` output in this chat. Those findings become issues. Do not collapse them into one “apply reviewer notes” action.

## Build the issue list (no edits)

Number issues `P1`, `P2`, … Each issue is **one** plan/task defect.

Sources, in order:

1. Numbered `P#`s already listed by the plan reviewer in this chat (preserve meaning; split if they bundled two problems). Keep their **plan** vs **spec** tag.
2. Fresh read of `plan.md` / `tasks.md` against `spec.md` (add only what the reviewer missed)

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
- Acceptance / REQ with no task (or task with no spec line)
- Files likely touched wrong, missing, or not `(proposed)` when there is no repo
- `## Linter` missing, or it never says whether this repo has a linter or checker for the code the tasks will touch
- Plan treats a kept-open spec question as decided

**Spec** tag: the plan is fine or cannot be honest until `spec.md` changes. Do not “fix” that by writing product behavior into the plan.

Skip nitpicks. Merge duplicates. Prefer fewer sharp issues.

If **no plan issues** remain (spec-tagged ones only, or none): say so. Next: spec-tagged → `/crav1-tighten-spec` / `/crav1-resolve-open-questions`; else **new chat**, `/crav1-build-tasks` with `plan.md`, `tasks.md`, and `spec.md` attached.

When `## Linter` says this repo has no linter or checker for the code the tasks will touch, do not name those Build commands. Stop before Build. The user decides to add the linter or to go on without one. Do not install one. When they already chose to go on without one in this turn, the Build next step applies, and the plan still says none. A plan that already says none is not a `P#` by itself.

## Walk one issue at a time

Walk **plan**-tagged `P#`s here. When the current item is **spec**-tagged: do not offer plan patches. Tell them `/crav1-tighten-spec` or `/crav1-resolve-open-questions` for that finding, mark it skipped-for-plan, advance.

### Index (every turn, short)

Remaining `P#` titles only. Mark the current one. Note plan vs spec.

### Current issue (full)

For **only** the current plan `P#`:

1. **Finding** — one or two sentences. Quote the plan/task line.
2. **Why it matters** — verify-ability, extra scope, or silent spec decision.
3. **Options** — 2–4 mutually exclusive **plan** resolutions, then **`suggest`**. Always keep `suggest`. Add `ask` / `keep` / `send-to-spec` when they fit.

Every option: **letter**, **name**, **what changes**, **impact** (which `T#`s / files). Never add a product feature as a “fix.”

4. How to answer: `A` / `B` / … or a batch: `P1 A, P3 C`. Unmentioned issues stay for later.

Stop. Do not edit. Do not preview a full patched plan.

If they already answered this `P#` with a **patch** letter in the same message, skip the menu and execute. If they asked for a suggestion, follow **When they pick `suggest`**.

### When they pick `suggest`

Do **not** patch. Stay on this `P#`. Name the letter you would pick and why (2–4 sentences). Re-offer the same patch letters, with the suggested one first and its label ending in ` (Recommended)` (letters do not change). At most **one** alternate suggestion, then they must pick a patch letter, `ask`, `keep`, or `send-to-spec`.

### After a choice

1. Patch **only** `plan.md` and/or `tasks.md` as that resolution allows. Never `spec.md`.
2. Recap **Added / Removed / Still open** for this `P#`.
3. If `export/openspec/design.md` or `tasks.md` exist, update them to **match** (same tasks, no extra scope) when the resolution changed tasks.
4. Advance to the next unanswered `P#`. If none remain, give the empty-queue next steps above.

**Batch (1.70.0).** Show every issue at once, each with its options and the recommended one first, and ask once: a single `yes` applies every recommendation; a batch such as `I1 B, I3 keep` overrides those issues; answering one issue at a time still works. Then patch, and give one recap for the run.

## Resolution catalog (per plan issue)

Build each `P#`'s options from [references/catalog.md](references/catalog.md) (`split-task`, `add-verify`, `add-cases`, `add-regression`, `add-integration`, `cover-security`, `drop-scope`, `fix-trace`, `retarget-files`, `name-linter`, `park-risk`, `send-to-spec`, `keep`, `suggest`, `ask`). Do **not** offer `apply-notes` for the whole review.

## Reviewed line

`plan.md` may have `Reviewed: <date>, P# open: <n>` under its title, written by `/crav1-review-plan`. After each patched `P#`, and when a `P#` is dropped as not an issue, lower `<n>` to the number of reviewer `P#`s still open. Keep the date. A `P#` the user leaves open stays counted. When there is no `Reviewed:` line, do not add one: only `/crav1-review-plan` records a review. This line is the only `plan.md` change this skill makes outside the picked patches.

## Hard rules

- Prefer **splitting or dropping** over adding product scope.
- Never edit `spec.md`, diagrams, or ADRs. Never write application code.
- Never resolve an Open question by encoding an answer in a `T#`.
- Do not start implement/complete-task in this chat unless they explicitly asked after plan issues are done. When `## Linter` says there is no linter, that ask is the choice to go on without one. Do not install a linter.
- Do not run `/crav1-review-pr`. Specify does not name the linter.
- Do not patch “to be helpful” when they have not chosen a **plan patch** (`suggest` and `send-to-spec` are not plan patches).
