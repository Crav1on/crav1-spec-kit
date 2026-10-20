# crav1-show-or-ask-open-questions: asked

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Pending first

Read `docs/specs/<slug>/spec.md` for every spec folder. Skip `_template`. Read `## Open questions`, leftover unresolved assumptions, and the records under each question.

When a question in this selection has a `Pending:` line, show those first, before any new question. One line per draft, as the reference file says, for example:

```text
Drafted for Dana on 2026-10-11 (mail), not marked as sent yet. 5 questions.
```

Ask for each draft. Options, each explained:

1. **Mark as sent** — you sent it. The kit writes `Asked:` on those questions, with the date you give, or today when you give none.
2. **Keep pending** — not sent yet. The mark stays and is shown again next run.
3. **Drop the mark** — it will not be sent. The kit removes the pending mark. The questions are open as before.

Stop until the user picks. Do not mix pending questions silently into the new draft. When the user wants them in the new draft too, they say so.

## Asked?

Ask once for the draft. Options only. Use the questions tool when it is available. Each option explained:

1. **Yes, asked** — you have sent it or asked it. The kit writes `Asked:` under each question in the spec, with today's date, the kind, and who.
2. **No** — not asking. The kit writes nothing.
3. **Pending** — you copied it and will send it later. The kit writes `Pending:` under each question, with today's date, the kind, and who. Next run shows it first.

When the user picks yes or pending, write the lines as the reference file says, with `Question <n>` from the draft. A question asked of the same person again replaces the earlier line for that person. When an import later shows the question being asked, that date replaces this one. Do not edit the question text. Do not edit any other line.

## Parked and retired specs (1.60.0)

Skip `docs/specs/retired/` and `Moved:` pointers. A parked spec (a `Parked:` line in `spec.md`) is still listed, its section heading marked `(parked)`; its questions can still be shown and asked. A note in `docs/notes/` (month folders since 1.61.0) with the slug in `waiting_for`, or an old `Waiting for <slug> (parked)` line, is not open work: list it as `waiting for parked <slug>` under that spec, not in the open counts.
