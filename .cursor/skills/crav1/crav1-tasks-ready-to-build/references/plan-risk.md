# Plan risk

Read only when `SKILL.md` says a `## Risks` line says do not implement until resolved. Do not open this file otherwise.

A line under `## Risks` in `plan.md` that says do not implement until resolved blocks every unticked task, `plan Risk "<short risk>" blocks the whole slice (inferred)`, only when that risk is not about a question that already has a `Blocks:` line. Any `Blocks:` line wins over that wording, including `Blocks: none`. The risk matches its question on the question's first sentence, on `(question: <first words>)`, or when the risk names the same `Blocks` tasks. A risk that uses the phrase and matches no question still blocks the slice.
