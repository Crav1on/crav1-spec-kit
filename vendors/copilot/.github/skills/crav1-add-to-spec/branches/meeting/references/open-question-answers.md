# Meeting to specs: **Answers to open questions**, **Recommendation**

Part of `branches/meeting/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Answers to open questions

Read `## Open questions` on every spec folder (skip `_template`), with the records under each question. Follow this skill's `references/open-questions.md`. Match by meaning. Matching works whether the question is asked, pending, or not marked.

- **Clear answer.** The item states the fact or the decision a spec open question asks for. The case is `answer`. The item shows `Answers: "<question>" on docs/specs/<slug>/` and `Linked without a question.` It is not asked keep, leave, dismiss, or note. Hand it to the fact branch of `/crav1-add-to-spec` as an answer link (see **Answer** under Keep). When it would change a spec line, also show `Then: /crav1-tighten-spec, then /crav1-resolve-open-questions for <slug>.`
- **Unclear or partial.** The item keeps its own case. It also shows `Possible answer to: "<question>" on docs/specs/<slug>/. The question stays open.` It is asked in the batch like any other item. Nothing is linked.
- **Asked in this input.** The input shows someone asking a spec open question. That is not an item. List it under `Asked in this <kind>` before the items, one line per question, with the spec. Its `Asked:` mark is written through the same handoff, with the date of this input. That date replaces a `Pending:` line, and an `Asked:` line from the user's yes, for the same person.

After a meeting, every question that was asked or pending for that meeting and got no clear answer goes back to open. Its asked mark stays, as the reference file says.

## Recommendation

Show one recommendation on the item and in the question. In the question, the recommended option comes first and its label ends with ` (Recommended)`; the question text does not repeat it. Do not pick for the user.

- **Keep** — the quote is a decision, a clarification, information, or an answer for an existing spec.
- **Leave** — the quote is worth keeping but fits no spec now. Exploration with no feature yet, technical debt, and general information gathering are this case. It stays in the full note (1.61.0); nothing else is written.
- **Dismiss** — the quote is only noise: a greeting, scheduling, or thanks.

This skill asks every item in one batch (1.70.0). A single yes takes every recommendation; answering item by item still works. The recommendation is the suggested answer.
