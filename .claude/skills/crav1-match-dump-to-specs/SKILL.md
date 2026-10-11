---
name: crav1-match-dump-to-specs
description: >-
  Sort a later dump of notes, tickets, old docs, diagrams, or screenshots
  onto specs that already exist; one dump may cover one slug or many.
  Quote the new bits into the matching spec.md files. A fact worth keeping
  that is not for an existing spec can be Note, which writes docs/notes/.
  Then report whether docs/system/ or another spec has to change. A kept
  quote is compared with docs/research/ and Research findings; research is
  marked stale only after a yes. Does not create a slug or seed
  docs/system/. When that folder exists, fills a missing glossary.md or
  appends new words only; a meaning not stated is `to be researched`. A
  clear answer to a spec open question is linked under it with the
  confirmed sort; unclear stays open. A source that shows a question being
  asked gives the asked-on date. The same pass adds what is new to the
  short description, the diagram, and how the parts connect. Does not
  write code, plan, implement, or commit.
disable-model-invocation: true
icon: filter
color: orange
---

# Match dump to specs

You sort a later dump onto specs that already exist. Then you write the new bits into the matching `spec.md` files. Then you check whether `docs/system/` or another spec has to change, and you report that impact. You do not silently rewrite those other files. The glossary append and the picture update are the exceptions: new glossary rows, and new picture lines, when `docs/system/` already exists. You do not rewrite existing glossary rows or existing picture lines. You do not write application code. You do not plan, implement, or commit.

This is not a mode of `/crav1-match-to-specs` or `/crav1-add-to-spec`. Match creates spec folders from repos plus a dump. Add takes information already aimed at one named spec. This skill is the later dump: the folders are already there, and the dump has to be sorted onto them. Do not send this job to those commands, and do not absorb theirs.

Do not copy the match worker that creates folders. Do not use `crav1-match-to-specs` `references/slice.md`. Do not launch a worker. There is no slice subagent.

This is not `/crav1-tighten-spec`. Tighten is for mushy wording. This skill is for a dump. If the message is only “make this tighter” and brings no dump, tell them `/crav1-tighten-spec` and do not edit.

This is not `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, or `/crav1-ideas-to-spec`. Those create the folders. Do not create a slug here.

This is not `/crav1-whats-known-about`. That command answers a question about the status of one feature, slice, or resource and writes nothing. This command sorts a dump. A status question with no dump is that other command.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding information does not start planning and does not write `plan.md` or `tasks.md`.

## Input

Everything after `/crav1-match-dump-to-specs`, and every `@`, is the dump: notes, tickets, old docs, diagrams, screenshots. Size is not a limit. Do not ask them to shrink it. Do not split one dump into several runs. One dump may be a lot about one slug, or it may cover many slugs. Both are this command.

Do not ask for a slug first. A hint in the dump about where something belongs is evidence for the sort, not a requirement. If it names a slug, use that. If it does not, match by what it says. An `@` of one spec folder is that kind of hint. It does not limit the sort to that folder.

## Specs (no sort yet)

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

Read those folders before you sort. Do not ask which slug.

If there are no spec folders, stop. Point at `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, or `/crav1-match-to-specs`. Do not create a slug. Do not seed `docs/system/`.

## Already noted

Read `docs/notes/` before the sort, when that folder exists. Skip `_template`. Compare each fact's words to the quote in each note. The same words are the same item. The `From` label is not part of that compare.

When the quote is already in a note, the line shows `Already noted: docs/notes/<file>.md`. Do not put it on the Note pile as a new note. Do not write a second file.

## Sort (no writes yet)

Read every existing `spec.md` (skip `_template`) and the dump. Then show four piles. Do not write files.

1. **Belongs to this spec** — new bits that are a decision, a clarification, information, or an answer for an existing slug. Name `docs/specs/<slug>/` and the heading the words would go under. Quote the dump. The line says `Recommendation: Keep.`
2. **Already in that spec** — the dump repeats what that `spec.md` already says. Name the slug and the heading. Do not plan a second copy.
3. **Note** — worth keeping, and not a decision, a clarification, information, or an answer for an existing spec. Exploration with no feature yet, input that may feed several features, technical debt, and general information gathering go here. A mapping of tables and views when no spec covers it goes here. Quote the dump. The line says `Recommendation: Note — keep it in the repo without tying it to a spec yet.`
4. **Does not fit any of them** — the dump’s words that match no existing spec and are not a note. Leave them on the list. Do not invent a slug.

