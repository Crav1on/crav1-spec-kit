---
name: crav1-open-pr
description: >-
  Use when commits exist on feat/<slug> or spec/<slug> and the user wants a
  pull request, or to push to an existing one. Pushes only after a yes, opens
  it with gh or az, or on an existing pull request offers to update its
  description or add a comment, posted only on a yes. Does not commit or merge.
disable-model-invocation: true
icon: git-pull-request
color: green
---

# Open a pull request

Push the change branch **only after an explicit yes**, open **one** pull request against the head's into branch (see **Base branch**; usually the default branch), then stop. Do not merge (that is `/crav1-merge-pr`, on its own explicit ask) and do not commit.

Create with `gh` on GitHub, `az repos pr` on Azure DevOps, otherwise print filled commands and GitKraken GUI paste fields. Do not claim a pull request was opened unless the host returned a URL.

Command: `/crav1-open-pr`.

Run it only when the user invoked `/crav1-open-pr` or clearly asked to open a pull request in this chat. Other skills may **name** it as an optional next step; do not run it from those steps. `crav1-build-task-agent` does not push or open a pull request.

## Inputs

Resolve these before you push or create anything. Prompt when a value is missing or ambiguous; show the resolved values with the draft.

| Input | Default |
| --- | --- |
| Base | The head's into branch, then the repo's `Merges into` branch, then the repo default branch. See **Base branch**. Confirm when ambiguous. |
| Head | Current branch when it is not the base. Otherwise ask. Do not check out a different branch in this skill. |
| Title | `<slug>: <short summary>` when the head is `feat/<slug>` or `spec/<slug>`. Summary is the `spec.md` H1 when `docs/specs/<slug>/spec.md` exists; otherwise the latest commit subject on the head. No slug: latest commit subject. |
| Body | Format A in `references/draft.md`: a short summary, then headed sections with link-first bullets pinned to the head commit. No spec link. |
| Push | Ask once, **after** the title and body are visible. Options in order: **push and open PR** (first/top), **open PR only** (remote already has the branch), **stop**. |

The steps shared with merge-pr, pr-status and review-pr (host order, finding the pull request for a branch, claims, catching up, signing in) are [pr-common.md](../crav1-docs/reference/pr-common.md) (1.158.0). Read it every run. This file keeps what open-pr drafts and pushes. On Windows, read `references/host.md` ("Windows").

## Base branch

The base is the head's into branch (skill `crav1-add-to-spec`, `references/branches.md`, "Base branch and Merges into"). Read `references/base.md` ("Base branch") to resolve it: the `(into …)` ask, the `Merges into` lookup (also in sibling checkouts), and the default-branch steps. Name where the base came from in the draft.

Remote: the single `git remote`; several: ask which one. None: draft the title and body if you can, then stop, say no remote is configured, and do not claim a push or a pull request.

## Checks (before the draft)

Every run, read `references/checks.md` ("Checks (before the draft)") and run its checks first: not a git repo, detached HEAD, dirty tree (point at `/crav1-finalize-commit`), no commits ahead of the base, no local head, or the head is the base. Abort in one short message. Do not commit, stash, or check out. If base or head is still ambiguous, that turn is the question only. No title, no body, no push menu.

## Draft title and body

Read `references/draft.md` ("Draft title and body") only when you draft the title and body (Format A, 1.98.0). Never link the spec; a missing rollback on an infra or PROD change is said in the chat only.

## Host

Read `references/host.md` to pick **one** create path: GitHub `gh`, then Azure DevOps `az`, then printed commands and GitKraken GUI paste.

## Push and open

Only after they pick `push` on the current draft.

1. `git push -u <remote> <head>`. Never `--force`, `--force-with-lease`, `--force-if-includes`, or a refspec that starts with `+`.
2. If the push fails, show the error. Do not open a pull request. Do not force-push. When it was rejected because the remote branch has commits this one lacks, say: `Pull <head> with git pull --no-rebase, resolve any conflicts, then push again.` A `walk-progress.md` conflict that is only version lines is `resolve-stamps`, the same command `/crav1-finalize-commit` runs (1.139.0). Never suggest a rebase or a force-push (1.66.0).
3. Open one pull request (below). If one already exists for this head → base, follow **Existing pull request** instead.

## Open only

Read `references/open-only.md` ("Open only") only after they pick `open` on the current draft.

## Create

- GitHub, when **Host** says `gh`: read `references/github.md` ("GitHub (Create)"). It checks for an open pull request for this head → base first (`scripts/pr_common.py find --branch <head> --base <base>`, or `gh pr list`), then runs `gh pr create` once.
- Azure DevOps: read `references/azure-devops.md` ("Azure DevOps (Create)") only when the remote is Azure DevOps.
- No host create: read `references/fallback.md` ("No host create") only when no host CLI can open the pull request.

## Existing pull request

Read `references/existing-pr.md` ("Existing pull request", 1.114.0) when a pull request is already open for this head → base. It offers **update description**, **add as comment**, **push only** and **stop**, and posts the exact text shown only on a yes.

## After it exists

Read `references/after.md` ("After it exists") only when the pull request exists.

## Hard rules

- No `git commit`, no `git commit --amend`, no stash, no `git checkout`, no new branch.
- No force-push. No advice to rebase or force-push; a rejected push is fixed by pulling with a merge.
- No merge (`gh pr merge`, completing an Azure DevOps pull request, or a local merge). Merging is `/crav1-merge-pr` on a later explicit ask for a named pull request. Do not run it or `/crav1-review-pr` from this skill; a review is not a merge ask.
- No second pull request for the same head → base.
- On an existing pull request, post a description update or a comment only on a yes to the latest shown text. Never change its title, reviewers or state.
- No repository setting changes.
- No `gk ai pr create` and no other interactive `gk` pull-request create. GitKraken stays GUI paste only.
- No dialog-box or browser Microsoft sign-in, and no token printed, as [pr-common.md](../crav1-docs/reference/pr-common.md) says.
- No `--work-items` and no `--transition-work-items` unless they asked for that in this chat. A **Work item** section in the body is not that flag.
- Do not block the pull request when `work-item.md` is missing. Do not create a work item and do not look one up.
- Do not claim a pull request was opened unless the host returned a URL. Do not run this skill from `crav1-build-task-agent`.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
