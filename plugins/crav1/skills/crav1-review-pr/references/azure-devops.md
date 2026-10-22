# crav1-review-pr: azure devops

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

### Azure DevOps (`az`)

Treat the remote, the pull request URL, or the `repos.md` URL as Azure DevOps when it matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read org, project, and repository from that URL the same way `/crav1-merge-pr` does.

Use `az repos pr` only when `az` is on `PATH` (on Windows, `az.cmd` counts), the azure-devops extension can run, and the CLI is already authenticated for a non-interactive call. Do not run `az login`, a device-code flow, or a web login. Do not create a token. Do not print a token.

Pass `--org` and `--id`, and pass `--detect false`. Do not pass `--project` or `--repository` on show or policy list.

If `az` is missing, the extension cannot run, or the CLI is not already authenticated, stop. Do not invent a review.

### Diff from a sibling checkout (Azure DevOps)

When the pull request is in another repo, read the diff in that repo's checkout (a workspace folder, else `../<repo>`). When there is none, ask for the path with options only (the sibling folders that are git checkouts, plus Other). A headless run stops: `No checkout found for <repo>. Name its path.`

First compare the copies on disk (`<remote>/<source>` and `<remote>/<target>`, else the local branches) with the pull request's `lastMergeSourceCommit.commitId` and `lastMergeTargetCommit.commitId`. A copy matches when it points at that commit or already contains it.

- **Both match.** No question. `git diff <target>...<source>` on the copies on disk.
- **A copy is missing or older.** Ask one question, options only:
  1. **Fetch only the PR's two branches (Recommended).** `git fetch <remote> <source> <target>` in that checkout, then the diff. This moves remote-tracking refs only. Never check out, merge, commit, or push there. It is the one exception to the no-fetch rule for a sibling checkout in `references/branches.md`.
  2. **Use what's on disk.** Diff the copies on disk. Say each copy's newest commit date and age, and `the copy on disk is older than the PR; newer commits may be missed`.
  3. **Stop.** Say `Fetch <source> and <target> in <path> and rerun.` and stop.

### Azure DevOps (Read it first)

```text
az repos pr show --org <org-url> --id <n> --detect false --output json
az repos pr policy list --org <org-url> --id <n> --detect false --output json
```

`status` must be `active`.

Read the diff without checking out a branch. When the pull request is in this checkout, fetch if the commits are not local, then diff the target and the source. Do not `git checkout`. Do not commit. Do not push.

```text
git fetch <remote> <source> <target>
git diff <target>...<source>
```

Strip a `refs/heads/` prefix when you name the branches. `<source>` is `sourceRefName`. `<target>` is `targetRefName`.

## Branches on disk: choice words

Moved word for word from `SKILL.md` in 1.80.2.

When the invocation contains one of these words (for example `/crav1-review-pr orders-api 71 use disk`), take that choice when the question comes up and do not ask. When the question comes up in a headless run or a bot run with no word, stop: `PR branches on disk are missing or older than the PR. Use one of: fetch pr branches, use disk, stop pr review.` A word that is not needed (the copies match) is ignored.
