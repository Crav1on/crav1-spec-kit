# crav1-add-to-spec: handoffs

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## From /crav1-read-environment

When `/crav1-read-environment` hands a confirmed fact for a slice Match already owns, run only this section. Add that quote to that spec only. The quote starts with `Seen in <host> <environment>.` When the quote says `shared with prod`, `prod only`, or shape and connections only, keep that label. Do not replace it with a paraphrase. Do not mark it as something the code shows. Do not change match status. Do not create a slug. Do not open the impact question. Do not edit `docs/system/` or another spec from this handoff. If no spec has `## Match` for that slice, write nothing. Do not start Specify, Plan, or Build. Do not continue into the main path. After the last read-environment item in this run, follow **Picture offer**, then stop.

## From /crav1-suggest-tests-for-code

When `/crav1-suggest-tests-for-code` hands one suggestion for an existing spec, run only this section. The spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a folder. Do not open the impact question. Do not edit `docs/system/` or another spec. Do not write `plan.md` or `tasks.md`. Do not write test code. Do not change application code. Do not start Specify, Plan, or Build. Do not continue into the main path. After the last suggestion in this run, follow **Picture offer**, then stop.

**Keep.** Quote the suggestion. Do not replace it with a paraphrase. Add one acceptance checkbox because it is a check a stranger could run. Label it `**New:**`. The checkbox stays yes/no. Name the kind the suggestion already named: unit for a function’s checks, browser for a page, integration for a boundary. Do not invent another check. Do not add another kind.

**Dismiss.** Quote the suggestion under `## Dismissed test suggestions`. The line starts with `Dismissed test suggestion.` Do not reword the check. Create that heading only when it is missing. Do not add an acceptance checkbox. Do not turn it into a goal. Plan does not turn this line into a task. The next run of `/crav1-suggest-tests-for-code` does not offer it.

## From the push features branch of /crav1-ado-sync

When `/crav1-ado-sync` hands a change that belongs in the spec before a Feature preview is rebuilt, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Quote the change. Do not replace it with a paraphrase. Label it `**New:**`. Then run **Add to that spec.md** and **Impact**. Do not write `work-item.md` from this handoff. That skill writes the id after Azure Boards accepts the Feature. Do not start Specify, Plan, or Build.

## From the pull spec changes branch of /crav1-ado-sync

When `/crav1-ado-sync` hands one kept change or one answer for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a spec folder.

Quote the item. Do not replace it with a paraphrase. A kept Azure Boards change starts with `From ADO <date>. <who>.` when the handoff includes a date and a person. When the handoff has a date and no person, it starts with `From ADO <date>.` An answer the user gave starts with `From the user <date>. Answer to the ADO question.` Do not invent a date or a person. Label it `**New:**` in the section the words belong to. An open question from a Feature discussion goes under `## Open questions`.

Then run **Add to that spec.md** and **Impact**. The impact check still runs. Do not write `plan.md`, `tasks.md`, or `work-item.md`. Do not change application code. Do not start Specify, Plan, or Build. Do not ask the picture offer.

## From the meeting branch of /crav1-add-to-spec

When `/crav1-add-to-spec` hands one kept addition for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a spec folder. A source folder that handoff already wrote stays. When it wrote none and the quote is an imported source, **Imported sources** writes that folder.

The handoff passes the kind and the date, and the source folder when that skill already wrote one. The kind is `meeting`, `email`, or `chat`. Quote the item. Do not replace it with a paraphrase. A `State:` line is not part of the quote. Do not write it. The quote starts with `From <kind> <date>.` when the handoff includes a date, otherwise `From <kind>.` Examples: `From email 2026-10-06.`, `From meeting.` Do not invent a kind or a date. Keep the speaker and the time in the quote when the input showed them. Label it `**New:**` in the section the words belong to, the same way any other new quote is labeled.

When the handoff includes a source folder, add the `Source:` and `Trace:` lines from [references/sources.md](sources.md). Do not ask the mail, image, binary, or personal-data questions again. Do not write a second copy of that folder. When the handoff has no folder and the quote is an imported source, follow **Imported sources** before the quote.

When the handoff includes a note path, that quote comes from that note. Run **Notes** after the spec quote. Do not ask what kind of note it is.

Then run **Add to that spec.md** and **Impact** in this skill. The impact check still runs, including research. Follow [references/research-stale.md](research-stale.md). Do not skip it. Do not run that research check a second time. Do not write `plan.md` or `tasks.md`. Do not change application code. Do not start Specify, Plan, or Build. Do not ask the picture offer. That offer is only the read-environment and suggest-tests handoffs.

## From an import: answer links and asked marks

When `/crav1-add-to-spec` hands an answer link or an asked mark for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not ask keep or apply. Follow [references/open-questions.md](open-questions.md).

- An answer link writes one `Answered:` line under that open question: the date, who, the kind, the quote as handed (after any redaction), and the source folder. Do not paraphrase. Do not rewrite the question. Do not remove it from `## Open questions`. Do not change any other spec line. When the answer would change a spec line, name `/crav1-resolve-open-questions` for that slug. Do not run it.
- An asked mark writes or replaces the `Asked:` line for that person under that question, with the date from the source. It replaces a `Pending:` line for the same person.

When the handoff includes a source folder, add the `Source:` and `Trace:` lines from [references/sources.md](sources.md). Do not ask the imported-sources questions again.

Then run **Impact** for the research part only. When the question is one a stale research point waits on, follow the answered-later part of [references/research-stale.md](research-stale.md). Do not ask the user whether the point is settled. Do not ask the landscape question for an answer link. Do not run the picture offer. Do not commit.

## Picture offer

The handoff sections **From /crav1-read-environment** and **From /crav1-suggest-tests-for-code** ask once at the end of the run, after every item this run wrote. Not after each item. The meeting handoff, the ado-sync handoff, and the ado-sync handoff do not ask. The main path does not ask. A run that wrote nothing from these handoffs does not ask.

The question is exactly:

The system picture may now be out of date. Run `/crav1-refresh-system-notes`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-refresh-system-notes`. Do not open the impact question from this offer. Do not edit the picture in this turn.

## Imported sources

When the new information is a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that will be quoted, or a paste of a mail, transcript, minutes, or chat, follow [references/sources.md](sources.md) (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`; plugin: this skill’s `references/sources.md`).

That check flags personal data with a keep or redact recommendation. An item it cannot place has no recommendation and is asked, all such items in one questions call. Secrets are redacted, by kind only, and are never a choice. When no transfer data policy exists, it asks once, then may write the rule after a yes. Cursor: `.cursor/rules/crav1-transfer-data-policy.mdc`. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. It never writes a secrets choice into that file. The template is `assets/crav1-transfer-data-policy.mdc`. For a mail, it lists each embedded image, inline or attached. It recommends convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. It asks once. Nothing is written to the source folder until every image has an answer. Auto-accept applies to those recommendations only when the transfer data policy clearly covers them.

Write `docs/sources/YYYY-MM-DD-<slug>/` once for that source, before the quote, when this run has not already written that folder. Then add the `Source:` and `Trace:` lines on the quote. Do not commit.

A short fact the user typed, a read-environment fact, and a test suggestion are not imported sources. Do not write `docs/sources/` for those.
