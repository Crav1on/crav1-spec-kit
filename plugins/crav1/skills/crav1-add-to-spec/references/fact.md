# crav1-add-to-spec: a fact

Read when the branch is a fact, or when a handoff in `SKILL.md` says to run a section named here. Moved word for word from `SKILL.md` in 1.71.3; the rules are unchanged. Shared steps stay in `SKILL.md`.

## Input

Everything after `/crav1-add-to-spec`, and every `@`, is input: the new information, and a target when they named one.

## Target (no edits yet)

Spec folders are `docs/specs/<slug>/` with a `spec.md`. Skip `_template`.

If there are no spec folders, stop. Point at `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, or `/crav1-existing-to-specs`. Do not create a slug. Do not seed `docs/system/`.

If the input is a file under `docs/research/` and there is no new quote for a spec, run the clear section, [references/research-stale-clear.md](research-stale-clear.md). Do not ask the user whether the update resolves the mark. Do not ask for a slug. Do not paste the note into a spec.

If they named one existing folder (a path in the message, or one `@` of that folder or its `spec.md`) and no other existing spec could fit the new information, that folder is the target. Do not ask.

If they did not name one, they named a folder that is not there, they named more than one, or more than one existing spec could fit, ask with options only. Use the questions tool when it is available. One option per existing spec folder. Label each option with `docs/specs/<slug>/` and the title line of that `spec.md` when it has one. Do not ask them to type a slug. Do not create a missing folder.

Stop until they pick, when a pick is required.

## Imported sources

Read `references/handoffs-imported-sources.md` ("Imported sources") only when the input is a mail, transcript, screenshot or other original.

## Add to that spec.md

Edit `docs/specs/<slug>/spec.md` in this step. An imported source also writes `docs/sources/YYYY-MM-DD-<slug>/` and, after a yes, one `.gitattributes` line, as [references/sources.md](sources.md) says, with the kind file it names. When an image inside a mail is converted to text, that folder also holds `<name>.md`. Do not write any other file in this step, except the note and its `used_by` under **Notes**.

- Quote their words. The quote is the record. Do not replace it with a paraphrase.
- Label what is new versus what was already there.
- Keep inferred facts labeled inferred. A fact you were not told, and that the file did not already say, is inferred or it stays out.
- Do not invent acceptance, architecture, or tasks to fill gaps. A proposed ADR or diagram edit later is only a change their words require.
- Do not change match status unless the new information itself says the status changed.
- Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md` in the spec folder.
- Do not replace the file with a template.

Labels, in the section the words belong to:

- `**New:** "…"` — their words, added this pass, in sorted place among the `**New:**` lines there (1.84.0, `references/merge-safe.md`).
- `**Already there:**` — do not paste a second copy. Leave the existing sentence. Say in the report which heading already had it.
- `**Inferred:**` — a connection you drew. Not an accepted fact.

Before the quote, read `## Open questions` on the target spec with the records under each question. When the new information clearly answers one, write an `Answered:` line under that question as [references/open-questions.md](open-questions.md) says, and say so in the report. An unclear or partial answer is shown in the report as a possible answer. The question stays open. When the new information is a mail, a transcript, or a chat that shows a question being asked, write the `Asked:` line with the date from the source. When the answer would change a spec line, name `/crav1-resolve-open-questions`. Do not run it. A clear answer to an open question on another spec is one listed impact edit.

When the file already has `## Trace`, append one line: what this pass marked new, already there, and inferred. Do not create `## Trace` only for that line. An imported source is the exception: the `Source:` and `Trace:` lines in [references/sources.md](sources.md) are required, and `## Trace` is created when it is missing so that line has a heading.

A thin spec stays thin, as **Thin spec** in `SKILL.md` says.

A fuller spec keeps its headings. Place the quote in the section it extends. Add an acceptance checkbox only when they stated a check a stranger could run, and label that checkbox `**New:**`. That checkbox stays yes/no. Name unit, system, or browser only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list. Do not turn a wish into a checkbox.

Expected headings when the file already uses the full spec shape: this skill’s `assets/spec.md` (same file as `docs/specs/_template/spec.md`; drop-in: `.cursor/skills/crav1/crav1-add-to-spec/assets/spec.md`; plugin: this skill’s `assets/spec.md`). A match-shaped spec does not have to grow those headings.

## Notes (1.61.0)

Read `references/notes-1.61.md` ("Notes (1.61.0)") only when you save the input as a note (every add saves one).

## Impact (before any other edit)

Read `docs/system/` when it exists (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`) and every other `docs/specs/<slug>/spec.md` (skip `_template`). Check whether the new information contradicts or extends the landscape, a repo row, a diagram, an ADR, or another spec.

Also compare the kept quote with research, as **Research compare** in `SKILL.md` says.

Section names for that read, not a file to paste over what exists: this skill’s `assets/system/` (same files as `docs/system/_template/`, including `glossary.md`; drop-in: `.cursor/skills/crav1/crav1-add-to-spec/assets/system/`; plugin: this skill’s `assets/system/`).

Do not edit anything outside the target spec in this step, except a research mark after a yes, or a clear, a narrowed mark, a resolved line, or an open question that [references/research-stale.md](research-stale.md) says to write. The clear does not wait for a yes. A source folder already written under **Imported sources** stays. A note already written under **Notes** stays. Neither is an impact edit. The research mark is not a landscape edit. Do not seed `docs/system/` when it is missing. Say it is missing and that this command does not create it. Do not create `glossary.md`. Do not commit.

When `glossary.md` exists, a missing row that the new information uses can be one of the listed edits to `docs/system/`. When the new information already states the expansion or meaning, that text is Meaning. When it does not, Meaning is `to be researched`. Do not invent the term or the meaning. Do not write TBD or to be decided. Do not rewrite, reorder, or edit an existing row. Do not change a Meaning cell that already has text. Do not write the new row unless they pick apply. A missing `glossary.md` is not a listed edit.

Do not edit `plan.md` or `tasks.md` when they exist, and do not list them as proposed edits. One line in the report when they exist: they were left alone. Adding information does not start planning.

Report:

- If nothing else is affected, say so. Do not ask. `docs/system/` and the other specs stay as they are. The research question is separate. Ask it when [references/research-stale.md](research-stale.md) lists a hit.
- If something else is affected, stop and ask. Options only. Use the questions tool when it is available. When the research question is also open, ask that one first. Do not ask this landscape question in that same turn.
  1. **Apply the listed edits**
  2. **Leave the other files alone**
- List each proposed edit in one line: the file, and what would change. One line per file change. No surrounding rewrite.

Do not silently rewrite `docs/system/` or other specs. Apply those edits only if they pick apply, and only the lines you listed. If they pick leave, do not edit those files. A listed edit to a `repos.md` row keeps the `Synced at` line in `repos.md`. Do not set it and do not clear it. This command does not record the commit.

## Stop

Read `references/stop.md` ("Stop") only when the input cannot be placed or the add must stop.

## Style

Be concise. Quote their words. Prefer the smaller edit. Do not fill gaps.
