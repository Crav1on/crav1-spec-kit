# Repos

Named repos this system may use. Specifying does **not** create remotes. Status stays `proposed` until a URL exists.

| Repo | Purpose | Status | URL | Synced at | Merges into | Work items go to |
| --- | --- | --- | --- | --- | --- | --- |
| | | proposed | | | | |

`Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. A consumer measuring drift uses the older of the repo column and the slice line, for each branch its own entry, and an empty value means unknown, so fall back to spec file commit dates.

`Merges into` is the branch this repo's work merges into, for example `develop`. Empty means the default branch (`origin/HEAD`, else `main` or `master`). Fork point, done and the open-pr base use it. `/crav1-add-to-spec` code change offers to fill it after one yes; edit the cell to change it.

`Work items go to` is the repo's work item home, `ADO: <org>/<project>` (`Jira: <project>` later). Empty until the user answers the first Azure Boards skill that needs it. Never set for the repo that holds the specs. Edit the cell to change it.

## Boundaries

What must not cross a repo boundary.
