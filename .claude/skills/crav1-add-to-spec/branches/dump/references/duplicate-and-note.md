# Match dump to specs: **Duplicate check (1.61.0)**, **Write the full note (1.61.0)**

Part of `branches/dump/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Duplicate check (1.61.0)

Before the sort, run the duplicate check in this skill's `references/notes.md`. The same source again (the same file, mail, or meeting) is not imported twice: say `already imported on <date> as docs/notes/YYYY-MM/<file>.md`, and ask **Reuse the existing note (Recommended)** or **Skip**. Reuse sorts only for specs that took nothing from that note yet. Skip stops. A dump of several files checks each file.

## Write the full note (1.61.0)

After the sort is confirmed, write **one note** holding the whole dump, as this skill's `references/notes.md` says. There is no Note pile and nothing is asked about the note. A dump of several separate sources (different mails, meetings, or files) writes one note per source; never split one source.

- Run the imported-sources convention first, in **Write the new bits**. The note holds the text after its redaction and its `source_folder` is that folder.
- Path: `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` by the **source date** the dump shows. No date: the import date, `source_date: none`, and say so.
- Each belongs quote is followed by `Full source: docs/notes/YYYY-MM/<file>.md`, and the slug goes in the note's `used_by`. A matching parked spec gets nothing; its slug goes in `waiting_for`.
- The same point already on a spec from another source adds this note as a second source on that line. A disagreement is a **Conflict:** line, never an overwrite.
- Never ask an absorb question. Never write `Absorbed by`.
- Run `scripts/notes_index.py` after the note changes. Do not hand-edit an index.

Do not commit.
