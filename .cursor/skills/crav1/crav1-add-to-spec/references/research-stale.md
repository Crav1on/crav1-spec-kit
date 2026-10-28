# Research marked stale

A kept quote can contradict a research note, or answer a question that note still leaves open. This file is how the kit marks that research stale, how it checks an updated note, how it clears or narrows the mark, how it routes a point that stays open, how it routes an open question the updated note still has, and how readers show it.

This file is the convention. Drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`. Plugin, from this skill: `references/research-stale.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/research-stale.md`.

The skills that follow this file write the mark, the clear, the narrowed line, and any open question this file names. They do not commit. They do not push. They do not open a pull request. The user commits.

A glossary row whose Meaning is `to be researched` is not a research note. Do not mark it from this file. `/crav1-glossary research` fills those rows (1.101.0). A note in `docs/notes/` is not a research note. Do not mark it from this file.

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

## Where the rest is

On a hit, read [research-stale-mark.md](research-stale-mark.md) for **Ask before marking**, **Mark**, and **Revisit request**. When this check clears, narrows, or routes a mark, or a kept quote answers a point already waiting, read [research-stale-clear.md](research-stale-clear.md) for **Clearing** and its sections. Readers follow **Readers** below. Moved word for word from `research-stale.md` in 1.71.1; the rules are unchanged.

## Readers

`/crav1-explain-existing-system`, `/crav1-what-do-we-know-about-this`, and `/crav1-ado-sync` show a stale note as stale. A narrowed line is still stale. Quote the mark. Name the path. Do not treat that research as current. Do not clear the mark. Do not route a point. Do not write the note's open questions onto a spec. Do not drop the note to keep a list short.

`/crav1-plan-from-spec` lists stale research findings under Risks. A narrowed mark is still stale. The plan does not stop because research is stale. Do not clear the mark. Do not route a point.

`/crav1-tighten-spec` may name a stale mark as an issue. A narrowed mark is still the mark. It does not clear the mark. It does not rewrite the research note. It does not route a point.

## Stop

Do not commit. Do not push. Do not open a pull request. Do not send a revisit request. Do not contact the note's owner. Do not ask the user whether an updated note resolves the mark. Do not count an older mark with no point lines as one point.
