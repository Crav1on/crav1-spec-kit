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

Every option: **letter**, **name**, **what it means**, **impact** (v0/demo/tests, and which files/sections). Use the catalog below. Tailor the answer letters to *this* question (e.g. “self-register” vs “admin-provisions”) — do not offer generic “apply notes.”

4. How to answer: `A` / `B` / … or prose (“Q2: passwords min 12 chars, no recovery in v0”). Batch on the card's free-text answer: `Q1 A, Q2 keep, Q4 C`.

Stop. Do not edit. Do not preview a full patched spec.

### After a choice

Read `references/after-choice.md` ("After a choice") only when the user has picked a letter for the current question, or a batch of `Q#: letter` answers. Do not patch before that. **None** writes `- Blocks: none`. **The whole slice** writes `- Blocks: whole slice`. Never remove an `Approved:` line.

Read `references/stale-point.md` ("Stale research point") only when this question was waiting on a stale research point.

Read `references/one-question.md` ("One question") only when the run named one question (`Q2`, `orders Q3`, or words matching one question).

Read `references/list-done.md` ("When the list is done") only when no questions or Conflict lines remain to walk.

**Batch (1.145.0).** Read **Batch of several items** in `crav1-docs/reference/question-cards.md` only when one card applies a recommendation to several questions. Print the findings table in this reply, then ask. Never write `table above` unless that table is in this reply. Never ask the card without the table. Hint: `Type your changes, e.g. Q1 A, Q3 keep`.

## Resolution catalog (per question)

| Id | Name | What it does | Typical impact |
| --- | --- | --- | --- |
| `keep-open` | Keep open | Leave this question unanswered. No product decision. | Still blocks a fully closed spec. Disk: none, unless they asked to rephrase. **Always offer this.** |
| `answer-A` … | Answer: \<concrete choice\> | Commit one of the real alternatives you listed. | `spec.md` gains a SHALL, constraint, or non-goal; this `Q#` leaves the open list. |
| `answer-custom` | Answer in my words | Use their prose as the decision. Put it in the correct section; do not dump the paragraph into Open questions. | Same as a concrete answer. Offer when choices might not fit. |
| `cut-from-v0` | Cut from v0 | Not deciding how — deciding **not in v0**. | Smaller demo; question removed; lives under non-goals/later. |
| `to-constraint` | Record as constraint | The answer is an accepted tech/limit, not a user journey. | `## Constraints`; not a REQ SHALL about libraries/tables. |
| `to-adr` | Decide via ADR | Real alternatives remain worth recording. Write/update `adr/NNNN`, status `proposed` or `accepted` as they said. | Requirements stay behavioral; question removed once the ADR captures the choice (or stays open if they only drafted the ADR as proposed **and** asked to keep the question — rare; default is remove). |
| `ask` | Narrow first | Ask at most 3 multiple-choice questions **about this Q#**. No file edits. | Retry this `Q#` next turn. Use when your answer options would be a guess. |
| `sync-here` | Sync this artifact | Update the diagram/ADR this answer invalidates. | Only with an answer, not with keep-open. |

Do **not** offer a turn-level “answer all with assumptions.” Guessing is `ask` or `keep-open`.

## Hard rules

- Prefer **cutting scope** over adding features.
- Keep-open is a valid finish for a question. Do not nag them into answering.
- Do not expand v0 to “solve” a question.
- Architecture answers go to Constraints or ADRs, not journeys.
- Do not write application code. Do not start Plan Mode until they are done or they ask.
- Do not patch “to be helpful” when they have not chosen.
- Never remove an `Approved:` line.

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says. The ending lines for an empty list are in `references/list-done.md`, read only when no questions or Conflict lines remain.
