# Open questions: asked marks and answer links

An open question on a spec can be asked of someone outside the kit, by mail, in a meeting, or in a chat. This file is how the kit records that a question was asked or is pending, how it links an answer that comes back in an import, and how it takes the asked-on date from the source.

`/crav1-show-or-ask-open-questions` writes the asked and pending marks after the user picks. `/crav1-add-to-spec` follow this file when they import a mail, a transcript, minutes, or a chat. `/crav1-resolve-questions` reads the answer links. None of them sends anything. None of them commits.

## Where the records live

An open question is a bullet, or a numbered item, under `## Open questions` in `docs/specs/<slug>/spec.md`. Its records are indented lines under that bullet. The question text is not rewritten. The spec is where the kit keeps which question came from which spec. A drafted mail, agenda, or chat never shows that.

```text
- <the open question, as the spec already has it>
  - Pending: drafted <date> for <who>, <channel>. Not marked as sent yet. Question <n> of that draft.
  - Asked: <date>, <channel> to <who>. Question <n>. Date from <the user's yes | email <date> | meeting <date> | chat <date>>.
  - Answered: <date>, <who>, <kind>: "<quote>" Source: docs/sources/YYYY-MM-DD-<slug>/
  - Blocks: T2, T4
```

- `<who>` is the person or group the user named. `<channel>` is `mail`, `meeting agenda`, `chat`, or `meeting questions`.
- `Question <n>` is the number the question had in that draft. It helps match "about question 3" in a reply. It is not shown as a spec id to anyone.
- A question has at most one `Pending:` line and at most one `Asked:` line per person. A later mark for the same person replaces the earlier line. A question asked of two people keeps one line per person.
- `Blocks:` names the tasks in `tasks.md` that wait on this question. `/crav1-resolve-questions` writes it after a keep-open pick, and `/crav1-plan-from-spec` writes it for a kept-open question it parks as a risk. At most one `Blocks:` line per question; a new one replaces it. No `Blocks:` line means the question blocks the whole slice for `/crav1-tasks-ready-to-build`. Remove the line when the question is answered.
- `Answered:` keeps the source's words. Do not paraphrase. When there is no source folder, end with `Source: <kind> <date>` or `Source: <kind>`.

## Asked, no, or pending

After a draft, the user picks one of three. The kit never sends anything.

- **Yes, asked** writes `Asked:` on each question in the draft, with today's date, the channel, and who. The date line says `Date from the user's yes.` It removes a `Pending:` line for the same person.
- **No** writes nothing. It is as if the draft was never made.
- **Pending** writes `Pending:` on each question in the draft, with today's date, the channel, and who. Use it when the text is copied now and sent later.

## Pending comes back

On the next `/crav1-show-or-ask-open-questions` run that touches a question with a `Pending:` line, show it first, before any new question. One line per draft:

```text
Drafted for <who> on <date> (<channel>), not marked as sent yet. <n> questions.
```

The user picks for each draft. Options, each explained:

1. **Mark as sent** — it was sent. Writes `Asked:` with the date the user gives, or today when they give none, and removes `Pending:`.
2. **Keep pending** — not sent yet. The line stays. It is shown again next run.
3. **Drop the mark** — it will not be sent. Removes `Pending:`. The questions are open as before.

Do not mix pending questions silently into the new draft. When the user wants them in the new draft too, they say so.

## Answer links during an import

When a skill imports a mail, a transcript, minutes, or a chat, read every `## Open questions` on the specs it reads (skip `_template`), with their records. Compare each extracted item with each open question. Match by meaning. The words can differ. A reply that says "about question 3" matches the question whose `Asked:` or `Pending:` line says `Question 3` for that person. Matching works whether the question is asked, pending, or not marked.

- **Clear answer.** The item states the fact or the decision the question asks for. Link it without a separate keep question. In `/crav1-add-to-spec` it is not asked. In `/crav1-add-to-spec` it is linked with the confirmed sort. Write `Answered:` under the question, with the date, who, the kind, the quote, and the source. Follow the imported-sources check in [sources.md](sources.md) first, so the quote is the one after any redaction. The question stays under `## Open questions` with its answer linked. It is marked answered. It is not folded into requirements here.
- **Unclear or partial.** The item only might answer, answers part, or is hedged ("probably", "I think", "need to check"). Show it as a possible answer, quote and question together. Do not write `Answered:`. The question stays open. The item still goes through the import skill's own keep, leave, or note path.
- **Changes a spec line.** When the linked answer would change a requirement, an acceptance line, a constraint, or another spec line, do not change that line here. Name `/crav1-resolve-questions` for that slug. Do not run it.
- **Settles a stale research point.** When the question is one a stale research point waits on, the existing re-check in [research-stale.md](research-stale.md) runs. It does not ask the user.

A link is one quote for one question. One item that clearly answers two questions links to both. Two items that answer one question are both linked, each on its own `Answered:` line.

## Asked-on date from the source

When the imported mail, transcript, or chat shows the question being asked, record the date from the source. The mail's sent date, the meeting date, or the chat message's date is the asked-on date. Write `Asked:` with `Date from <kind> <date>.` This replaces a `Pending:` line and an `Asked:` line from the user's yes for the same person. It is also written when the question had no mark. The user's yes date is used only when no source shows the asking.

A question that is only quoted back in a reply, under a quoted earlier mail, is asked on the date of that earlier mail when the reply shows it. Do not invent a date. When the source shows no date and the run has none, leave the existing mark as it is.

## After a meeting

After a meeting import, each question that got a clear answer is linked. Every other question that was asked or pending for that meeting goes back to open. Its `Asked:` line stays, with the meeting date when the transcript shows it was asked. Its `Pending:` line becomes `Asked:` when the transcript shows it was asked. A question that was on the list and was not reached keeps the mark it had.

## Summary

The import skill's end-of-run summary lists:

- each answer linked: the question, the spec, and the source
- each possible answer shown and left open
- each asked mark written or updated, with the date and where it came from
- each `/crav1-resolve-questions` named, and for which slug

## Do not

- Do not send, post, or reply to anything.
- Do not rewrite the question text.
- Do not remove an answered question from `## Open questions`. `/crav1-resolve-questions` does that when the user picks.
- Do not show a spec slug, a spec path, or a `Q#` id in drafted text that goes to another person.
- Do not commit.
