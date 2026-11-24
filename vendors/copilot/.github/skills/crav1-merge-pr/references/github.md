# GitHub (What must pass)

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.95.1; the rules are unchanged.

Stop unless all of these are true after the ready step:

| Check | Pass | Stop and report |
| --- | --- | --- |
| `mergeStateStatus` | `CLEAN` | `BLOCKED`, `DIRTY`, `DRAFT`, `BEHIND`, `UNSTABLE`, `UNKNOWN`, or anything else |
| `reviewDecision` | `APPROVED`, or empty when `mergeStateStatus` is `CLEAN` | `REVIEW_REQUIRED`, `CHANGES_REQUESTED` |
| `gh pr checks` | every required check passed; exit 0 | failing or pending lines |

`BEHIND` means the head is behind the base. `DIRTY` means the branch has conflicts with the base. Report that. Do not update the branch in this skill. Say how to fix it by merging the base in, never a rebase (1.66.0): `Merge <base> into <head> (resolve any conflicts there), push, then ask to merge again.` When they want the steps: `git switch <base>`, `git pull --ff-only`, `git switch <head>`, `git merge <base>`, `git push`. If that merge leaves `walk-progress.md` conflicted only on version lines, run `resolve-stamps` as `/crav1-finalize-commit` `references/pull.md` says (1.139.0). On GitHub, **Update branch** with **Update with merge commit** does the same for a branch that is only behind.

`UNSTABLE` is not a pass. Report the check names. Do not merge.

# GitHub (Host)

Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

Use `gh` only when **both** are true: `gh auth status` succeeds, and the pull request is on GitHub (`github.com` in the URL or the remote, or `gh repo view` succeeds for that repo).

**Merge** then uses the GitHub steps. If the pull request is on GitHub and `gh auth status` does not succeed, print the GitHub fallback below. Do not use `az`.

When the pull request is neither GitHub nor Azure DevOps, print the GitHub-shaped fallback below. Do not claim it was merged.

# GitHub (Read it first)

Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

```text
gh pr view <n-or-url> --json number,url,title,body,author,createdAt,state,isDraft,baseRefName,headRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
gh pr checks <n-or-url>
```

`state` must be `OPEN`.
