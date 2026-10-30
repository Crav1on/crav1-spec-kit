# Show or ask open questions: Show branch

Read only when `SKILL.md` routes here (`show`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Show

Read `## Open questions` in every `docs/specs/<slug>/spec.md` (skip `_template`), with the lines under each question, as `crav1-add-to-spec` `references/open-questions.md` describes. Write nothing. Draft nothing. Send nothing.

- One section per spec with open questions, then one line per question that has no `Answered:` line: its `Q#` (document order, display only, never written; 1.84.0), the question in plain words, then its marks: `Asked <date>, <channel> to <who>`, `Pending since <date> for <who>`, `Blocks T2, T4`, or `not asked yet`.
- An answered question still waiting on `/crav1-resolve-open-questions` is listed under **Answered, not resolved**.
- End with counts: open, asked, pending, not asked, answered not resolved; then by person: who has how many asked or pending.
- Next: `/crav1-show-or-ask-open-questions` with **Ask** for the ones not asked yet, or `/crav1-resolve-open-questions` for the answered ones. Do not run them.


The specs hold open questions that only someone outside the kit can answer, such as a partner, a customer, or a colleague. You gather those questions and draft them so the user can ask them by mail, in a meeting, or in a chat. You record whether they were asked. You never send anything.

Command: `/crav1-show-or-ask-open-questions`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command.

This is not `/crav1-resolve-open-questions`. Resolve walks the questions with the user and writes the decisions into the spec. This command drafts the questions for someone else and writes only the asked and pending marks.

The record format, pending, answer links, and the asked-on date are shared with the import skills. Follow `crav1-add-to-spec` `references/open-questions.md` (drop-in: `.claude/skills/crav1-add-to-spec/references/open-questions.md`; plugin: sibling `skills/crav1-add-to-spec/references/open-questions.md`).
