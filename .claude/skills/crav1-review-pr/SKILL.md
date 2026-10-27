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
  description, findings and follow-ups in the PR note's shared PR record
  in the specs repo's docs/notes/YYYY-MM/, with the comment as drafted
  and as posted, and marks drafted points left out. Does not edit, test,
  or merge.
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

## Comment as posted first

Read `references/posted-comments.md` ("Comment as posted first") only when the user says they posted the comment themselves, or a review of this PR was posted before.

## Which pull request

Read `references/which-pr.md` ("Which pull request") only when you resolve the named pull request (a number, a URL, `<repo> <n>`, or a branch) or none is named.

## Specs repo and code repo

Read `references/cross-repo.md` ("Specs repo and code repo") only when the pull request is in a different repo from the specs (repos.md), or both repos are open.

## Host

Read `crav1-open-pr` `references/host.md` (drop-in: `.claude/skills/crav1-open-pr/references/host.md`; plugin: sibling `skills/crav1-open-pr/references/host.md`) to pick **one** read path: GitHub `gh`, then Azure DevOps `az`, then say you cannot read the pull request.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it. A draft counts as open (`OPEN` on GitHub, `active` on Azure DevOps).

### GitHub

Read `references/github.md` ("GitHub (Read it first)") only when the remote is GitHub.

### Azure DevOps

Read `references/azure-devops.md` ("Azure DevOps (Read it first)") only when the remote is Azure DevOps.

### Diff from a sibling checkout (Azure DevOps)

Read `references/azure-devops.md` ("Diff from a sibling checkout (Azure DevOps)") only when Azure DevOps gives no diff and a sibling checkout exists.

## Choice words

Exact words for bots and scripted runs (`branch`, `fetch pr branches`, `use disk`, `stop pr review`, `comment posted`, `newest comment`, `skip comment record`). There are no `--flags`. Read `references/choice-words.md` ("Choice words") when a word is given or a question would offer them.

## What to read besides the diff

Read `references/reading.md` ("What to read besides the diff") only when you gather the spec, plan, verify, body and linter state, before the first section.

## Recorded tests (outside the kit only)

Read `references/outside-the-kit.md` ("Recorded tests (outside the kit only)") only when the slug has no plan.md or tasks.md (outside the kit).

## First section

This section must be true before the review says ship.

When every slug under review has `plan.md`, walk these five checks: Spec, Plan, Verify, Body, and Linter.

Read `references/outside-the-kit.md` ("Outside pull request, in the review") only when the pull request is outside the kit (no plan.md).

Each miss is its own finding (`F1 — <check> — <lane>`, then What is off, What could happen, Decision: ship | fix | drop). Any **fix** or **drop** means the review does not say ship. Read `references/first-section.md` ("Finding format") when you write a finding. Name the lane. Do not start it. Do not run the command you name.

Read `references/first-section.md` ("Miss table") only when a first-section check misses (to pick its decision and lane).

Read `references/first-section.md` ("First section: special cases") only when verify.md is missing, there is no spec, or the diff has no code the plan named.

A secret in the diff is a first-section finding on every pull request. Decision: **fix**. Name Build. Do not print the secret. Name the path. A secret is not a suggestion. A secret is not an info note.

## Info

Read `references/outside-the-kit.md` ("Info") only when the slug has no plan.md or tasks.md, or some slugs do and some don't.

## Second section

Style, patterns, and practices. Suggestions only.

Read `references/second-section.md` ("Second section") before you write any suggestion, or to say none.

## Bugs, tests, questions

Read `references/comment.md` ("Bugs, tests, questions") only when the review found bugs, missing tests or questions.

## Fixed checks

Every run, read `references/checklist.md` and show its 7 check lines, one line each even when clean: spec and plan match, tests, secrets, infrastructure access per environment, environment parity, spec wording a bug touches, merge order (1.95.0).

## Ship or not

Show the check lines, then findings, then info notes, then suggestions, then bugs, tests to add and questions.

When the first section has no **fix** and no **drop**, the review says **ship**. Say it is clean. Info notes do not change that.

When any first-section decision is **fix** or **drop**, the review does not say ship.

```text
Next, after this pull request merges: /crav1-refresh-system-notes, to bring its changes into the spec and docs/system/.
```

Then `Verdict: <Approve | Approve with comments | Changes needed>` (any Blocker or Bug: Changes needed; only tests to add or a question: Approve with comments; nothing: Approve), then the [paste-ready comment](#paste-ready-comment), then the [post offer](#post-it). Then stop.

Do not merge. Merge stays a later explicit `/crav1-merge-pr` ask for this named pull request. Do not run it. A review is not that ask. `/crav1-merge-pr` still stops on its own when a required host check is red. This skill does not replace that stop, and it does not clear it.

Do not post or vote except as [Post it](#post-it) says. Do not open a spec. Do not edit the pull request body.

## Re-review

Read `references/re-review.md` ("Re-review") only when this pull request was reviewed before (an earlier review comment, PR record Point, or old follow-ups note exists).

## Paste-ready comment

Read `references/comment.md` ("Paste-ready comment") only when you write the paste-ready comment (after Ship or not).

## Comment style

Read `references/comment.md` ("Comment style") only when you write the paste-ready comment (after the review is done).

## PR record

Read `references/notes.md` ("PR record") only when you save the review's points, follow-ups and comment (after the comment). 1.97.0: one shared record in the PR note, no follow-ups note.

## PR note

Read `references/notes.md` ("PR note") only when you save the notes, after the comment.

## Post it

Read `references/posting.md` ("Post it") only when the user answers the post question.

## Hard rules

- No edits to code, `spec.md`, `plan.md`, `tasks.md`, or `verify.md`. The only writes are the PR note (with its PR record) in the specs repo's `docs/notes/YYYY-MM/` and the generated indexes.
- Read-only toward the code repo and its host. The only git write there is the fetch of the pull request's two branches after **Fetch only the PR's two branches** or `fetch pr branches`.
- No test run, and no ask to run tests. When the slug has `plan.md`, quote `verify.md` or say it is missing. When the pull request is outside the kit, do not say `verify.md` is missing. Read the pipeline's recorded test results.
- No linter install. No branch-protection change. No required-check edit.
- Read `references/comment-as-posted.md` ("Record step rules") only when the record step runs.
- No comment, no vote, and no thread resolve without the user's yes in [Post it](#post-it). One comment, no inline threads, never Reject. No label, no reviewer assignment.
- Suggest merging `<base>` into the branch, never a rebase, `pull --rebase`, or a force-push.
- Do not run `/crav1-refresh-system-notes`. On an outside pull request, name it once, as the next step after the pull request merges.
- Do not run this skill from `/crav1-open-pr`, `/crav1-merge-pr`, spark, specify, plan, or verify.
- No `git checkout`, no `git commit`, no new branch, no push.
- No dialog-box or browser Microsoft sign-in. No token printed or created.
