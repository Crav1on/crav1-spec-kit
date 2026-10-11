---
name: crav1-add-to-spec
description: >-
  Add new information to one existing spec, then report whether
  docs/system/ or another spec has to change; edits there only on apply.
  Does not create a glossary; a missing row is one listed edit. A meaning
  not stated is `to be researched`. An imported original follows
  references/sources.md and goes under docs/sources/ before the quote; the
  personal-data check recommends keep or redact, redacts secrets, and may
  write the transfer data policy after a yes. A quoted note in docs/notes/
  gets Used by; Absorbed by only after a yes. A kept quote is compared
  with docs/research/ and Research findings and marked stale only after a
  yes; unclear is not marked. May draft a revisit request for the note's
  owner; does not send it. An updated research note is checked per listed
  point, an older mark is split into its hits, and its open questions are
  routed, without asking. A clear answer to an open question is linked
  under it (references/open-questions.md); unclear stays open. Does not
  plan, implement, write code, or commit.
disable-model-invocation: true
icon: file-plus
color: blue
---

# Add to spec

You add new information to **one existing** spec. Then you check whether `docs/system/` or another spec has to change, and you report that impact. You do not silently rewrite those other files. You do not write application code. You do not plan, implement, or commit.

This is not `/crav1-tighten-spec`. Tighten is for mushy wording. This skill is for new information. If the message is only “make this tighter” and brings no new fact, tell them `/crav1-tighten-spec` and do not edit.

This is not `/crav1-match-to-specs`, `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, or `/crav1-ideas-to-spec`. Those create the folders. This skill updates one spec that already exists. Do not send this job to those commands, and do not absorb theirs. Do not create a new slug here.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding information does not start planning and does not write `plan.md` or `tasks.md`.

## From /crav1-environment-read

When `/crav1-environment-read` hands a confirmed fact for a slice Match already owns, run only this section. Add that quote to that spec only. The quote starts with `Seen in <host> <environment>.` When the quote says `shared with prod`, `prod only`, or shape and connections only, keep that label. Do not replace it with a paraphrase. Do not mark it as something the code shows. Do not change match status. Do not create a slug. Do not open the impact question. Do not edit `docs/system/` or another spec from this handoff. If no spec has `## Match` for that slice, write nothing. Do not start Specify, Plan, or Build. Do not continue into the main path. After the last environment-read item in this run, follow **Picture offer**, then stop.

## From /crav1-suggest-tests-for-code

When `/crav1-suggest-tests-for-code` hands one suggestion for an existing spec, run only this section. The spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a folder. Do not open the impact question. Do not edit `docs/system/` or another spec. Do not write `plan.md` or `tasks.md`. Do not write test code. Do not change application code. Do not start Specify, Plan, or Build. Do not continue into the main path. After the last suggestion in this run, follow **Picture offer**, then stop.

**Keep.** Quote the suggestion. Do not replace it with a paraphrase. Add one acceptance checkbox because it is a check a stranger could run. Label it `**New:**`. The checkbox stays yes/no. Name the kind the suggestion already named: unit for a function’s checks, browser for a page, integration for a boundary. Do not invent another check. Do not add another kind.

**Dismiss.** Quote the suggestion under `## Dismissed test suggestions`. The line starts with `Dismissed test suggestion.` Do not reword the check. Create that heading only when it is missing. Do not add an acceptance checkbox. Do not turn it into a goal. Plan does not turn this line into a task. The next run of `/crav1-suggest-tests-for-code` does not offer it.

## From /crav1-specs-to-ado

When `/crav1-specs-to-ado` hands a change that belongs in the spec before a Feature preview is rebuilt, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Quote the change. Do not replace it with a paraphrase. Label it `**New:**`. Then run **Add to that spec.md** and **Impact**. Do not write `work-item.md` from this handoff. That skill writes the id after Azure Boards accepts the Feature. Do not start Specify, Plan, or Build.

## From /crav1-ado-to-specs

When `/crav1-ado-to-specs` hands one kept change or one answer for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a spec folder.

Quote the item. Do not replace it with a paraphrase. A kept Azure Boards change starts with `From ADO <date>. <who>.` when the handoff includes a date and a person. When the handoff has a date and no person, it starts with `From ADO <date>.` An answer the user gave starts with `From the user <date>. Answer to the ADO question.` Do not invent a date or a person. Label it `**New:**` in the section the words belong to. An open question from a Feature discussion goes under `## Open questions`.

