# Picture offer

Read only when `SKILL.md` says so.

When this run marks a slug `done` on the board, or a slice on this board is marked `retired`, ask once at the end, after the board TL;DR. A slice is marked `retired` when the user says it is retired in this run, or that slug’s feature-index Notes or `## Match` status says `retired`. Do not write `retired` into a file. Do not edit `spec.md`.

Ask once for the board, not once per slug. The question is exactly:

The system picture may now be out of date. Run `/crav1-refresh-system-notes`?

Options are yes and no. Do not run `/crav1-refresh-system-notes`. A yes waits for a later turn. A no ends without that command.

Do not ask when no slug was marked done and none was marked retired. Do not add this question to `/crav1-build-tasks`.
