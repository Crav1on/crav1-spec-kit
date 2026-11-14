# Shared pull-request steps

`/crav1-open-pr`, `/crav1-merge-pr`, `/crav1-pr-status` and `/crav1-review-pr` share these steps (1.158.0). Each skill's `SKILL.md` points here and keeps only its own judgement: what open-pr drafts, when merge-pr merges, how pr-status sorts points, and what review-pr checks. When this page and a skill's own rule differ, the skill's rule wins for that skill.

The shared script is `scripts/pr_common.py`. Each of the four skills ships a copy (the full script lives in skill `crav1-open-pr`; the other three run it from there). It is read-only: it never pushes, posts, merges, completes, votes, signs in, or prints a token, and it never writes `claims.md`. Pick the interpreter as `running-scripts.md` says. Every subcommand prints one JSON object with a `line` to quote.

## Command family

The four are one command family and none runs another. `/crav1-open-pr` may name `/crav1-review-pr` or `/crav1-merge-pr` as a later step; it does not run them. `/crav1-merge-pr` does not run `/crav1-review-pr`, and a review is not a merge ask. `/crav1-review-pr` and `/crav1-pr-status` do not run `/crav1-merge-pr`. `crav1-build-task-agent` does not push and does not open a pull request. A skill names the next command; it runs it only where its own `SKILL.md` says so.

## Which pull request

Accept a number (`123`) or a URL.

| URL | Id |
| --- | --- |
| `https://github.com/<owner>/<repo>/pull/<n>` | `<n>` |
| `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |
| `https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |

`<interpreter> -X utf8 scripts/pr_common.py parse --ref <n-or-url> --remote-url <remote-url>` reads it. A branch name is not a pull request. Do not pick the newest pull request for the current branch. When the URL's repository is not this git remote, the script says `mismatch`: stop and name both. Compare without a trailing `.git`, ignore case, and treat `dev.azure.com/<org>` and `<org>.visualstudio.com` as the same. `/crav1-review-pr` and `/crav1-pr-status` also accept `<repo> <n>` and a workspace folder or `repos.md` row, as skill `crav1-review-pr` `references/which-pr.md` says.

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL still names the host. A bare number needs that remote, or a `gh` repo that matches it.

## Finding the pull request for a branch

`<interpreter> -X utf8 scripts/pr_common.py find --branch <head> --base <base>` lists the open pull requests for one head branch: `gh pr list --head <head> --base <base> --state open` on GitHub, `az repos pr list --source-branch refs/heads/<head> --status active` on Azure DevOps. It never picks the newest. Exactly one match is `pick`; more than one is `pick: null` with every match listed, and the skill asks which one. Only `/crav1-open-pr` (an existing pull request for this head and base) and `/crav1-pr-status` (no pull request named, and the current branch has exactly one open pull request) use a branch this way. `/crav1-merge-pr` never merges a pull request it found from a branch.

## Host

Resolve **one** path, in this order: GitHub `gh`, then Azure DevOps `az`, then the skill's no-host step. `<interpreter> -X utf8 scripts/pr_common.py host --remote-url <remote-url>` says `github`, `azure`, or `other`. Use `gh` only when `gh auth status` succeeds and the pull request is on GitHub. Each skill's own Azure DevOps file holds its `az` calls. Never claim a host did something it did not return: a URL for open, the diff and body for a read, a merge commit hash for a merge.

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`. `az` may be `az.cmd`. Quote any `--query` value that contains parentheses; `cmd.exe` treats an unquoted `(` as syntax. A multi-line pull-request description uses the `@file` steps in `/crav1-open-pr`. `/crav1-merge-pr` does not pass a multi-line body to `az`; a multi-line `--description` on Windows uses those `@file` steps.

## State and checks

A pull request that a skill reads, reviews or merges must be **open** (`OPEN` on GitHub, `active` on Azure DevOps; a draft counts as open). Anything else: stop and say the state. Do not reopen it.

`<interpreter> -X utf8 scripts/pr_common.py checks --ref <n-or-url>` sums up the state, the draft flag, and the checks, policies and reviews as passing, failing and pending, and lists what blocks a merge under `blocked`. It is a summary for the chat. `/crav1-merge-pr` still reads the host itself before it merges, as its `SKILL.md` says, and stops on any required check, policy or review that is not passing. Never bypass a check: no `--admin`, no `--bypass-policy`, no `bypassPolicy: true`.

## Claims

A build walk's claim is an `In progress:` line in `docs/specs/<slug>/claims.md` (1.151.0, 1.155.0). `<interpreter> -X utf8 scripts/pr_common.py claim --root <spec-folder> --branch <branch>` reads the lines for one branch. The PR skills only read claims. They never write, clear, commit or push `claims.md`. A claim stays until the merge; after the merge, `/crav1-build-walk` clears its own claim, as skill `crav1-build-walk` `references/claims.md` says. A standalone `/crav1-merge-pr` leaves `claims.md` as it is.

## Behind the base, and catching up

`<interpreter> -X utf8 scripts/pr_common.py behind --head <head> --base <base>` counts the commits the head is behind and ahead of the base. A branch that is behind, or has conflicts, catches up by merging the base into it: `git merge <base>` on the head, or `git pull --no-rebase`, resolve any conflicts, then push. Never suggest a rebase, `pull --rebase`, or a force-push. A rejected push is fixed by pulling with a merge.

## Signing in and secrets

Never start a dialog-box or browser Microsoft sign-in (`az login`, `az devops login`, device code, or a web login). Never print, echo, store, or create a token. An `AZURE_DEVOPS_EXT_PAT` the user already set may be used, as skill `crav1-merge-pr` `references/fallback.md` ("Auth notes") says. Redact secrets and personal data in anything shown or saved.

## Run ending

Each of the four ends as `run-ending.md` says (1.122.0): one `Next:` line, then `Waiting:` lines, then `Uncommitted:` when a note it wrote is not committed. When `/crav1-build-walk` opened the skill, the skill prints no line of its own for what to run next; the walk prints its Run next block (1.142.0, 1.157.0).
