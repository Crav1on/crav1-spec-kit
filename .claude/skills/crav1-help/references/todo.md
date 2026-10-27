# crav1-help: todo (1.75.0)

Read only on `todo`. What to do next, ranked from the records the kit already keeps. Read-only. Nothing is stored, written, or committed.

## Words and scope

- `todo`: every item, grouped by rank.
- `todo next`: the top 5. `todo top N`: the top N.
- A scope may follow: a person, a spec, a topic, a branch, or a pull request (`pr71`, `pr 71`, `#71`, `pr <repo> 71`), as `crav1-add-to-spec` `references/scope.md` says (drop-in: `.claude/skills/crav1-add-to-spec/references/scope.md`; plugin: sibling `skills/crav1-add-to-spec/references/scope.md`). No scope: every spec. `todo for <name>` sets who "you" are.

## What it reads

Every `docs/specs/<slug>/spec.md` in scope (skip `_template`, `retired/`, `Moved:` pointers): `## Open questions` with their `Asked:`, `Pending:`, `Answered:`, `Blocks:` lines, `Waiting for <who>` and `Decision.` points, `## Research findings` stale lines, a `Parked:` line, and dates written in `## Constraints`. Each `tasks.md`, counted with the readiness rules of `/crav1-tasks-ready-to-build`. The generated notes indexes for `waiting_for`. The `## PR record` of each PR note whose `State` is not `merged`, `abandoned` or `closed` (1.97.0; `crav1-add-to-spec` `references/pr-record.md`): its `waiting on <name>` and `needs <name>` Points. No Azure Boards, no pipeline runs, no host read.

## Ranking

Fixed order. Within a rank: more tasks unblocked first, then the older date first.

1. An open question that blocks tasks that are otherwise ready. Reason: `unblocks <n> tasks`.
2. Answered, not resolved.
3. A pending draft older than 3 days.
4. An ask older than 7 days with no answer.
5. A pull request point `waiting on` or `needs` someone (1.97.0). Reason: `PR <n> <repo>, since <date>`, the date of the newest `Read`, else the Point's `from` date.
6. A date written in `## Constraints` within 14 days.
7. A stale research mark with open points.
8. A decision waiting for the team.
9. Ready tasks.
10. A parked spec.

Ages are whole calendar days from the record's date to today.

## Yours first

Match `git config user.name` (or its first word), or the `todo for <name>` name, against the `<who>` in `Pending:`, `Asked:`, `Waiting for`, a PR Point's `waiting on` and `needs`, and who can answer, and the research owner. A `Pending:` research mark (1.77.0) with no name counts as a match. Matches go first under **Yours first**, still in rank order. No match: leave the group out. Do not ask.

## Each line

`<n>. <slug>: <the item in plain words>. <reason with the age>. Next: <skill>`. The next skill is resolve-open-questions (1, 2, 8), show-or-ask-open-questions (3, 4), pr-status (5; the line is `<n>. PR <n> <repo>: …`), a revisit request (7), build-tasks (9), retire-spec un-park (10), and for 6 the skill the dated item needs. End with `<m> more: todo top <N>` when cut, and the Source line.