Before the piles, read `## Open questions` on every spec with the records under each question. Follow `crav1-add-to-spec` `references/open-questions.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/open-questions.md`; plugin: sibling `skills/crav1-add-to-spec/references/open-questions.md`). Match by meaning, whether the question is asked, pending, or not marked. A fact that clearly answers one goes on the **belongs** pile with `Answers: "<question>"` and `Linked with the sort.` There is no separate question for it. When it would change a spec line, the line also says `Then: /crav1-resolve-questions for <slug>.` A fact that only might answer, or answers part, keeps its pile and shows `Possible answer to: "<question>". The question stays open.` When the dump is a mail, a transcript, or a chat that shows a spec open question being asked, list it under `Asked in this dump` with the spec and the date the source shows. That is not a pile.

A greeting, scheduling, and thanks are noise. Drop them. They are not a note. Dismiss stays for that noise. A dropped line is not on a pile.

A named slug in the dump is evidence. It does not skip the other piles. Something with no slug is sorted by what it says.

Split a passage that is partly new and partly already there. One fact is in one pile.

Put every fact you will treat as accepted on the sort. A fact you leave off stays inferred.

This skill does not ask keep, leave, dismiss, or note one fact at a time. It does not add an accept-all question. The recommendation is on the sort. The user confirms or edits the sort. That confirmation is the choice.

On an edit, the user can mark a fact keep, leave, dismiss, or note. Keep moves it to belongs. Leave and dismiss write nothing. Note keeps it on the Note pile. Do not ask a second question after Note. Do not ask what kind of note it is.

Stop. They confirm or edit the sort. Do not write files. That confirmation is the only stop before writes. Do not ask for a slug. Do not open a mushy interview, an architecture interview, or an export-format question. If they edit the sort, the edit is the confirmation. Do not ask again. Use their slugs and piles. A fact they struck, or that you never put on the sort, stays labeled inferred if it appears later. Confirming the sort confirms the facts they left on it, including the Note pile.

## Write the notes

When the confirmed sort leaves a fact on the Note pile, and it is not already noted, write one note. Do not ask what kind of note it is. Do not create a slug. Do not hand it to a starter.

A note is not owned by one spec. The home is `docs/notes/` in the product repo.

Create `docs/notes/` and `docs/notes/index.md` when they are missing. The shapes are this skill’s `assets/note.md` and `assets/index.md` (same files as `docs/notes/_template/note.md` and `docs/notes/_template/index.md`; drop-in: `.claude/skills/crav1-match-dump-to-specs/assets/`; plugin: this skill’s `assets/`).

One file per note: `docs/notes/YYYY-MM-DD-<slug>.md`. `YYYY-MM-DD` is the date the source shows. Do not invent a date. When the source shows no date, the file is `docs/notes/undated-<slug>.md`. `<slug>` is a short name from the subject or the quote. Lowercase. Hyphens. Do not put a person's name in the slug. A second note on the same day gets its own slug. When that file already exists and the quote is different, pick another slug. Do not overwrite a note.

The note file has:

- a title
- the date, or `not shown` when the source shows no date
- the quote, verbatim. When the dump is a mail, minutes, a transcript, or a chat, it starts with `From <kind> <date>.` when a date is shown, otherwise `From <kind>.` The kind is `email`, `meeting`, or `chat`, from what the input shows. Do not guess. When the dump is not one of those, it starts with `From the dump <date>.` when a date is shown, otherwise `From the dump.` Keep a speaker and a time in the quote when the input showed them. Do not paraphrase.
- `Source: docs/sources/YYYY-MM-DD-<slug>/` when the input was imported. When it was not, omit that line.
- `## Used by`, with nothing under it

When the input was imported, follow the imported-sources convention before the note, in **Write the new bits**. One source folder for that source. The note's `Source:` line is that folder. Do not ask the imported-sources questions a second time for a folder this run already wrote.

`docs/notes/index.md` gets one line for the new note: title, date, status `open`, and an empty used-by cell. The title links to the file. One line looks like `| [Source to target mapping](2026-10-06-source-to-target-mapping.md) | 2026-10-06 | open | |`. When the date is not shown, the date cell says `not shown`. Do not rewrite another row.

Do not commit. A leave, a dismiss, and a does-not-fit fact do not get a note.

When a belongs quote is the quote of a note already in `docs/notes/`, add `Used by <slug>` on that note and update the index, the same way `/crav1-add-to-spec` writes it. Status stays open. `Absorbed by <slug>` only when that spec clearly takes the whole note, and only after the user says yes. Partial use never closes the note.

