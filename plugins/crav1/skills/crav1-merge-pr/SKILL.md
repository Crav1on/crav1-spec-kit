---
name: crav1-merge-pr
description: >-
  Merge one named pull request with a merge commit. GitHub uses gh pr merge
  --merge. Azure Repos uses az repos pr update --status completed
  --merge-strategy noFastForward. Use only when this turn explicitly asks to
  merge a pull request by number or URL. Cross-cutting. Never squash, rebase,
  bypass policy, or follow on from open-pr.
disable-model-invocation: true
icon: git-merge
color: green
---

# Merge a pull request

Merge **one** named pull request with a **merge commit**, then stop. Never squash. Never rebase.

Command: `/crav1-merge-pr`.

Run it only when **this turn** explicitly asks to merge a specific pull request, named by number or URL. `/crav1-open-pr`, a complete-task loop, a review, or an earlier turn naming a URL is not that ask. Do not run this skill from those steps. If this turn does not name a pull request, ask which one. That turn is the question only. No merge.

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`.

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

Resolve **one** merge path, in this order: GitHub `gh`, then Azure DevOps `az`, then printed commands and web UI steps. Do not claim the pull request was merged unless that path returned a merge commit hash.

### GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub (`github.com` in the URL or the remote, or `gh repo view` succeeds for that repo).

**Merge** then uses the GitHub steps. If the pull request is on GitHub and `gh auth status` does not succeed, print the GitHub fallback below. Do not use `az`.

### Azure DevOps (`az`)

Treat the remote or the pull request URL as Azure DevOps when it matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read org, project, and repository from that URL when you can:

| Shape | Org / project / repo |
| --- | --- |
| `https://dev.azure.com/<org>/<project>/_git/<repo>` | path segments |
| `https://<org>@dev.azure.com/<org>/<project>/_git/<repo>` | path segments (ignore the userinfo) |
| `https://<org>.visualstudio.com/<project>/_git/<repo>` | host label is the org |
| `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` | path after `v3/` |
| `git@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` | path after `v3/` |
| `<org>@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` | path after `v3/` |

`ssh://` URLs use the same path segments. Strip a trailing `.git`. Percent-decode project and repository when the URL encoded them. A collection segment such as `DefaultCollection` stays in the web URL; it is not the `--project` value.

Use `az repos pr` only when **all** of these are true:

1. `az` is on `PATH` (on Windows, `az.cmd` counts).
2. The azure-devops extension works or can be used. `az repos pr list -h` exits 0, or the first `az repos pr` call succeeds. Microsoft documents that this extension installs automatically the first time an `az repos pr` command runs (Azure CLI 2.30.0 or higher). If that first call still cannot run `az repos pr`, the extension is not usable.
3. The CLI is already authenticated for a non-interactive call. A show or list call for this pull request that returns without an auth error counts. `az account show` exiting 0 is a hint, not proof. A dialog box or a browser Microsoft sign-in is not a merge path. Do not run `az login`, a device-code flow, or a web login. Do not create a token.

Prefer org, project, and repository parsed from the pull request URL, else the remote. Pass them on the command and pass `--detect false`:

- `--org` is the organization URL, for example `https://dev.azure.com/<org>` or `https://<org>.visualstudio.com`
- `--project` is the team project
- `--repository` is the repo name or id

`--detect` is documented as "Automatically detect organization" (`true` or `false`; default `true`). From a local Azure Repos checkout it reads **that** git remote and overrides `az devops configure` defaults. Command flags win over detection. Use `--detect true`, and omit only the flags you could not parse, **only** when the URL did not yield org, project, and repository **and** this command runs in a local checkout of that same remote. Otherwise do not use `--detect true`.

**Merge** then uses the Azure DevOps steps. If `az` is missing, the extension is not usable, the CLI is not already authenticated, or show/update fails, print the Azure DevOps fallback below. Do not invent a merge commit hash.

### Other remotes

When the pull request is neither GitHub nor Azure DevOps, print the GitHub-shaped fallback below. Do not claim it was merged.

## Read it first

The pull request must be **open**. Anything else: stop and say the state. Do not reopen it.

### GitHub

```text
gh pr view <n-or-url> --json number,url,title,state,isDraft,baseRefName,headRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
gh pr checks <n-or-url>
```

`state` must be `OPEN`.

### Azure DevOps

