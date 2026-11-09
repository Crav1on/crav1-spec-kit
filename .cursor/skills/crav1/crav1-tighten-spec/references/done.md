# crav1-tighten-spec: done

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## When the spec is tight enough

All remaining issues resolved **and**:

- One primary user
- v0 vs later is explicit
- Non-goals are written
- Happy, fail, and empty paths exist
- Every acceptance line is a yes/no check. No test list. A kind is named only when the source already made unit, system, or browser obvious.
- Open questions are listed, not buried

Then stop the issue walk.

If **Open questions** (or unresolved assumptions) remain: `Next: /crav1-resolve-open-questions, because open questions are still listed.` Not Plan Mode. That skill walks each question with keep-open vs answer.

If the open-question list is empty: `Next: /crav1-plan-from-spec, because the spec is tight enough to plan.` A new chat in Plan Mode (`Shift+Tab`) with `spec.md` attached is the same step. Do not name the spec reviewer in the ending.
