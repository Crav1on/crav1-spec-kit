# How a run ends

Every skill ends a run in this shape (1.122.0). The skill still chooses which step is now, by the rules it already has. This page is only the shape.

A skill names the next step. It does not run it, unless that skill already runs the step today. The tighten-and-plan walk runs the steps inside the walk. Every other skill only names the step.

## Next

`Next:` is exactly one line. It names the single step to run now, and a short reason why.

```text
Next: /crav1-pr-status pr71, pr73, pr74, because this run added Points nothing has sorted yet.
```

A skill that runs on several pull requests or slugs at once may name them in that one command. That is still one step.

When nothing is needed now:

```text
Next: nothing needed now.
```

Do not list a second step on that line, in a second `Next:` line, or as an equal bullet. A step that depends on this step's result is not listed. The step named here says what comes after, when that applies. Do not list `pr<n> candidates` in the same ending as pr-status. That later command is named when the record has candidates.

## Waiting

`Waiting:` appears when a step is blocked, and when a step waits on a person's yes that is not a blocker (1.129.0). It names the step and who or what it waits on. One line per such step. Keep it short. Leave the line out when nothing is waiting.

A yes that is not on record is not a blocker. The task stays unticked. `Next` is to rerun that task after the yes.

```text
Waiting: /crav1-resolve-open-questions orders-retry, after a reviewer answers the open question.
Waiting: the partner's yes to turn off pipelines 7 and 24.
```

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
- The committed or changed files include a `walk-progress.md`, and `resume` for that folder reports a `continue_from` (1.123.0). `Next` is `/crav1-tighten-and-plan-ready-to-build`, with the playbook path when the progress file has one, because the walk paused before that step. This comes before a pull request.

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