```text
az repos pr show --org <org-url> --id <n> --detect false --output json
az repos pr policy list --org <org-url> --id <n> --detect false --output json
```

Use the `--detect true` form from **Host** only in the case Host allows, and only for the flags you could not parse.

`status` must be `active`. That is the open set, including drafts.

Keep `title`, source branch (`headRefName` or `sourceRefName`), and target branch (`baseRefName` or `targetRefName`). Strip a `refs/heads/` prefix when you show the branches.

## Mark ready

Only when this turn is the explicit merge ask, and the pull request is a draft.

GitHub: `gh pr ready <n-or-url>`. That is the whole ready step. Do not pass extra flags.

Azure DevOps: set `isDraft` false and do not complete in the same call.

```text
az repos pr update --org <org-url> --project <project> --repository <repo> --id <n> --draft false --detect false --output json
```

Then read the pull request and its policies again. Publishing can queue checks. If they are not passing yet, stop and report that. Do not complete while they are queued.

If `az` is missing and the pull request is a draft, print a first PATCH body `{"isDraft": false}` in the fallback below, then the complete PATCH. Do not claim either call was sent.

## What must pass

Required checks, branch policies, and reviews must pass. If anything blocks, stop and report what. Do not merge.

Never bypass. No `gh pr merge --admin`. No `--bypass-policy`. No `bypassPolicy: true`. No admin override in the web UI steps you print.

### GitHub

Stop unless all of these are true after the ready step:

| Check | Pass | Stop and report |
| --- | --- | --- |
| `mergeStateStatus` | `CLEAN` | `BLOCKED`, `DIRTY`, `DRAFT`, `BEHIND`, `UNSTABLE`, `UNKNOWN`, or anything else |
| `reviewDecision` | `APPROVED`, or empty when `mergeStateStatus` is `CLEAN` | `REVIEW_REQUIRED`, `CHANGES_REQUESTED` |
| `gh pr checks` | every required check passed; exit 0 | failing or pending lines |

`BEHIND` means the head is behind the base. Report that. Do not update the branch in this skill.

`UNSTABLE` is not a pass. Report the check names. Do not merge.

### Azure DevOps

Stop unless all of these are true after the ready step:

| Check | Pass | Stop and report |
| --- | --- | --- |
| `mergeStatus` | `succeeded` | `conflicts`, `failure`, `rejectedByPolicy`, `queued`, or anything else |
| Required reviewers | `isRequired` and vote `10` or `5` | vote `0`, `-5`, or `-10` on a required reviewer |
| Blocking policies | enabled and `isBlocking`, status `approved` or `notApplicable` | `queued`, `rejected`, `broken`, `running`, or any other status |

Do not call `az repos pr set-vote`. Do not vote for them.

## Show, then merge

Before the merge command, show:

```text
Title: <title>
Source: <source> → Target: <target>
Strategy: merge commit (GitHub --merge; Azure Repos noFastForward). Not squash. Not rebase.
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

When **Host** says to use `az`:

```text
az repos pr update --org <org-url> --project <project> --repository <repo> --id <n> --status completed --merge-strategy noFastForward --detect false --output json
```

That is a normal merge commit (`noFastForward`). Do not pass `--squash`, `--bypass-policy`, `--bypass-policy-reason`, `--delete-source-branch`, `--transition-work-items`, `--auto-complete`, or `--merge-commit-message`.

The published `az repos pr update` command may not list `--merge-strategy` (it has `--squash`, which this skill does not use). If this `az` rejects `--merge-strategy`, stop. Do not retry with `--squash`, with `--squash false`, or with `--status completed` alone. A status-only complete copies completion options already on the pull request, and those can be squash. Print the Azure DevOps fallback. Do not claim the pull request was merged.

On success, report `lastMergeCommit.commitId` from the JSON. That is the merge commit. Also say `status` and `completionOptions.mergeStrategy` when they are present. If `mergeStrategy` is not `noFastForward`, say what the host returned. Do not invent a hash. If `lastMergeCommit` is empty, say the merge commit is not in the response yet. Do not guess.

If update fails for any other reason, print the Azure DevOps fallback. Do not invent a hash. Do not start a sign-in.

## Fallback (no merge)

Print the title, `source` → `target`, and the strategy line from **Show, then merge**. Then the filled commands. This printout is not a completed merge.

GitHub, or a remote that is not Azure DevOps:

```text
gh pr ready <n>
gh pr checks <n>
gh pr merge <n> --merge
gh pr view <n> --json mergeCommit --jq .mergeCommit.oid
```

Web UI: open the pull request. If it is a draft, choose **Ready for review**. Then **Merge pull request** → **Create a merge commit**. Do not choose **Squash and merge** or **Rebase and merge**. Do not use an admin override. Do not delete the branch unless they asked in this turn.

Azure DevOps. Fill org, project, and repository from the URL or the remote when you have them. Name any you could not parse. Do not invent them. Repository id from `repository.id` on a show payload when you have it; otherwise the repository name from the URL.

The call uses the git credential or `az login` session they already have. Do not create a PAT. Do not print a token. Do not add an Authorization header. `az rest` is fine only when `az` is already logged in; if `az` is missing, print the request and the web UI, and do not run `az rest`.

Draft, when it is still a draft:

```text
PATCH https://dev.azure.com/<org>/<project>/_apis/git/repositories/<repo>/pullrequests/<id>?api-version=7.1
Content-Type: application/json

