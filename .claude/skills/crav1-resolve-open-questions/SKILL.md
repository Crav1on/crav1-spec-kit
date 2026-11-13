---
name: crav1-resolve-open-questions
description: >-
  Use after /crav1-tighten-spec when open questions remain in spec.md. Walks
  them one by one with keep-open or answer options and patches only that
  question after a pick. Also settles **Conflict:** lines. `detailed` shows more context. `apply <file>`
  reads back a filled-in playbook report and writes its answers after a
  confirm. Does not write application code.
disable-model-invocation: true
icon: book-open
color: yellow
---

# Resolve questions

You close **Open questions** and leftover **Assumptions** in one batch (1.70.0): every `Q#` with options and impact, then patch what was answered.

Do not re-run architecture findings unless they are already open questions.

## Choice words

Exact words, no `--flags`. `detailed`: each question shows the extended entry in [references/detailed.md](references/detailed.md); read that file only then. Without it, the list is short.

`apply` (1.110.0), as `apply <file>`: read back a playbook report whose `Answer:` and `Change:` lines were filled in, by the user or by others it was sent to. On that yes, a filled playbook is copied to `docs/playbooks/<topic>.md` (1.120.0). Follow [references/apply.md](references/apply.md); read that file only then.

**Do not patch until the user picks a letter for the current question** (or a batch of `Q#: letter` answers).

## Find the spec

Use the spec the user @-mentions. A branch, a pull request (`pr71`, `#71`), or words or `orders Q3` (one question) pick as `crav1-add-to-spec` `references/scope.md` says; several specs: ask which. Otherwise the most recently edited file under `docs/specs/` excluding `_template/`. If several, ask which slug. Expected `spec.md` headings: this skill’s `assets/spec.md`.

Read `spec.md` (`## Open questions`, `## Assumptions`, `## Constraints`, and `## Research findings` when that heading is there). Note `diagrams.md` and `adr/`.

## Build the question list (no edits)

Number `Q1`, `Q2`, … in document order, for display only (1.84.0): never write a `Q#` into a file. A `Q#: letter` answer maps to the question shown with that number, and the patch finds that question in `spec.md` by its words, as `crav1-add-to-spec` `references/merge-safe.md` says.

Include:

1. Every bullet under **Open questions** (an older numbered item counts too)
2. Assumptions still marked unresolved (A1, A2, …) if they are not already duplicated as an open question
3. Every `**Conflict:**` line in the spec, listed after the questions as `C1`, `C2`, … (1.111.0, no choice word). Follow [references/conflicts.md](references/conflicts.md); read that file only when there is one.

Skip empty placeholders. Do not invent new questions. If the list is empty, say so and point to Plan Mode (`Shift+Tab`) with `spec.md` attached — not to this skill.

## Walk one question at a time

### Index (every turn, short)

Remaining `Q#` titles only. Mark the current one.

### Current question (full)

For **only** the current `Q#`:

1. **Question** — quote the spec line. One sentence on what is undecided (product vs architecture). When the question has an `Answered:` line (see `crav1-add-to-spec` `references/open-questions.md`), quote that answer and its source, and offer the answer it states as the first answer option. Keep open is still offered. `Asked:` and `Pending:` lines are shown in `detailed`.
2. **Why it is still open** — what v0, tests, or an ADR cannot finish without this.
3. **Options** — 2–4 letters.

**Always** include **Keep open**. Always include at least two **substantive** answers (not only keep vs cut) unless the only honest answers are keep vs cut-from-v0.

Every option: **letter**, **name**, **what it means**, **impact** (v0/demo/tests, and which files/sections). When you write the Options for the current question, read [references/catalog.md](references/catalog.md). Do not open it when you are only printing the index. Tailor the answer letters to *this* question (e.g. “self-register” vs “admin-provisions”) — do not offer generic “apply notes.”

4. How to answer: `A` / `B` / … or prose (“Q2: passwords min 12 chars, no recovery in v0”). Batch on the card's free-text answer: `Q1 A, Q2 keep, Q4 C`.

Stop. Do not edit. Do not preview a full patched spec.

### After a choice

1. Patch **only** this question.
   - **Keep open:** leave the bullet. You may sharpen the wording if they asked; do not resolve it. When the slice has `tasks.md`, ask once which tasks it blocks, as options: each unticked `T#` (multi-select), **The whole slice**, or **None**. A pick of tasks writes one indented line under the question, `- Blocks: T2, T4`, replacing an earlier `Blocks:` line (see `crav1-add-to-spec` `references/open-questions.md`). **None** writes `- Blocks: none`, not nothing. Reason may follow. **The whole slice** writes `- Blocks: whole slice`, not nothing. `Blocks: none` blocks no current task. A missing `Blocks:` line is not this pick.
   - **Answer:** fold the decision into the right place (requirement/journey/acceptance, `## Constraints`, non-goals/later, or a new/updated ADR). When the question had an `Answered:` line, keep that quote and its source with the decision. **Remove** it from Open questions, with its `Asked:`, `Pending:`, and `Answered:` lines (or mark the assumption resolved). Never remove an `Approved:` line. An acceptance line you add is yes/no. Name unit, system, or browser only when that kind is already obvious from the answer. Otherwise leave the kind for plan. Do not invent a test list.
   - **Cut from v0:** move to non-goals/later; remove from Open questions.
2. Recap **Added / Removed / Still open** for this `Q#`.
3. If the answer makes a named diagram/ADR wrong, either they also chose `sync-here`, or the **next** item is that drift (do not silently skip).
4. When this question was waiting on a stale research point, read [references/stale-point.md](references/stale-point.md). Keep open does not re-check and does not open that file.
5. When the run named one question (`Q2`, `orders Q3`, or words matching one question), read [references/one-question.md](references/one-question.md) and stop after it (1.90.5). Do not open that file when the run is walking the whole list. Otherwise advance to the next unanswered `Q#`.

If none remain, print one of these and not both.

- New gaps appeared: `Next: /crav1-tighten-spec <slug>, because new gaps are not tightened yet.`
- No new gaps: `Next: /crav1-plan-from-spec <slug>, because the open questions are settled or kept open.`

**Batch (1.145.0).** Read **Batch of several items** in `crav1-docs/reference/question-cards.md` now. Print the findings table in this reply, then ask. Never write `table above` unless that table is in this reply. Never ask the card without the table. Hint: `Type your changes, e.g. Q1 A, Q3 keep`.

## Hard rules

- Prefer **cutting scope** over adding features.
- Keep-open is a valid finish for a question. Do not nag them into answering.
- Do not expand v0 to “solve” a question.
- Architecture answers go to Constraints or ADRs, not journeys.
- Do not write application code. Do not start Plan Mode until they are done or they ask.
- Do not patch “to be helpful” when they have not chosen.

## When the list is done

- Remaining items are only those they **kept open** (questions or Conflict lines), or the list is empty.
- Kept-open items stay as the spec’s honest unknowns. `Next: nothing needed now.`
- Empty list: `Next: /crav1-plan-from-spec <slug>, because the open questions are settled or kept open.`
- Do not list export or an architecture review in the ending.

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
