---
name: crav1-review-pr
description: >-
  Read one named open pull request and report whether it can ship. When
  the slug has a plan, spec, plan, verify.md, the body, and a required
  green linter. When it has no plan.md or tasks.md, an info note, spec
  and the body, the pipeline's recorded tests, and that linter.
  Cross-cutting. Not a lane and not a bot. Same family as /crav1-open-pr
  and /crav1-merge-pr. Ends with a paste-ready comment, link-first per
  point; posts it as one comment and votes only after the user's yes. Re-review marks earlier
  findings fixed or open. Works across repos: from the specs repo for a
  PR in a repo listed in repos.md, or with both open. Saves the PR
  description as a PR note and follow-ups as a note in the specs repo's
  docs/notes/YYYY-MM/. Does not edit, test, or merge.
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

You read the diff. You do not edit code, the spec, or the plan. You do not run the tests. You do not ask to run the tests. You do not install a linter, change branch protection, or merge. You post comments or set a verdict only as [Post it](#post-it) says, after the user's yes.

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`. `az` may be `az.cmd`. Quote any `--query` value that contains parentheses.

## Which pull request

Accept a number (`123`), a URL, or `<repo> <n>` (1.65.0), for example `orders-api 71`, where `<repo>` is a repo in `docs/system/repos.md` or a workspace folder.

| URL | Id |
| --- | --- |
| `https://github.com/<owner>/<repo>/pull/<n>` | `<n>` |
| `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |
| `https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |

A branch name is not a pull request. Do not pick the newest pull request for the current branch.

A URL or `<repo> <n>` is accepted when its repository is one of these (1.65.0):

1. this checkout's git remote
2. the git remote of another folder in this workspace
3. a row of `docs/system/repos.md` in the specs repo, matched on its `URL` cell: compare without a trailing `.git`, ignore case, and treat `dev.azure.com/<org>` and `<org>.visualstudio.com` as the same

Otherwise stop and name what you looked at: `PR repository <url> is not this remote, a workspace folder, or a repos.md row.` Do not review across that mismatch.

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL still names the host. A bare number needs that remote, or a `gh` repo that matches it.

## Specs repo and code repo (1.65.0)

The **code repo** is the repo the pull request is in. The **specs repo** is the checkout that has `docs/specs/`. They may be the same repo.

- **Same repo.** Everything below works as before: spec files come from the pull request head.
- **Both open.** The specs repo is the workspace folder with `docs/specs/`. The code repo is the folder whose git remote matches the pull request. When several folders have `docs/specs/`, ask which one, options only. A headless run stops: `Several spec repos open: <a>, <b>. Name one.`
- **Run from the specs repo.** A pull request from a repo in its `docs/system/repos.md`. The code repo's checkout is `../<repo>`, as `crav1-add-to-spec` `references/branches.md` says under **Sibling checkout** (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`). Only an Azure DevOps diff needs that checkout.
- **Run from the code repo, specs repo not open.** Look read-only for a sibling `../*/docs/system/repos.md` with a row for this repo. When one is found, that is the specs repo: read the spec there, and write the notes there without committing; name the full path in the report.

When no specs repo is found, review against the pull request head and body as before, and print the notes in the chat with the path they would have.

The review is read-only toward the code repo and its host. The only exception is the fetch in [Diff from a sibling checkout](#diff-from-a-sibling-checkout-azure-devops), after a pick.

## Host

Resolve **one** read path, in this order: GitHub `gh`, then Azure DevOps `az`, then say you cannot read the pull request. Do not claim you read it unless that path returned the diff and the body.

### GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub (`github.com` in the URL, the remote, or the `repos.md` URL, or `gh repo view` succeeds for that repo).

If the pull request is on GitHub and `gh auth status` does not succeed, stop. Say `gh` is not authenticated. Do not use `az`. Do not invent a review.

### Azure DevOps (`az`)

Treat the remote, the pull request URL, or the `repos.md` URL as Azure DevOps when it matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read org, project, and repository from that URL the same way `/crav1-merge-pr` does.

Use `az repos pr` only when `az` is on `PATH` (on Windows, `az.cmd` counts), the azure-devops extension can run, and the CLI is already authenticated for a non-interactive call. Do not run `az login`, a device-code flow, or a web login. Do not create a token. Do not print a token.

Pass `--org` and `--id`, and pass `--detect false`. Do not pass `--project` or `--repository` on show or policy list.

If `az` is missing, the extension cannot run, or the CLI is not already authenticated, stop. Do not invent a review.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it. A draft counts as open (`OPEN` on GitHub, `active` on Azure DevOps).

### GitHub

```text
gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,isDraft,baseRefName,headRefName,headRefOid,headRepository,headRepositoryOwner,files,statusCheckRollup
gh pr diff <n-or-url>
gh pr checks <n-or-url>
```

For a pull request in another repo, pass its URL (or `--repo <owner>/<repo>` with the number). `gh pr diff` reads the diff from the host, so no local checkout is needed.

`state` must be `OPEN`.

### Azure DevOps

```text
az repos pr show --org <org-url> --id <n> --detect false --output json
az repos pr policy list --org <org-url> --id <n> --detect false --output json
```

`status` must be `active`.

Read the diff without checking out a branch. When the pull request is in this checkout, fetch if the commits are not local, then diff the target and the source. Do not `git checkout`. Do not commit. Do not push.

```text
git fetch <remote> <source> <target>
git diff <target>...<source>
```

Strip a `refs/heads/` prefix when you name the branches. `<source>` is `sourceRefName`. `<target>` is `targetRefName`.

### Diff from a sibling checkout (Azure DevOps)

When the pull request is in another repo, read the diff in that repo's checkout (a workspace folder, else `../<repo>`). When there is none, ask for the path with options only (the sibling folders that are git checkouts, plus Other). A headless run stops: `No checkout found for <repo>. Name its path.`

First compare the copies on disk (`<remote>/<source>` and `<remote>/<target>`, else the local branches) with the pull request's `lastMergeSourceCommit.commitId` and `lastMergeTargetCommit.commitId`. A copy matches when it points at that commit or already contains it.

- **Both match.** No question. `git diff <target>...<source>` on the copies on disk.
- **A copy is missing or older.** Ask one question, options only:
  1. **Fetch only the PR's two branches (Recommended).** `git fetch <remote> <source> <target>` in that checkout, then the diff. This moves remote-tracking refs only. Never check out, merge, commit, or push there. It is the one exception to the no-fetch rule for a sibling checkout in `references/branches.md`.
  2. **Use what's on disk.** Diff the copies on disk. Say each copy's newest commit date and age, and `the copy on disk is older than the PR; newer commits may be missed`.
  3. **Stop.** Say `Fetch <source> and <target> in <path> and rerun.` and stop.

## Choice words (1.65.0)

Exact words for bots and scripted runs. There are no `--flags`.

- Branches on disk older than the pull request: `fetch pr branches` / `use disk` / `stop pr review`.

When the invocation contains one of these words (for example `/crav1-review-pr orders-api 71 use disk`), take that choice when the question comes up and do not ask. When the question comes up in a headless run or a bot run with no word, stop: `PR branches on disk are missing or older than the PR. Use one of: fetch pr branches, use disk, stop pr review.` A word that is not needed (the copies match) is ignored.

## What to read besides the diff

Read these from the pull request head when the specs repo is the code repo. Do not edit them. `git show <source-sha>:<path>` is enough. Do not check out. When the pull request is in another repo (1.65.0), read `docs/specs/`, `docs/system/` and the spec files from the specs repo's working tree instead, read-only, and name it in the review: `specs from <specs repo> <branch> (working tree)`.

- **Spec and plan.** When the head is `feat/<slug>` or `spec/<slug>`, or the body links `docs/specs/<slug>/`, or (1.64.0) a spec's `Synced at` entries, Match `Branch:` list or task `(branch: …)` parts name the head (for a pull request in another repo, the entries, items and parts for that repo: its `Synced at` line, items with that repo prefix or without one when the spec has one repo, and `(branch: <repo> <head>)`), the same lookup as `/crav1-open-pr`, read that folder's `spec.md`, `plan.md`, and `tasks.md` when they exist. When several spec folders changed against the target, read each. Skip `_template`. When none exist, say so.
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

A spec over several repos (1.65.0): an item or task that belongs to another repo is not a spec miss on this pull request. That is a task `(branch: <other repo> …)`, a Match `Branch:` item with another repo's prefix, or a requirement the spec ties to another repo. List those parts in the `I3` info note.

When the slug has `plan.md` and the diff has no code the plan should have named, say so. That is not a plan miss. When the slug has `plan.md` and the diff has code and no plan task named the files or the checks, that is a plan miss. When the slug has no `plan.md`, that is the outside-the-kit info note, not a plan miss.

A secret in the diff is a first-section finding. Decision: **fix**. Name Build. Do not print the secret. Name the path. A secret is not a suggestion. A secret is not an info note.

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

## Bugs, tests, questions (1.66.0)

Each point that goes into the comment has a chat line, two lines each:

```text
B1 — bug
What you noticed: <one line>
Where: <path>, line <n> | no line
```

`T1 — test to add` is a concrete test for a changed behavior or a bug. `Q1 — question` is something the author or team must answer about the code repo. Same two lines. They do not change the ship line. A question is saved in the follow-ups note as a bullet that starts `Asked on the PR:`. Which section each one goes to: `references/comment-layout.md` **Which section** (drop-in: `.claude/skills/crav1-review-pr/references/comment-layout.md`; plugin: `skills/crav1-review-pr/references/comment-layout.md`).

## Ship or not

Show findings, then info notes, then suggestions, then bugs, tests to add and questions.

When the first section has no **fix** and no **drop**, the review says **ship**. Say it is clean. Info notes do not change that.

When any first-section decision is **fix** or **drop**, the review does not say ship.

On an outside pull request, the last line names `/crav1-refresh-system-notes` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. This includes a mixed pull request, where any slug was built outside the kit. Do not run it. A pull request whose slugs all have `plan.md` does not get this line.

```text
Next, after this pull request merges: /crav1-refresh-system-notes, to bring its changes into the spec and docs/system/.
```

For a pull request in another repo (1.65.0), the same line also names `/crav1-add-to-spec code change <repo> <head branch>`, which brings the merged branch into the spec. Do not run either.

Then `Verdict: <Approve | Approve with comments | Changes needed>` (any Blocker or Bug: Changes needed; only tests to add or a question: Approve with comments; nothing: Approve), then the [paste-ready comment](#paste-ready-comment), then the [post offer](#post-it). Then stop.

Do not merge. Merge stays a later explicit `/crav1-merge-pr` ask for this named pull request. Do not run it. A review is not that ask. `/crav1-merge-pr` still stops on its own when a required host check is red. This skill does not replace that stop, and it does not clear it.

Do not post or vote except as [Post it](#post-it) says. Do not open a spec. Do not edit the pull request body.

## Re-review

When the pull request already has an earlier review, this run is a re-review. Read the earlier findings from the pull request's own review comments and threads, including the bullets of an earlier one-comment review (each link gives the path and lines) (GitHub `gh api repos/<owner>/<repo>/pulls/<n>/comments` and `gh pr view <n> --json reviews,comments`; Azure DevOps `az repos pr thread list` or `az rest --method get` on the pull request threads). Comments from anyone count, including ones this skill posted. A paste-ready block still in this chat is the fallback only when the pull request has no earlier review comments. When neither exists, do a first review.

Go through each earlier finding, one line each, before the new findings:

- **Fixed:** the code changed and the problem is gone. Name the commit that fixed it (short SHA).
- **Partly fixed:** some of it changed. Say what is left.
- **Still open:** the problem is still there.
- **No longer relevant:** the code was removed or rewritten so the finding no longer applies.

A thread marked resolved whose problem is still there is flagged `resolved but still open`. Do not guess a status: when the diff does not settle it, say so.

Status lines and thread replies follow [Comment style](#comment-style): first person, friendly, varied, for example "Thanks, this looks sorted now in `abc1234`" or "I think there is still a little bit left here: …". A still-open finding is said softly, with the same information.

In the comment, earlier points go under `### Since last time` and new points under the normal sections (`references/comment-layout.md` **Re-review**). The ship-or-not rule counts still-open, partly-fixed, and new first-section findings.

## Paste-ready comment

End every review with one fenced Markdown block the user can paste into the pull request as one comment. Build it exactly as `references/comment-layout.md` says (1.66.0; drop-in: `.claude/skills/crav1-review-pr/references/comment-layout.md`; plugin: `skills/crav1-review-pr/references/comment-layout.md`). In short:

- No verdict line in the block; the chat shows `Verdict: …` just above it.
- One short, plain opening line, then `### Blockers`, `### Bugs`, `### Tests to add with this PR`, `### A question` (or `### Questions`), leaving out a section with nothing in it.
- Each point starts with the host link to its file and line on the pull request's source branch (or the PR overview, or a branch link), then a blank line and the explanation as an indented paragraph. At most one fix per point, no tails.
- No follow-ups, no table, no closing line, no files-view link, no HTML, no kit details.
- Advice about a branch that is behind, has conflicts, or must take another branch first says to merge `<base>` into this branch. Never a rebase.
- English, unless the user asks for another language for this comment in this turn.

## Comment style

The default style for the paste-ready block, every posted comment, and every re-review reply (agreed by Thomas and Rhea, 2026-10-12):

- Write in the user's own first-person voice. Friendly, so the author never feels criticised, harped on, or wrong. Do not say that outright.
- Keep the source of the findings vague: "me and my checks". Never name a tool, a skill, a bot, or the kit. Never write that a tool found the author's mistakes.
- The opening is one short, plain line, in the spirit of "I've looked through the PR and run it through my checks. This is what I found:". It may vary slightly. Never praise, a greeting by name, or thanks (1.66.0).
- One fix per point at most. No second option, and nothing after the fix or the question ("your call", "let me know") (1.66.0).
- Soft wording, same information: "I noticed…", "It looks like… maybe they could…?", "Would it be worth adding a test that…?". No flat statements of fault. Do not drop or water down a fact to sound soft.
- Read the pull request description first. A choice the description says is deliberate is not raised as a fault. When it suggests something they "might like" or that "may be a good idea", it is a follow-up and goes to the note, not into the comment.

The chat review above the block (F, I, S, B, T, Q lines) keeps its plain format for the user. The style applies to what the author will read.

The block is text in the chat. Showing it posts nothing.

## Follow-ups note

Follow-ups are not posted and not in the paste-ready block. The chat review still shows them, under **Follow-ups (not for this PR)**, then one line: `Follow-ups saved: docs/notes/YYYY-MM/<file>.md`.

When the review has at least one follow-up or question, write a note in `docs/notes/` of the specs repo, in the notes format of `crav1-add-to-spec` `references/notes.md` (1.61.0; `docs/notes/_template/note.md`; the same shape `/crav1-add-to-spec` writes, drop-in: `.claude/skills/crav1-add-to-spec/branches/meeting/assets/`; plugin: sibling `skills/crav1-add-to-spec/branches/meeting/assets/`):

- File: `docs/notes/YYYY-MM/review-pr-<n>-follow-ups.md`, in the month folder of the review date, where `<n>` is the pull request number. When two repos in this specs repo have the same pull request number, use `review-pr-<repo>-<n>-follow-ups.md`. A pull request in a repo other than the specs repo always uses `review-pr-<repo>-<n>-follow-ups.md` (1.65.0).
- Title: `Follow-ups from PR <n> (<repo>)`.
- Front matter: `kind: review-pr`, `source: PR <n> <repo>`, `source_date` and `imported` the review date, `pr_note:` the PR note's path (1.65.0), `used_by: []`.
- `From review <date>. PR <n>, <repo>, <PR title>.` then one bullet per follow-up: `<path>`, line `<n>`: the follow-up in plain words. Paths and lines are kept, because the note stays in the specs repo. Use `no line` when the follow-up has no line. A question asked in the comment is a bullet too, starting `Asked on the PR:` (1.66.0); a re-review adds `(answered on the PR <date>)` when the thread has an answer.
- Then run the notes index generator (`scripts/notes_index.py` in `crav1-add-to-spec`). Do not hand-edit an index.

**Re-review.** When the note for that pull request exists (in any month folder, or flat in `docs/notes/` from before 1.61.0), update it where it is. Do not write a second note. Set `imported` to this review's date, add new follow-ups, and mark one the code now addresses as `(done in <short sha>)`. Do not remove a line. Leave `used_by` as it is, then rerun the generator. When the review has no follow-ups and the note exists, leave the note.

**No follow-ups.** Write no note.

When the specs repo is not in this workspace, write the note into the specs repo found as a sibling (see [Specs repo and code repo](#specs-repo-and-code-repo-1650)), never commit it, and name its full path. When no specs repo is found, write nothing and print the note in the chat with the path it would have.

## PR note (1.65.0)

Every review writes or reuses the **PR note**, whatever the follow-ups, as `crav1-add-to-spec` `references/notes.md` **PR note** says (drop-in: `.claude/skills/crav1-add-to-spec/references/notes.md`; plugin: sibling `skills/crav1-add-to-spec/references/notes.md`): one note per pull request, `kind: pull request`, `source: PR <n> <repo URL path>`, filed by the pull request's created date, a new `## Description as of <date>` section only when the description changed, the personal-data and secrets check, and the four image options. A pull request that `/crav1-open-pr` made gets one too. It goes in the same specs repo as the follow-ups note. Then one line: `PR note: <full path> (written | reused | updated: description changed)`.

The follow-ups come back through the existing note flow: `/crav1-ado-sync` reads open notes, and a spec that takes one adds itself to the note's `used_by`. Notes are never absorbed. This skill does not do that marking.

Writing the PR note and the follow-ups note are the only files this skill writes. It does not commit. Name `/crav1-finalize-commit` and do not run it.

## Post it

After the paste-ready block, offer to post. One question. Use the questions tool when it is available. Say it posts under the user's own account as one comment, and name the vote it will set. Options: post, or do not post. Nothing posts without that yes.

On yes (1.66.0):

1. Post the block as **one comment**. No inline threads. GitHub: one review whose body is the block, submitted with the vote (`gh api repos/<owner>/<repo>/pulls/<n>/reviews` with `body` and `event`). Azure DevOps: one pull request thread whose comment is the block, then the vote.
2. The vote follows the verdict: Changes needed is **Request changes** (GitHub) or **Wait for author** (Azure DevOps); Approve with comments is **Comment** or **Approve with suggestions**; Approve is **Approve**. Never Reject.
3. On a re-review, post the new block as a reply in the earlier comment's thread (Azure DevOps) or as a new review (GitHub). Reply in an earlier inline thread only when one exists.
4. Follow-ups are never posted.
5. Never resolve a thread. On a re-review, after posting, offer to resolve existing threads whose points are now fixed. Resolve only on that yes.

When a post fails, say what failed and what already posted. Do not retry by another route.

## Hard rules

- No review unless this turn names the pull request or clearly asks to review that one.
- Do not pick the newest pull request.
- No edits to code, `spec.md`, `plan.md`, `tasks.md`, or `verify.md`. The only writes are the PR note and the follow-ups note in the specs repo's `docs/notes/YYYY-MM/` and the generated indexes.
- Read-only toward the code repo and its host. The only git write there is the fetch of the pull request's two branches after **Fetch only the PR's two branches** or `fetch pr branches`.
- No test run, and no ask to run tests. When the slug has `plan.md`, quote `verify.md` or say it is missing. When the pull request is outside the kit, do not say `verify.md` is missing. Read the pipeline's recorded test results.
- No linter install. No branch-protection change. No required-check edit.
- No comment, no vote, and no thread resolve without the user's yes in [Post it](#post-it). One comment, no inline threads, never Reject. No label, no reviewer assignment.
- Suggest merging `<base>` into the branch, never a rebase, `pull --rebase`, or a force-push.
- No merge. Do not run `/crav1-merge-pr`.
- Do not run `/crav1-refresh-system-notes`. On an outside pull request, name it once, as the next step after the pull request merges.
- Do not run this skill from `/crav1-open-pr`, `/crav1-merge-pr`, spark, specify, plan, or verify.
- No `git checkout`, no `git commit`, no new branch, no push.
- No dialog-box or browser Microsoft sign-in. No token printed or created.
