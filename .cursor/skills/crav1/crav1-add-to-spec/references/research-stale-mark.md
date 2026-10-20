# Research marked stale: mark

Read only on a hit from [research-stale.md](research-stale.md). That file is the convention. Moved word for word from `research-stale.md` in 1.71.1; the rules are unchanged.

## Ask before marking

List every hit. Then ask once. Options only. Use the questions tool when it is available.

Mark this research stale?

1. **Yes**
2. **No**

Stop until the user picks. Do not mark before that yes. No leaves the note and the findings as they are.

This question is not the landscape apply question. Do not fold the hits into that list. When both questions are open, ask this one first. Do not ask the other in that same turn.

This yes is only for a new mark. It is not the check of an updated note. That check does not ask the user.

## Mark

On yes, write the mark. Do not change the note's own text. Do not rewrite a recommendation, an inferred line, or a question.

The date is the date the kept quote already carries. When that quote has no date, the date is the calendar date of this run. Do not invent a date and call it the source date.

**On the research note.** Below the title and the owner line, add one blockquote. The owner line is the note's first attribution line, when the note has one. When the note names no owner, put the blockquote below the title.

```text
> Stale since <date>: <one line on what changed>. Source: docs/sources/YYYY-MM-DD-<slug>/
```

When the quote was not imported, end with the source line this run already uses for that quote. Do not invent a source.

The one line uses the quote's words. One line. Do not retell the note.

When a stale block for the same quote is already on that note, do not add a second one. Say it is already marked.

**On the spec.** Under `## Research findings`, add one line:

```text
Stale since <date>: <one line>. See <note path>.
```

`See` names the note this pass marked. When the hit is only in the findings and no note was marked, omit `See`.

Under that line, add one line per hit. These are the listed points. A later check counts them. Do not drop one.

```text
Point: <short label>. <the research line or the question, quoted>.
```

The short label is a few words from that quote. One point per hit.

Create `## Research findings` only when it is missing and this line needs a heading. Do not rewrite a findings line that is already there. The stale line is new. The point lines are new. The note's own text stays.

A spec this quote was written into gets the line. A spec whose findings link to the marked note gets the line too. Do not add the line to a spec that neither received the quote nor links to the note.

## Revisit request

After the mark is written, offer to draft a short revisit request in the chat. The owner is taken from the note, for example its first attribution line. The owner is a person or anything else the note names. Do not invent an owner.

When the note names an owner, the question is: Draft a revisit request for the note's owner?

When the note names no owner, say the note names no owner. The question is: Draft a revisit request without an owner?

Options are only:

1. **Yes**
2. **No**

Use the questions tool when it is available. Stop until the user picks.

Yes drafts the request in the chat. The draft has these sections:

- Note path and owner. When the note names no owner, say so.
- What changed. The quote, and the source.
- What it contradicts. Each listed point, quoted, with its section. Plus any open question the quote answers, quoted.
- Question. For each listed point, ask the owner to say resolved, partly, or not addressed. When it is still open, ask why. Examples: needs a partner to confirm, not in public sources, needs a decision.
- Status. The kit checks the updated note against each listed point when it comes back to `docs/research/`.

The kit drafts only. It does not send the request. It does not contact anyone. Do not name a way to reach the owner.

No draft when they pick no. Do not offer the draft when they did not mark the research.

One note, one draft. When more than one note was marked, draft them one at a time. The next note waits until this draft is done or skipped.