## Write the new bits

When a confirmed quote comes from a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file, follow the imported-sources convention before that quote (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). That check flags personal data with a keep or redact recommendation. An item it cannot place has no recommendation and is asked one at a time. Secrets are redacted, by kind only, and are never a choice. When no transfer data policy exists, it asks once, then may write the rule after a yes. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. It never writes a secrets choice into that file. For a mail, it lists each embedded image, inline or attached. It recommends convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. It asks once. Nothing is written to the source folder until every image has an answer. Auto-accept applies to those recommendations only when the transfer data policy clearly covers them. Write `docs/sources/YYYY-MM-DD-<slug>/` once per source. Add the `Source:` and `Trace:` lines from that file. Do not commit. A quote that is not from an imported source does not get a source folder.

Edit `docs/specs/<slug>/spec.md` for slugs in the confirmed **belongs** pile. An imported source also writes its source folder, as that convention says. Write them in this chat. Do not launch a worker.

For each of those files:

- Quote their words. The quote is the record. Do not replace it with a paraphrase. For a diagram or screenshot, quote the text on it. A reading you add that the file does not state is inferred or it stays out.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not told, and that the file did not already say, is inferred or it stays out. A fact that was not on the confirmed sort stays inferred or stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change their words require.
- Do not change match status unless the new information itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — their words, added this pass.
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. The **already** pile is the report, not a second paste.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line. An imported source is the exception: the `Source:` and `Trace:` lines in the imported-sources convention are required, and `## Trace` is created when it is missing.

A thin spec (match status `not in the code`, or only Match / What the dump says / In the code / Trace / Open questions) stays thin. Put the quote under the heading it belongs to. Add a heading only when their words are that content. Do not add Problem, Goals, Users and journeys, or Acceptance criteria to fill the file out. Do not add `## In the code` unless their words name code that is there.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when they stated a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a wish into a checkbox.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; drop-in: `.claude/skills/crav1-match-dump-to-specs/assets/spec.md`; plugin: this skill’s `assets/spec.md`). A match-shaped spec does not have to grow those headings.

For a confirmed fact with `Answers:`, write the `Answered:` line under that open question, as `references/open-questions.md` says, after the imported-sources check for that source. Do not rewrite the question. Do not remove it from `## Open questions`. Do not change the spec line it would change. Name `/crav1-resolve-questions` for that slug. Do not run it. For each line under `Asked in this dump`, write or replace the `Asked:` line with the date from the source. That date replaces a `Pending:` line, and an `Asked:` line from the user's yes, for the same person. A possible answer writes no `Answered:` line. When the question is one a stale research point waits on, the research re-check below runs.

The **Note** pile is written under **Write the notes**. It does not become a spec. The **does not fit** pile is listed and left alone. Do not create a spec for it. If they say to create one, do not write a folder here. Point at the skill that creates a spec, and do not run it:

- one or two sentences for one feature: `/crav1-spark-to-spec`
- one unstructured pile for one feature: `/crav1-ideas-to-spec`
- several new features, or several repos: `/crav1-intake-to-specs`
- repos that already make up the system, and this leftover is a slice to match: `/crav1-match-to-specs`

## Impact (before any other edit)

