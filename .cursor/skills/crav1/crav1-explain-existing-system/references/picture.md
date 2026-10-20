# crav1-explain-existing-system: picture

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Feature index and the picture

On every run, at the end of the answer, compare `## Feature index` in `docs/system/landscape.md` with the picture. Run this check on a longer answer too. When the notes are missing and `docs/system/landscape.md` can still be read, run it before you finish. When that file cannot be read, there is no list. Do not invent slices. Do not name `/crav1-refresh-system-notes` for this check.

The picture for this check is two places only: the slice's node in `docs/system/diagrams.md`, and its line under `## How the parts connect` in `landscape.md`. The short description is not this check.

Read every index row that has a slug. Skip a row whose slug cell is empty. Include a row whose Notes say `done` or `retired`. Include a spec whose `## Match` status says `done` or `retired`. Do not skip those slices.

Names that count, and only these:

- the slug
- the spec title, the `#` line of `docs/specs/<slug>/spec.md`
- the main resource name: the Repos cell on that index row, and the `Repo:` line under `## Match` when that line is there

A diagram node matches when its id or its label is that slug, that spec title, or that main resource name, as that whole name. A connection line matches when that line names the same whole name as its own token. A shorter piece, a longer name that only contains it, a synonym, or a similar spelling is not a match. Do not fuzzy-match.

A slice is missing entirely when neither the node nor the line matches. It is missing partly when one matches and the other does not. A slice with both a matching node and a matching line is not listed.

This check may read the title line, the feature-index row, and the Match `Status:` and `Repo:` lines. It does not answer the question from the rest of the spec.

At the end of the answer, list each missing slice, one line per slice. Show the status on the line. Copy the Notes cell. When `## Match` has a `Status:` line, show that word too if the Notes cell does not already say it. `done` and `retired` stay visible. When the Notes cell is empty and there is no Match status, the status is `no status`.

- `<slug> — <status> — missing the diagram node and the connection line`
- `<slug> — <status> — missing the connection line`
- `<slug> — <status> — missing the diagram node`

When the list has one or more slices, name `/crav1-refresh-system-notes`. Do not run it. Do not update the picture. When the list is empty, do not name refresh-system-notes for this check.
