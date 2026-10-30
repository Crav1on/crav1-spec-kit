# Repos vs specs: units

Part of `branches/recheck/BRANCH.md`, read at the large-repo count and the compare step. Paths in backticks are relative to the skill folder unless they start with `docs/`.

## What a unit is

One thing a spec would describe. Use the first that fits the code:

- An HTTP route or controller, a GraphQL resolver, or an RPC handler (one per route group).
- A background job, worker, scheduled task, or message consumer.
- A public module or package entry point other code calls.
- A UI feature folder, page, or screen.
- A CLI command.
- A feature flag or config switch that turns behavior on or off.
- A migration set that adds a table or a column a feature owns (one unit per feature, not per file).

A file that is only glue for one unit belongs to that unit.

## Skip

Not units; count them under skipped:

- Tests, fixtures, and snapshots.
- Generated code, vendored code, lock files, build output.
- Build, CI, and editor config.
- Docs, including `docs/`.

## Changed since last read

With `since`, take the files changed in the repo's history after its `Synced at` time (`git log --since` in that checkout, read only), and compare only the units those files belong to. A stale-claim check still covers every cited path in the scope, since a deletion is a change.
