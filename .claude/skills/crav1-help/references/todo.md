# crav1-help: todo (1.75.0)

Read only on `todo`. What to do next, ranked from the records the kit already keeps. Read-only. Nothing is stored, written, or committed.

## Words and scope

- `todo`: every item, grouped by rank.
- `todo next`: the top 5. `todo top N`: the top N.
- A scope may follow: a person, a spec, a topic, a branch, or a pull request (`pr71`, `pr 71`, `#71`, `pr <repo> 71`), as `crav1-add-to-spec` `references/scope.md` says (drop-in: `.claude/skills/crav1-add-to-spec/references/scope.md`; plugin: sibling `skills/crav1-add-to-spec/references/scope.md`). No scope: every spec. `todo for <name>` sets who "you" are.

## What it reads

Every `docs/specs/<slug>/spec.md` in scope (skip `_template`, `retired/`, `Moved:` pointers): `## Open questions` with their `Asked:`, `Pending:`, `Answered:`, `Blocks:` lines, `Waiting for <who>` and `Decision.` points, `## Research findings` stale lines, a `Parked:` line, and dates written in `## Constraints`. Each `tasks.md`, counted with the readiness rules of `/crav1-tasks-ready-to-build`. The generated notes indexes for `waiting_for`. No Azure Boards, no pipeline runs.

## Ranking

Fixed order. Within a rank: more tasks unblocked first, then the older date first.

1. An open question that blocks tasks that are otherwise ready. Reason: `unblocks <n> tasks`.
2. Answered, not resolved.
3. A pending draft older than 3 days.
4. An ask older than 7 days with no answer.
5. A date written in `## Constraints` within 14 days.
6. A stale research mark with open points.
7. A decision waiting for the team.
8. Ready tasks.
9. A parked spec.

Ages are whole calendar days from the record's date to today.

## Yours first

Match `git config user.name` (or its first word), or the `todo for <name>` name, against the `<who>` in `Pending:`, `Asked:`, `Waiting for`, and who can answer, and the research owner. A `Pending:` research mark (1.77.0) with no name counts as a match. Matches go first under **Yours first**, still in rank order. No match: leave the group out. Do not ask.

## Each line

`<n>. <slug>: <the item in plain words>. <reason with the age>. Next: <skill>`. The next skill is resolve-open-questions (1, 2, 7), show-or-ask-open-questions (3, 4), a revisit request (6), build-tasks (8), retire-spec un-park (9), and for 5 the skill the dated item needs. End with `<m> more: todo top <N>` when cut, and the Source line.
