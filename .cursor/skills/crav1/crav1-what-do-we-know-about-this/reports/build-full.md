# report-build-full

Everything left before the slice is done, and the order to do it. Rules: `reports/common.md`.

Read the slice's `spec.md`, `plan.md`, `tasks.md`, open questions and verify notes. Order tasks with `/crav1-tasks-ready-to-build` **Dependency order** (its `scripts/task_order.py` when Python runs). Do not run that skill.

Diagrams: a `flowchart` of the whole task graph (ticked tasks greyed, ready ones marked, blocked edges labelled with why); a short `flowchart` of the finish order, one box per wave. No C4.

```markdown
# <Slice>: what's left and in what order

## Verdict
## Status                   (spec, plan, tasks ticked/total, verify)
## Gaps
### Spec                    (open questions, missing sections)
### Plan                    (missing decisions, tasks without `(after: …)` where order matters)
### Tasks                   (blocked tasks, cycles, failed verify)
## Unblock order            (`Order:` line, then one ### per wave with its tasks)
## Task graph               (diagram)
## Next                     (the ready task that unblocks the most)
## Asks                     (`Ask <person the docs name>: …`, with file and heading)
## Tracked elsewhere
## Source
```
