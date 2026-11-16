# Claims and a fresh copy (1.151.0)

Read this at the start of `/crav1-tasks-ready-to-build`.

Before reading a slice, run `<interpreter> -X utf8 scripts/repo_sync.py status --repo <specs-repo>`, as `crav1-docs/reference/running-scripts.md` says. That fetch is read-only.

- Behind or diverged: stop. Run next is `git pull --no-rebase`. Never rebase.
- No upstream, or the fetch failed (offline): say so once and continue.
- Ahead: continue, and print the Waiting line to push.
- In step, or no git repository: continue.

Then also read `docs/specs/<slug>/claims.md` when it exists. A task with an `In progress:` line is held `in progress by <user> since <date>` and is not offered in Run next. When its `build-progress` file shows it built and the branch is not merged, it reads `built by <user>, waits for PR <n> to merge` instead (1.175.0). `Continue the build walk on <branch>:` is offered only when the walk's claim user matches `git config user.name`; someone else's walk is a Waiting line. A claim older than three days, or the file's `Claim max age:` line, gets a warning and is never cleared on its own. Never read Azure Boards.
