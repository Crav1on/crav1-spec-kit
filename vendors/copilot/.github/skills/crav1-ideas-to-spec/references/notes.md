# crav1-ideas-to-spec: notes

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## A quoted note

When this run quotes a note from `docs/notes/` (month folders `docs/notes/YYYY-MM/` since 1.61.0; older flat notes are still read), add `<slug>` to that note's `used_by` front matter (an old note without front matter gets a `Used by <slug>` line under `## Used by`), and link the note from the spec line as `Full source: <note path>`. Then run the notes index generator as `crav1-add-to-spec` `references/notes.md` says; do not hand-edit an index. Many specs can be listed. A note is not owned by one spec and is never absorbed: do not write `Absorbed by`. Do not commit. The same write is in `/crav1-add-to-spec`. This is not the optional `notes.md` in the spec folder.
