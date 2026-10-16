# Notes (1.61.0)

Every `/crav1-add-to-spec` input (fact, dump, code change, meeting) becomes **one note** that holds the full input and its source. Specs get only their own short points, each with a link to that note. This file is the rule for every skill that writes or reads `docs/notes/`.

## One note per input

- One input, one note. Do not split it. A meeting, a mail, a dump, a code change: the whole text (after the imported-sources redaction). A fact: the fact plus the passage around it, as the user gave it.
- The note is the shared full source. It is **never absorbed**. Do not ask an absorb question. Do not write `Absorbed by`. `used_by` grows as specs take points from it.
- There is no Note choice. Every input is noted, whatever happens to its points. An item that is left or dismissed stays in the full note; nothing extra is written for it.
- No "never used" flag. A note nobody has used yet is just a note.

## Where and named how

`docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md`. The date and the month folder are the **source date**: the meeting date, the mail's sent date, the commit date, the date a file or dump shows. When the source shows no date, use the import date, set `source_date: none`, and say `no source date, filed under the import date` in the report. `<slug>` is a short name from the subject: lowercase, hyphens, no person's name. Never overwrite a note; a clash on a different input picks another slug.

## Shape

The shape is this skill's `assets/note.md` (same file as `docs/notes/_template/note.md`): front matter `title`, `kind`, `source`, `source_date`, `imported`, `source_folder` (when imported), `used_by`, `waiting_for`; then the title, a `Source date: … Imported: …` line, and the full input verbatim.

`source` names the input so it can be recognised again: the mail's subject, sender, and sent date; the meeting date and title; the file path; the commit SHA or range.

## Indexes are generated

Do not edit `docs/notes/index.md` or `docs/notes/YYYY-MM/index.md` by hand. After writing or changing notes, run the generator from the product repo root:

- Cursor drop-in: `python3 .cursor/skills/crav1/crav1-add-to-spec/scripts/notes_index.py`
- Plugin: this skill's `scripts/notes_index.py`
- Claude Code: `python3 .claude/skills/crav1-add-to-spec/scripts/notes_index.py`

`--check` exits 1 when an index differs from the front matter (a product repo can run it in CI). When Python cannot run, say the indexes need a rebuild and name the command; do not hand-edit.

## Writing the spec points

Each matching spec gets only its own short points, quoted as **Add to that spec.md** in `SKILL.md` says, each followed by `Full source: docs/notes/YYYY-MM/<file>.md`. Then add the slug to the note's `used_by`.

A **parked** spec (a `Parked:` line) gets nothing written. Add its slug to the note's `waiting_for`. Say `saved as a note for <slug> (parked)`. Un-park is `/crav1-retire-spec`; it moves the slug from `waiting_for` to `used_by`.

## Duplicate check (before writing)

Lookups for a spec follow the `Full source:` links. Matching new input and the duplicate check read the generated indexes and the note front matter.

- **Same source again** (the same mail, the same meeting date and title, the same file, the same commit): do not write a second note. Say `already imported on <imported date> as docs/notes/YYYY-MM/<file>.md`. Ask, options only: **Reuse the existing note (Recommended)** for specs that took nothing from it yet, or **Skip**. Reuse adds points and `used_by` only for those specs.
- **Same point from a different source:** write the new note as usual. On the spec line that already says it, add the new note as a second source (`Full source: <first>; <second>`). Do not repeat the point.
- **Disagreement:** when the new source says something different about a point already on a spec, do not overwrite. Write the new point under the old one as `**Conflict:** "<new words>" (Full source: <note>) vs the line above`, and list it in the report for the user to decide.

## Old notes

Notes written before 1.61.0 (no front matter, flat in `docs/notes/`, maybe `Absorbed by`) are still read. `Absorbed by <slug>` counts as used by that slug; do not add new ones. Old spec lines keep their source lines; nothing is backfilled. The one-time move into month folders is `notes_index.py migrate` (named by `/crav1-refresh-system-notes`).