{"isDraft": false}
```

Complete (merge commit). `lastMergeSourceCommit.commitId` is the pull request's current source tip (`lastMergeSourceCommit` on the open pull request). Do not invent that SHA. If you could not read it, leave the placeholder and say so.

```text
PATCH https://dev.azure.com/<org>/<project>/_apis/git/repositories/<repo>/pullrequests/<id>?api-version=7.1
Content-Type: application/json

{
  "status": "completed",
  "lastMergeSourceCommit": { "commitId": "<lastMergeSourceCommit.commitId>" },
  "completionOptions": { "mergeStrategy": "noFastForward" }
}
```

Use `https://<org>.visualstudio.com/...` when that is the host. Do not set `bypassPolicy`, `deleteSourceBranch`, `squashMerge`, or `transitionWorkItems`.

Web UI: open `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<id>` (or the `*.visualstudio.com` form). If it is a draft, **Publish**. Then **Complete**. Merge type: **Merge (no fast forward)**. Do not choose **Squash commit**, **Rebase and fast-forward**, or **Semi-linear merge**. Leave bypass policies off. Do not delete the source branch unless they asked in this turn. Do not change work-item links.

GitKraken stays **GUI paste only** when they already use it for this repo: complete the named pull request with a merge commit (no fast-forward). Do not squash. Do not rebase.

## After it merged

Report the merge commit hash, the title, and `source` → `target`. Repeat the strategy: merge commit.

When you only printed commands, stop after those commands. Do not invent a hash.

## Local main

When the working tree is clean, fast-forward local `main`:

```text
git checkout main && git pull --ff-only
```

Clean means `git status --porcelain` is empty, ignoring `agent-tools/`. If anything else is dirty, skip the checkout and say so. The merge on the host still stands.

When the pull request target is not `main`, use that target branch name in the same two commands. If the local branch does not exist, say so. Do not create it. If the pull is not a fast-forward, show the error. Do not `reset`, rebase, or force.

## Branches

Do not delete the remote branch or the local branch unless they asked in this turn. No `--delete-branch`. No `deleteSourceBranch`. If they asked, delete only the source branch they named: `git branch -d <branch>` and, when they asked for the remote, `git push <remote> --delete <branch>`. Do not use `git branch -D` unless they asked to force.

## Tracker

Tracker-neutral. Do not change work-item links.

Do not read or write `work-item.md`. Do not pass `--work-items` or `--transition-work-items`. Do not call `az repos pr work-item`. Do not set `transitionWorkItems`. Do not edit the pull request title or description.

## Hard rules

- No merge unless this turn names the pull request and asks to merge it.
- No squash (`--squash`, squash merge, `mergeStrategy` `squash`).
- No rebase (`--rebase`, rebase and fast-forward, semi-linear / `rebaseMerge`).
- No `--admin`, no `--bypass-policy`, no `bypassPolicy`.
- No second strategy attempt after a refusal.
- No `git commit`, no stash, no new branch, no force-push.
- No branch delete unless they asked in this turn.
- No dialog-box or browser Microsoft sign-in (`az login`, device code, or a web login).
- No token handling. Their existing git credential or `az login` is what the host call uses.
- Do not claim a merge commit hash the host did not return.
- Do not run this skill from `/crav1-open-pr`, `crav1-complete-task-agent`, or a review.
