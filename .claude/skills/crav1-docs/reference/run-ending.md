# How a run ends

Every skill ends a run in this shape (1.122.0). The skill still chooses which step is now, by the rules it already has. This page is only the shape.

A skill names the next step. It does not run it, unless that skill already runs the step today. The tighten-and-plan walk runs the steps inside the walk. Every other skill only names the step.

## Next

`Next:` is exactly one line. It names the single step to run now, and a short reason why.

The ready check is the exception (1.133.0). When tasks that can start sit on more than one build-map branch, `/crav1-tasks-ready-to-build` and the tighten-and-plan ready check print one `Next:` line per branch. Since 1.143.0 each of those lines recommends `/crav1-build-walk`, with the T number beside the task name and the branch, and names `/crav1-build-tasks` as the alternative for building one task without the walk. That alternative is not a second Next. Those branches do not wait on each other, so they can start together. One ready branch stays one line. Since 1.155.0 a ready branch with two or more open tasks also gets a whole-branch entry, `` `/crav1-build-walk <slug> <branch>` ``, beside its next-task entry. Since 1.150.0 the tighten-and-plan ready and ready-partial endings print `Run next:` first, before any Waiting line. Each command is alone in a code span and is a complete invocation for a new session: the T#s on that branch, and the slug when `docs/specs` has more than one slice. Since 1.153.0 that ending has exactly one Run next block, and the walk command appears only there. The bottom keeps Waiting lines and at most a one-line `/crav1-build-tasks` alternative, with no second copy of the command and no `Next:` line of its own. The ready-check reply must print that ending verbatim and must never write a `Next:` line. Each held line is in that same reply. The reply does not say above or listed above. `/crav1-build-walk` has the same shape at the start (1.142.0). When it is started from a ready-to-build report and no branch is chosen, it prints one `Next:` line per ready branch. Each line names that branch's tasks as `T#` plus the short name. Once one branch is in progress, the walk prints `Run next:` first, then Waiting and Uncommitted, then one full `Next:` line for that branch. Another branch whose tasks can start is its own Run next entry. A step skill it opened does not add its own `Next:` line. Every other skill keeps one `Next:` line.

```text
Next: /crav1-pr-status pr71, pr73, pr74, because this run added Points nothing has sorted yet.
```

A skill that runs on several pull requests or slugs at once may name them in that one command. That is still one step.

When nothing is needed now:

```text
Next: nothing needed now.
```

Do not list a second step on that line, in a second `Next:` line, or as an equal bullet. The ready check's one line per ready branch is the exception above, and the `/crav1-build-tasks` name on that line is the alternative for one task, not a second step. A step that depends on this step's result is not listed. The step named here says what comes after, when that applies. Do not list `pr<n> candidates` in the same ending as pr-status. That later command is named when the record has candidates.

## Waiting

`Waiting:` appears when a step is blocked, and when a step waits on a person's yes that is not a blocker (1.129.0). It names the step and who or what it waits on. One line per such step. Keep it short. Leave the line out when nothing is waiting.

A yes that is not on record is not a blocker. The task stays unticked. `Next` is to rerun that task after the yes.

A recorded yes that the assistant's permission check refused is not a missing yes (1.143.0). Waiting says the yes is on record and the check blocked the command. The offer is to run that exact command, or allow that one command and rerun. Next is the build step again after the command has run. Do not suggest working around the check.

```text
Waiting: /crav1-resolve-open-questions orders-retry, after a reviewer answers the open question.
Waiting: the partner's yes to turn off pipelines 7 and 24.
Waiting: your yes is on record. The assistant's permission check blocked the command.
Waiting: /crav1-verify-build-against-spec orders-api - verify.md is behind tasks.md (T2, T45)
```

When the ready check says `verify.md` is behind `tasks.md` (1.135.0), that last line is the Waiting line. Do not print the `Next:` line from `verify.md`. `Next` stays the ready check's own line for tasks that can still start.

## Uncommitted

A commit is not a step. When this run changed files and they are not committed, add one trailing line. Leave it out when nothing changed, or the changes are already committed.

```text
Uncommitted: 3 files; commit with /crav1-finalize-commit when ready.
```

Do not put the commit command in `Next` or `Waiting`.

## Which step stays Next

Rules that already pick a first step keep that choice, and use this shape.

- A `Conflict:` line was written: `Next` is `/crav1-resolve-open-questions` for that slug, because the conflict is unsettled.
- New information changed an existing slice, and no `Conflict:` line was written: `Next` is `/crav1-tighten-spec` for that slug, because the new information is not tightened yet. Resolve and the plan are not listed here.
- Spark, ideas, and bundle keep one `Left:` line with one `Next:` on that same last line. `Next` is `/crav1-tighten-spec` while gaps or open questions remain, and `/crav1-plan-from-spec` when nothing is left to tighten.
- The committed or changed files include a `walk-progress.md` with at least one `- Step:` record (`resume` reports `has_steps`), and `resume` for that folder reports a `continue_from` (1.123.0). A file that has only `- Branch run:` status lines (1.155.0) is not a paused tighten-and-plan walk. `Next` is `/crav1-tighten-and-plan-ready-to-build`, with the playbook path when the progress file has one, because the walk paused before that step. This comes before a pull request.
- The checkout has an unfinished `build-progress` file for the branch HEAD is on (1.142.0). `Next` is `/crav1-build-walk`, because that walk has not finished this branch. This comes before a pull request, after the specify walk when both are unfinished.

```text
Next: /crav1-tighten-and-plan-ready-to-build docs/playbooks/orders-retry.md, because the walk paused before plan-from-spec.
```

- That does not apply, and HEAD is a base branch (`main`, `master`, `develop`, the `Merges into` branch, or `release/*`). Do not name `/crav1-open-pr`. That command cannot open a pull request from the base into itself. `Next` is the push, using the branch name HEAD is on.

```text
Next: push main, because a pull request cannot open from main into itself.
```

On a feature branch, with no unfinished walk, `Next` stays `/crav1-open-pr` when the skill that just committed already names it.

```text
Left: 2 gaps to tighten, 3 open questions. Next: /crav1-tighten-spec orders-retry, because those gaps are still in the spec.
```

## Order

After the skill's own recap, print `Next`, then any `Waiting` lines, then `Uncommitted` when it applies. Nothing else is a next-step list.

The tighten-and-plan ready check is the exception (1.150.0). Print `Run next:` first, then each held line, then any `Loop` and `Waiting` lines, then at most the one-line `/crav1-build-tasks` alternative, then `Uncommitted` when it applies. No `Next:` line follows the Waiting lines (1.153.0). `Run next:` is not a second step. It is the same build-walk command, short enough to start in a new session.
