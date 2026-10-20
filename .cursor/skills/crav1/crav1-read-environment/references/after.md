# crav1-read-environment: after

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-plan-from-spec`, `/crav1-build-tasks`, `/crav1-create-feature-branch`, `/crav1-finalize-commit`, or `/crav1-map-pipeline-environments`.

Output only:

- Host, or that the read stopped before a reader
- The reader used (Azure, AWS, or Google Cloud), or that this host has no reader, or the exact CLI or login that is missing
- Counts: seen, shape only, skipped, not read, connections shown, databases opened, storage accounts opened. Shape only counts pre-prod, shared, and prod-only resources that were read. A prod-only resource the user declined is counted in skipped and in not read. A look-inside that did not open says not opened. A production database or store that stayed closed says not opened.
- Files this skill appended (`docs/environments/marks.md`) and files the owners changed, or that nothing was written
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.
- Picture offer, when this run appended one or more lines to `docs/environments/marks.md`
