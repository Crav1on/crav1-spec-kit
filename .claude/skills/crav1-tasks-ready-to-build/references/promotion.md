# Promotion (1.69.0)

Read only when `SKILL.md` says the spec repo has `docs/environments/promotion.md`. Do not open this file otherwise. The rules are unchanged.

**Promotion (1.69.0)** reads `docs/environments/promotion.md`, as skill `crav1-add-to-spec`, `references/branches.md` says under **Promotion**. Report only. It does not change readiness or the Done count. The choice word `pipeline runs` runs the promotion check; headless without it gives the git answer plus `Pipeline runs not checked. Add the word: pipeline runs.`

## Choice words (1.69.0)

- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
