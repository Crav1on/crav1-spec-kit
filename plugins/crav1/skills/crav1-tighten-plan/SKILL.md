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

## Computed output (1.159.0)

The index, counts, dependency order, batch card, empty-queue `Next` line and Reviewed line come from one script, run as `crav1-docs/reference/running-scripts.md` says. Print its stdout as-is. Never add, drop, or rewrite a line, and never write a second `Next` line. The rules it computes are in [references/issues.md](references/issues.md).

- `<interpreter> -X utf8 scripts/plan_check.py order --root <spec-folder>`: the waves and any ordering or task-line problem.
- `<interpreter> -X utf8 scripts/plan_check.py queue --items <file> --root <spec-folder>`: the index and counts; with no plan `P#` open, the one empty-queue `Next` line. Flags: `--went-on-without-linter` (chosen this turn), `--uncommitted <n>`.
- `<interpreter> -X utf8 scripts/plan_check.py batch --items <file>`: the findings table and its `Card:` line.
- `<interpreter> -X utf8 scripts/plan_check.py reviewed --root <spec-folder> --open <n> --write`.

Its `<file>` fields are in `references/issues.md` ("Items file"). Choosing those values is your judgement; the script does the rest. When Python cannot run, follow `references/issues.md` by hand with the same wording.

## Find the spec folder

Use the folder the user @-mentions. Otherwise the most recently edited tree under `docs/specs/` excluding `_template/`. If several, ask which slug. Expected headings: this skill’s `assets/plan.md` and `assets/tasks.md`.

Need `spec.md`, `plan.md`, and `tasks.md`. If plan/tasks are missing, stop (`/crav1-plan-from-spec`).

Read those three. Note `diagrams.md` / `adr/` / `export/openspec/` if present. Read `docs/system/security.md` and a Security section on the spec when those exist. Check rules: `crav1-plan-from-spec` [references/checks.md](../crav1-plan-from-spec/references/checks.md) (skill `crav1-plan-from-spec`, `references/checks.md`).

Also read the latest **crav1-plan-reviewer-agent** / `/crav1-review-plan` output in this chat. Those findings become issues. Do not collapse them into one “apply reviewer notes” action.

## Build the issue list (no edits)

Number issues `P1`, `P2`, … Each issue is **one** plan/task defect.

Sources, in order:

1. Numbered `P#`s already listed by the plan reviewer in this chat (preserve meaning; split if they bundled two problems). Keep their **plan** vs **spec** tag.
2. Fresh read of `plan.md` / `tasks.md` against `spec.md` (add only what the reviewer missed), starting from what `order` printed. The typical plan shapes, the **spec** tag, and skip-nitpicks are in `references/issues.md`.

If **no plan issues** remain, print the `queue` output: it says so and prints one `Next` line.

## Walk one issue at a time

Walk **plan**-tagged `P#`s here. When the current item is **spec**-tagged: do not offer plan patches. Tell them `/crav1-tighten-spec` or `/crav1-resolve-open-questions` for that finding, mark it skipped-for-plan, advance.

### Index (every turn, short)

Print the `queue` output: remaining `P#` titles only, the current one marked, plan vs spec.

### Current issue (full)

For **only** the current plan `P#`:

1. **Finding** — one or two sentences. Quote the plan/task line.
2. **Why it matters** — verify-ability, extra scope, or silent spec decision.
3. **Options** — 2–4 mutually exclusive **plan** resolutions, then **`suggest`**. Always keep `suggest`. Add `ask` / `keep` / `send-to-spec` when they fit.

Every option: **letter**, **name**, **what changes**, **impact** (which `T#`s / files). Never add a product feature as a “fix.”

4. How to answer: `A` / `B` / … or a batch: `P1 A, P3 C`. On the batch card that line is the free-text answer, not its own option. Unmentioned issues stay for later. A batch card follows **Batch (1.145.0)** below. Do not ask it from this menu.

Stop. Do not edit. Do not preview a full patched plan.

If they already answered this `P#` with a **patch** letter in the same message, skip the menu and execute. If they asked for a suggestion, follow **When they pick `suggest`**.

### When they pick `suggest`

Do **not** patch. Stay on this `P#`. Follow `references/issues.md` ("When they pick `suggest`").

### After a choice

1. Patch **only** `plan.md` and/or `tasks.md` as that resolution allows. Never `spec.md`.
2. Recap **Added / Removed / Still open** for this `P#`.
3. If `export/openspec/design.md` or `tasks.md` exist, update them to **match** (same tasks, no extra scope) when the resolution changed tasks.
4. Run `reviewed` when the `Reviewed:` line applies (`references/issues.md`, "Reviewed line"). Advance to the next unanswered `P#`. If none remain, print the `queue` output.

**Batch (1.145.0).** Follow **Batch of several items** in `crav1-docs/reference/question-cards.md` before this card. Print the findings table in this reply, then ask: the `batch` command prints the table and the `Card:` line together. The card names each item and its recommendation, for example `P4 tasks miss the 400 path: A add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table. `yes (Recommended)` applies every recommendation. The card's free-text answer carries the hint `Type your changes, e.g. P1 A, P3 keep`. An item that answer does not mention keeps its recommendation. One issue at a time still works. Then patch, and give one recap for the run.

## Resolution catalog (per plan issue)

Build each `P#`'s options from [references/catalog.md](references/catalog.md) (`split-task`, `add-verify`, `add-cases`, `add-regression`, `add-integration`, `cover-security`, `drop-scope`, `fix-trace`, `retarget-files`, `name-linter`, `park-risk`, `send-to-spec`, `keep`, `suggest`, `ask`). Do **not** offer `apply-notes` for the whole review.

## Claimed tasks (1.151.0)

A task listed in `docs/specs/<slug>/claims.md` as `In progress:` is left unchanged: no renumber, reorder, rewrite, or removal. Other tasks may change. After writing `tasks.md`, run `<interpreter> -X utf8 scripts/claims.py preserve --before <old tasks.md> --after docs/specs/<slug>/tasks.md --root <spec-folder> --write`, as `crav1-docs/reference/running-scripts.md` says, and say once which claimed tasks were kept.

## Hard rules

- Prefer **splitting or dropping** over adding product scope.
- Never edit `spec.md`, diagrams, or ADRs. Never write application code.
- Never resolve an Open question by encoding an answer in a `T#`.
- Do not start implement/complete-task in this chat unless they explicitly asked after plan issues are done. When `## Linter` says there is no linter, that ask is the choice to go on without one. Do not install a linter.
- Do not run `/crav1-review-pr`. Specify does not name the linter.
- Do not patch “to be helpful” when they have not chosen a **plan patch** (`suggest` and `send-to-spec` are not plan patches).

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
