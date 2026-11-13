# Which spec section reopens which step (1.148.0)

Read this when `resume` or `readiness` returns `reopen_line`. Say that line once. It names what changed and which steps reopen. Redo only those steps. Leave every other recorded step as it is. The progress file records `Section stamps:` on each step that covers the spec, and `Question ids:` on resolve-open-questions.

A step recorded before 1.148.0 has no `Section stamps` line. That step still uses the 1.137 rule: a spec change outside `## Open questions` reopens tighten-spec, resolve-open-questions, and the plan steps.

## Map

The first step in the list is the owner. Later steps are listed only when the plan was written from that section. An unknown `##` heading uses the requirement row. That is the safe default: a new constraint still reopens the plan.

| Section | Reopen |
| --- | --- |
| Text before the first heading | tighten-spec, plan-from-spec, review-and-tighten-plan, tasks-ready-to-build |
| Problem, Goals, Non-goals, Users and journeys, Acceptance criteria | same |
| Constraints, Requirements, Scope, Decisions, Background, Context | same |
| What the dump says, Trace, Research findings | same |
| Any other `##` heading | same |
| Open questions, when a question's words or stable id changed | resolve-open-questions |
| Match, In the code | none |
| A new question that already has `Answered:`, or an `Answered:` line on the same words | none |
| Synced at | none |
| Approval needed | none |

A requirement change does not reopen resolve-open-questions when `changed_questions` is empty. Settled questions stay settled. When resolve-open-questions is in the line, ask only the ids in `changed_questions`. Do not re-ask a question whose id is unchanged. A stable id is an `Id:`, `Qid:`, or `Stable id:` mark under the question, or the id `question_blocks.py` exposes when that function is not the word hash (1.146.0). Without one, the id is the hash of the question's words, so a reword is a new id and a removed id.

`## Match` and `## In the code` set `restamp_only`. So does a `Synced at:` line, and an already-answered question. No step reopens. `/crav1-add-to-spec` may restamp. A `Blocks:` or `Asked:` line that does not change the question's words also reopens nothing. It does not set `restamp_only`.

When the architecture review is the only spec step recorded so far, a requirement change reopens that review. Once a later spec step is recorded, a spec change does not send the walk back there.

A plan or tasks change is unchanged: it reopens the plan review and the ready check, not plan-from-spec. A `verify.md` change does not reopen the ready check. A progress mark does not reopen any step.
