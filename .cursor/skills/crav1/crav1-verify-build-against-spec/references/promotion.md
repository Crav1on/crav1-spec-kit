# Promotion (1.69.0)

Read only when `SKILL.md` says the spec repo has `docs/environments/promotion.md`. Do not open this file otherwise. The rules are unchanged.

**Promotion (1.69.0).** When the spec repo has `docs/environments/promotion.md`, add the `Promotion:` line after the Branches line, as skill `crav1-add-to-spec`, `references/branches.md` says under **Promotion**: per repo, the furthest environment reached and each later one not yet reached, as `on the branch that deploys to <env> (<branch>)` or `not yet on the branch that deploys to <env> (<branch>)`, release patterns as `on release/<x> (deploys to <env>)`, tag lines as `in tag <tag> (deploys to <env>)` or `not yet tagged`, the chain at the end, `Unclear:` for an unknown word with no `(after …)`, and `<branch>: not back on <base>` for a release fix. Branch reach, never `deployed to`. When a pipeline-sourced line is behind it, end with **Also check the latest pipeline runs?** (**Check pipeline runs** / **No, keep the git answer**); the choice word `pipeline runs` runs the check without asking; headless without it gives the git answer plus `Pipeline runs not checked. Add the word: pipeline runs.` Azure DevOps only, read-only; `az has no login` keeps the git answer. Report only: done stays merged into the base. In verify.md the Promotion line goes in the TL;DR under the Branches line.

## Choice words (1.69.0)

- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