Then run **Add to that spec.md** and **Impact**. The impact check still runs. Do not write `plan.md`, `tasks.md`, or `work-item.md`. Do not change application code. Do not start Specify, Plan, or Build. Do not ask the picture offer.

## From /crav1-meeting-to-specs

When `/crav1-meeting-to-specs` hands one kept addition for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a spec folder. A source folder that handoff already wrote stays. When it wrote none and the quote is an imported source, **Imported sources** writes that folder.

The handoff passes the kind and the date, and the source folder when that skill already wrote one. The kind is `meeting`, `email`, or `chat`. Quote the item. Do not replace it with a paraphrase. A `State:` line is not part of the quote. Do not write it. The quote starts with `From <kind> <date>.` when the handoff includes a date, otherwise `From <kind>.` Examples: `From email 2026-10-06.`, `From meeting.` Do not invent a kind or a date. Keep the speaker and the time in the quote when the input showed them. Label it `**New:**` in the section the words belong to, the same way any other new quote is labeled.

When the handoff includes a source folder, add the `Source:` and `Trace:` lines from [references/sources.md](references/sources.md). Do not ask the mail, image, binary, or personal-data questions again. Do not write a second copy of that folder. When the handoff has no folder and the quote is an imported source, follow **Imported sources** before the quote.

When the handoff includes a note path, that quote comes from that note. Run **Notes** after the spec quote. Do not ask what kind of note it is.

Then run **Add to that spec.md** and **Impact** in this skill. The impact check still runs, including research. Follow [references/research-stale.md](references/research-stale.md). Do not skip it. Do not run that research check a second time. Do not write `plan.md` or `tasks.md`. Do not change application code. Do not start Specify, Plan, or Build. Do not ask the picture offer. That offer is only the environment-read and suggest-tests handoffs.

## From an import: answer links and asked marks

When `/crav1-meeting-to-specs` hands an answer link or an asked mark for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not ask keep or apply. Follow [references/open-questions.md](references/open-questions.md).

- An answer link writes one `Answered:` line under that open question: the date, who, the kind, the quote as handed (after any redaction), and the source folder. Do not paraphrase. Do not rewrite the question. Do not remove it from `## Open questions`. Do not change any other spec line. When the answer would change a spec line, name `/crav1-resolve-questions` for that slug. Do not run it.
- An asked mark writes or replaces the `Asked:` line for that person under that question, with the date from the source. It replaces a `Pending:` line for the same person.

When the handoff includes a source folder, add the `Source:` and `Trace:` lines from [references/sources.md](references/sources.md). Do not ask the imported-sources questions again.

Then run **Impact** for the research part only. When the question is one a stale research point waits on, follow the answered-later part of [references/research-stale.md](references/research-stale.md). Do not ask the user whether the point is settled. Do not ask the landscape question for an answer link. Do not run the picture offer. Do not commit.

## Picture offer

The handoff sections **From /crav1-environment-read** and **From /crav1-suggest-tests-for-code** ask once at the end of the run, after every item this run wrote. Not after each item. The meeting handoff, the specs-to-ado handoff, and the ado-to-specs handoff do not ask. The main path does not ask. A run that wrote nothing from these handoffs does not ask.

The question is exactly:

The system picture may now be out of date. Run `/crav1-keep-current`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-keep-current`. Do not open the impact question from this offer. Do not edit the picture in this turn.

## Input

Everything after `/crav1-add-to-spec`, and every `@`, is input: the new information, and a target when they named one.

## Target (no edits yet)

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

If there are no spec folders, stop. Point at `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, or `/crav1-match-to-specs`. Do not create a slug. Do not seed `docs/system/`.

If the input is a file under `docs/research/` and there is no new quote for a spec, run the clear section of [references/research-stale.md](references/research-stale.md). Do not ask the user whether the update resolves the mark. Do not ask for a slug. Do not paste the note into a spec.

If they named one existing folder (a path in the message, or one `@` of that folder or its `spec.md`) and no other existing spec could fit the new information, that folder is the target. Do not ask.

If they did not name one, they named a folder that is not there, they named more than one, or more than one existing spec could fit, ask with options only. Use the questions tool when it is available. One option per existing spec folder. Label each option with `docs/specs/<slug>/` and the title line of that `spec.md` when it has one. Do not ask them to type a slug. Do not create a missing folder.

