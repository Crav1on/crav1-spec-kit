# Meeting to specs: **The full note (1.61.0)**, **After each answer**

Part of `branches/meeting/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## The full note (1.61.0)

Every run writes **one note** holding the whole input, before the first item question, as this skill's `references/notes.md` says. There is no Note option; nothing is asked about the note.

- Run the imported-sources convention first when the input is imported and the source folder is not written yet (this skill's `references/sources.md`). The note holds the text after its redaction.
- Path: `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` by the **source date** (the meeting date or the mail's sent date). No date in the input: the import date, `source_date: none`, and say so.
- Front matter `kind` is `meeting`, `email`, or `chat`; `source` names the mail (subject, sender, sent date) or the meeting (date and title); `imported` is today.
- Each kept addition and each answer link names this note as `Full source:`. A matching parked spec gets nothing; its slug goes in `waiting_for`.
- Run `scripts/notes_index.py` after the note changes. Do not hand-edit an index.

Do not commit.

## After each answer

Recap that one item: answer linked, kept as addition, kept as new feature, kept as bug, left, or dismissed. Name the spec when a handoff ran. Name the full note path. Name the next command when one was named. Do not run that command.

When the addition handoff asks apply or leave, or asks whether to mark research stale, or asks to draft a revisit request, that question is this turn. Do not ask the next meeting item in that same turn.

Then ask the next unanswered item.

When every item has an answer, stop. Repeat the full list with kept, left, or dismissed on each line. Then the counts:

```text
Extracted: <n>
Answers linked: <n>
Possible answers shown: <n>
Asked marks: <n>
Kept as addition: <n>
Kept as new feature: <n>
Kept as bug: <n>
Noted: <n>
Left: <n>
Dismissed: <n>
Handoffs: docs/specs/<slug>/, or none
Note: docs/notes/YYYY-MM/<file>.md (source date, or no source date)
Named, not run: <commands>, or none
```

Then the answer summary from the reference file: each answer linked, each possible answer left open, each asked mark and where its date came from, and each `/crav1-resolve-open-questions` named.

When the fact branch of `/crav1-add-to-spec` changed an existing spec, name the next steps from the **New information on an existing slice** route (`docs/reference/workflow.md#new-info`) for that slug: `/crav1-tighten-spec` first, then `/crav1-resolve-open-questions`, then `/crav1-plan-from-spec` when the slice has `plan.md` or `tasks.md`. A named `/crav1-resolve-open-questions` comes after `/crav1-tighten-spec`, never before it. For the full order, name `/crav1-help next`. Do not run any of them.

When the fact branch of `/crav1-add-to-spec` changed a file, or this command wrote a source folder or a note, name `/crav1-finalize-commit`. Do not run it. Do not commit the note.
