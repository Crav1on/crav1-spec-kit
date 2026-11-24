# crav1-review-pr: reading

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## What to read besides the diff

Read these from the pull request head when the specs repo is the code repo. Do not edit them. `git show <source-sha>:<path>` is enough. Do not check out. When the pull request is in another repo (1.65.0), read `docs/specs/`, `docs/system/` and the spec files from the specs repo's working tree instead, read-only, and name it in the review: `specs from <specs repo> <branch> (working tree)`.

- **Spec and plan.** When the head is `feat/<slug>` or `spec/<slug>`, or the body links `docs/specs/<slug>/`, or (1.64.0) a spec's `Synced at` lines, Match `Branch:` list or task `(branch: …)` parts name the head (for a pull request in another repo, the entries, items and parts for that repo: its `Synced at` line, items with that repo prefix or without one when the spec has one repo, and `(branch: <repo> <head>)`), the same lookup as `/crav1-open-pr`, read that folder's `spec.md`, `plan.md`, and `tasks.md` when they exist. When several spec folders changed against the target, read each. Skip `_template`. When none exist, say so.
- **Outside the kit.** The slug was built outside the kit when that folder has no `plan.md` on the head. `tasks.md` without `plan.md` is still outside the kit. When both files are absent, the info note says the slug has no `plan.md` or `tasks.md`. A pull request with no slug has no `plan.md` or `tasks.md` for a slug, so the whole pull request was built outside the kit. Do not invent a slug. Record that as an info note, not a fix finding. Do not report a missing `verify.md`. Review that pull request against `spec.md` when it is on the head, and against the pull request body. A slug that has `plan.md` keeps today's plan and `verify.md` checks. A missing `tasks.md` on that slug stays on those checks.
- **Verify.** Only when the slug has `plan.md`. Quote `verify.md` when that file is already on the branch. Say so when it is missing. Do not run the tests. Do not write `verify.md`. When the slug has no `plan.md`, do not quote `verify.md` and do not say it is missing.
- **Recorded tests.** Only when the pull request is outside the kit (any slug, or no slug). Read the test results that pull request's own pipeline already recorded. See [Recorded tests](../SKILL.md#recorded-tests-outside-the-kit-only). Do not run the tests. Do not ask to run the tests.
- **Pull request body.** The description as the host returned it.
- **Linter.** Whether a linter or checker covers the code in the diff, and whether that check is required on this pull request and green. Read the check rollup (GitHub) or the policy list (Azure DevOps), and the lint or checker config on the head when you need it to see coverage. Do not install a linter. Do not change branch protection.

A test run is not a linter. When the slug has `plan.md`, verify stays the quote from `verify.md`. When the pull request is outside the kit, the recorded-test note replaces that quote for the outside slug. The linter check stays separate on both paths.

When the diff has no code, say there is no code for a linter to cover. That linter check holds. Do not invent a linter for a diff the repo's own checker does not claim.
