---
name: crav1-review-pr
description: >-
  Use when the user asks whether one named open pull request can ship, or to
  re-review it. Checks it against the spec, plan, verify and linter, drafts a
  paste-ready comment, and posts or votes only after a yes. Works across
  repos. Does not edit, test, or merge.
disable-model-invocation: true
icon: git-pull-request
color: orange
---

# Review a pull request

Read **one** named open pull request and say whether it can ship. Then stop.

Command: `/crav1-review-pr`.

This is cross-cutting, not a lane and not a bot, in the same command family as `/crav1-open-pr` and `/crav1-merge-pr`.

Run it only when **this turn** names an open pull request (number or URL), or clearly asks to review that pull request. Any open pull request, not only a feature branch. If this turn does not name one, ask which one. That turn is the question only. Do not pick the newest. Do not review a pull request the user did not name.

Read `references/which-pr.md` ("Other skills") only when another skill names or would run this one.

You read the diff. You do not edit code, the spec, or the plan, run or ask to run the tests, install a linter, change branch protection, or merge. You post comments or set a verdict only as [Post it](#post-it) says, after the user's yes. Read `references/windows.md` ("Windows") only when git or az is not found (Windows).

## Output (1.113.0)

Read `references/output.md` ("Output") every run, before you show anything. The chat shows only the postable review, its verdict, one line naming the PR note, and the post offer; everything else is the kit record in the PR note, and outside context gets its own read-only section. After the post offer: `Next: nothing needed now.` The Uncommitted line goes in the kit record when the note is not committed.

## Which file, when

- Posted by the user, or posted before: `references/posted-comments.md` ("Comment as posted first").
- Resolving the pull request (a number, a URL, `<repo> <n>`, or a branch), or none named: `references/which-pr.md` ("Which pull request").
- Gathering spec, plan, verify, body and linter state: `references/reading.md` ("What to read besides the diff").
- No plan.md or tasks.md (outside the kit): `references/outside-the-kit.md` ("Recorded tests (outside the kit only)"; "Info" also when only some slugs have them).
- Bugs, missing tests or questions found: `references/comment.md` ("Bugs, tests, questions").
- Reviewed before (an earlier review comment, PR record Point, or old follow-ups note): `references/re-review.md` ("Re-review").
- The record step runs: `references/comment-as-posted.md` ("Record step rules").
- Saving the review's points, follow-ups and comment, after the comment: `references/notes.md` ("PR record"; 1.97.0, one shared record in the PR note, no follow-ups note).

## Specs repo and code repo

Read `references/cross-repo.md` ("Specs repo and code repo") only when the pull request is in a different repo from the specs (repos.md), or both repos are open.

## Host and reading the pull request

Shared steps (host order, Windows, state, claims, catching up, signing in): [pr-common.md](../crav1-docs/reference/pr-common.md) (1.158.0). Pick **one** read path with skill `crav1-open-pr`, `references/host.md`: GitHub `gh`, then Azure DevOps `az`, then say you cannot read the pull request. It must be **open**; a draft counts (`OPEN` on GitHub, `active` on Azure DevOps). Anything else: stop and say the state. Do not reopen it. Then read `references/github.md` ("GitHub (Read it first)") or `references/azure-devops.md` ("Azure DevOps (Read it first)"), and its "Diff from a sibling checkout (Azure DevOps)" only when Azure DevOps gives no diff and a sibling checkout exists.

## Choice words

Exact words for bots and scripted runs (`branch`, `fetch pr branches`, `use disk`, `stop pr review`, `comment posted`, `newest comment`, `skip comment record`). There are no `--flags`. Read `references/choice-words.md` ("Choice words") when a word is given or a question would offer them.

## First section

This section must be true before the review says ship. When every slug under review has `plan.md`, walk these five checks: Spec, Plan, Verify, Body, and Linter. Outside the kit (no plan.md): `references/outside-the-kit.md` ("Outside pull request, in the review").

Each miss is its own finding (`F1 — <check> — <lane>`, then What is off, What could happen, Decision: ship | fix | drop), written as `references/first-section.md` ("Finding format") says. Its "Miss table" picks the decision and lane when a check misses, and its "First section: special cases" covers a missing verify.md, no spec, or no code the plan named. Any **fix** or **drop** means the review does not say ship. Name the lane. Do not start it. Do not run the command you name.

A secret in the diff is a first-section finding on every pull request. Decision: **fix**. Name Build. Do not print the secret. Name the path. A secret is not a suggestion. A secret is not an info note.

## Second section

Style, patterns, and practices; suggestions only, as `references/second-section.md` ("Second section") says. Read it before any suggestion, or to say none.

## Fixed checks

Every run, read `references/checklist.md` and write its 7 check lines into the kit record, one line each even when clean (1.95.0).

## Ship or not

Every run, read `references/ship.md` ("Ship or not") for the kit record order, the verdict words and the closing line. When the first section has no **fix** and no **drop**, the review says **ship**; any **fix** or **drop**, it does not. Then show the verdict, the [paste-ready comment](#paste-ready-comment), the `Kit record:` line and the [post offer](#post-it), and stop.

Do not merge. Merge stays a later explicit `/crav1-merge-pr` ask for this named pull request; do not run it, since a review is not that ask. `/crav1-merge-pr` still stops on its own when a required host check is red; this skill neither replaces nor clears that stop. Do not post or vote except as [Post it](#post-it) says. Do not open a spec or edit the pull request body.

## Paste-ready comment

Read `references/comment.md` ("Paste-ready comment" and "Comment style") only when you write the paste-ready comment (after Ship or not).

## PR note

Read `references/notes.md` ("PR note") only when you save the notes, after the comment.

## Post it

Read `references/posting.md` ("Post it") only when the user answers the post question.

## Hard rules

- No edits to code, `spec.md`, `plan.md`, `tasks.md`, or `verify.md`. The only writes are the PR note (with its PR record), the context file when outside context was added, in the specs repo's `docs/notes/YYYY-MM/`, and the generated indexes.
- Read-only toward the code repo and its host. The only git write there is the fetch of the pull request's two branches after **Fetch only the PR's two branches** or `fetch pr branches`.
- No test run, and no ask to run tests. When the slug has `plan.md`, quote `verify.md` or say it is missing. When the pull request is outside the kit, do not say `verify.md` is missing. Read the pipeline's recorded test results.
- No linter install, branch-protection change, or required-check edit.
- No comment, no vote, and no thread resolve without the user's yes in [Post it](#post-it). One comment, no inline threads, never Reject. No label, no reviewer assignment.
- Suggest merging `<base>` into the branch, never a rebase, `pull --rebase`, or a force-push.
- Do not run `/crav1-refresh-system-notes`; the kit record names it once, for after the merge.
- Posting takes only the review block. Never the kit record or the context file.
- Do not run this skill from `/crav1-open-pr`, `/crav1-merge-pr`, spark, specify, plan, or verify.
- No `git checkout`, no `git commit`, no new branch, no push.
- No dialog-box or browser Microsoft sign-in. No token printed or created ([pr-common.md](../crav1-docs/reference/pr-common.md), "Signing in and secrets").

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
