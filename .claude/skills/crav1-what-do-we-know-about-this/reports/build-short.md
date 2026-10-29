# report-build-short

One screen: can this slice be built, and what is next. Rules: `reports/common.md`.

Read the slice's `spec.md`, `plan.md` and `tasks.md`. Order tasks with `/crav1-tasks-ready-to-build` **Dependency order** (its `scripts/task_order.py` when Python runs). Do not run that skill.

Diagrams: none, unless more than one task is ready; then one small `flowchart` of the next wave. No C4.

```markdown
# <Slice>: build status

## Verdict
<ready to build | blocked on <what> | done>

## Status
| Spec | Plan | Tasks | Open questions |
| --- | --- | --- | --- |
| <state> | <state> | <ticked>/<total> | <count> |

## Next tasks
1. **T# <title>** — Next (unblocks <n>)
2. <the next one or two, in dependency order>

## Source
```
