# Match dump to specs: **Impact (before any other edit)**

Part of `branches/dump/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Impact (before any other edit)

The new quotes are already in the matching specs. Read `docs/system/` when it exists (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`) and every other `docs/specs/<slug>/spec.md` (skip `_template`). Other means a spec that did not just receive a new quote, plus any heading on a spec you did edit that the confirmed sort did not already cover. Check whether the new information contradicts or extends the landscape, a repo row, a diagram, an ADR, or another spec.

Also compare each kept quote with research, as **Research compare** in `crav1-add-to-spec` `SKILL.md` says. This question is not an apply option. When it is open, ask it before the landscape question. Do not ask both in the same turn. Do not commit.

When `docs/system/` exists, read this skill's `references/dump-landscape.md` for the glossary and the picture.

Do not edit anything outside the confirmed belongs writes in this step, except the glossary gap, the picture update below, a research mark that `crav1-add-to-spec` `references/research-stale.md` already allowed after a yes, or a clear, a narrowed mark, a resolved line, or an open question that the same file says to write. The clear does not wait for a yes. A note already written under **Write the full note** stays. A source folder already written under **Write the new bits** stays. Do not edit it in this step. Notes are not an impact edit. Do not list them as an apply option. The research mark is not a landscape edit. Do not seed `docs/system/` when it is missing. Say it is missing and that this command does not create it. When that folder is missing, do nothing about a glossary and do nothing about the picture. The research check still runs.

Do not edit `plan.md` or `tasks.md` when they exist, and do not list them as proposed edits. One line in the report when they exist: they were left alone. Adding information does not start planning.

Report:

- If nothing else is affected, say so. Do not ask. `docs/system/` and the specs outside those writes stay as they are.
- If something else is affected, stop and ask. Options only. Use the questions tool when it is available.
  1. **Apply the listed edits**
  2. **Leave the other files alone**
- List each proposed edit in one line: the file, and what would change. One line per file change. No surrounding rewrite.

Do not silently rewrite `docs/system/` or specs the sort did not already write. The glossary write above is one exception: a missing file, or new rows appended to an existing file. The picture update is the other: new lines on the short description, the diagram, and how the parts connect. Apply the other edits only if they pick apply, and only the lines you listed. If they pick leave, do not edit those files. Do not rewrite existing glossary rows or existing picture lines either way. Do not list the picture lines again as an apply option. A listed edit to a `repos.md` row keeps the `Synced at` line in `repos.md`. Do not set it and do not clear it. This command does not record the commit.
