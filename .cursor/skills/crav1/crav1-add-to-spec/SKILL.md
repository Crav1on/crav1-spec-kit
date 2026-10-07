---
name: crav1-add-to-spec
description: >-
  Add new information to one existing spec, then report whether docs/system/
  or another spec has to change. Does not silently rewrite those files.
  Does not create a glossary. A missing row on an existing glossary can be
  one listed edit. It is not written unless apply is chosen. A meaning the
  new information does not state is `to be researched`.
  Does not write application code. Does not plan, implement, or commit.
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

## From /crav1-meeting-to-specs

When `/crav1-meeting-to-specs` hands one kept addition for an existing spec, the spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a folder.

The handoff passes the kind and the date. The kind is `meeting`, `email`, or `chat`. Quote the item. Do not replace it with a paraphrase. A `State:` line is not part of the quote. Do not write it. The quote starts with `From <kind> <date>.` when the handoff includes a date, otherwise `From <kind>.` Examples: `From email 2026-10-06.`, `From meeting.` Do not invent a kind or a date. Keep the speaker and the time in the quote when the input showed them. Label it `**New:**` in the section the words belong to, the same way any other new quote is labeled.

Then run **Add to that spec.md** and **Impact** in this skill. The impact check still runs. Do not skip it. Do not write `plan.md` or `tasks.md`. Do not change application code. Do not start Specify, Plan, or Build. Do not ask the picture offer. That offer is only the environment-read and suggest-tests handoffs.

## Picture offer

The handoff sections **From /crav1-environment-read** and **From /crav1-suggest-tests-for-code** ask once at the end of the run, after every item this run wrote. Not after each item. The meeting handoff does not ask. The main path does not ask. A run that wrote nothing from these handoffs does not ask.

The question is exactly:

The system picture may now be out of date. Run `/crav1-keep-current`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-keep-current`. Do not open the impact question from this offer. Do not edit the picture in this turn.

## Input

Everything after `/crav1-add-to-spec`, and every `@`, is input: the new information, and a target when they named one.

## Target (no edits yet)

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

If there are no spec folders, stop. Point at `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, or `/crav1-match-to-specs`. Do not create a slug. Do not seed `docs/system/`.

If they named one existing folder (a path in the message, or one `@` of that folder or its `spec.md`) and no other existing spec could fit the new information, that folder is the target. Do not ask.

If they did not name one, they named a folder that is not there, they named more than one, or more than one existing spec could fit, ask with options only. Use the questions tool when it is available. One option per existing spec folder. Label each option with `docs/specs/<slug>/` and the title line of that `spec.md` when it has one. Do not ask them to type a slug. Do not create a missing folder.

Stop until they pick, when a pick is required.

## Add to that spec.md

Edit only `docs/specs/<slug>/spec.md` in this step.

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

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line.

A thin spec (match status `not in the code`, or only Match / What the dump says / In the code / Trace / Open questions) stays thin. Put the quote under the heading it belongs to. Add a heading only when their words are that content. Do not add Problem, Goals, Users and journeys, or Acceptance criteria to fill the file out. Do not add `## In the code` unless their words name code that is there.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when they stated a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a wish into a checkbox.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; drop-in: `.cursor/skills/crav1/crav1-add-to-spec/assets/spec.md`; plugin: this skill’s `assets/spec.md`). A match-shaped spec does not have to grow those headings.

## Impact (before any other edit)

Read `docs/system/` when it exists (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`) and every other `docs/specs/<slug>/spec.md` (skip `_template`). Check whether the new information contradicts or extends the landscape, a repo row, a diagram, an ADR, or another spec.

Section names for that read, not a file to paste over what exists: this skill’s `assets/system/` (same files as `docs/system/_template/`, including `glossary.md`; drop-in: `.cursor/skills/crav1/crav1-add-to-spec/assets/system/`; plugin: this skill’s `assets/system/`).

Do not edit anything outside the target spec in this step. Do not seed `docs/system/` when it is missing. Say it is missing and that this command does not create it. Do not create `glossary.md`.

When `glossary.md` exists, a missing row that the new information uses can be one of the listed edits to `docs/system/`. When the new information already states the expansion or meaning, that text is Meaning. When it does not, Meaning is `to be researched`. Do not invent the term or the meaning. Do not write TBD or to be decided. Do not rewrite, reorder, or edit an existing row. Do not change a Meaning cell that already has text. Do not write the new row unless they pick apply. A missing `glossary.md` is not a listed edit.

Do not edit `plan.md` or `tasks.md` when they exist, and do not list them as proposed edits. One line in the report when they exist: they were left alone. Adding information does not start planning.

Report:

- If nothing else is affected, say so. Do not ask. `docs/system/` and the other specs stay as they are.
- If something else is affected, stop and ask. Options only. Use the questions tool when it is available.
  1. **Apply the listed edits**
  2. **Leave the other files alone**
- List each proposed edit in one line: the file, and what would change. One line per file change. No surrounding rewrite.

Do not silently rewrite `docs/system/` or other specs. Apply those edits only if they pick apply, and only the lines you listed. If they pick leave, do not edit those files. A listed edit to a `repos.md` row keeps the `Synced at` cell. Do not set it and do not clear it. This command does not record the commit.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-finalize-commit` or `/crav1-plan-from-spec`.

Output only:

- Target `docs/specs/<slug>/spec.md`
- What was added (their quotes, labeled new) and what was already there
- Impact: nothing else, or the one-line edit list and which option they picked
- Next: `/crav1-finalize-commit` if any file changed (no push). `/crav1-plan-from-spec` only if they say they want to start planning this slug. Do not run either.

## Style

Be concise. Quote their words. Prefer the smaller edit. Do not fill gaps.
