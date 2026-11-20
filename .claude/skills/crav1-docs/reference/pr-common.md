# Shared pull-request steps

`/crav1-open-pr`, `/crav1-merge-pr`, `/crav1-pr-status` and `/crav1-review-pr` share these steps (1.158.0). Each skill's `SKILL.md` points here and keeps only its own judgement: what open-pr drafts, when merge-pr merges, how pr-status sorts points, and what review-pr checks. When this page and a skill's own rule differ, the skill's rule wins for that skill.

The shared script is `scripts/pr_common.py`. Each of the four skills ships a copy (the full script lives in skill `crav1-open-pr`; the other three run it from there). It is read-only: it never pushes, posts, merges, completes, votes, signs in, or prints a token, and it never writes `claims.md`. Pick the interpreter as `running-scripts.md` says. Every subcommand prints one JSON object with a `line` to quote.

## Command family

The four are one command family and none runs another. `/crav1-open-pr` may name `/crav1-review-pr` or `/crav1-merge-pr` as a later step; it does not run them. `/crav1-merge-pr` does not run `/crav1-review-pr`, and a review is not a merge ask. `/crav1-review-pr` and `/crav1-pr-status` do not run `/crav1-merge-pr`. `crav1-build-task-agent` does not push and does not open a pull request. A skill names the next command; it runs it only where its own `SKILL.md` says so.

## Which pull request

Accept a number (`123`, `pr82`, `PR 82`, `#82`) or a URL.

| URL | Id |
| --- | --- |
| `https://github.com/<owner>/<repo>/pull/<n>` | `<n>` |
| `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |
| `https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |

`<interpreter> -X utf8 scripts/pr_common.py parse --ref <n-or-url> --remote-url <remote-url>` reads it. A branch name is not a pull request. Do not pick the newest pull request for the current branch. When the URL's repository is not this git remote, the script says `mismatch`: stop and name both. Compare without a trailing `.git`, ignore case, and treat `dev.azure.com/<org>` and `<org>.visualstudio.com` as the same. `/crav1-review-pr` and `/crav1-pr-status` also accept `<repo> <n>` and a workspace folder or `repos.md` row, as skill `crav1-review-pr` `references/which-pr.md` says.

**A bare number (1.177.0).** Resolve it from the kit's own records before the remote: `<interpreter> -X utf8 scripts/pr_common.py resolve --ref <ref> --root <specs-repo>`. It reads the build-progress files (`docs/specs/<slug>/build-progress/`), the merge list (`build-map.md`, `walk-progress.md`), the PR notes in `docs/notes/` and `docs/system/repos.md`, and is read-only.

- The records name exactly one pull request with that number: use its URL and host (`status: ok`, `source: records`). That holds even when this checkout's remote is on another host, for example a GitHub specs checkout and an Azure DevOps code repo.
- The records name several, or one record and this checkout's host already showed a pull request with that number (`--remote-has-pr`): `status: ask`. List every candidate with its URL and ask which one. Do not pick.
- Only when the records name none does it fall back to this checkout's single `git remote` (`source: remote`). No record and no GitHub or Azure DevOps remote: ask for the pull request URL.
- No record, and this checkout holds no code (1.197.0): its `docs/system/repos.md` row says so (purpose such as `specs` or `no code`), or the remote is not a listed repo while other rows are. Then the script checks each code repo's host read-only (`gh` or `az`, with the short timeouts) and uses the one that has that pull request (`source: host-check`). None or several: `status: ask`, with the code repos as candidates. Never tell the user to install or sign in to a CLI until the host is known. `--no-host-check` skips the host checks.

Since 1.177.1 `--root` may be the specs repo root, `docs/specs`, or one spec folder; the script reads the whole specs repo either way. Pass the specs repo root. A record that names `PR 82` without a URL takes its host from a `Code repo:` line in the build-progress file (a URL or a `repos.md` name), else from the only row of `docs/system/repos.md`. When the host cannot be worked out, the answer is `status: ask` with that record as the candidate, for example `PR 82 is in build-progress for feat/orders-cicd, but its host isn't recorded.` It never falls back to the remote then, and `tool` is empty: ask for the pull request URL and name no CLI to install until the host is known.

