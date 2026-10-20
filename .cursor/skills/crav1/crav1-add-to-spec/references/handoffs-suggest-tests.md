# crav1-add-to-spec: handoff

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0 and from `handoffs.md` in 1.71.1; the rules are unchanged.

## From /crav1-suggest-tests-for-code

When `/crav1-suggest-tests-for-code` hands one suggestion for an existing spec, run only this section. The spec is the one that skill already named. Do not ask for a slug. Do not create a slug. Do not create a folder. Do not open the impact question. Do not edit `docs/system/` or another spec. Do not write `plan.md` or `tasks.md`. Do not write test code. Do not change application code. Do not start Specify, Plan, or Build. Do not continue into the main path. After the last suggestion in this run, follow **Picture offer**, then stop.

**Keep.** Quote the suggestion. Do not replace it with a paraphrase. Add one acceptance checkbox because it is a check a stranger could run. Label it `**New:**`. The checkbox stays yes/no. Name the kind the suggestion already named: unit for a function’s checks, browser for a page, integration for a boundary. Do not invent another check. Do not add another kind.

**Dismiss.** Quote the suggestion under `## Dismissed test suggestions`. The line starts with `Dismissed test suggestion.` Do not reword the check. Create that heading only when it is missing. Do not add an acceptance checkbox. Do not turn it into a goal. Plan does not turn this line into a task. The next run of `/crav1-suggest-tests-for-code` does not offer it.
