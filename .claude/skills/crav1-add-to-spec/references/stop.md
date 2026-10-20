# crav1-add-to-spec: stop

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Stop

Do not plan. Do not implement. Do not commit. Do not run `/crav1-finalize-commit` or `/crav1-plan-from-spec`.

Output only:

- Target `docs/specs/<slug>/spec.md`
- Source folder `docs/sources/YYYY-MM-DD-<slug>/` when this pass wrote one, or that none was written
- The note this pass wrote or reused (`docs/notes/YYYY-MM/<file>.md`), its source date or `no source date`, and any duplicate or conflict found
- The transfer data policy when this pass wrote it, or that none was written
- What was added (their quotes, labeled new) and what was already there
- Open questions: each answer linked, each possible answer left open, each asked mark written and where its date came from, or none
- Impact: nothing else, or the one-line edit list and which option they picked
- Research: each hit, whether it was marked, the note path and the findings line, or that none was marked. The revisit draft when one was written in the chat, or that none was drafted. The clear summary: what was cleared, narrowed, and routed where, each open question from the updated note and where it went, and when an older mark had no points, or that this run did not check an updated note
- Next: when this changed an existing spec, `/crav1-tighten-spec` for that slug first, as the **New information on an existing slice** route says (`docs/reference/workflow.md#new-info`): tighten, then resolve questions, then the plan when the slice has `plan.md` or `tasks.md`. `/crav1-finalize-commit` if any file changed (no push). For the full order, `/crav1-help next`. Do not run any of them.
