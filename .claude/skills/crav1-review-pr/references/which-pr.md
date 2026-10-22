# crav1-review-pr: which pr

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Which pull request

Accept a number (`123`), a URL, or `<repo> <n>` (1.65.0), for example `orders-api 71`, where `<repo>` is a repo in `docs/system/repos.md` or a workspace folder.

| URL | Id |
| --- | --- |
| `https://github.com/<owner>/<repo>/pull/<n>` | `<n>` |
| `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |
| `https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<n>` | `<n>` |

A branch name is not a pull request; only the `branch` word starts a branch review (1.80.0). Do not pick the newest pull request for the current branch.

A URL or `<repo> <n>` is accepted when its repository is one of these (1.65.0):

1. this checkout's git remote
2. the git remote of another folder in this workspace
3. a row of `docs/system/repos.md` in the specs repo, matched on its `URL` cell: compare without a trailing `.git`, ignore case, and treat `dev.azure.com/<org>` and `<org>.visualstudio.com` as the same

Otherwise stop and name what you looked at: `PR repository <url> is not this remote, a workspace folder, or a repos.md row.` Do not review across that mismatch.

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL still names the host. A bare number needs that remote, or a `gh` repo that matches it.
