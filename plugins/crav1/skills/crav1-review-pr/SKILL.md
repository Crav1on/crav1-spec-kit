---
name: crav1-review-pr
description: >-
  Read one named open pull request and report whether it can ship. Spec,
  plan, verify.md, the pull request body, and a required green linter.
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

Run it only when **this turn** names an open pull request (number or URL), or clearly asks to review that pull request. Any open pull request, not only a feature branch. If this turn does not name one, ask which one. That turn is the question only. Do not pick the newest. Do not review a pull request they did not name.

`/crav1-open-pr` may name this command as an optional next step. It must not run it. `/crav1-merge-pr` must not run it. A review is not a merge ask. Spark, specify, and verify do not run this command. Do not run it from those skills. Do not run it from plan.

You read the diff. You do not edit code, the spec, or the plan. You do not run the tests. You do not vote, post a comment, install a linter, change branch protection, or merge. A comment or a vote is a later explicit ask, not this skill.

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

- **Spec and plan.** When the head is `feat/<slug>` or `spec/<slug>`, or the body links `docs/specs/<slug>/`, read that folder's `spec.md`, `plan.md`, and `tasks.md` when they exist. When several spec folders changed against the target, read each. When none exist, say so.
- **Verify.** Quote `verify.md` when that file is already on the branch. Say so when it is missing. Do not run the tests. Do not write `verify.md`.
- **Pull request body.** The description as the host returned it.
- **Linter.** Whether a linter or checker covers the code in the diff, and whether that check is required on this pull request and green. Read the check rollup (GitHub) or the policy list (Azure DevOps), and the lint or checker config on the head when you need it to see coverage. Do not install a linter. Do not change branch protection.

A test run is not a linter. Verify stays the quote from `verify.md`. The linter check is separate.

When the diff has no code, say there is no code for a linter to cover. That linter check holds. Do not invent a linter for a diff the repo's own checker does not claim.

## First section

This section must be true before the review says ship.

Walk these five checks. Each miss is its own finding. Do not bundle two misses into one finding. Any finding whose decision is **fix** or **drop** means the review does not say ship.

A check that holds has no finding.

Each finding is three lines:

```text
F1 — <Spec | Plan | Verify | Body | Linter | Secret> — <lane or next step>
What is off: <one line>
What could happen: <one line>
Decision: <ship | fix | drop>
```

Number `F1`, `F2`, …. A miss on these five checks is **fix** or **drop**, not ship. **Drop** means the extra behavior should come out. **Fix** means the diff, the plan, the proof, the body, or the check should change so the review can ship later. **Ship** on a finding is only for a note that does not block. Do not use it to wave a miss through.

Name the lane. Do not start it. Do not run the command you name.

| Miss | Decision | Lane or next step |
| --- | --- | --- |
| Spec: the diff adds product behavior the spec never asked for | drop | Specify (acceptance and diff disagree) |
| Spec: the diff leaves out something the spec said must be true | fix | Specify (acceptance and diff disagree) |
| Plan: a task never named a needed file or check | fix | Plan |
| Verify: `verify.md` is on the branch and its quote shows a failure, or the quote does not cover a check the plan named for this diff | fix | Build |
| Verify: `verify.md` is missing and the plan named checks for this diff | fix | Build. Say the file is missing. Do not run the tests |
| A file the plan already named is not in the diff | fix | Build. This is not a plan miss |
| Body: the description is wider or narrower than the diff | fix | Rewrite the pull request body. Not a new spec. The mismatch stays on this pull request. Do not edit the body in this skill |
| Linter: none covers the code in the diff, or one exists but is not required on this pull request, or it is required and red | fix | Build. Do not install a linter |

When `verify.md` is missing and the plan named no checks for this diff, say the file is missing. That is not a verify miss.

When no spec exists and the diff adds no product behavior, say there is no spec for this diff. That is not a spec miss.

When no plan exists and the diff has no code the plan should have named, say there is no plan. That is not a plan miss. When the diff has code and no plan named the files or the checks, that is a plan miss.

A secret in the diff is a first-section finding. Decision: **fix**. Name Build. Do not print the secret. Name the path. A secret is not a suggestion.

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

When the first section has no **fix** and no **drop**, the review says **ship**. Say it is clean, then stop.

When any first-section decision is **fix** or **drop**, the review does not say ship. List those findings, then the suggestions, then stop.

Do not merge. Merge stays a later explicit `/crav1-merge-pr` ask for this named pull request. Do not run it. A review is not that ask. `/crav1-merge-pr` still stops on its own when a required host check is red. This skill does not replace that stop, and it does not clear it.

Do not post the review as a comment. Do not vote. Do not open a spec. Do not edit the pull request body.

## Hard rules

- No review unless this turn names the pull request or clearly asks to review that one.
- Do not pick the newest pull request.
- No edits to code, `spec.md`, `plan.md`, `tasks.md`, or `verify.md`.
- No test run. Quote `verify.md` or say it is missing.
- No linter install. No branch-protection change. No required-check edit.
- No comment, no vote, no label, no reviewer assignment.
- No merge. Do not run `/crav1-merge-pr`.
- Do not run this skill from `/crav1-open-pr`, `/crav1-merge-pr`, spark, specify, plan, or verify.
- No `git checkout`, no `git commit`, no new branch, no push.
- No dialog-box or browser Microsoft sign-in. No token printed or created.
