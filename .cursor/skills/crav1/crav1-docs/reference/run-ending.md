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

`Waiting:` appears only when a step is blocked. It names the step and who or what it waits on. One line per blocked step. Keep it short. Leave the line out when nothing is blocked.

```text
Waiting: /crav1-resolve-open-questions orders-retry, after a reviewer answers the open question.
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

```text
Left: 2 gaps to tighten, 3 open questions. Next: /crav1-tighten-spec orders-retry, because those gaps are still in the spec.
```

## Order

After the skill's own recap, print `Next`, then any `Waiting` lines, then `Uncommitted` when it applies. Nothing else is a next-step list.