Stop until they pick, when a pick is required.

## Imported sources

When the new information is a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that will be quoted, or a paste of a mail, transcript, minutes, or chat, follow [references/sources.md](references/sources.md) (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: this skill’s `references/sources.md`).

That check flags personal data with a keep or redact recommendation. An item it cannot place has no recommendation and is asked one at a time. Secrets are redacted, by kind only, and are never a choice. When no transfer data policy exists, it asks once, then may write the rule after a yes. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. It never writes a secrets choice into that file. The template is `assets/crav1-transfer-data-policy.mdc`. For a mail, it lists each embedded image, inline or attached. It recommends convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. It asks once. Nothing is written to the source folder until every image has an answer. Auto-accept applies to those recommendations only when the transfer data policy clearly covers them.

Write `docs/sources/YYYY-MM-DD-<slug>/` once for that source, before the quote, when this run has not already written that folder. Then add the `Source:` and `Trace:` lines on the quote. Do not commit.

A short fact the user typed, an environment-read fact, and a test suggestion are not imported sources. Do not write `docs/sources/` for those.

## Add to that spec.md

Edit `docs/specs/<slug>/spec.md` in this step. An imported source also writes `docs/sources/YYYY-MM-DD-<slug>/` and, after a yes, one `.gitattributes` line, as [references/sources.md](references/sources.md) says. When an image inside a mail is converted to text, that folder also holds `<name>.md`. Do not write any other file in this step. A note's `Used by` line is **Notes**, not this step.

- Quote their words. The quote is the record. Do not replace it with a paraphrase.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not told, and that the file did not already say, is inferred or it stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change their words require.
- Do not change match status unless the new information itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — their words, added this pass.
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. Say in the report which heading already had it.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

Before the quote, read `## Open questions` on the target spec with the records under each question. When the new information clearly answers one, write an `Answered:` line under that question as [references/open-questions.md](references/open-questions.md) says, and say so in the report. An unclear or partial answer is shown in the report as a possible answer. The question stays open. When the new information is a mail, a transcript, or a chat that shows a question being asked, write the `Asked:` line with the date from the source. When the answer would change a spec line, name `/crav1-resolve-questions`. Do not run it. A clear answer to an open question on another spec is one listed impact edit.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line. An imported source is the exception: the `Source:` and `Trace:` lines in [references/sources.md](references/sources.md) are required, and `## Trace` is created when it is missing so that line has a heading.

A thin spec (match status `not in the code`, or only Match / What the dump says / In the code / Trace / Open questions) stays thin. Put the quote under the heading it belongs to. Add a heading only when their words are that content. Do not add Problem, Goals, Users and journeys, or Acceptance criteria to fill the file out. Do not add `## In the code` unless their words name code that is there.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when they stated a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a wish into a checkbox.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; drop-in: `.claude/skills/crav1-add-to-spec/assets/spec.md`; plugin: this skill’s `assets/spec.md`). A match-shaped spec does not have to grow those headings.

## Notes

A note is not owned by one spec. This section runs when the quote just written into the spec comes from a note in `docs/notes/`. That is when the user pointed at that file, the handoff passed that path, or the quote is the quote already in a note. Skip `_template`. When no note matches, write nothing here.

The file shape is this skill’s `assets/note.md` and `assets/index.md` (same files as `docs/notes/_template/note.md` and `docs/notes/_template/index.md`; drop-in: `.claude/skills/crav1-add-to-spec/assets/`; plugin: this skill’s `assets/`). Do not create a note here. Meeting and match-dump create notes.

Add one line under `## Used by` on that note:

`Used by <slug>`

`<slug>` is the spec this run quoted into. Do not add a line that is already there. Update that note's row on `docs/notes/index.md`. The used-by cell lists every slug on the note, separated by `; `. Do not rewrite the title or the date. Status stays `open`. Many specs can be listed.

Partial use never closes the note. When the spec quote is only part of the note, do not ask. Do not write `Absorbed by`.

When this spec clearly takes the whole note, ask once. The whole note means the spec quote is the note's quote, not a part of it. When that is unclear, it is partial. Do not guess.

The question is: Absorb this note into <slug>?

Options are only:

1. **Yes**
2. **No**

Use the questions tool when it is available. Stop until the user picks.

Yes adds this line under `## Used by`:

`Absorbed by <slug>`

Yes sets that index row's status to `absorbed`. No leaves the status `open`. The `Used by` line stays either way.

