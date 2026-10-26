# Fill every section

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.95.1; the rules are unchanged.

Fill every section. Rules:

- Goals are outcomes, not features (“a runner can log a 5k in under 30 seconds” not “add a form”).
- Non-goals are as important as goals. If unsure, put the tempting extra in non-goals. Brownfield: “do not replace existing auth / do not add a second user table” belong here unless the spark is exactly that change.
- Journeys: one happy path, one failure path, one empty/first-run path (first-run of **this** feature, not necessarily first-run of the whole app).
- Acceptance criteria must be testable by a stranger with no chat history. Each item is a yes/no checkbox. Name the kind of check (unit, system, or browser) only when that kind is already obvious from the source. Otherwise leave the kind for plan. Do not invent a test list.
- Open questions stay open. Do not silently resolve them in the spec body.
- Mark remaining assumptions in a short `## Assumptions` section.
- **Brownfield:** do not respec the entire existing product. Do not invent a new architecture. If you skimmed the repo, note only constraints that affect this slice.
- **Landscape index:** after the spec exists, add one feature-index row on `docs/system/landscape.md` when this turn created a new spec folder: slug, `docs/specs/<slug>/`, repo name, `v0`. If they said **extend**, do not add a second row for that slug. Do not run `/crav1-bundle-to-specs`.
