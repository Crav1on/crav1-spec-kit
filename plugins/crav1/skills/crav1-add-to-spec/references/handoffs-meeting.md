# crav1-add-to-spec: handoff

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0 and from `handoffs.md` in 1.71.1; the rules are unchanged.

## From the meeting branch of /crav1-add-to-spec

When `/crav1-add-to-spec` hands one kept addition for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a spec folder. A source folder that handoff already wrote stays. When it wrote none and the quote is an imported source, **Imported sources** writes that folder.

The handoff passes the kind and the date, and the source folder when that skill already wrote one. The kind is `meeting`, `email`, or `chat`. Quote the item. Do not replace it with a paraphrase. A `State:` line is not part of the quote. Do not write it. The quote starts with `From <kind> <date>.` when the handoff includes a date, otherwise `From <kind>.` Examples: `From email 2026-10-06.`, `From meeting.` Do not invent a kind or a date. Keep the speaker and the time in the quote when the input showed them. Label it `**New:**` in the section the words belong to, the same way any other new quote is labeled.

When the handoff includes a source folder, add the `Source:` and `Trace:` lines from [references/sources.md](sources.md). Do not ask the mail, image, binary, or personal-data questions again. Do not write a second copy of that folder. When the handoff has no folder and the quote is an imported source, follow **Imported sources** before the quote.

When the handoff includes a note path, that quote comes from that note. Run **Notes** after the spec quote. Do not ask what kind of note it is.

Then run **Add to that spec.md** and **Impact** in this skill. The impact check still runs, including research. Follow [references/research-stale.md](research-stale.md). Do not skip it. Do not run that research check a second time. Do not write `plan.md` or `tasks.md`. Do not change application code. Do not start Specify, Plan, or Build. Do not ask the picture offer. That offer is only the read-environment and suggest-tests handoffs.
