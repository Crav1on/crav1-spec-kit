---
name: crav1-open-pr
description: >-
  Open a pull request for the current change branch (push with explicit yes).
  GitHub uses gh; Azure DevOps uses az when the CLI is available. Use after
  commits exist on feat/<slug> or spec/<slug>, or when the user asks for a PR.
  Cross-cutting. Does not merge; that is /crav1-merge-pr on a later
  explicit ask. May name /crav1-review-pr as an optional next step
  and does not run it. Do not commit. When that slug has work-item.md, add a
  Work item section to the body.
disable-model-invocation: true
icon: git-pull-request
color: green
---

# Open a pull request

Push the change branch **only after an explicit yes**, open **one** pull request against the head's into branch (see **Base branch**; usually the default branch), then stop. Do not merge in this skill. Merging is `/crav1-merge-pr`, a separate step, and only when they explicitly ask in that turn to merge a named pull request. Do not commit.

Create with GitHub `gh` when that host's checks pass. On Azure DevOps, create with `az repos pr` when the Azure CLI can run it. Otherwise print filled commands and GitKraken GUI paste fields. Do not claim a pull request was opened unless the host returned a URL.

Command: `/crav1-open-pr`.

Other skills may **name** this command as an optional next step. Do not run it from those steps. Run it only when the user invoked `/crav1-open-pr` or clearly asked to open a pull request in this chat. `crav1-build-task-agent` does not push and does not open a pull request.

## Inputs

Resolve these before you push or create anything. Prompt when a value is missing or ambiguous. Show the resolved values with the title and body draft.

| Input | Default |
| --- | --- |
| Base | The head's into branch, then the repo's `Merges into` branch, then the repo default branch. See **Base branch**. Confirm when ambiguous. |
| Head | Current branch when it is not the base. Otherwise ask. Do not check out a different branch in this skill. |
| Title | `<slug>: <short summary>` when the head is `feat/<slug>` or `spec/<slug>`. Summary is the `spec.md` H1 when `docs/specs/<slug>/spec.md` exists; otherwise the latest commit subject on the head. No slug: latest commit subject. |
| Body | Template below. |
| Push | Ask once, **after** the title and body are visible. Options in order: **push and open PR** (first/top), **open PR only** (remote already has the branch), **stop**. |

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`. `az` may be `az.cmd`. When PowerShell calls `az.cmd`, `cmd.exe` cuts a multi-line argument at the first newline, and an unquoted `--query` value that contains parentheses is a syntax error. Quote every `--query` value (`--query "value[].pullRequestId"`). A multi-line pull-request description uses the `@file` steps in **Create**.

## Base branch

**Into and Merges into (1.64.0).** Before the default-branch steps below, as `crav1-add-to-spec` `references/branches.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says:

1. **Into.** When the head is listed in a spec's Match `Branch:` list with an `(into <branch>)` marker, that branch is the base. When the head has no marker and its fork point (as `crav1-add-to-spec` `references/branches.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says) is another spec branch, ask once before the draft (1.68.0): "<head> split off <parent>. Does it merge into <parent>?" A yes writes `(into <parent>)` on the head's entry, and `(spec branch)` on the parent's entry when it has none, in the spec repo (not committed), and the base is <parent>. A no writes nothing and goes on to step 2. A headless run doesn't ask and writes nothing. A sub-branch's PR goes into its spec branch; the spec branch's PR goes into the Merges into branch.
2. **Merges into.** Else, when `docs/system/repos.md` has a `Merges into` cell for this repo, that branch is the base. When the open repo has no `docs/system/repos.md` row for itself (the specs live in another repo), look read-only in the sibling checkouts (`../*/docs/system/repos.md`) for one row naming this repo, and use its cell. Several rows that disagree: ask.
3. Else the default branch, from the steps below.

Name where the base came from in the draft (`Base: develop (Merges into in ../orders-specs/docs/system/repos.md)`).

Default branch:

