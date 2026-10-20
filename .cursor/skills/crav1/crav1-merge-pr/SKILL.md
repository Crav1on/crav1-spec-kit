---
name: crav1-merge-pr
description: >-
  Merge one named pull request with a merge commit. GitHub uses gh pr merge
  --merge. Azure Repos uses az repos pr update --status completed --squash
  false. Use only when this turn explicitly asks to merge a pull request by
  number or URL. Cross-cutting. Never squash, rebase, bypass policy, or
  follow on from open-pr. Do not run /crav1-review-pr. A review is not this ask.
  After the merge, saves the PR description as a PR note in the specs repo.
disable-model-invocation: true
icon: git-merge
color: green
---

# Merge a pull request

Merge **one** named pull request with a **merge commit**, then stop. Never squash. Never rebase.

Command: `/crav1-merge-pr`.

Run it only when **this turn** explicitly asks to merge a specific pull request, named by number or URL. `/crav1-open-pr`, a build-tasks loop, `/crav1-review-pr`, or an earlier turn naming a URL is not that ask. Do not run this skill from those steps. Do not run `/crav1-review-pr` from this skill. A review is not a merge ask. If this turn does not name a pull request, ask which one. That turn is the question only. No merge.

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`. `az` may be `az.cmd`. Quote any `--query` value that contains parentheses; `cmd.exe` treats an unquoted `(` as syntax. This skill does not pass a multi-line body to `az`. A multi-line `--description` on Windows uses the `@file` steps in `/crav1-open-pr`.

## Which pull request

Accept a number (`123`) or a URL.

| URL | Id |
| --- | --- |
| `https://github.com/<owner>/<repo>/pull/<n>` | `<n>` |
| `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |
| `https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |

A branch name is not a pull request. Do not pick the newest pull request for the current branch. If the URL's repository is not this git remote, stop and name both. Do not merge across that mismatch.

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL still names the host. A bare number needs that remote, or a `gh` repo that matches it.

## Host

Resolve **one** merge path, in this order: GitHub `gh`, then Azure DevOps `az`, then printed commands and web UI steps. Do not claim the pull request was merged unless that path returned a merge commit hash. On Azure DevOps, that commit must also have two parents, counted with `git rev-list` after the completed re-read (commits API only when git cannot see the commit).

### GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub (`github.com` in the URL or the remote, or `gh repo view` succeeds for that repo).

**Merge** then uses the GitHub steps. If the pull request is on GitHub and `gh auth status` does not succeed, print the GitHub fallback below. Do not use `az`.

### Azure DevOps (`az`)

Read `references/azure-devops.md` ("Azure DevOps (`az`)") only when the remote is Azure DevOps.

### Other remotes

When the pull request is neither GitHub nor Azure DevOps, print the GitHub-shaped fallback below. Do not claim it was merged.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it.

### GitHub

```text
gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,isDraft,baseRefName,headRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
gh pr checks <n-or-url>
```

`state` must be `OPEN`.

### Azure DevOps

Read `references/azure-devops.md` ("Azure DevOps (Read it first)") only when the remote is Azure DevOps.

## Mark ready

Only when this turn is the explicit merge ask, and the pull request is a draft.

GitHub: `gh pr ready <n-or-url>`. That is the whole ready step. Do not pass extra flags.

Azure DevOps: set `isDraft` false and do not complete in the same call.

```text
az repos pr update --org <org-url> --id <n> --draft false --detect false --output json
```

`--draft` accepts `false` or `true`. This call uses `--draft false`. Do not pass `--project`, `--repository`, or `--status` on it.

Then read the pull request and its policies again. Publishing can queue checks. If the checks are not passing yet, stop and report that. Do not complete while the checks are queued. If this update fails, print the Azure DevOps fallback. Do not complete. Do not retry.

If `az` is missing and the pull request is a draft, print a first PATCH body `{"isDraft": false}` in the fallback below, then the complete PATCH. Do not claim either call was sent.

## What must pass

Required checks, branch policies, and reviews must pass. If anything blocks, stop and report what. Do not merge. This skill still stops when a required host check is red. `/crav1-review-pr` does not replace that stop, and this skill does not run it.

Never bypass. No `gh pr merge --admin`. No `--bypass-policy`. No `bypassPolicy: true`. No admin override in the web UI steps you print.

### GitHub

Stop unless all of these are true after the ready step:

| Check | Pass | Stop and report |
| --- | --- | --- |
| `mergeStateStatus` | `CLEAN` | `BLOCKED`, `DIRTY`, `DRAFT`, `BEHIND`, `UNSTABLE`, `UNKNOWN`, or anything else |
| `reviewDecision` | `APPROVED`, or empty when `mergeStateStatus` is `CLEAN` | `REVIEW_REQUIRED`, `CHANGES_REQUESTED` |
| `gh pr checks` | every required check passed; exit 0 | failing or pending lines |

`BEHIND` means the head is behind the base. `DIRTY` means the branch has conflicts with the base. Report that. Do not update the branch in this skill. Say how to fix it by merging the base in, never a rebase (1.66.0): `Merge <base> into <head> (resolve any conflicts there), push, then ask to merge again.` When they want the steps: `git switch <base>`, `git pull --ff-only`, `git switch <head>`, `git merge <base>`, `git push`. On GitHub, **Update branch** with **Update with merge commit** does the same for a branch that is only behind.

`UNSTABLE` is not a pass. Report the check names. Do not merge.

### Azure DevOps

Read `references/azure-devops.md` ("Azure DevOps (What must pass)") only when the remote is Azure DevOps.

## Show, then merge

Before the merge command, show:

```text
Title: <title>
Source: <source> → Target: <target>
Strategy: merge commit (GitHub --merge; Azure Repos noFastForward via --squash false). Not squash. Not rebase.
```

Then merge. If a blocker stopped you, show those three lines and the blocker, and do not merge.

## Merge

### GitHub

When **Host** says to use `gh`:

```text
gh pr merge <n-or-url> --merge
```

Do not pass `--squash`, `--rebase`, `--admin`, `--auto`, or `--delete-branch`.

On success, read the merge commit:

```text
gh pr view <n-or-url> --json state,mergeCommit --jq .mergeCommit.oid
```

Report that hash. If it is empty, say the host did not return a merge commit. Do not invent one.

If merge fails, show the error and the GitHub fallback. Do not retry with another strategy. Do not claim a merge.

### Azure DevOps

Read `references/azure-devops.md` ("Azure DevOps (Merge)") only when the remote is Azure DevOps.

## Fallback (no merge)

Read `references/fallback.md` ("Fallback (no merge)") only when the merge cannot run (no CLI, no rights, blocked).

## After it merged

Read `references/after-merge.md` ("After it merged") only when the merge went through.

## Local main

Read `references/after-merge.md` ("Local main") only when the merge went through.

## Branches

Read `references/after-merge.md` ("Branches") only when the merge went through.

## Tracker

Read `references/after-merge.md` ("Tracker") only when the merge went through and a work item is linked.

## Auth notes

Read `references/fallback.md` ("Auth notes") only when a CLI says it is not signed in or lacks rights.

## Hard rules

- No merge unless this turn names the pull request and asks to merge it.
- No squash (`--squash true`, squash merge, `mergeStrategy` `squash`). Azure DevOps complete uses `--squash false`, which is the no-fast-forward merge commit.
- No rebase (`--rebase`, rebase and fast-forward, semi-linear / `rebaseMerge`). Advice for a branch that is behind or has conflicts says to merge the base into it, never to rebase it.
- No `--admin`, no `--bypass-policy`, no `bypassPolicy`.
- No second strategy attempt after a refusal or a failed `az repos pr update`.
- No `git commit`, no stash, no new branch, no force-push.
- The only file this skill writes is the PR note (and the generated notes indexes) in the specs repo, after a confirmed merge. Never committed.
- No branch delete unless the user asked in this turn.
- No dialog-box or browser Microsoft sign-in (`az login`, `az devops login`, device code, or a web login).
- No token printed, echoed, or created. An `AZURE_DEVOPS_EXT_PAT` the user already set is the PAT route in **Auth notes**.
- Do not run `az rest` to complete, update, or bypass a pull request. The parent-count fallback in **Merge** may GET one commit when git cannot see it.
- Do not claim a merge commit hash the host did not return.
- Do not claim a no-fast-forward merge unless the parent count was verified as two. A null `lastMergeCommit.parents` is not that count.
- Do not run this skill from `/crav1-open-pr`, `crav1-build-task-agent`, or `/crav1-review-pr`.
- Do not run `/crav1-review-pr`. A review is not a merge ask. A required host check that is red still stops this skill.


## Choice words (1.69.0)

- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
