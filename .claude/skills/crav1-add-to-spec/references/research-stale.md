# Research marked stale

A kept quote can contradict a research note, or answer a question that note still leaves open. This file is how the kit marks that research stale, how it checks an updated note, how it clears or narrows the mark, how it routes a point that stays open, how it routes an open question the updated note still has, and how readers show it.

This file is the convention. Drop-in: `.claude/skills/crav1-add-to-spec/references/research-stale.md`. Plugin, from this skill: `references/research-stale.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/research-stale.md`.

The skills that follow this file write the mark, the clear, the narrowed line, and any open question this file names. They do not commit. They do not push. They do not open a pull request. The user commits.

A glossary row whose Meaning is `to be researched` is not a research note. Do not mark it from this file. A note in `docs/notes/` is not a research note. Do not mark it from this file.

## When to compare

Compare after a quote is kept in a spec. The skills are `/crav1-add-to-spec`.

`/crav1-add-to-spec` hands a kept addition to `/crav1-add-to-spec`. That handoff runs this check. Meeting does not run it a second time.

A kept new feature, a kept bug, a leave, a dismiss, and a note written to `docs/notes/` do not run this check.

## What to read

Read every `docs/research/*.md`. Do not skip a file to keep the list short. When that folder is missing, there are no research notes. Say so.

Read `## Research findings` on each spec this quote was written into. Skip a spec that has no such heading.

A findings line that names a path is a link. Read that note too. A path the findings do not name is not a link. Do not invent a link.

An inferred line in the note is still a line. Include it. Quote it as written.

## What is a hit

Two kinds. List both. Do not drop one to keep the list short.

1. **Contradiction.** The quote clearly contradicts a line in the note or under `## Research findings`. Show the new quote and the research line. Quote both. Name the file and the section.
2. **Answer.** The quote answers an open question in the note or under `## Research findings`. Show the new quote and the question. Quote both. Name the file and the section.

An unclear case is not a hit. Do not mark it. It stays an open question on the spec, the same way that quote is written today. A line that only might disagree is unclear. Do not mark it.

Example of both hits on one note. The quote is `A fixed, dedicated public IP address that we can allowlist in our proxy firewall`. That contradicts an inferred line `since the partner calls us (we originate no partner traffic), mTLS itself doesn't need one`. It answers the open question `Does the partner require a static IP from us?`. List both. The example is a shape. It is not a fact in this kit repo.

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

## Clearing

A stale mark is the blockquote on the note, or a `Stale since` line under `## Research findings` that sees that note. A narrowed line is still that mark.

Run this section when either is true:

- This run writes a file under `docs/research/` for a note that has a stale mark.
- The user replaced a file under `docs/research/` and pointed `/crav1-add-to-spec` or `/crav1-refresh-system-notes` at it, and the note or a spec that sees it has a stale mark.

Do not ask the user whether the update resolves the mark. The user does not judge the research. Judge from the update's text.

Writing the file does not resolve a point. A replaced file that dropped the blockquote does not clear the mark. When a spec line still sees the note, put the mark back from this check.

A file under `docs/research/` that this command is pointed at, with no separate quote for a spec, is this check. It is not a new quote. Do not paste the note into a spec. Do not ask for a slug.

When the note has no stale mark and no spec line sees it, there is nothing to check.

When this check runs, also read the updated note's own open questions, under the heading `The note's own open questions`. That read does not wait on an open point. It still runs when the mark clears.

### Listed points

The listed points are the `Point:` lines under the stale line, when those lines are still there.

When a later check has already replaced those lines, the listed points are the points named on the narrowed stale line, plus each `Resolved` line for this mark. Do not treat the whole narrowed line as one point.

M is how many listed points the mark has. Do not add a point the mark did not list. Do not drop one.

When an older mark has no `Point:` lines and no narrowed line, that mark is not one point. Do not give the stale line a label and count it as one.

Split that mark into the hits it was made from. A hit is a contradiction, or an answered question. Read the contradiction lines and the answered-question lines named in the note's stale block. Read the same kinds of lines named in the spec's stale line. When this run can see the run that wrote those lines, read the hits that run listed. The example earlier in this file is a shape. It is not that hit list. Do not copy it onto a note.

Each hit is one listed point. On each spec whose stale line sees the note, write it under that line as a `Point:` line, the same way a new mark writes one. Then judge it. M is how many hits this run found. Do not add a hit that was not named in the block, the spec line, or that run.

When this run cannot find those hits, there are no listed points. Do not invent one. Do not set M to 1. Judge the whole update against the original quote. The original quote is the quote the stale line names. Use the same three words. Resolved means the update now agrees with that quote, or states the answer that quote gave. Partly means the update speaks to that quote and leaves part of it open. Not addressed means the update does not speak to that quote. Say in the summary that the older mark had no points.

When that judgment is resolved, remove the blockquote from the note. Remove the `Stale since` line that sees that note. Under `## Research findings`, add `Cleared <date>: updated note <path or commit>.` Do not add a per-point line. The date and the path follow All resolved. Do this on every spec whose stale line sees that note.

When that judgment is partly or not addressed, leave the older mark as written. Do not rewrite it as `N of M points`.