1. `git symbolic-ref refs/remotes/<remote>/HEAD` (for example `origin/main` → `main`) when that ref exists.
2. Else, when `gh auth status` succeeds and the remote is GitHub, `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.
3. Else the local branch `main`, else `master`, else `develop`, when exactly one of those exists.
4. If more than one candidate remains, or none does, **ask**. Do not guess.

Remote: the single `git remote`. If several remotes exist, ask which one. If none exist, draft the title and body if you can, then stop. Say no remote is configured. Do not claim a push or a pull request.

## Checks (before the draft)

Run these first. Abort in one short message. Do not commit, stash, or check out.

| Condition | Stop |
| --- | --- |
| Not a git repo | Say so. |
| Detached HEAD (`git branch --show-current` empty) and they did not name an existing local head | There is no branch to open from. |
| Dirty tree | `git status --porcelain`, ignoring `agent-tools/`. Point them at `/crav1-finalize-commit`. This skill does not commit. |
| Head has no commits ahead of base | `git rev-list --count <base-ref>..<head>` is 0. Name the refs. Nothing to open. |
| Head branch does not exist locally | Ask for a local branch name. Do not create one. |

Compare against `refs/remotes/<remote>/<base>` when that ref exists, otherwise the local `<base>` branch. If neither ref exists, ask them to name the base. Do not treat a missing ref as “zero commits ahead.”

`agent-tools/` left dirty is fine. Mention that those paths stay uncommitted.

If the current branch **is** the base, ask for the head. Do not open a pull request of the default branch into itself.

If base or head is still ambiguous, that turn is the question only. No title, no body, no push menu.

## Draft title and body

Read `references/draft.md` ("Draft title and body") only when you draft the title and body.

## Host

Resolve **one** create path, in this order: GitHub `gh`, then Azure DevOps `az`, then printed commands and GitKraken GUI paste. Do not claim a pull request was opened unless that path returned a URL.

### GitHub (`gh`)

Use `gh` only when **both** are true: `gh auth status` succeeds, and the remote URL is GitHub (`github.com`, or `gh repo view` succeeds for that repo).

**Create** then uses the GitHub steps. If the remote is GitHub and `gh auth status` does not succeed, print the GitHub-shaped fallback below. Do not use `az`.

### Azure DevOps (`az`)

Read `references/azure-devops.md` ("Azure DevOps (`az`)") only when the remote is Azure DevOps.

### Other remotes

When the remote is neither GitHub nor Azure DevOps, print the GitHub-shaped fallback below. Do not claim a pull request was opened.

### Fallback (no URL)

Read `references/fallback.md` ("Fallback (no URL)") only when no host CLI can open the pull request.

## Push and open

Only after they pick `push` on the current draft.

1. `git push -u <remote> <head>`. Never `--force`, `--force-with-lease`, `--force-if-includes`, or a refspec that starts with `+`.
2. If the push fails, show the error. Do not open a pull request. Do not force-push. When it was rejected because the remote branch has commits this one lacks, say: `Pull <head> with git pull --no-rebase, resolve any conflicts, then push again.` Never suggest a rebase or a force-push (1.66.0).
3. Open one pull request (below). If one already exists for this head → base, print that URL instead.

## Open only

Only after they pick `open` on the current draft.

1. `git ls-remote --heads <remote> <head>`. If it is missing, say the remote has no such branch. Do not create a pull request. They can pick **push and open PR**.
2. If the local head has commits that are not on that remote head, say so and **do not push**. The pull request would miss them. They can pick **push and open PR**, or stop.
3. Open one pull request (below). If one already exists for this head → base, print that URL instead.

## Create

### GitHub

When **Host** says to use `gh`:

```text
gh pr list --head <head> --base <base> --state open --json number,url
```

If the list is non-empty, print the URL. Do not run `gh pr create`.

Otherwise:

```text
gh pr create --base <base> --head <head> --title <title> --body <body>
```

Pass the body with a HEREDOC or `--body-file` so quotes survive. Do not pass `--draft`, `--reviewer`, `--label`, `--assignee`, or `--milestone` unless they asked for that in this chat.

If create fails because a pull request already exists, print that URL. Do not open a second.

On success, follow **After it exists**.

### Azure DevOps

Read `references/azure-devops.md` ("Azure DevOps (Create)") only when the remote is Azure DevOps.

### No host create

Read `references/fallback.md` ("No host create") only when no host CLI can open the pull request.

## After it exists

Read `references/after.md` ("After it exists") only when the pull request exists.

## Hard rules

- No `git commit`, no `git commit --amend`, no stash, no `git checkout`, no new branch.
- No force-push. No advice to rebase or force-push; a rejected push is fixed by pulling with a merge.
- No merge (`gh pr merge`, completing an Azure DevOps pull request, or a local merge). Merging is `/crav1-merge-pr` on a later explicit ask for a named pull request. Do not run it from this skill. Do not run `/crav1-review-pr`. A review is not a merge ask.
- No second pull request for the same head → base.
- No repository setting changes.
- No `gk ai pr create` and no other interactive `gk` pull-request create. GitKraken stays GUI paste only.
- No dialog-box or browser Microsoft sign-in (`az login`, device code, or a web login).
- No `--work-items` and no `--transition-work-items` unless they asked for that in this chat. A **Work item** section in the body is not that flag.
- Do not block the pull request when `work-item.md` is missing. Do not create a work item and do not look one up.
- Do not claim a pull request was opened unless the host returned a URL.
- Workers stay no push and no pull request. Do not run this skill from `crav1-build-task-agent`.
