# crav1-plan-from-spec: the After writing recap

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.159.0; the rules are unchanged. The recap command in `SKILL.md` prints this output in this order. Follow it by hand only when Python cannot run.

## After writing (the rules the recap computes)

Output only:

- Paths written
- Task count and any acceptance line with no task, not marked `already there`, and not `left as committed` (must be none, or the plan failed)
- Each built piece: already there, finish the gap, add a verify test, or left as committed
- The branch read, when **Built pieces** ran
- Any verify note with no kind, and any kept security check with no task (must be none, or you failed)
- Kept-open questions parked as risks, one line each. The current-or-later batch is the only ask, and only when a leftover is unclear.
- Each stale research finding listed under Risks, or that none was marked stale
- These notes name the checks. `/crav1-verify-build-against-spec` is the gate that says they passed. Do not run it here.
- The linter line: the tool and command, or that this repo has none for the code these tasks will touch.
- One `Next` line, as `crav1-docs/reference/run-ending.md` says. Do not run it. Add the Uncommitted line when a file changed and is not committed. Do not name tighten-plan or build in this ending.
- This branch is `spec/<slug>`: `Next: /crav1-open-pr, because this specify-only branch is not on the default branch yet.` Do not implement here.
- Any other branch: `Next: /crav1-review-plan, because the plan is written and not reviewed.` When the plan says there is no linter, say build is not named until they add one or choose to go on without one. Do not install one.

Do not start coding in this chat.
