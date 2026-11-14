# crav1-review-pr: ship or not

Read every run, after the fixed checks, when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

## Ship or not

In the kit record, list the check lines, then findings, then info notes, then suggestions, then bugs, tests to add and questions.

When the first section has no **fix** and no **drop**, the review says **ship**. Say it is clean. Info notes do not change that.

When any first-section decision is **fix** or **drop**, the review does not say ship.

The kit record ends with `Next, after this pull request merges: /crav1-refresh-system-notes, to bring its changes into the spec and docs/system/.`

The chat shows `Verdict: <Approve | Approve with comments | Changes needed>` (any Blocker or Bug: Changes needed; only tests to add or a question: Approve with comments; nothing: Approve), then the paste-ready comment (**Paste-ready comment** in `SKILL.md`), the `Kit record:` line, then the post offer (**Post it**), as `references/output.md` says. Then stop.
