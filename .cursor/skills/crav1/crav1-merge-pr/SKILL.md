---
name: crav1-merge-pr
description: >-
  Use only when this turn explicitly asks to merge a named pull request.
  Merges with a merge commit on GitHub or Azure Repos, never squash or rebase,
  and stops when the PR record says not ready unless told anyway. Saves the
  merged state in the PR note.
disable-model-invocation: true
icon: git-merge
color: green
---

# Merge a pull request

Merge **one** named pull request with a **merge commit**, then stop. Never squash. Never rebase.

Command: `/crav1-merge-pr`.

Run it only when **this turn** explicitly asks to merge a specific pull request, named by number or URL. `/crav1-open-pr`, a build-tasks loop, `/crav1-review-pr`, or an earlier turn naming a URL is not that ask. Do not run this skill from those steps. If this turn does not name a pull request, ask which one. That turn is the question only. No merge.

The steps shared with open-pr, pr-status and review-pr (which pull request, host order, Windows, state, claims, catching up, signing in) are [pr-common.md](../crav1-docs/reference/pr-common.md) (1.158.0). Read it every run. The merge rules here win over that page.

## Which pull request

A number (`123`) or a URL, as [pr-common.md](../crav1-docs/reference/pr-common.md) ("Which pull request") says. A branch name is not a pull request; never pick the newest. A URL whose repository is not this git remote: stop, name both, and do not merge across that mismatch.

## Host

Resolve **one** merge path, in this order: GitHub `gh`, then Azure DevOps `az`, then printed commands and web UI steps. Do not claim the pull request was merged unless that path returned a merge commit hash. On Azure DevOps, that commit must also have two parents, counted with `git rev-list` after the completed re-read (commits API only when git cannot see the commit).

Read `references/github.md` ("GitHub (Host)") for GitHub or another host, `references/azure-devops.md` ("Azure DevOps (`az`)") for Azure DevOps.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it.

Read `references/github.md` ("GitHub (Read it first)") on GitHub, where `state` must be `OPEN`, and `references/azure-devops.md` ("Azure DevOps (Read it first)") on Azure DevOps.

## Mark ready

Only when this turn is the explicit merge ask, and the pull request is a draft.

GitHub: `gh pr ready <n-or-url>`. That is the whole ready step. Do not pass extra flags. Azure DevOps, or `az` missing: read `references/azure-devops.md` ("Azure DevOps (Mark ready)").

## What must pass

Required checks, branch policies, and reviews must pass. If anything blocks, stop and report what. Do not merge. A red required host check stops this skill; `/crav1-review-pr` does not replace that stop. Never bypass (no `gh pr merge --admin`, `--bypass-policy`, `bypassPolicy: true`, or admin override in the web UI steps you print).

Read `references/github.md` ("GitHub (What must pass)") only when the remote is GitHub, and `references/azure-devops.md` ("Azure DevOps (What must pass)") only when it is Azure DevOps. `scripts/pr_common.py checks --ref <n-or-url>` only sums them up for the chat; it is not the gate.

## PR record gate (1.97.0)

Read `references/pr-record-gate.md` ("The Ready line") before **Show, then merge**, every run. The PR note's `Ready: no` stops the merge unless this turn says `anyway`. `anyway` never skips a required check, policy or review.

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

## Fallback and after the merge

- The merge cannot run (no CLI, no rights, blocked): `references/fallback.md` ("Fallback (no merge)"). Not signed in or no rights: its "Auth notes".
- The merge went through: `references/after-merge.md` ("After it merged", "Local main", "Branches"; "Tracker" when a work item is linked).

## Claims (1.158.0)

This skill never writes, clears, commits or pushes `claims.md`. `/crav1-build-walk` clears its own claim after the merge; a standalone merge leaves `claims.md` as it is.

## Hard rules

- No merge unless this turn names the pull request and asks to merge it.
- No squash (`--squash true`, squash merge, `mergeStrategy` `squash`). Azure DevOps complete uses `--squash false`, which is the no-fast-forward merge commit.
- No rebase (`--rebase`, rebase and fast-forward, semi-linear / `rebaseMerge`). Advice for a branch that is behind or has conflicts says to merge the base into it, never to rebase it.
- No `--admin`, no `--bypass-policy`, no `bypassPolicy`.
- No second strategy attempt after a refusal or a failed `az repos pr update`.
- No `git commit`, no stash, no new branch, no force-push.
- The only file this skill writes is the PR note with its PR record (and the generated notes indexes) in the specs repo, after a confirmed merge. Never committed.
- No branch delete unless the user asked in this turn.
- No dialog-box or browser Microsoft sign-in (`az login`, `az devops login`, device code, or a web login). No token printed, echoed, or created; an `AZURE_DEVOPS_EXT_PAT` the user already set is the PAT route in **Auth notes**.
- Do not run `az rest` to complete, update, or bypass a pull request. The parent-count fallback in **Merge** may GET one commit when git cannot see it.
- Do not claim a merge commit hash the host did not return.
- Do not claim a no-fast-forward merge unless the parent count was verified as two. A null `lastMergeCommit.parents` is not that count.
- Do not run this skill from `/crav1-open-pr`, `crav1-build-task-agent`, or `/crav1-review-pr`. A yes on `/crav1-build-walk`'s card that names this pull request is the ask in this turn. The walk opens this file after that yes.
- Do not run `/crav1-review-pr`. A review is not a merge ask. A required host check that is red still stops this skill.
- When `/crav1-build-walk` opened this file, do not print a line of your own for what to run next. The walk prints its one line (1.142.0).

## Choice words (1.69.0)

- Pipeline runs: `pipeline runs` (check the latest successful Azure DevOps runs behind the Promotion line without asking). There are no `--flags`.
- Not ready: `anyway` (1.97.0; merge although the PR record says `Ready: no`; host checks still apply).

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