**Who opened it (1.177.1).** The ready check asks the pull request's own host, read-only and with a short timeout: `gh pr view <n> --json author` on GitHub, `az repos pr show --id <n>` (`createdBy.displayName`) on Azure DevOps, only the CLI for the host the records name, when no author is recorded. `pr_common.py` stays read-only: the ready check writes a found name as `PR author: <name>` in the build-progress file that names that pull request, and `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py pr-author --root <spec-folder> --pr <n> --name "<who>"` records the user's answer.

**Did it merge (1.177.2).** `host_state` asks the same way whether a pull request merged: `gh pr view <n> --json state,mergeCommit,mergedAt,closedAt` on GitHub (`MERGED`, `CLOSED`, `OPEN`), `az repos pr show --id <n>` (`status`, `lastMergeCommit`, `closedDate`) on Azure DevOps (`completed`, `abandoned`, `active`). It returns the state, the merge commit when the host gives it, and the date, or nothing when the CLI is missing, not signed in, slow or fails. The ready check records a merge in build-progress itself; a `Code repo:` line written by `walk_progress.py code-repo --root <spec-folder> --pr <n> --repo <name-or-url>` gives a number-only record its host.

**One lookup (1.178.0).** `host_state` also asks for who opened the pull request (`author` on GitHub, `createdBy.displayName` on Azure DevOps) and returns it as `author` when the host names one, so the ready check reads the owner and the merge state in one call. `host_author` is then not called again for that pull request in the same run.

**A reason, not silence (1.179.0).** `host_lookup` makes that one call and returns `{ok, error, detail}`. It runs the CLI by the full path `shutil.which` found (`az.cmd` or `az.bat` on Windows), with stdin closed, UTF-8 output, `--detect false`, `AZURE_EXTENSION_USE_DYNAMIC_INSTALL=no`, and a 20-second timeout for `az` (8 seconds for `gh`, or `CRAV1_HOST_TIMEOUT`). When it cannot read the pull request, `error` is one of `cli-missing`, `cli-not-runnable`, `timeout`, `not-signed-in`, `extension-missing`, `not-found`, `bad-output`, `unknown-status` or `host-error`, and `detail` is the first line of what the CLI said. `host_state` and `host_author` stay as thin wrappers.

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL names its host.

## Finding the pull request for a branch

`<interpreter> -X utf8 scripts/pr_common.py find --branch <head> --base <base>` lists the open pull requests for one head branch: `gh pr list --head <head> --base <base> --state open` on GitHub, `az repos pr list --source-branch refs/heads/<head> --status active` on Azure DevOps. It never picks the newest. Exactly one match is `pick`; more than one is `pick: null` with every match listed, and the skill asks which one. Only `/crav1-open-pr` (an existing pull request for this head and base) and `/crav1-pr-status` (no pull request named, and the current branch has exactly one open pull request) use a branch this way. `/crav1-merge-pr` never merges a pull request it found from a branch.

## Host

Resolve **one** path, in this order: GitHub `gh`, then Azure DevOps `az`, then the skill's no-host step. `<interpreter> -X utf8 scripts/pr_common.py host --remote-url <remote-url>` says `github`, `azure`, or `other`. Use `gh` only when `gh auth status` succeeds and the pull request is on GitHub. Each skill's own Azure DevOps file holds its `az` calls. The host is the resolved pull request's host (`resolve` says `tool: gh` or `tool: az`), not this checkout's remote. Never tell the user to install or sign in to `gh` unless the resolved pull request is on GitHub, and never to set up `az` unless it is on Azure DevOps (1.177.0). When the remote is GitHub and the records point to Azure DevOps, take the `az` path. Never claim a host did something it did not return: a URL for open, the diff and body for a read, a merge commit hash for a merge.

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

Each of the four ends with Run next (1.177.0), as `run-ending.md` ("Run next for every other skill") says: `Run next:`, then a short reason, then a label on its own line and the command alone in its code span on the next line. Then `Waiting:` lines, then `Uncommitted:` when a note it wrote is not committed. Nothing needed now: `Run next: nothing needed now.` The four never print a `Next:` line. When `/crav1-build-walk` opened the skill, the skill prints no Run next of its own; the walk prints its Run next block (1.142.0, 1.157.0).

```text
Run next:
Thread 104 is waiting on you.

Post the drafted reply in thread 104:
`/crav1-pr-status pr42`
```
