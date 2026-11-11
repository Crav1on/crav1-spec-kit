# Migrations

Read this only after kit files are replaced, and only when the plan's `migration_ids` is not empty. The registry is `migrations.json` next to this skill. A step is included when the installed version is below `below` and the target is at least `at_least`.

Run `migrations` with no `--apply`. That is the dry run. Show each id, its summary, and the dry-run output. A step whose output mentions `walk-progress.md` is blocked and is not applied.

Question: Apply these migration steps?

- `apply (Recommended)`. Writes what the dry run showed.
- `leave`. Leaves project files as they are. The kit update still stands.
- `stop`. Does not apply the migration.

The card's free-text answer is not used for a second list. `leave` is a real option.

On `apply`, run `migrations --apply --yes`. On `leave` or `stop`, do not. The kit commit does not stage migration edits. They stay unstaged so a spec that was already dirty on a walk is not swept into the kit commit. The run ending's `Uncommitted` line names them when they changed.
