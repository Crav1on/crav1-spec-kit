# crav1-review-pr: comment

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Comment style

The default style for the paste-ready block, every posted comment, and every re-review reply (agreed by Thomas and Rhea, 2026-10-12):

- Write in the user's own first-person voice. Friendly, so the author never feels criticised, harped on, or wrong. Do not say that outright.
- Keep the source of the findings vague: "me and my checks". Never name a tool, a skill, a bot, or the kit. Never write that a tool found the author's mistakes.
- The opening is one short, plain line, in the spirit of "I've looked through the PR and run it through my checks. This is what I found:". It may vary slightly. Never praise, a greeting by name, or thanks (1.66.0).
- One fix per point at most. No second option, and nothing after the fix or the question ("your call", "let me know") (1.66.0).
- Soft wording, same information: "I noticed…", "It looks like… maybe they could…?", "Would it be worth adding a test that…?". No flat statements of fault. Do not drop or water down a fact to sound soft.
- Read the pull request description first. A choice the description says is deliberate is not raised as a fault, unless it contradicts something written in the repo (a code comment, a README, a design rule); then it is a bug or a question with one fix (1.66.0). When it suggests something they "might like" or that "may be a good idea", it is a follow-up and goes to the note, not into the comment.

The chat review above the block (F, I, S, B, T, Q lines) keeps its plain format for the user. The style applies to what the author will read.

The block is text in the chat. Showing it posts nothing.

## Bugs, tests, questions (1.66.0)

Each point that goes into the comment has a chat line, two lines each:

```text
B1 — bug
What you noticed: <one line>
Where: <path>, line <n> | no line
```

`T1 — test to add` is a concrete test for a changed behavior or a bug. `Q1 — question` is something the author or team must answer about the code repo. Same two lines. They do not change the ship line. A question is saved in the follow-ups note as a bullet that starts `Asked on the PR:`. Which section each one goes to: `references/comment-layout.md` **Which section** (drop-in: `.claude/skills/crav1-review-pr/references/comment-layout.md`; plugin: `skills/crav1-review-pr/references/comment-layout.md`).

## Paste-ready comment

End every review with one fenced Markdown block the user can paste into the pull request as one comment. Build it exactly as `references/comment-layout.md` says (1.66.0; drop-in: `.claude/skills/crav1-review-pr/references/comment-layout.md`; plugin: `skills/crav1-review-pr/references/comment-layout.md`). In short:

- No verdict line in the block; the chat shows `Verdict: …` just above it.
- One short, plain opening line, then `### Blockers`, `### Bugs`, `### Tests to add with this PR`, `### A question` (or `### Questions`), leaving out a section with nothing in it.
- Each point starts with the host link to its file and line on the pull request's source branch (or the PR overview, or a branch link), then a blank line and the explanation as an indented paragraph. At most one fix per point, no tails.
- No follow-ups, no table, no closing line, no files-view link, no HTML, no kit details.
- Advice about a branch that is behind, has conflicts, or must take another branch first says to merge `<base>` into this branch. Never a rebase.
- English, unless the user asks for another language for this comment in this turn.
