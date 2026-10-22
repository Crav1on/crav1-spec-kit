# Ask research (1.77.0)

Read only on `ask research`, as in `/crav1-show-or-ask-open-questions ask research static IP Dana`.

## Pick and who

The words pick the question as [scope.md](../../crav1-add-to-spec/references/scope.md) says (topic words or `<spec> Q#`). One match: no question. The researcher is a typed name; else `git config user.name`, as `/crav1-help todo` finds **Yours first**; else nobody.

## The request

Draft one self-contained request that works pasted into any tool, person or agent. No spec slugs, paths or Q# in it.

- **Question.** In plain words.
- **Why it matters.** What it blocks: the spec line, `Blocks:` tasks, a deadline in `## Constraints`.
- **Known so far.** Assumptions, earlier answers, `## Research findings`.
- **Sources.** Notes, sources and links the spec already cites.
- **Who decides.** Who can answer or approve the result, from the question.
- **Bring back.** A research note in `docs/research/` naming the question, the finding, sources, and what is still open.

Run the personal-data and secrets check on the draft. Nothing is sent.

## Mark

Write the `Pending:` line of open-questions.md with channel `research`, with no question: `Pending: drafted <date> for <who>, research.` (shown as `Pending since <date> for <who> (research)`), or `Pending: drafted <date>, research.` with no name.

## Back

The returning note goes through `/crav1-add-to-spec`: a clear answer is linked as `Answered:`, open points are routed. `/crav1-help todo` ranks the mark as a pending draft, under **Yours first** for that name; an unnamed research mark counts as yours.
