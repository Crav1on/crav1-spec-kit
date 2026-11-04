# crav1-review-pr: output

Read every run, before you show anything (1.113.0). It sets what the chat shows and where the rest goes.

## Two parts

Every review has two parts:

- **The review.** What the author reads: the opening line, Blockers, Bugs, Tests to add, Questions, and the verdict. Built as `references/comment-layout.md` says, in the comment style of `references/comment.md`. It is kit-neutral. It never names a spec, a spec line, a lane, a plan, tasks, a kit skill or step, a next step, a commit hint, a note, an added source, or a tool aside (such as a merge-tree check). Each point reads as a normal review comment.
- **The kit record.** Everything else this skill works out: the check lines, first-section findings (F lines with lanes), spec and plan checks, spec drift, info notes, suggestions, follow-ups, the next step after merge, and names of other skills. It goes into the PR note (`references/notes.md`).

## Plain run

When this turn adds no outside context, the chat shows only:

1. `Verdict: <Approve | Approve with comments | Changes needed>`
2. The review as one fenced block, ready to paste.
3. One line: `Kit record: <PR note path>` (or `Kit record: not saved, no specs repo` when none is found).
4. The post offer (`references/posting.md`).

Nothing else. Write the kit record into the PR note silently. A question the run must ask (which pull request, fetching branches, posting) still goes to the chat as its own turn.

## With outside context

Outside context is anything this turn adds besides the pull request: a mail, a meeting or its transcript, a chat, a document, a workshop plan.

The context shapes the review: which points come first, what is left out (for example items a workshop will settle), and questions it raises. The review still never mentions the context, the kit or the specs. A point the context raises is written as the reviewer's own observation about the code.

The chat shows:

1. The review exactly as in a plain run (items 1 to 3), first and alone.
2. A line `---`, then the heading `Read-only: kit record and context (not for posting)`.
3. Under it, short: the kit record as above, then what the context changes: comparisons between the context and the pull request, items left out of the review and why (for example the workshop list), and questions kept for later.
4. The post offer.

Also save that read-only section as its own file next to the PR note, named after it with `-context` at the end (`<date>-pr-<repo>-<n>-context` in the same `docs/notes/YYYY-MM/` folder). Run the personal-data and secrets check of skill `crav1-add-to-spec`, `references/sources.md`, on it first. Front matter `kind: review context`, `pr_note:` the PR note path, and `source:` naming each added source. Link it from the PR note's record as `Context: <path>`. A re-review adds a dated section; it never rewrites an old one. No specs repo: write nothing and keep the section in the chat.

## Posting

Posting or pushing to a host only ever takes the review block. Never the kit record, the read-only section, or the context file.
