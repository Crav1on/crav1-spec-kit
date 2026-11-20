# crav1-review-pr: which pr

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Which pull request

Accept a number (`123`, `pr82`, `PR 82`), a URL, or `<repo> <n>` (1.65.0), for example `orders-api 71`, where `<repo>` is a repo in `docs/system/repos.md` or a workspace folder.

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

Remote: the single `git remote`. If several remotes exist, ask which one. A full URL names its host.

A bare number is resolved from the kit's records first (1.177.0): `<interpreter> -X utf8 scripts/pr_common.py resolve --ref <ref> --root <specs-repo>`, as `crav1-docs/reference/pr-common.md` ("A bare number") says. One record match is the pull request, on its own host, even when this checkout's remote is another host. `ask` lists every candidate and asks which one. Only with no record does the number mean this checkout's remote. `--root` is the specs repo root (1.177.1); a record that names the number without its host is `ask` with that record as the candidate, never the remote. Use the `tool` it names: never tell the user to install or sign in to `gh` for an Azure DevOps pull request, or to set up `az` for a GitHub one. When this checkout holds no code, the script checks the code repos in `repos.md` read-only first and asks only when none or several have that number (1.197.0).

**No host yet (1.197.0).** When the run ends because the pull request or its host is not known (`ask` with no answer, or `needs-remote`), end with the Run next layout, never a CLI install hint:

Run next:

Review the pull request by its URL:
`/crav1-review-pr <pull request URL>`

## Other skills

Moved word for word from `SKILL.md` in 1.80.2.

`/crav1-open-pr` may name this command as an optional next step. It must not run it. `/crav1-merge-pr` must not run it. A review is not a merge ask. Spark, specify, and verify do not run this command. Do not run it from those skills. Do not run it from plan.
