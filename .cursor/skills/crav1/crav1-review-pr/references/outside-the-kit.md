# crav1-review-pr: outside the kit

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Recorded tests (outside the kit only)

Skip this section when every slug under review has `plan.md`.

Read results the pipeline already stored for this pull request. Do not queue a run, retry a run, approve a run, or start a workflow. Do not install a test runner. Do not run a test command. Do not ask the user to let this skill run the tests.

A test check is a check whose name says test, tests, unit, integration, e2e, pytest, jest, vitest, or the repo's test command, and it is not the linter check from the linter section. A red test check stays in the info note. It is not a linter miss.

### GitHub

Use the check rollup and `gh pr checks` already read. When a completed workflow run is already stored for a test check, read that run. Keep a run whose `headSha` is this pull request's head. Do not `gh workflow run`. Do not `gh run rerun`.

```text
gh run list --branch <headRefName> --json databaseId,name,conclusion,status,event,headSha,url
gh run view <run-id> --json conclusion,jobs,url,displayTitle
```

When the job log or the check-run annotations already list individual tests, read only enough of that stored log to name the tests and the pass or fail.

```text
gh run view <run-id> --log
```

### Azure DevOps

Use the policy list already read. When that evaluation names a build that already ran, read that build and the test runs it already stored. GET only. Do not call `az pipelines run`. Do not queue, retry, or approve.

```text
az pipelines runs show --org <org-url> --project <project> --id <build-id> --detect false --output json
az rest --method get --uri "<org-url>/<project>/_apis/test/runs?buildUri=vstfs:///Build/Build/<build-id>&api-version=7.1"
az rest --method get --uri "<org-url>/<project>/_apis/test/runs/<run-id>/results?api-version=7.1"
```

Do not print a token, a secret, or a connection string from those payloads.

### What the info note reports

When the pipeline recorded a test run, the note names which tests ran, whether they passed, and which changed files no test touches.

- Name individual tests when the stored log, annotations, or test results list them. When the pipeline recorded only the check, name that check and say individual test names were not recorded.
- Passed is yes only when every recorded test check succeeded. Passed is no when any failed, was cancelled, or timed out. When a run has not finished, say it has not finished. That is not a pass, and it is not the no-run note.
- A changed file is every file in the diff that is not itself a test. A test file is a file whose name contains `test` or `spec`, or that sits in a `tests` or `__tests__` directory, and that the repo's test tool would collect.
- A recorded test touches a changed file when the stored output names that file, or the test name pairs with the file's base name (the file name without its extension). List every changed file that no recorded test touches. When the pipeline recorded a run and did not name files, say that, then list changed files whose base name pairs with no test the log named and with no test file the pull request includes.
- The note states that these are the pull request's own tests, not a check against the spec.

When the pipeline shows no test run, the note names the tests the pull request includes: test files the diff adds or changes, plus test files already on the head whose base name pairs with a changed file. Name each path. When the pull request includes no test files, say that. Tell the user they can run those tests manually and then rerun this review. Say that a rerun only sees results the pipeline recorded, so a local run shows up only if the user pastes its output. The note states that these are the pull request's own tests, not a check against the spec.

When this turn pastes test output, add what that paste shows: which tests it names, and whether they passed. Say the paste is the user's output, not a pipeline result. A later review still only sees a pipeline result, or a new paste.

When the read of stored results fails, the note says the pipeline results could not be read and names the issue. Do not invent a pass. Do not turn that into a fix finding.

This note does not block ship.

## Info

Skip this section when every slug under review has `plan.md` and the spec covers only this repo.

Info notes do not block ship. They are not findings. They are not suggestions. A failed recorded test stays here.

```text
I1 — info — outside the kit
What the files show: <slug, or this pull request> has no plan.md or tasks.md. It was built outside the kit.
```

List every outside slug in that one note. When `tasks.md` is on the head and `plan.md` is not, say there is no `plan.md` for that slug. When there is no slug, say this pull request has no `plan.md` or `tasks.md` for a slug.

```text
I2 — info — tests
Ran: <tests, checks, or the pipeline recorded no test run>
Passed: <yes | no | not finished | no run>
Changed files no test touches: <paths, or none>
These are the pull request's own tests, not a check against the spec.
```

When the pipeline recorded no test run, use this `I2` instead:

```text
I2 — info — tests
The pipeline recorded no test run.
Tests this pull request includes: <paths, or none>
The user can run them manually and then rerun this review.
A rerun only sees results the pipeline recorded. A local run shows up only if the user pastes its output.
These are the pull request's own tests, not a check against the spec.
```

When the spec spans several repos (1.65.0), add:

```text
I3 — info — other repos
Not in this PR: <repo>: <task, item, or requirement>, …
Branches: 0 of 2 merged into develop. Not merged: feat/orders-retry (2 commits), …
```

The `Branches:` line is the one in `crav1-add-to-spec` `references/branches.md` **The Branches line**, one per repo, measured against each repo's into branch (its `Merges into` cell in `docs/system/repos.md`, else the default branch), report only.

## Outside pull request, in the review

When the pull request is outside the kit, walk Spec, Body, Linter, and Secret. Do not walk Plan. Do not walk Verify. Do not report a missing `verify.md`. Do not report a missing plan as a plan miss. That absence is the info note. When some slugs have `plan.md` and some do not, walk Plan and Verify only for the slugs that have `plan.md`.

On an outside pull request, the last line names `/crav1-refresh-system-notes` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. This includes a mixed pull request, where any slug was built outside the kit. Do not run it. A pull request whose slugs all have `plan.md` does not get this line.