When the note is already absorbed, do not ask again. Another spec can still add `Used by <slug>`. Status stays `absorbed`.

Do not commit. This is not an impact question. Do not list the note as an apply option.

## Impact (before any other edit)

Read `docs/system/` when it exists (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`) and every other `docs/specs/<slug>/spec.md` (skip `_template`). Check whether the new information contradicts or extends the landscape, a repo row, a diagram, an ADR, or another spec.

Also compare the kept quote with research. Follow [references/research-stale.md](references/research-stale.md). Read `docs/research/*.md` and `## Research findings` on the specs this quote touches, and the notes those findings link to. List a clear contradiction and an answered open question. An unclear case is not a hit. Ask before any new mark. Write the stale block and the findings line only after the user says yes. Then offer the revisit draft. The kit drafts only. It does not send it. It does not contact the note's owner. When the user pointed this command at an updated note in `docs/research/`, or this run writes one, follow the clear section of that file. Judge each listed point. An older mark with no point lines is not one point. Split it as that file says. Also route the note's own open questions when the answer lies outside the note's owner. That still runs when the mark clears. Do not ask the user whether the update resolves the mark. A kept quote that answers a point already waiting is re-checked there too. That re-check does not ask.

Section names for that read, not a file to paste over what exists: this skill’s `assets/system/` (same files as `docs/system/_template/`, including `glossary.md`; drop-in: `.claude/skills/crav1-add-to-spec/assets/system/`; plugin: this skill’s `assets/system/`).

Do not edit anything outside the target spec in this step, except a research mark after a yes, or a clear, a narrowed mark, a resolved line, or an open question that [references/research-stale.md](references/research-stale.md) says to write. The clear does not wait for a yes. A source folder already written under **Imported sources** stays. A note line already written under **Notes** stays. Neither is an impact edit. The research mark is not a landscape edit. Do not seed `docs/system/` when it is missing. Say it is missing and that this command does not create it. Do not create `glossary.md`. Do not commit.

When `glossary.md` exists, a missing row that the new information uses can be one of the listed edits to `docs/system/`. When the new information already states the expansion or meaning, that text is Meaning. When it does not, Meaning is `to be researched`. Do not invent the term or the meaning. Do not write TBD or to be decided. Do not rewrite, reorder, or edit an existing row. Do not change a Meaning cell that already has text. Do not write the new row unless they pick apply. A missing `glossary.md` is not a listed edit.

Do not edit `plan.md` or `tasks.md` when they exist, and do not list them as proposed edits. One line in the report when they exist: they were left alone. Adding information does not start planning.

Report:

- If nothing else is affected, say so. Do not ask. `docs/system/` and the other specs stay as they are. The research question is separate. Ask it when [references/research-stale.md](references/research-stale.md) lists a hit.
- If something else is affected, stop and ask. Options only. Use the questions tool when it is available. When the research question is also open, ask that one first. Do not ask this landscape question in that same turn.
  1. **Apply the listed edits**
  2. **Leave the other files alone**
- List each proposed edit in one line: the file, and what would change. One line per file change. No surrounding rewrite.

Do not silently rewrite `docs/system/` or other specs. Apply those edits only if they pick apply, and only the lines you listed. If they pick leave, do not edit those files. A listed edit to a `repos.md` row keeps the `Synced at` cell. Do not set it and do not clear it. This command does not record the commit.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-finalize-commit` or `/crav1-plan-from-spec`.

Output only:

- Target `docs/specs/<slug>/spec.md`
- Source folder `docs/sources/YYYY-MM-DD-<slug>/` when this pass wrote one, or that none was written
- The note line when this pass wrote `Used by` or `Absorbed by`, or that none was written
- The transfer data policy when this pass wrote it, or that none was written
- What was added (their quotes, labeled new) and what was already there
- Open questions: each answer linked, each possible answer left open, each asked mark written and where its date came from, or none
- Impact: nothing else, or the one-line edit list and which option they picked
- Research: each hit, whether it was marked, the note path and the findings line, or that none was marked. The revisit draft when one was written in the chat, or that none was drafted. The clear summary: what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run did not check an updated note
- Next: `/crav1-finalize-commit` if any file changed (no push). `/crav1-plan-from-spec` only if they say they want to start planning this slug. Do not run either.

## Style

Be concise. Quote their words. Prefer the smaller edit. Do not fill gaps.
