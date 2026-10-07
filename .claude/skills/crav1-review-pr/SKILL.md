---
name: crav1-review-pr
description: >-
  Read one named open pull request and report whether it can ship. When
  the slug has a plan, spec, plan, verify.md, the body, and a required
  green linter. When it has no plan.md or tasks.md, an info note, spec
  and the body, the pipeline's recorded tests, and that linter.
  Cross-cutting. Not a lane and not a bot. Same family as /crav1-open-pr
  and /crav1-merge-pr. Does not edit, test, vote, comment, or merge.
disable-model-invocation: true
icon: git-pull-request
color: orange
---

# Review a pull request

Read **one** named open pull request and say whether it can ship. Then stop.

Command: `/crav1-review-pr`.

This is cross-cutting. It is not a lane. It is not a bot. It is the same command family as `/crav1-open-pr` and `/crav1-merge-pr`.

Run it only when **this turn** names an open pull request (number or URL), or clearly asks to review that pull request. Any open pull request, not only a feature branch. If this turn does not name one, ask which one. That turn is the question only. Do not pick the newest. Do not review a pull request the user did not name.

`/crav1-open-pr` may name this command as an optional next step. It must not run it. `/crav1-merge-pr` must not run it. A review is not a merge ask. Spark, specify, and verify do not run this command. Do not run it from those skills. Do not run it from plan.

You read the diff. You do not edit code, the spec, or the plan. You do not run the tests. You do not ask to run the tests. You do not vote, post a comment, install a linter, change branch protection, or merge. A comment or a vote is a later explicit ask, not this skill.

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`. `az` may be `az.cmd`. Quote any `--query` value that contains parentheses.

## Which pull request

Accept a number (`123`) or a URL.

| URL | Id |
| --- | --- |
| `https://github.com/<owner>/<repo>/pull/<n>` | `<n>` |
| `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |
| `https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |

A branch name is not a pull request. Do not pick the newest pull request for the current branch. If the URL's repository is not this git remote, stop and name both. Do not review across that mismatch.

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL still names the host. A bare number needs that remote, or a `gh` repo that matches it.

## Host

Resolve **one** read path, in this order: GitHub `gh`, then Azure DevOps `az`, then say you cannot read the pull request. Do not claim you read it unless that path returned the diff and the body.

### GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub (`github.com` in the URL or the remote, or `gh repo view` succeeds for that repo).

If the pull request is on GitHub and `gh auth status` does not succeed, stop. Say `gh` is not authenticated. Do not use `az`. Do not invent a review.

### Azure DevOps (`az`)

Treat the remote or the pull request URL as Azure DevOps when it matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read org, project, and repository from that URL the same way `/crav1-merge-pr` does.

Use `az repos pr` only when `az` is on `PATH` (on Windows, `az.cmd` counts), the azure-devops extension can run, and the CLI is already authenticated for a non-interactive call. Do not run `az login`, a device-code flow, or a web login. Do not create a token. Do not print a token.

Pass `--org` and `--id`, and pass `--detect false`. Do not pass `--project` or `--repository` on show or policy list.

If `az` is missing, the extension cannot run, or the CLI is not already authenticated, stop. Do not invent a review.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it. A draft counts as open (`OPEN` on GitHub, `active` on Azure DevOps).

### GitHub

```text
gh pr view <n-or-url> --json number,url,title,body,state,isDraft,baseRefName,headRefName,files,statusCheckRollup
gh pr diff <n-or-url>
gh pr checks <n-or-url>
```

`state` must be `OPEN`.

### Azure DevOps

```text
az repos pr show --org <org-url> --id <n> --detect false --output json
az repos pr policy list --org <org-url> --id <n> --detect false --output json
```

`status` must be `active`.

Read the diff without checking out a branch. Fetch if the commits are not local, then diff the target and the source. Do not `git checkout`. Do not commit. Do not push.

```text
git fetch <remote> <source> <target>
git diff <target>...<source>
```

Strip a `refs/heads/` prefix when you name the branches. `<source>` is `sourceRefName`. `<target>` is `targetRefName`.

## What to read besides the diff

Read these from the pull request head. Do not edit them. `git show <source-sha>:<path>` is enough. Do not check out.

- **Spec and plan.** When the head is `feat/<slug>` or `spec/<slug>`, or the body links `docs/specs/<slug>/`, read that folder's `spec.md`, `plan.md`, and `tasks.md` when they exist. When several spec folders changed against the target, read each. Skip `_template`. When none exist, say so.
- **Outside the kit.** The slug was built outside the kit when that folder has no `plan.md` on the head. `tasks.md` without `plan.md` is still outside the kit. When both files are absent, the info note says the slug has no `plan.md` or `tasks.md`. A pull request with no slug has no `plan.md` or `tasks.md` for a slug, so the whole pull request was built outside the kit. Do not invent a slug. Record that as an info note, not a fix finding. Do not report a missing `verify.md`. Review that pull request against `spec.md` when it is on the head, and against the pull request body. A slug that has `plan.md` keeps today's plan and `verify.md` checks. A missing `tasks.md` on that slug stays on those checks.
- **Verify.** Only when the slug has `plan.md`. Quote `verify.md` when that file is already on the branch. Say so when it is missing. Do not run the tests. Do not write `verify.md`. When the slug has no `plan.md`, do not quote `verify.md` and do not say it is missing.
- **Recorded tests.** Only when the pull request is outside the kit (any slug, or no slug). Read the test results that pull request's own pipeline already recorded. See [Recorded tests](#recorded-tests-outside-the-kit-only). Do not run the tests. Do not ask to run the tests.
- **Pull request body.** The description as the host returned it.
- **Linter.** Whether a linter or checker covers the code in the diff, and whether that check is required on this pull request and green. Read the check rollup (GitHub) or the policy list (Azure DevOps), and the lint or checker config on the head when you need it to see coverage. Do not install a linter. Do not change branch protection.

