# Repos

Named repos this system may use. Specifying does **not** create remotes. Status stays `proposed` until a URL exists.

| Repo | Purpose | Status | URL | Merges into | Work items go to |
| --- | --- | --- | --- | --- | --- |
| | | proposed | | | |

`## Synced at` below holds one line per repo and branch, `- <repo> <branch>@<short sha>, <date>`, sorted by repo, then branch (1.84.0). A new read replaces only that repo and branch's line. A consumer measuring drift uses, for each repo and branch, the older of this line and the slice line; no line means unknown, so fall back to spec file commit dates.

`Merges into` is the branch this repo's work merges into, for example `develop`. Empty means the default branch (`origin/HEAD`, else `main` or `master`). Fork point, done and the open-pr base use it. `/crav1-add-to-spec` code change offers to fill it after one yes; edit the cell to change it.

`Work items go to` is the repo's work item home, `ADO: <org>/<project>` (`Jira: <project>` later). Empty until the user answers the first Azure Boards skill that needs it. Never set for the repo that holds the specs. Edit the cell to change it.

## Synced at

## Boundaries

What must not cross a repo boundary.