### Judge each point

For each listed point, one of three, from the update's text:

- **Resolved.** The update states the fact or the answer the point asked for.
- **Partly.** The update speaks to the point and leaves part of it open. Partly stays open.
- **Not addressed.** The update does not speak to the point. Not addressed stays open.

When the owner says resolved, partly, or not addressed, use that word. When the word and the rest of the update disagree, the point stays open. Say that in the summary. When the owner does not use those words, judge from what the update says about that point.

Quote the update. Do not retell it.

### All resolved

When the mark has listed points and every one of them is resolved:

- Remove the blockquote from the note.
- Remove the `Stale since` line that sees that note.
- Under that spec's `## Research findings`, add:

```text
Cleared <date>: updated note <path or commit>.
```

- Under that, one short line per point on how it was resolved:

```text
<point>: resolved. <how>.
```

The date is the calendar date of this run. The path is the note. When this run can see the commit that updated the note, the line may name that commit. Do not invent a commit. Do not commit.

Remove the old `Point:` lines, the `Resolved` lines, and the waiting lines for this mark. The lines under `Cleared` replace them.

Do this on every spec whose stale line sees that note.

### Still open

When any point is partly or not addressed, the mark stays. Narrow it. On the note, replace the blockquote with:

```text
> Stale since <date>, N of M points open: <points>.
```

On the spec, replace the `Stale since` line with the same sentence, plus `See <note path>.` when the line already sees the note. The date is the original stale date. N is how many points are still open. Name those points. Do not use today's date as the stale date.

Replace each old `Point:` line for this mark with the resolved line or the waiting line. Record each resolved point. Leave it out of N.

```text
Resolved <date>: <point>. Updated note <path or commit>. <how>.
```

The date is the calendar date of this run. Do not invent a commit.

### Route each open point

Route each open point from the reason the update gives. Quote that reason. Do not invent a reason. Do not send the point back to the owner when the update says someone else has the fact, or that it needs a decision.

On the spec, each open point names where it waits, on its own line:

```text
<point>: waiting for the note's owner. Follow-up <N> of this mark.
```

```text
<point>: open question on <slug>, waiting for <who>.
```

1. **Research missed it or got it wrong.** The update says the research missed the point or got it wrong, and it does not name someone else who has the fact, and it does not say it needs a decision. Draft a follow-up revisit request in the chat, for those points only. The line says `waiting for the note's owner`.
2. **Someone else has the fact.** The update says a partner, a customer, or a document not yet read has the fact. Write an open question on the spec. Name who can answer when the update or the note says so. Do not draft a revisit for that point. The line says `open question on <slug>, waiting for <who>`.
3. **A decision.** The update says it needs a decision, such as cost or which option. Write an open question on the spec. Mark it as a decision. When the note names who decides, that is who. When it does not, who is `a decision`. Do not draft a revisit for that point.
4. **No why.** The update does not say why the point is still open. Draft one request back to the note's owner, asking who can answer it. Once per point. When that point already says `Asked who can answer`, do not draft it again. The line stays `waiting for the note's owner`.

`<slug>` is the spec that has the stale line. When more than one spec has it, write the question on each of those specs. The same words. Do not add a second question when that point already has one. Same meaning is the same fact or the same decision. The words can differ. When the update names a different who, add that name on the existing question.

This routing is for listed points that stayed open. The note's own open questions are a later section. They are not these points.

### Follow-up revisit request

Draft it in the chat. Do not send it. Do not contact anyone. Do not name a way to reach the owner. The owner is a person or anything else the note names. Do not invent an owner. When the note names no owner, say so.

Number it `Follow-up N of this mark`. N is one more than the highest follow-up number already written for this mark. When none is written, N is 1. One draft, one number. The points in that draft share it.

Sections:

- Note path.
- Owner. When the note names no owner, say so.
- Updated version read. The path, and the commit when this run can see it. Do not invent a commit.
- Resolved since last request. One line each. When none, say none.
- Still open, per point. The original quote. What the update said, quoted. Why the kit judged it open.
- One narrow question per open point.
- Status. The kit checks the next updated note against each point still open.

When this draft asks who can answer, the question is that, and the spec line adds `Asked who can answer.`

When N is 3 or more, the draft also says the point has been open a while and suggests a conversation instead of another note. The kit does not decide that.

### Open question on the spec

Under `## Open questions`, add one bullet. Create that heading only when it is missing and this bullet needs it. Do not rewrite another question.

Someone else has the fact:

```text
- <point>. Waiting for <who>. The updated note <path> says: "<quoted why>".
```

A decision:

```text
- Decision. <point>. Waiting for <who>. The updated note <path> says: "<quoted why>".
```

### A spec line to change

When the update says a line in the spec should change, add an open question on that spec. When the update does not name the spec, use the spec that has the stale line. Do not rewrite the spec line.

Name the source of the suggested wording. Do not attribute to the note a wording that is only in the note's owner's revisit answer. The revisit answer is that owner's reply to the revisit request. It may be in the chat, or pasted with the note. When the note's own text holds the wording, name that section, even if the answer repeats it. When the wording is only in the reply, name the reply.

