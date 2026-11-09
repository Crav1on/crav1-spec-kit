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
- End as `crav1-docs/reference/run-ending.md` says. Do not run the next step. Add the Uncommitted line when a file changed and is not committed.
- An existing spec changed: `Next: /crav1-tighten-spec <slug>, because the new information is not tightened yet.`
- No existing spec changed: `Next: nothing needed now.`
