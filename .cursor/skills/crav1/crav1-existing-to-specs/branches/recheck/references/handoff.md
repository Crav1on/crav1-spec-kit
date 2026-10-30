# Repos vs specs: what to do with each gap

Part of `branches/recheck/BRANCH.md`, read only when the report lists at least one gap. Paths in backticks are relative to the skill folder unless they start with `docs/`.

Ask in one batch. For each gap, one choice, the recommended one first:

- **Add to `<nearest spec>` (Recommended when a nearest spec exists):** after a yes, hand the gap (repo, path, what it does) to the fact branch of `/crav1-add-to-spec` for that spec. That skill writes the quote by its own rules. This branch writes nothing into the spec.
- **New spec:** name `/crav1-spark-to-spec` (one feature) or `/crav1-ideas-to-spec` (several), with the gap as the input line. Do not run it.
- **Ignore:** move the line under `## Dismissed` in `## Code with no slice` in `docs/system/landscape.md`. It is not offered again.
- **Leave:** keep the line in the note. Nothing else changes.

A headless or bot run does not ask and does not hand off. It writes the note, reports, and stops.

Never add an open question to a spec from here.

Stale claims get no choice here. Name `/crav1-tighten-spec` for the spec that cites them.
