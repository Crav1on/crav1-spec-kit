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
4. **A gone, unmerged branch (1.64.0)** may be one issue. A listed work branch that is gone (no local branch, no `origin/<name>`) and is not merged by any test in skill `crav1-add-to-spec`, `references/branches.md` under **Gone, rewritten, shared** (its recorded SHA in the base, its `commits:` in the base as the same change, or a merged PR on GitHub or Azure DevOps). Offer `mark-dropped` (end its `Synced at` line with ` (dropped)`) and `to-open-question` (ask where the work went), plus `keep`, so it stops counting toward done. A branch that is gone but merged gets `merged, branch deleted` in the summary and no offer. A branch that still exists is never offered `(dropped)`. A rewritten branch is reported as `branch rewritten since last read` and is not an issue by itself.
5. A stale mark may be one issue. Read `## Research findings` and a note that section links to. Follow the readers section of skill `crav1-add-to-spec`, `references/research-stale.md`. Quote the mark. Name the path. Do not clear the mark. Do not rewrite the research note. When no mark is there, do not invent this issue.

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

Every option: a **plain name** (no letters, no catalog ids such as `tick-from-verify` on the card; 1.196.0), **what changes**, **impact** (who/v0/tests, and which files). Name the item in its own words in the question, put the evidence and the quoted spec line in a bullet above the card, and end with an `On yes:` line, as **Walk card rules** in `crav1-docs/reference/question-cards.md` says. Use the resolution catalog below. Drop resolutions that do not fit this issue (keep **`suggest`** only for wording findings). Never add a product feature as a “fix.”

Offer **2–4** mutually exclusive **patch** resolutions. Add `ask` / `keep` only when they fit. Offer **`suggest`** only for a wording finding (1.196.0); it does not count toward the 2–4. Still at most 4 options on the card.

**Whether, and sources (1.195.0).** When the finding asks *whether* something is so (a reviewer question such as "say whether DEV gets the new hostname") and no spec line, note, or dated source decides it, the recommended option is `ask` (an open question to the named owner) or `keep`, never a patch that makes the decision. When a patch would contradict a source line (a dated meeting line, a note, an ADR), the card quotes that line next to the patch, and that patch is never the recommended option. Such an item always lists `ask` or `keep`, also on the batch card.

4. How to answer: `A` / `B` / … for this issue, or a batch: `I1 A, I3 C, I4 D`. On the batch card that line is the free-text answer, not its own option. Unmentioned issues stay for later.

Stop. Do not edit. Do not preview a full patched spec.

If they already answered this `I#` in the same message with a **patch** letter (`make-testable`, `cut-from-v0`, …), skip the menu and execute. If they asked for a suggestion in the same message, follow **When they pick `suggest`**.

### When they pick `suggest`

Read `references/catalog.md` ("When they pick `suggest`") only when the user picks suggest.

### After a choice

1. Patch **only** what that resolution allows for **that issue**. (`suggest` never reaches here.)
2. Recap: **Added / Removed / Still open** for this issue.
3. If acceptance is still mushy on *this* issue and they did not choose `make-testable`, say so — do not silently rewrite.
4. Advance to the next unanswered issue (same format). If none remain, run the tight-enough checklist.

**Batch (1.145.0).** When there are 8 or fewer issues, one question card for the whole list. A whether-item with no deciding source (above) is recommended `ask` or `keep` on the card too. Follow **Batch of several items** in `crav1-docs/reference/question-cards.md` before this card. Print the findings table in this reply, then ask. The card names each item and its recommendation, for example `Tasks miss the 400 path (P4): add a test`. Never write `table above` unless that table is in this reply. Never ask the card without the table. `yes (Recommended)` applies every recommendation. The card's free-text answer carries the hint `Type your changes, e.g. Login page (I1) keep`. An item that answer does not mention keeps its recommendation. One issue at a time still works. Then patch, and give one recap for the run.

**Open questions (1.123.0).** An issue whose only work is an `Answered:` line, or that only repeats a question already under `## Open questions`, is not walked. One line, no menu: `Left for /crav1-resolve-open-questions: I3, I10.`

**Large batch (1.123.0).** More than 8 issues: read [references/pacing.md](references/pacing.md). Do not print the full list first.

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
- Never tick a spec acceptance box (`- [ ]` to `- [x]`) except through the `tick-from-verify` resolution, which quotes the passing `verify.md` row (1.195.0). Since 1.196.0 clear cases need no card: run `scripts/walk_progress.py tickable --root <spec-folder> --write` in `crav1-tighten-and-plan-ready-to-build` first. It ticks every item whose verify row passed on the base with its evidence named, adds `recheck item N (verify A#)` to the verify note of any later open task that touches the evidence files, and prints one line such as `Ticked 2 acceptance items from verify: item 1 (A1), item 4 (A4, recheck on T15).` Say that line. Only its `cards` (a failing or unmatched row) become issues with a card. This skill owns that tick; `/crav1-verify-build-against-spec` only reports that the box is still open.
- Notes saved for later on this spec (a note's `later_for` names the slug, 1.195.0) are listed once at the start as `Saved for later: <note>`; they are input to read, not issues by themselves. Run `notes_index.py later` with `--slug <slug>` in the `crav1-add-to-spec` skill folder (see `crav1-docs/reference/running-scripts.md`).

## When the spec is tight enough

Read `references/done.md` ("When the spec is tight enough") only when no issues are left.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