A test run is not a linter. When the slug has `plan.md`, verify stays the quote from `verify.md`. When the pull request is outside the kit, the recorded-test note replaces that quote for the outside slug. The linter check stays separate on both paths.

When the diff has no code, say there is no code for a linter to cover. That linter check holds. Do not invent a linter for a diff the repo's own checker does not claim.

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

## First section

This section must be true before the review says ship.

When every slug under review has `plan.md`, walk these five checks: Spec, Plan, Verify, Body, and Linter. A secret is a first-section finding on every pull request.

When the pull request is outside the kit, walk Spec, Body, Linter, and Secret. Do not walk Plan. Do not walk Verify. Do not report a missing `verify.md`. Do not report a missing plan as a plan miss. That absence is the info note. When some slugs have `plan.md` and some do not, walk Plan and Verify only for the slugs that have `plan.md`.

Each miss is its own finding. Do not bundle two misses into one finding. Any finding whose decision is **fix** or **drop** means the review does not say ship.

A check that holds has no finding.

Each finding is three lines:

```text
F1 — <Spec | Plan | Verify | Body | Linter | Secret> — <lane or next step>
What is off: <one line>
What could happen: <one line>
Decision: <ship | fix | drop>
```

Number `F1`, `F2`, …. A miss on these checks is **fix** or **drop**, not ship. **Drop** means the extra behavior should come out. **Fix** means the diff, the plan, the proof, the body, or the check should change so the review can ship later. **Ship** on a finding is only for a note that does not block. Do not use it to wave a miss through. An info note is not a finding. Do not give it an `F` number or a decision.

Name the lane. Do not start it. Do not run the command you name.

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

When the slug has `plan.md`, and `verify.md` is missing, and the plan named no checks for this diff, say the file is missing. That is not a verify miss. When the slug has no `plan.md`, do not say `verify.md` is missing.

When no spec exists and the diff adds no product behavior, say there is no spec for this diff. That is not a spec miss.

When the slug has `plan.md` and the diff has no code the plan should have named, say so. That is not a plan miss. When the slug has `plan.md` and the diff has code and no plan task named the files or the checks, that is a plan miss. When the slug has no `plan.md`, that is the outside-the-kit info note, not a plan miss.

A secret in the diff is a first-section finding. Decision: **fix**. Name Build. Do not print the secret. Name the path. A secret is not a suggestion. A secret is not an info note.

## Info

Skip this section when every slug under review has `plan.md`.

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

## Second section

Style, patterns, and practices. Suggestions only.

They do not block ship. They are not a fix. A secret in the diff is the exception: that one is a first-section fix, not a suggestion.

Only flag a practice the repo already wrote down (for example `AGENTS.md` or its lint rules), plus dead code, or a name that hides what the code does. Do not invent a house style the repo never stated.

```text
S1 — suggestion
What you noticed: <one line>
Where: <path>
```

No suggestions: say none.

## Ship or not

Show findings, then info notes, then suggestions.

When the first section has no **fix** and no **drop**, the review says **ship**. Say it is clean. Info notes do not change that.

When any first-section decision is **fix** or **drop**, the review does not say ship.

On an outside pull request, the last line names `/crav1-keep-current` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. This includes a mixed pull request, where any slug was built outside the kit. Do not run it. A pull request whose slugs all have `plan.md` does not get this line.

```text
Next, after this pull request merges: /crav1-keep-current, to bring its changes into the spec and docs/system/.
```

Then stop.

Do not merge. Merge stays a later explicit `/crav1-merge-pr` ask for this named pull request. Do not run it. A review is not that ask. `/crav1-merge-pr` still stops on its own when a required host check is red. This skill does not replace that stop, and it does not clear it.

Do not post the review as a comment. Do not vote. Do not open a spec. Do not edit the pull request body.

## Hard rules

- No review unless this turn names the pull request or clearly asks to review that one.
- Do not pick the newest pull request.
- No edits to code, `spec.md`, `plan.md`, `tasks.md`, or `verify.md`.
- No test run, and no ask to run tests. When the slug has `plan.md`, quote `verify.md` or say it is missing. When the pull request is outside the kit, do not say `verify.md` is missing. Read the pipeline's recorded test results.
- No linter install. No branch-protection change. No required-check edit.
- No comment, no vote, no label, no reviewer assignment.
- No merge. Do not run `/crav1-merge-pr`.
- Do not run `/crav1-keep-current`. On an outside pull request, name it once, as the next step after the pull request merges.
- Do not run this skill from `/crav1-open-pr`, `/crav1-merge-pr`, spark, specify, plan, or verify.
- No `git checkout`, no `git commit`, no new branch, no push.
- No dialog-box or browser Microsoft sign-in. No token printed or created.
