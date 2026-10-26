# Convert to note

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.95.1; the rules are unchanged.

1. Write `docs/notes/<YYYY-MM>/<YYYY-MM-DD>-<slug>.md` in the note shape (`docs/notes/_template/note.md`, see `crav1-add-to-spec` `references/notes.md`), dated by the spec's first commit date (the source date), with `imported` today. Front matter `kind: converted spec`, `source: docs/specs/<slug>/spec.md`. The title is the spec's title. Add `Source: docs/specs/<slug>/spec.md (converted <YYYY-MM-DD>)` and `Converted from spec, no research owner`. The body is the spec's content as it was.
2. Run the notes index generator so the note gets its index row. Do not hand-edit an index.
3. Add one line under `## How the parts connect` in `docs/system/landscape.md`: `<title>: reference only, see docs/notes/<YYYY-MM>/<YYYY-MM-DD>-<slug>.md`. Append only. Do not rewrite a line that is there.
4. Remove that slug's feature-index row.
5. Move the rest of the spec folder to `docs/specs/retired/<slug>/` and leave the pointer at the old path.

A converted note has no research owner. Skills that find it stale do not send a revisit request. They show it as stale and stop there.
