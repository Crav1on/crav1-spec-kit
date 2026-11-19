# Meeting to specs: **The full note (1.61.0)**, **After each answer**

Part of `branches/meeting/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## The full note (1.61.0)

Every run writes **one note** holding the whole input, before the first item question, as this skill's `references/notes.md` says. There is no Note option; nothing is asked about the note.

- Run the imported-sources convention first when the input is imported and the source folder is not written yet (this skill's `references/sources.md`). The note holds the text after its redaction.
- Path: `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` by the **source date** (the meeting date or the mail's sent date). No date in the input: the import date, `source_date: none`, and say so.
- Front matter `kind` is `meeting`, `email`, or `chat`; `source` names the mail (subject, sender, sent date) or the meeting (date and title); `imported` is today.
- Each kept addition and each answer link names this note as `Full source:`. A matching parked spec gets nothing; its slug goes in `waiting_for`.
- Run `scripts/notes_index.py` after the note changes. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not hand-edit an index.

Do not commit.

## After each answer

Recap that one item: answer linked, kept as addition, kept as new feature, kept as bug, left, or dismissed. Name the spec when a handoff ran. Name the full note path. Name the next command when one was named. Do not run that command.

When the addition handoff asks apply or leave, or asks whether to mark research stale, or asks to draft a revisit request, that question is this turn. Do not ask the next meeting item in that same turn.

Then ask the next unanswered item.

When every item has an answer, stop. Repeat the full list with kept, saved for later, left, or dismissed on each line. Then the counts:

```text
Extracted: <n>
Answers linked: <n>
Possible answers shown: <n>
Asked marks: <n>
Kept as addition: <n>
Kept as new feature: <n>
Kept as bug: <n>
Saved for later: <n>
Left: <n>
Dismissed: <n>
Handoffs: docs/specs/<slug>/, or none
Note: docs/notes/YYYY-MM/<file>.md (source date, or no source date)
Named, not run: <commands>, or none
```

`Saved for later` counts the items saved with **Save for later** (each one a slug or `general` in the note's `later_for`). There is no Noted count: every input is noted, as `references/notes.md` in `crav1-add-to-spec` says (1.195.0).

Then the answer summary from the reference file: each answer linked, each possible answer left open, each asked mark and where its date came from, and each `/crav1-resolve-open-questions` named.

Then one ending, as `crav1-docs/reference/run-ending.md` says. The first matching case wins. Do not list resolve or the plan. Do not run the next step. Add the Uncommitted line when a file changed and is not committed. Do not commit the note.

Each ending is Run next first: the reason, then the label on its own line and the command alone in its code span. Never write a `Next:` line (1.193.0).

- The fact branch changed an existing spec whose open walk the edit reopened (`walk-progress.md` beside the spec records a step whose section changed, as `references/section-reopen.md` in `crav1-tighten-and-plan-ready-to-build` says): reason `The new information reopened the walk.`, label `Resume the spec walk:`, command `/crav1-tighten-and-plan-ready-to-build <slug>` (1.195.0).
- The fact branch changed an existing spec: reason `The new information is not tightened yet.`, label `Tighten the spec:`, command `/crav1-tighten-spec <slug>`.
- A kept new feature was the only handoff: reason `It fits no existing spec.`, label `Start the new feature:`, command the one starter that item named (spark, ideas, or bundle).
- A kept bug was the only handoff: reason `The item is a bug and no lane has started.`, label `Start the bug fix:`, command `/crav1-fix-bug`.
- None of those: `Run next: nothing needed now.`

**Several changed specs (1.195.0).** Every changed spec is named; none is dropped. The first changed spec, in list order, gets the Run next block above (a reopened walk wins over a plain tighten for that first place). Every other changed spec follows on one line under it, `Also changed, not tightened: <slug-b>, <slug-c>.`, and a reopened walk among them is named on its own line, `Also reopened, resume its walk: <slug>.` Each command still names one slug.

```text
Run next:
The new information is not tightened yet.

Tighten the spec:
`/crav1-tighten-spec orders-api`
```

Two changed specs, the first with a reopened walk:

```text
Run next:
The new information reopened the walk.

Resume the spec walk:
`/crav1-tighten-and-plan-ready-to-build orders-api`

Also changed, not tightened: orders-export.
```
