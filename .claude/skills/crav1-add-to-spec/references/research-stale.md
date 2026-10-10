# Research marked stale

A kept quote can contradict a research note, or answer a question that note still leaves open. This file is how the kit marks that research stale, how it clears the mark, and how readers show it.

This file is the convention. Drop-in: `.claude/skills/crav1-add-to-spec/references/research-stale.md`. Plugin, from this skill: `references/research-stale.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/research-stale.md`.

The skills that follow this file write the mark. They do not commit. They do not push. They do not open a pull request. The user commits.

A glossary row whose Meaning is `to be researched` is not a research note. Do not mark it from this file. A note in `docs/notes/` is not a research note. Do not mark it from this file.

## When to compare

Compare after a quote is kept in a spec. The skills are `/crav1-meeting-to-specs`, `/crav1-add-to-spec`, `/crav1-match-dump-to-specs`, and `/crav1-code-into-specs`.

`/crav1-meeting-to-specs` hands a kept addition to `/crav1-add-to-spec`. That handoff runs this check. Meeting does not run it a second time.

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

Example of both hits on one note. The quote is `A fixed, dedicated public IP address that we can allowlist in our proxy firewall`. That contradicts an inferred line `since NRCC calls us (we originate no NRCC traffic), mTLS itself doesn't need one`. It answers the open question `Does NRCC require a static IP from us?`. List both. The example is a shape. It is not a fact in this kit repo.

## Ask before marking

List every hit. Then ask once. Options only. Use the questions tool when it is available.

Mark this research stale?

1. **Yes**
2. **No**

Stop until the user picks. Do not mark before that yes. No leaves the note and the findings as they are.

This question is not the landscape apply question. Do not fold the hits into that list. When both questions are open, ask this one first. Do not ask the other in that same turn.

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

Create `## Research findings` only when it is missing and this line needs a heading. Do not rewrite a findings line that is already there. The stale line is new. The note's own text stays.

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
- What it contradicts. Each quoted line with its section. Plus any open question the quote answers, quoted.
- Question. One or two lines. Please revisit. Does the recommendation still hold?
- Status. Marked stale since the date. Cleared when an updated note comes back to `docs/research/`.

The kit drafts only. It does not send the request. It does not contact anyone. Do not name a way to reach the owner.

No draft when they pick no. Do not offer the draft when they did not mark the research.

One note, one draft. When more than one note was marked, draft them one at a time. The next note waits until this draft is done or skipped.

## Clearing

A stale mark is the blockquote on the note, or a `Stale since` line under `## Research findings` that sees that note.

Run this section when either is true:

- This run writes a file under `docs/research/`. Any kit skill that writes there runs this section.
- The user replaced a file under `docs/research/` and pointed `/crav1-add-to-spec` or `/crav1-keep-current` at it.

Read the note. When the note or a spec that sees it still has the mark, ask. Options only. Use the questions tool when it is available.

Does this update resolve the stale mark on <path>?

1. **Yes**
2. **No**

Stop until the user picks. Do not clear before that yes.

Yes removes the blockquote from the note. Yes removes each `Stale since` line that sees that note. Yes adds one line under that spec's `## Research findings`:

```text
Cleared <date>: updated note <path or commit>.
```

The date is the calendar date of this run. The path is the note. When this run can see the commit that updated the note, the line may name that commit. Do not invent a commit. Do not commit.

No leaves the mark. Do not remove the block. Do not remove the spec line.

When the updated note no longer has the blockquote, and no spec line sees it, there is nothing to ask.

A file under `docs/research/` that this command is pointed at, with no separate quote for a spec, is this clear check. It is not a new quote. Do not paste the note into a spec. Do not ask for a slug.

## Readers

`/crav1-explain`, `/crav1-whats-known-about`, and `/crav1-feature-candidates` show a stale note as stale. Quote the mark. Name the path. Do not treat that research as current. Do not clear the mark. Do not drop the note to keep a list short.

`/crav1-plan-from-spec` lists stale research findings under Risks. The plan does not stop because research is stale. Do not clear the mark.

`/crav1-tighten-spec` may name a stale mark as an issue. It does not clear the mark. It does not rewrite the research note.

## Stop

Do not commit. Do not push. Do not open a pull request. Do not send a revisit request. Do not contact the note's owner.
