# Task list

Read only when `SKILL.md` says so.

Lead with the summary, then the lists. One line per task. Leave out an empty list.

```text
Tasks ready to build — <slug> | all specs (<n> slices)

| Slice | Ready | Waiting | Waits in order | Blocked | Needs verify | Done |
| --- | --- | --- | --- | --- | --- | --- |
| <slug> | 1 | 1 | 1 | 1 | 1 | 4 |

Result: ready-partial

Ready now
- `feat/orders-retry` (wave 1): T5 refund to the original card
- `feat/orders-export` (wave 1): T6 export the receipt

Held
- `feat/orders-currency` (wave 1): T7 choose the currency — open question "Which currency for refunds?" Waiting for the partner.
- `feat/orders-archive` (wave 2): T8 archive the receipt — held, waits on T7

Waits in order (dependency order)
- T9 send the mail: waits on T5 (recorded).

Blocked (dependency order)
- T10 cycle T10 → T11 → T10 (recorded).

Needs verify
- T3 short name: no verify.md row.

Done: 4
Order: T5 → T9 → T7 → T8

Next: /crav1-build-walk T5 refund to the original card, because that work is on feat/orders-retry. /crav1-build-tasks builds one task without the walk.
Next: /crav1-build-walk T6 export the receipt, because that work is on feat/orders-export. /crav1-build-tasks builds one task without the walk.
Source: docs/specs/<slug>/spec.md, plan.md, tasks.md, verify.md
Build map: docs/specs/<slug>/build-map.md
```

- **By branch (1.133.0).** When Python runs, `scripts/walk_progress.py readiness --root <spec-folder>` (skill `crav1-tighten-and-plan-ready-to-build`) prints `ready_lines`, `held_lines`, and `next_lines`. Print those. Do not flatten them. The branch is `scripts/build_map.py docs/specs/<slug> --recommend T#`, the same row as the map. Order is wave, then map order. A task is `T#` plus its short name, in the lists and on the map. One ready branch is still one group and one Next line. Without Python, use `references/build-map.md` under Ready check.
- **Result (1.132.0)** is `ready` when the tasks that are not done can start or only wait in order, `ready-partial` when some can start now and some are held, and `not-ready` when nothing can start. The walk record stays `Result: ready-partial`. A cycle, a missing task, no plan, Needs verify, or a plan-review warning still records `not-ready`.
- **Order** shows the slice's unticked tasks in dependency order, `|` between tasks of the same wave. One Order line per slice when listing all specs. The Order line keeps task ids.
- **Next** is the script's `next_lines` when the result is `ready` or `ready-partial`: `/crav1-build-walk`, and `/crav1-build-tasks` builds one task without the walk. See `run-ending.md`. Do not run it.
- **Source** names every file it read, per slice.
- **Build map** is one line per slice, the path the script just wrote. The task list above it is unchanged.