The new quotes are already in the matching specs. Read `docs/system/` when it exists (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`) and every other `docs/specs/<slug>/spec.md` (skip `_template`). Other means a spec that did not just receive a new quote, plus any heading on a spec you did edit that the confirmed sort did not already cover. Check whether the new information contradicts or extends the landscape, a repo row, a diagram, an ADR, or another spec.

Also compare each kept quote with research. Follow `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`). Read `docs/research/*.md` and `## Research findings` on the specs this quote touches, and the notes those findings link to. List a clear contradiction and an answered open question. An unclear case is not a hit. Ask before any new mark. Write the stale block and the findings line only after the user says yes. Then offer the revisit draft. The kit drafts only. It does not send it. It does not contact the note's owner. This question is not an apply option. When it is open, ask it before the landscape question. Do not ask both in the same turn. Do not commit. A kept quote that answers a point already waiting is re-checked there too. That re-check does not ask.

Section names for that read, not a file to paste over what exists: this skill’s `assets/system/` (same files as `docs/system/_template/`, including `glossary.md`; drop-in: `.claude/skills/crav1-match-dump-to-specs/assets/system/`; plugin: this skill’s `assets/system/`).

Do not edit anything outside the confirmed belongs writes in this step, except the glossary gap, the picture update below, a research mark that `crav1-add-to-spec` `references/research-stale.md` already allowed after a yes, or a clear, a narrowed mark, a resolved line, or an open question that the same file says to write. The clear does not wait for a yes. A note already written under **Write the notes** stays. A source folder already written under **Write the new bits** stays. Do not edit it in this step. Notes are not an impact edit. Do not list them as an apply option. The research mark is not a landscape edit. Do not seed `docs/system/` when it is missing. Say it is missing and that this command does not create it. When that folder is missing, do nothing about a glossary and do nothing about the picture. The research check still runs.

**Glossary.** When `docs/system/` is missing, do nothing about a glossary. When it exists and `glossary.md` is missing, write only that file from `assets/system/glossary.md`. When `glossary.md` already exists, append only words or abbreviations the dump uses that are not already rows. Do not rewrite, reorder, or edit existing rows. Do not change a Meaning cell that already has text. Source is the dump. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation the dump already uses. When that same dump already says the expansion or meaning, put that text in Meaning. When the dump never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the dump already treats that word as a term. Write the file even when it has no rows. This write is not an apply option, and it does not rewrite any other landscape file except the picture update below. Do not list a rewrite of existing rows.

**Picture.** When `docs/system/` is missing, do nothing about the picture. When it exists, follow [picture.md](../crav1-keep-current/references/picture.md) (drop-in: `.claude/skills/crav1-keep-current/references/picture.md`; plugin: sibling `skills/crav1-keep-current/references/picture.md`). Source is the confirmed new quotes, not a sentence marked inferred. Add what those quotes added to the short description, the diagram, and how the parts connect. Do not rewrite a sentence, a diagram node, a diagram edge, or a connection line that is already there. Do not run `/crav1-keep-current` as a second turn. This write is not an apply option. Do not rewrite existing glossary rows.

Do not edit `plan.md` or `tasks.md` when they exist, and do not list them as proposed edits. One line in the report when they exist: they were left alone. Adding information does not start planning.

Report:

- If nothing else is affected, say so. Do not ask. `docs/system/` and the specs outside those writes stay as they are.
- If something else is affected, stop and ask. Options only. Use the questions tool when it is available.
  1. **Apply the listed edits**
  2. **Leave the other files alone**
- List each proposed edit in one line: the file, and what would change. One line per file change. No surrounding rewrite.

Do not silently rewrite `docs/system/` or specs the sort did not already write. The glossary write above is one exception: a missing file, or new rows appended to an existing file. The picture update is the other: new lines on the short description, the diagram, and how the parts connect. Apply the other edits only if they pick apply, and only the lines you listed. If they pick leave, do not edit those files. Do not rewrite existing glossary rows or existing picture lines either way. Do not list the picture lines again as an apply option. A listed edit to a `repos.md` row keeps the `Synced at` cell. Do not set it and do not clear it. This command does not record the commit.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-finalize-commit` or `/crav1-plan-from-spec`.

Output only:

- Each `docs/specs/<slug>/spec.md` that gained a new quote
- Each note `docs/notes/YYYY-MM-DD-<slug>.md` this pass wrote, and the index line, or that none was written
- Each source folder `docs/sources/YYYY-MM-DD-<slug>/` this pass wrote, or that none was written
- The transfer data policy when this pass wrote it, or that none was written
- What was added (their quotes, labeled new) and what was already there
- Open questions: each answer linked, each possible answer left open, each asked mark written and where its date came from, and each `/crav1-resolve-questions` named, or none
- The does-not-fit list, left alone. If they asked for a new spec, which existing skill you pointed at
- An item already noted, with its path, and that no second file was written
- `glossary.md` when this turn created it or appended rows. If `docs/system/` was missing, say no glossary was written. If no new rows were appended, say so
- Picture lines added, or that the picture is current. If `docs/system/` was missing, say no picture was written
- Impact: nothing else, or the one-line edit list and which option they picked
- Research: each hit, whether it was marked, the note path and the findings line, or that none was marked. The revisit draft when one was written in the chat, or that none was drafted. The clear summary: what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run did not check an updated note
- Next: `/crav1-finalize-commit` if any file changed and they want those spec edits committed (no push). `/crav1-plan-from-spec` only for a slice they choose. Do not run either.

## Style

Be concise. Quote the dump. Prefer the smaller edit. Do not invent content to fill gaps. A missing `glossary.md` is written only when `docs/system/` already exists. New rows are appended to an existing glossary. Existing rows are not rewritten. The picture update adds what is new and does not rewrite what is already there.
