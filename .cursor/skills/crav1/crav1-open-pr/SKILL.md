---
name: crav1-open-pr
description: >-
  Open a pull request for the current change branch (push with explicit yes).
  Use after commits exist on feat/<slug> or spec/<slug>, or when the user asks
  for a PR. Cross-cutting. Do not merge. Do not commit.
disable-model-invocation: true
icon: git-pull-request
color: green
---

# Open a pull request

Push the change branch **only after an explicit yes**, open **one** pull request against the default branch, then stop. Do not merge. Do not commit.

Command: `/crav1-open-pr`.

Other skills may **name** this command as an optional next step. Do not run it from those steps. Run it only when the user invoked `/crav1-open-pr` or clearly asked to open a pull request in this chat. `crav1-complete-task-agent` does not push and does not open a pull request.

## Inputs

Resolve these before you push or create anything. Prompt when a value is missing or ambiguous. Show the resolved values with the title and body draft.

| Input | Default |
| --- | --- |
| Base | Repo default branch. See **Base branch**. Confirm when ambiguous. |
| Head | Current branch when it is not the base. Otherwise ask. Do not check out a different branch in this skill. |
| Title | `<slug>: <short summary>` when the head is `feat/<slug>` or `spec/<slug>`. Summary is the `spec.md` H1 when `docs/specs/<slug>/spec.md` exists; otherwise the latest commit subject on the head. No slug: latest commit subject. |
| Body | Template below. |
| Push | Ask once, **after** the title and body are visible. Options in order: **push and open PR** (first/top), **open PR only** (remote already has the branch), **stop**. |

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`.

## Base branch

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

When base, head, and the checks are settled, write the draft into the user-visible reply **before** any choice UI.

**Title** (one line):

```text
<slug>: <short summary>
```

**Body:**

```markdown
## What / why

<Two to four sentences from spec.md or the commits on base..head. Do not invent scope.>

## Spec

- docs/specs/<slug>/

## Verify

<One line from verify.md when that file exists (pass, fail, or missing). Otherwise: No verify.md on this branch.>
```

Omit **Spec** when `docs/specs/<slug>/` is not on the head. Slug comes from `feat/<slug>` or `spec/<slug>`. If the head name has no slug and exactly one `docs/specs/<slug>/` folder changed vs base (not `_template/`), use that slug. If several changed, leave the slug out of the title and omit **Spec** rather than picking one.

Show base, head, remote, title, and body. Say they can edit any of those before you act.

**Then** offer the choices (questions tool when available). Put the actual title and body in the question prompt, for example:

```text
Base: <base>
Head: <head>
Title: <one line>

Body:
<the draft>

What next?
```

Options, **in this order**:

| Id | Choice | What it does |
| --- | --- | --- |
| `push` | Push and open PR | `git push -u <remote> <head>` (no force), then open one pull request. **Always list this first.** |
| `open` | Open PR only | Remote already has this head. Do not push. Open one pull request for that remote head. |
| `stop` | Stop | No push. No pull request. They can still copy the draft. |

Never call the questions tool before the title and body are in the reply. If they named `push` or `open` before any draft existed, ignore it, draft, show the text, then offer the choices.

If they edit the title, body, base, or head: apply only that edit, re-run the checks when base or head changed, show the new draft, **then** the same three choices (`push` still first). Do not push in the edit turn unless they pick `push` or `open` **after** seeing the new draft.

## Host

Use the GitHub CLI only when **both** are true: `gh auth status` succeeds, and the remote URL is GitHub (`github.com`, or `gh repo view` succeeds for that repo).

Otherwise do **not** claim a pull request was opened. After a successful `git push` (push path only), or instead of create (open-only path), print:

- base ← head
- the title and body they accepted
- the exact commands, with their title and body filled in:

```text
git push -u <remote> <head>
gh pr create --base <base> --head <head> --title "<title>" --body "<body>"
```

GitKraken: open a pull request from `<head>` into `<base>`. Paste the title and body. Do not merge.

On the open-only path, omit the `git push` line and say the remote branch must already exist.

## Push and open

Only after they pick `push` on the current draft.

1. `git push -u <remote> <head>`. Never `--force`, `--force-with-lease`, `--force-if-includes`, or a refspec that starts with `+`.
2. If the push fails, show the error. Do not open a pull request. Do not force-push.
3. Open one pull request (below). If one already exists for this head → base, print that URL instead.

## Open only

Only after they pick `open` on the current draft.

1. `git ls-remote --heads <remote> <head>`. If it is missing, say the remote has no such branch. Do not create a pull request. They can pick **push and open PR**.
2. If the local head has commits that are not on that remote head, say so and **do not push**. The pull request would miss them. They can pick **push and open PR**, or stop.
3. Open one pull request (below). If one already exists for this head → base, print that URL instead.

## Create

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

When **Host** says not to use `gh`, print the commands and GitKraken fields from that section. Do not claim a pull request was opened. Tell them that if one already exists for this head → base, they should use that URL and not open a second.

## After it exists

When the host returned a pull request URL, print that URL and `base` ← `head`.

One sentence: they can review and merge when they want. This skill does not merge, and it does not delete the branch.

When you only printed commands, stop after those commands. Do not invent a URL.

## Hard rules

- No `git commit`, no `git commit --amend`, no stash, no `git checkout`, no new branch.
- No force-push.
- No merge (`gh pr merge` or a local merge).
- No second pull request for the same head → base.
- No repository setting changes.
- Do not claim a pull request was opened unless the host returned a URL.
- Workers stay no push and no pull request. Do not run this skill from `crav1-complete-task-agent`.
