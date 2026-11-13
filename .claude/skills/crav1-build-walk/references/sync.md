# Specs-repo sync (1.151.0)

Read this at the start of `/crav1-build-walk`, and again when a walk branch finishes or the user stops.

## Pull before reading

Before reading or writing the spec folder, run `<interpreter> -X utf8 scripts/repo_sync.py status --repo <specs-repo>`, as `crav1-docs/reference/running-scripts.md` says. That fetch is read-only.

- Behind origin: stop. Print the script's `ending`. Run next is `git pull --no-rebase` (merge, never rebase). Do not read or write yet.
- Diverged: stop. The same Run next applies. Merge origin in, never rebase.
- Ahead: continue. Print the Waiting line to push.
- No upstream, or the fetch failed (offline): say so once and continue from the local copy.
- No git repository: continue. Say nothing.
- In step: continue.

## Settle and push at the end

When the walk finishes, or the user says `stop`, list every uncommitted file in the specs repo that this walk or its step skills wrote: the progress file, `claims.md`, `verify.md`, `tasks.md` ticks, `build-map.md`, and notes such as `docs/notes/<month>/…` and their indexes. `<interpreter> -X utf8 scripts/repo_sync.py settle --repo <specs-repo> --written <path> <path>` lists them. Files this walk did not write are listed and left uncommitted.

On `yes` (Recommended), commit the walk's files with the persisted commit style, the draft-commit rule already in the repo. Then one card to push the specs repo, naming how many commits it is ahead. `stop` does not push. A headless run stops and names `yes` and `stop`.

If the branch is behind origin, fetch and merge origin in first. Never rebase. On a conflict, stop and name the files. Nothing is pushed.

After a successful push, the ending says the specs repo is in step with origin. An unpushed repo is a Waiting line, never a buried note.

`Run next:` stays first, in the 1.150.0 shape, with the full command alone in a code span.
