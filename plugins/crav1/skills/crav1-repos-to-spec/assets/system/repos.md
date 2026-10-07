# Repos

Named repos this system may use. Specifying does **not** create remotes. Status stays `proposed` until a URL exists.

| Repo | Purpose | Status | URL | Synced at |
| --- | --- | --- | --- | --- |
| | | proposed | | |

`Synced at` is `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. A consumer measuring drift uses the older of the repo column and the slice line, and an empty value means unknown, so fall back to spec file commit dates.

## Boundaries

What must not cross a repo boundary.
