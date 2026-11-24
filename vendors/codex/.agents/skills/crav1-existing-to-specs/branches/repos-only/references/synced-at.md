# Repos to spec: **Synced at**

Part of `branches/repos-only/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Synced at

This command reads each named repo as a whole. Record the commit actually read. `Synced at` is one line per repo and branch, `- <repo> <branch>@<short sha>, <date>`, in the `## Synced at` section of `repos.md`, for example `- orders-api main@abc1234, 2026-10-07` (1.84.0, `crav1-add-to-spec` `references/merge-safe.md`). The branch is the branch that was read. The short sha is seven characters. The date is the date of that read, `YYYY-MM-DD`.

Set that repo's `Synced at` line in `repos.md` to the branch and commit actually read. When that repo and branch already have a line, replace only that line; a new one goes in sorted place (repo, then branch). Leave every other line. Touch only the repos this run read. Do not change Purpose, Status, URL, or Boundaries. When the `## Synced at` section is missing and `repos.md` exists, add it after the table. A checkout with no commit stays empty. Do not write a slice `Synced at` line. This command does not write `docs/specs/<slug>/spec.md`.

On the missing-architecture pass, update that cell only when `repos.md` already exists. Do not create the file on that pass.

Do not stamp a repo this run did not read. A repo or branch with no line keeps no line. A consumer measuring drift uses, for each repo and branch, the older of the repo line and the slice line, and no line means unknown, so fall back to spec file commit dates.
