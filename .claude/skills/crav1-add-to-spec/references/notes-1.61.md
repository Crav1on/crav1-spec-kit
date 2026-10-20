# crav1-add-to-spec: notes 1.61

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Notes (1.61.0)

Every input becomes **one note** with the full input and its source, as [references/notes.md](notes.md) says. That file is the rule; follow it for the path (`docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md` by **source date**, `Imported: <date>`), the shape, the generated indexes, the duplicate check, and parked specs.

For a fact: the note holds the fact plus the passage around it. Write the note before the spec quote. The spec quote is this spec's own short point, followed by `Full source: docs/notes/YYYY-MM/<file>.md`. Add the slug to the note's `used_by`. When the input came through a branch or a handoff that already wrote the note, reuse that note; do not write a second one.

- Run the duplicate check first. The same source again is `already imported on <date> as <note>`, reuse or skip; never a second copy. The same point from another source adds a second source to the spec line. A disagreement is written as a **Conflict:** line, never an overwrite.
- A parked spec (a `Parked:` line) gets nothing written; its slug goes in the note's `waiting_for`. Say `saved as a note for <slug> (parked)`. Skip `docs/specs/retired/` and `Moved:` pointers as targets.
- Never ask an absorb question. Never write `Absorbed by`. An old note's `Absorbed by` is read as used by.
- Do not edit `docs/notes/index.md` or a month index by hand. Run `scripts/notes_index.py` after the note write.
- A note converted from a spec says `Converted from spec, no research owner`. When it is stale, show it as stale and do not offer a revisit request.

Do not commit. This is not an impact question. Do not list the note as an apply option.
