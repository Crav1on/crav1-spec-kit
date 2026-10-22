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
  docs/notes/YYYY-MM/, with the comment as drafted and as posted, and
  marks drafted points left out. Does not edit, test, or merge.
disable-model-invocation: true
icon: git-pull-request
color: orange
---

# Review a pull request

Read **one** named open pull request and say whether it can ship. Then stop.

Command: `/crav1-review-pr`.

This is cross-cutting. It is not a lane. It is not a bot. It is the same command family as `/crav1-open-pr` and `/crav1-merge-pr`.

Run it only when **this turn** names an open pull request (number or URL), or clearly asks to review that pull request. Any open pull request, not only a feature branch. If this turn does not name one, ask which one. That turn is the question only. Do not pick the newest. Do not review a pull request the user did not name.

Read `references/which-pr.md` ("Other skills") only when another skill names or would run this one.

You read the diff. You do not edit code, the spec, or the plan. You do not run the tests. You do not ask to run the tests. You do not install a linter, change branch protection, or merge. You post comments or set a verdict only as [Post it](#post-it) says, after the user's yes.

Read `references/windows.md` ("Windows") only when git or az is not found (Windows).

## Comment as posted first (1.67.0)

Read `references/posted-comments.md` ("Comment as posted first (1.67.0)") only when the user says they posted the comment themselves, or a review of this PR was posted before.

## Which pull request

Read `references/which-pr.md` ("Which pull request") only when you resolve the named pull request (a number, a URL, `<repo> <n>`, or a branch) or none is named.

## Specs repo and code repo (1.65.0)

Read `references/cross-repo.md` ("Specs repo and code repo (1.65.0)") only when the pull request is in a different repo from the specs (repos.md), or both repos are open.

## Host

Resolve **one** read path, in this order: GitHub `gh`, then Azure DevOps `az`, then say you cannot read the pull request. Do not claim you read it unless that path returned the diff and the body.

### GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub (`github.com` in the URL, the remote, or the `repos.md` URL, or `gh repo view` succeeds for that repo).

Read `references/github.md` ("GitHub not signed in") only when `gh auth status` fails.

### Azure DevOps (`az`)

Read `references/azure-devops.md` ("Azure DevOps (`az`)") only when the remote is Azure DevOps.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it. A draft counts as open (`OPEN` on GitHub, `active` on Azure DevOps).

### GitHub

```text
gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,isDraft,baseRefName,headRefName,headRefOid,headRepository,headRepositoryOwner,files,statusCheckRollup
gh pr diff <n-or-url>
gh pr checks <n-or-url>
```

Read `references/cross-repo.md` ("Other repo, in the review") only when the pull request is in another repo.

`state` must be `OPEN`.

### Azure DevOps

Read `references/azure-devops.md` ("Azure DevOps (Read it first)") only when the remote is Azure DevOps.

### Diff from a sibling checkout (Azure DevOps)

Read `references/azure-devops.md` ("Diff from a sibling checkout (Azure DevOps)") only when Azure DevOps gives no diff and a sibling checkout exists.

## Choice words (1.65.0)

Exact words for bots and scripted runs. There are no `--flags`.

- No pull request: `branch` (1.80.0), see `references/branch.md`.
- Branches on disk older than the pull request: `fetch pr branches` / `use disk` / `stop pr review`.
- The comment as posted (1.67.0): `comment posted` (run only the record step, no review), `newest comment` (several candidates: take the newest match by the signed-in user), `skip comment record` (do not record; the review goes on).

Read `references/azure-devops.md` ("Branches on disk: choice words") only when the branches-on-disk question comes up.

Read `references/comment-as-posted.md` ("Headless and bot runs") only when the record step runs headless or by a bot with no word.

## What to read besides the diff

Read `references/reading.md` ("What to read besides the diff") only when you gather the spec, plan, verify, body and linter state, before the first section.

## Recorded tests (outside the kit only)

Read `references/outside-the-kit.md` ("Recorded tests (outside the kit only)") only when the slug has no plan.md or tasks.md (outside the kit).

## First section

This section must be true before the review says ship.

When every slug under review has `plan.md`, walk these five checks: Spec, Plan, Verify, Body, and Linter. A secret is a first-section finding on every pull request.

Read `references/outside-the-kit.md` ("Outside pull request, in the review") only when the pull request is outside the kit (no plan.md).

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

Read `references/first-section.md` ("Miss table") only when a first-section check misses (to pick its decision and lane).

Read `references/first-section.md` ("First section: special cases") only when verify.md is missing, there is no spec, or the diff has no code the plan named.

A secret in the diff is a first-section finding. Decision: **fix**. Name Build. Do not print the secret. Name the path. A secret is not a suggestion. A secret is not an info note.

## Info

Read `references/outside-the-kit.md` ("Info") only when the slug has no plan.md or tasks.md, or some slugs do and some don't.

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

Read `references/comment.md` ("Bugs, tests, questions (1.66.0)") only when the review found bugs, missing tests or questions.

## Ship or not

Show findings, then info notes, then suggestions, then bugs, tests to add and questions.

When the first section has no **fix** and no **drop**, the review says **ship**. Say it is clean. Info notes do not change that.

When any first-section decision is **fix** or **drop**, the review does not say ship.

```text
Next, after this pull request merges: /crav1-refresh-system-notes, to bring its changes into the spec and docs/system/.
```

Then `Verdict: <Approve | Approve with comments | Changes needed>` (any Blocker or Bug: Changes needed; only tests to add or a question: Approve with comments; nothing: Approve), then the [paste-ready comment](#paste-ready-comment), then the [post offer](#post-it). Then stop.

Do not merge. Merge stays a later explicit `/crav1-merge-pr` ask for this named pull request. Do not run it. A review is not that ask. `/crav1-merge-pr` still stops on its own when a required host check is red. This skill does not replace that stop, and it does not clear it.

Do not post or vote except as [Post it](#post-it) says. Do not open a spec. Do not edit the pull request body.

## Re-review

Read `references/re-review.md` ("Re-review") only when this pull request was reviewed before (an earlier review comment or follow-ups note exists).

## Paste-ready comment

Read `references/comment.md` ("Paste-ready comment") only when you write the paste-ready comment (after Ship or not).

## Comment style

Read `references/comment.md` ("Comment style") only when you write the paste-ready comment (after the review is done).

## Follow-ups note

Read `references/notes.md` ("Follow-ups note") only when the review has follow-ups to save (after the comment).

## PR note (1.65.0)

Read `references/notes.md` ("PR note (1.65.0)") only when you save the notes, after the comment.

## Post it

Read `references/posting.md` ("Post it") only when the user answers the post question.

## Hard rules

- No review unless this turn names the pull request or clearly asks to review that one.
- Do not pick the newest pull request.
- No edits to code, `spec.md`, `plan.md`, `tasks.md`, or `verify.md`. The only writes are the PR note and the follow-ups note in the specs repo's `docs/notes/YYYY-MM/` and the generated indexes.
- Read-only toward the code repo and its host. The only git write there is the fetch of the pull request's two branches after **Fetch only the PR's two branches** or `fetch pr branches`.
- No test run, and no ask to run tests. When the slug has `plan.md`, quote `verify.md` or say it is missing. When the pull request is outside the kit, do not say `verify.md` is missing. Read the pipeline's recorded test results.
- No linter install. No branch-protection change. No required-check edit.
- Read `references/comment-as-posted.md` ("Record step rules") only when the record step runs.
- No comment, no vote, and no thread resolve without the user's yes in [Post it](#post-it). One comment, no inline threads, never Reject. No label, no reviewer assignment.
- Suggest merging `<base>` into the branch, never a rebase, `pull --rebase`, or a force-push.
- No merge. Do not run `/crav1-merge-pr`.
- Do not run `/crav1-refresh-system-notes`. On an outside pull request, name it once, as the next step after the pull request merges.
- Do not run this skill from `/crav1-open-pr`, `/crav1-merge-pr`, spark, specify, plan, or verify.
- No `git checkout`, no `git commit`, no new branch, no push.
- No dialog-box or browser Microsoft sign-in. No token printed or created.