When the wording is in the revisit answer:

```text
- The note's owner, in their revisit answer (<date>), suggests changing "<old line>" to: "<wording>".
```

When the note or the answer names the owner, use that name instead of `The note's owner`. Do not invent a name.

The date is the date the revisit answer carries. When that answer has no date, write `no date`. Do not invent a date.

When the wording is in the note, name the section:

```text
- The note <path>, in <section>, suggests changing "<old line>" to: "<wording>".
```

When an open question on that spec already has the same meaning, do not add another. Same meaning is the same change to the same line. The words can differ. This question is not a listed point. It does not clear the mark.

### The note's own open questions

Run this on every check in this Clearing section. Run it when the mark had open points. Run it when the mark had none. Run it when this run clears the mark. Run it when the older mark had no points.

Before the clear, list each spec whose `## Research findings` name this note's path. A findings line that names the path is a link. A `See` line that names the path is a link. Keep that list. When the clear already ran in this check, use that list. When no list was made, a spec still counts if a findings line, a `See` line, or the `Cleared` line this run wrote names the path. When no spec names the path, say so. Do not invent a spec.

Read the updated note's `## Open questions`. Also read a line the note marks as needing a source, or as needing confirmation. Skip a line that only records a fact. A question that appears twice in the note is one question. Same meaning is one question.

A question stays in the note when the note's owner can still answer it. That is when the note does not say someone else has the fact, and it does not say the question needs a decision. Do not write it on a spec. When it is unclear who can answer, leave it in the note. Do not guess.

A question whose answer lies outside the note's owner is written on each spec in that list. The same words on each spec.

Someone else has the fact. The note says a partner, a customer, another team, or another person has the fact. Name who the note says has the fact. A person the note names only as a way to reach them is not who has the fact. Do not name a way to reach them. When the note does not name who, write `the note does not name who`. Do not invent a name.

```text
- <question>. Waiting for <who>. The note <path>, in <section>, says: "<quoted line>".
```

A decision. The note says the question needs a decision. Mark it as a decision. When the note names who decides, that is who. When it does not, who is `a decision`.

```text
- Decision. <question>. Waiting for <who>. The note <path>, in <section>, says: "<quoted line>".
```

Do not add a second question when that spec already has an open question with the same meaning. Same meaning is the same fact or the same decision. The words can differ. A different fact is a different question. Do not drop one because it shares a few words with another. When the note names a who that the existing question does not, add that name on the existing question.

These questions are not listed points. They do not change N. They do not keep the mark open. They do not clear the mark. Do not remove them from the note.

Create `## Open questions` on the spec only when it is missing and this bullet needs it. Do not rewrite another question.

### Answered later

Run this when either is true:

- `/crav1-resolve-open-questions` answers an open question that a stale point is waiting on. Keep open does not run this. The question stays. The point stays.
- A kept quote in the impact check answers that open question, or settles a listed point that is still open.

Read the answer and the point. Do not ask the user.

The point is settled when the answer states the fact or the decision the point was waiting for. A cut from v0 settles it as not in v0. An answer that does not state that fact or that decision leaves the point open. Say why in the summary.

When it is settled, replace that point's waiting line with:

```text
Resolved <date>: <point>. <how>.
```

Remove that open question when this pass did not already remove it. Lower N. Rewrite the narrowed line. When no point is open, remove the blockquote and the `Stale since` line. Remove the `Resolved` lines and the waiting lines for this mark. The lines under `Cleared` replace them. Write:

```text
Cleared <date>: updated note <path or commit>.
```

when an updated note finished it, or:

```text
Cleared <date>: open question on <slug> answered.
```

when an answer finished it. One short line per point on how it was resolved, including points resolved earlier.

Do this on every spec whose stale line sees that note.

### Summary

End the run with one short summary. Name what was cleared, what was narrowed, and where each open point was routed. List every open question read from the updated note. For each, name the spec it was written on and who it waits for, or say it stayed in the note because the note's owner can still answer it. When the older mark had no points, say so. Name each draft as drafted and not sent. When a spec line was left as an open question, name where the suggested wording came from.

Everything in this section is written in the files. Nothing is sent. Nothing is committed. Drafts stay in the chat.

## Readers

`/crav1-explain-existing-system`, `/crav1-what-do-we-know-about-this`, and `/crav1-ado-sync` show a stale note as stale. A narrowed line is still stale. Quote the mark. Name the path. Do not treat that research as current. Do not clear the mark. Do not route a point. Do not write the note's open questions onto a spec. Do not drop the note to keep a list short.

`/crav1-plan-from-spec` lists stale research findings under Risks. A narrowed mark is still stale. The plan does not stop because research is stale. Do not clear the mark. Do not route a point.

`/crav1-tighten-spec` may name a stale mark as an issue. A narrowed mark is still the mark. It does not clear the mark. It does not rewrite the research note. It does not route a point.

## Stop

Do not commit. Do not push. Do not open a pull request. Do not send a revisit request. Do not contact the note's owner. Do not ask the user whether an updated note resolves the mark. Do not count an older mark with no point lines as one point.
