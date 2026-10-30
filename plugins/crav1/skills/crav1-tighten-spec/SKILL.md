---
name: crav1-tighten-spec
description: >-
  Use when spec.md exists and needs tightening. Walks each issue (including
  architecture review notes) with explained choices and patches only that
  issue after a pick; reads the code first when the slice is partial. Does not
  write application code.
disable-model-invocation: true
icon: book-open
color: cyan
---

# Tighten spec

You refine a spec **one issue at a time**. The spec is the source of truth; chat is commentary.

Do **not** offer a single menu of workflow modes (“apply the whole review”, “make everything testable”, “full pass”). That hides per-finding decisions.

**Do not patch until the user picks a resolution for the current issue** (or sends a batch of `I#: letter` answers). `suggest` is not a patch.

## Find the spec

Use the spec the user @-mentions. Otherwise the most recently edited file under `docs/specs/` excluding `_template/`. If several, ask which slug. Expected `spec.md` headings: this skill’s `assets/spec.md`.

Read `spec.md` and note `diagrams.md`, `adr/`, `tasks.md`, `export/`.

Also read the latest **crav1-review-architecture-agent** / **crav1-spec-reviewer-agent** output in this chat if present. Those findings become issues. Do not collapse them into one “apply reviewer notes” action.

## Read committed code first

Read `references/code-first.md` ("Read committed code first") only when the spec's slice has committed code.

## Build the issue list (no edits)

Number issues `I1`, `I2`, … Each issue is **one** defect, ambiguity, or decision smuggled into the wrong layer.

Sources, in order:

1. Numbered issues already listed by a reviewer in this chat (preserve their meaning; split if they bundled two problems)
2. When the committed-code read happened, one issue per disagreement with that code. Quote both sides. Do not rewrite the spec to match the code.
3. Fresh read of `spec.md` / diagrams / ADRs (add only issues the reviewer missed). Wording issues come after the code read.
4. **A gone, unmerged branch (1.64.0)** may be one issue. A listed work branch that is gone (no local branch, no `origin/<name>`) and is not merged by any test in `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) under **Gone, rewritten, shared** (its recorded SHA in the base, its `commits:` in the base as the same change, or a merged PR on GitHub or Azure DevOps). Offer `mark-dropped` (end its `Synced at` line with ` (dropped)`) and `to-open-question` (ask where the work went), plus `keep`, so it stops counting toward done. A branch that is gone but merged gets `merged, branch deleted` in the summary and no offer. A branch that still exists is never offered `(dropped)`. A rewritten branch is reported as `branch rewritten since last read` and is not an issue by itself.
5. A stale mark may be one issue. Read `## Research findings` and a note that section links to. Follow the readers section of `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). Quote the mark. Name the path. Do not clear the mark. Do not rewrite the research note. When no mark is there, do not invent this issue.

Typical issue shapes (from this skill’s job):

- Acceptance / SHALL that is not yes/no
- A test list, or a check kind (unit, system, browser) the source did not already make obvious
- Missing happy, fail, or **empty** path
- Mechanism in a requirement (flag, relational DB, library) that should be constraint, ADR, or non-goal
- Open question that could be cut to a non-goal now
- Missing home for a tech gap (no ADR, no open question, no constraint)
- Diagram or ADR that contradicts `spec.md`

Skip nitpicks. Merge duplicates. Prefer fewer sharp issues over a laundry list.

If **no issues** and the tight-enough checklist passes, say so and offer only: stop and Plan Mode, or run `crav1-spec-reviewer-agent`.

## Walk one issue at a time

### Index (every turn, short)

List remaining issues as one line each: `I2` … `In` titles only. Mark the current one.

### Current issue (full)

For **only** the current `I#`:

1. **Finding** — one or two sentences. Quote the spec/ADR/diagram line.
2. **Why it matters** — testability, v0 size, or requirement-vs-decision blur.
3. **Options** — 2–4 mutually exclusive resolutions.

Every option: **letter**, **name**, **what changes**, **impact** (who/v0/tests, and which files). Use the resolution catalog below. Drop resolutions that do not fit this issue (always keep **`suggest`**). Never add a product feature as a “fix.”

Offer **2–4** mutually exclusive **patch** resolutions, then **`suggest`**. Add `ask` / `keep` only when they fit. `suggest` does not count toward the 2–4.

4. How to answer: `A` / `B` / … for this issue, or a batch: `I1 A, I3 C, I4 D`. Unmentioned issues stay for later.

Stop. Do not edit. Do not preview a full patched spec.

If they already answered this `I#` in the same message with a **patch** letter (`make-testable`, `cut-from-v0`, …), skip the menu and execute. If they asked for a suggestion in the same message, follow **When they pick `suggest`**.

### When they pick `suggest`

Read `references/catalog.md` ("When they pick `suggest`") only when the user picks suggest.

### After a choice

1. Patch **only** what that resolution allows for **that issue**. (`suggest` never reaches here.)
2. Recap: **Added / Removed / Still open** for this issue.
3. If acceptance is still mushy on *this* issue and they did not choose `make-testable`, say so — do not silently rewrite.
4. Advance to the next unanswered issue (same format). If none remain, run the tight-enough checklist.

**Batch (1.70.0).** Show every issue at once, each with its options and the recommended one first, and ask once: a single `yes` applies every recommendation; a batch such as `I1 B, I3 keep` overrides those issues; answering one issue at a time still works. Then patch, and give one recap for the run.

## Resolution catalog (per issue, not per turn)

Read `references/catalog.md` ("Resolution catalog (per issue, not per turn)") only when you write the options for an issue.

## A quoted note

Read `references/notes.md` ("A quoted note") only when a fix quotes a note.

## Hard rules

- Prefer **cutting scope** over adding features.
- Architecture/stack in the user’s answers goes to `## Constraints` or an ADR, not journeys.
- Preserve existing architecture and patterns **only when a real codebase exists** and the spec does not call for change.
- Never “fix” the idea by expanding v0.
- Do not leave `diagrams.md` / `adr/` / `export/` contradicting `spec.md` after a patch that affects them — either the chosen resolution includes `sync-here`, or the next issue is that drift.
- Do not start Plan Mode or write application code unless they explicitly ask after issues are done.
- Do not patch “to be helpful” when they have not chosen a **patch** resolution (`suggest` is not a patch).
- Do not silently rewrite the spec to match the code. Call the disagreement out.
- Do not add finish the gap, add a verify test, or leave it. Those choices belong to `/crav1-plan-from-spec`.

## When the spec is tight enough

Read `references/done.md` ("When the spec is tight enough") only when no issues are left.
