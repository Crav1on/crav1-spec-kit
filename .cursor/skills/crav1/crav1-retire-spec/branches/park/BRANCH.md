# Retire spec: Park and un-park branch

Read only when `SKILL.md` routes here (`park`, or un-park). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Park

Add as the first line of `spec.md`: `Parked: <YYYY-MM-DD>, <reason>`. Do not move the spec. Do not change the feature-index row.

While parked:

- `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-build-features`, and the push branches of `/crav1-ado-sync` skip it and say `skipped: <slug> (parked)`.
- `/crav1-help` and `/crav1-show-or-ask-open-questions` list it as parked, with the count of notes waiting for it.
- `/crav1-add-to-spec` writes nothing into it. Input that matches it is saved as one note waiting for it (see that skill's **Parked specs**).

## Un-park

1. Find every note in `docs/notes/` (month folders and their generated indexes) with the slug in `waiting_for`, or an old `Waiting for <slug> (parked)` line.
2. Read each waiting note in full. Suggest what fits the spec now, including points that already went to other specs, when they matter to this one too. Match each point against every active spec as well, and say when another spec is now the better fit.
3. Show the summary: the `Parked:` line removed, each point to add, and each note that gets `Used by <slug>`.
4. On yes: remove the `Parked:` line, add the chosen points through the same rules as `/crav1-add-to-spec`, and on each waiting note move the slug from `waiting_for` to `used_by` (an old line becomes `Used by <slug>`). Run the notes index generator; do not hand-edit an index.

A waiting note is never marked absorbed. It stays open as the shared full source for any spec.
