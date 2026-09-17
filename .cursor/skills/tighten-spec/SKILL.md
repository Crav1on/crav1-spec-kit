---
name: tighten-spec
description: Iterate an existing spec from critique, answers, or new constraints. Offer explained options first; do not patch until the user chooses. Use when a spec.md already exists and the user wants it sharper, smaller, or more testable. Do not write application code.
disable-model-invocation: true
icon: book-open
color: cyan
---

# Tighten spec

You refine a spec in place. The spec is the source of truth; chat is commentary.

**Do not patch files on the first response of a turn.** Find the spec, summarize, then offer options. Wait for a choice. Only then edit.

## Find the spec

Use the spec the user @-mentions. Otherwise the most recently edited file under `docs/specs/` excluding `_template/`. If several, ask which slug.

Read `spec.md` and note whether `diagrams.md`, `adr/`, `tasks.md`, or `export/` exist.

## Each turn

### 1. Brief (no edits)

- 2–4 bullets: what their latest message is asking for
- 2–4 bullets: what is weak in the spec *right now* (untestable acceptance, bloated v0, hunches in journeys, export/diagram drift)
- If the spec already meets the “tight enough” checklist, say so up front

### 2. Options (always, before any patch)

Present **only the options that apply this turn** (usually 3–6). Use the questions tool when available (multiple-choice). Every option needs: **name**, **what it does**, **what it will change on disk**, **when to pick it**.

Base the menu on this list. Drop options that do not apply (e.g. skip “sync artifacts” if there are no diagrams/ADRs/exports). Never invent extra product features as an option.

| Id | Name | What it does | Disk | Pick when |
| --- | --- | --- | --- | --- |
| `cut-scope` | Cut v0 | Move tempting extras to non-goals / later. Prefer this over adding. | Edits `spec.md` only (goals, non-goals, journeys, acceptance). | v0 cannot be demoed in one sitting, or they said “too big.” |
| `make-testable` | Make acceptance falsifiable | Rewrite mushy checks into yes/no lines a stranger could run. Does not add features. | Edits acceptance (and journeys if they are too vague to test). | Criteria read like “fast,” “intuitive,” or “handle errors.” |
| `apply-notes` | Apply this message | Fold their new answers, constraints, or corrections into the spec. | Edits `spec.md`. Architecture/stack goes under `## Constraints`, not journeys. | They gave concrete corrections (A3 is wrong, offline matters, not for teams). |
| `ask-first` | Ask, don’t patch | Ask at most 5 clarifying questions and list assumptions. No file edits. | None. | Their message is ambiguous, or patching would guess. |
| `sync-artifacts` | Sync diagrams / ADRs / exports | After spec intent is clear, update related files so they do not contradict `spec.md`. Or tell them to `/export-spec` if a full re-projection is cleaner. | May edit `diagrams.md`, `adr/`, `export/`. Never changes product intent. | Those files exist and drift, or they just accepted a spec patch. |
| `review-product` | Critique via spec-reviewer | Delegate to `spec-reviewer`. Independent read of testability and gaps. | None from this skill. | They want a second opinion before more edits. |
| `review-architecture` | Critique via architecture-reviewer | Delegate to `architecture-reviewer`. Hunches vs decisions, ADR/diagram gaps. | None from this skill. | Technical thoughts are smuggled into requirements, or ADRs look weak. |
| `accept-plan` | Accept and plan | Stop tightening. Spec is tight enough. | None. Tell them: new chat, Plan Mode (`Shift+Tab`), `@` the spec. | Checklist below is true, or they explicitly want to plan. |

You may combine **one** edit option with `sync-artifacts` as a single choice (“cut v0, then sync diagrams”) if drift would otherwise be guaranteed. Do not combine cut + apply + make-testable in one shot unless they asked for a full pass — that hides the decision.

If they already named an option (`cut-scope`, “just apply”, “don’t edit, ask”), skip the menu and do that.

### 3. After they choose (edits only now)

Execute the chosen option.

For edit options (`cut-scope`, `make-testable`, `apply-notes`, `sync-artifacts`):

1. Patch only what that option allows.
2. Recap **Added / Removed / Still open**.
3. Point at any acceptance line that is still not falsifiable. Do **not** silently rewrite those unless they chose `make-testable` or a full pass.
4. Re-offer a **short** next-step menu (2–4 options) if work remains. Stop if they chose `accept-plan` or a reviewer.

## Hard rules

- Prefer **cutting scope** over adding features.
- If they introduce architecture or stack, put it in a `## Constraints` section — do not let it replace user journeys.
- Preserve existing architecture and patterns **only when a real codebase exists** and the spec does not call for change. On a greenfield spark, there is nothing to preserve.
- Never “fix” the idea by expanding v0.
- If `diagrams.md`, `adr/`, or `export/` exist, do not leave them contradicting `spec.md`. Offer `sync-artifacts` or `/export-spec` instead of silently ignoring drift.
- Do not start Plan Mode or write code unless they explicitly ask or choose `accept-plan`.
- Do not patch “to be helpful” when they have not chosen.

## When the spec is tight enough

Say so when all of these are true:

- One primary user
- v0 vs later is explicit
- Non-goals are written
- Happy, fail, and empty paths exist
- Every acceptance line is a yes/no check
- Open questions are listed, not buried

Then the default option to highlight is `accept-plan`. Optionally include `review-product`.
