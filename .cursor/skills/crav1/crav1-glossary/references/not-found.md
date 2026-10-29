# crav1-glossary: not found

Read only when **Research one term** found no meaning in `docs/` and none on the web (1.105.0).

The glossary is definitions only. Nothing here writes to a spec: no open question, no `Pending:` line, no `Asked:` line, no task. Do not run or hand off to `/crav1-show-or-ask-open-questions`, and do not use `crav1-add-to-spec` `references/open-questions.md`. Open questions without `Blocks:` stop `/crav1-tasks-ready-to-build`, and a word's meaning must never stop a build.

## Offer what you may know

1. Collect the lines in `docs/` that use the term (path and line, at most three).
2. When those lines, or general knowledge for a public term, suggest a meaning, write one short guess and label it `(inference, not in the docs)`. Never guess from an internal-only term's web results; there are none.
3. Ask, in the run's one question (with the web meanings when there are some), per term:
   - **Correct** — write the row: `<guess> Source: confirmed in chat (<date>)`, replacing only `to be researched` (or adding the row in sorted place in Term mode).
   - **Needs research** — the row stays `to be researched` (Term mode: added as `to be researched`).
   When there is no guess, say so and offer only **Needs research**.
4. A headless or bot run asks nothing: it writes nothing for these terms and lists each guess under **Guesses waiting**.

## Needs research

Optionally draft a research request in the chat for a person to pick up: Term, Seen in (paths and lines), Guess so far, Who may know (the author or sender of the first source that uses the word, when written), Bring back (one sentence meaning and its source). Nothing is written to a spec, nothing is sent, and no file is created. The next `/crav1-glossary research` picks the row up again.
