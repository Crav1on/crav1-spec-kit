# crav1-review-pr: first section

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## First section: special cases

When the slug has `plan.md`, and `verify.md` is missing, and the plan named no checks for this diff, say the file is missing. That is not a verify miss. When the slug has no `plan.md`, do not say `verify.md` is missing.

When no spec exists and the diff adds no product behavior, say there is no spec for this diff. That is not a spec miss.

When the slug has `plan.md` and the diff has no code the plan should have named, say so. That is not a plan miss. When the slug has `plan.md` and the diff has code and no plan task named the files or the checks, that is a plan miss. When the slug has no `plan.md`, that is the outside-the-kit info note, not a plan miss.

## Miss table

| Miss | Decision | Lane or next step |
| --- | --- | --- |
| Spec: the diff adds product behavior the spec never asked for | drop | Specify (acceptance and diff disagree) |
| Spec: the diff leaves out something the spec said must be true | fix | Specify (acceptance and diff disagree) |
| Plan: a task never named a needed file or check (only when that slug has `plan.md`) | fix | Plan |
| Verify: `verify.md` is on the branch and its quote shows a failure, or the quote does not cover a check the plan named for this diff (only when that slug has `plan.md`) | fix | Build |
| Verify: `verify.md` is missing and the plan named checks for this diff (only when that slug has `plan.md`) | fix | Build. Say the file is missing. Do not run the tests |
| A file the plan already named is not in the diff (only when that slug has `plan.md`) | fix | Build. This is not a plan miss |
| Body: the description is wider or narrower than the diff | fix | Rewrite the pull request body. Not a new spec. The mismatch stays on this pull request. Do not edit the body in this skill |
| Linter: none covers the code in the diff, or one exists but is not required on this pull request, or it is required and red | fix | Build. Do not install a linter |
