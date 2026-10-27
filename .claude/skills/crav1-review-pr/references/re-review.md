# crav1-review-pr: re review

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Re-review

When the pull request already has an earlier review, this run is a re-review. Read the PR note's `## PR record` first (1.97.0; `crav1-add-to-spec` `references/pr-record.md`): its Points are the earlier findings, follow-ups and questions, with their statuses. Then read the earlier findings from the pull request's own review comments and threads, including the bullets of an earlier one-comment review (each link gives the path and lines) (read as `crav1-add-to-spec` `references/pr-threads.md` says, 1.97.0; drop-in: `.claude/skills/crav1-add-to-spec/references/pr-threads.md`; plugin: sibling `skills/crav1-add-to-spec/references/pr-threads.md`. GitHub `gh api repos/<owner>/<repo>/pulls/<n>/comments` and `gh pr view <n> --json reviews,comments`; Azure DevOps `az devops invoke --area git --resource pullRequestThreads` or `az rest --method get` on the pull request threads. `az repos pr` has no thread command). Comments from anyone count, including ones this skill posted. When the PR note has a `## Comment as posted` section (1.67.0), the earlier points are the points of the newest one, after the record step. When the host has no earlier review comments, nothing was posted: the comment is a first-review comment with no `### Since last time`, and the chat goes through the newest `## Comment as drafted` section's points under `compared with the draft; nothing posted was found`. When there is no draft either, do a first review.

Go through each earlier finding, one line each, before the new findings:

- **Fixed:** the code changed and the problem is gone. Name the commit that fixed it (short SHA); its Point becomes `done <short sha>`.
- **Partly fixed:** some of it changed. Say what is left.
- **Still open:** the problem is still there.
- **No longer relevant:** the code was removed or rewritten so the finding no longer applies.

A thread marked resolved whose problem is still there is flagged `resolved but still open`. Do not guess a status: when the diff does not settle it, say so.

Status lines and thread replies follow [Comment style](../SKILL.md#comment-style): first person, friendly, varied, for example "Thanks, this looks sorted now in `abc1234`" or "I think there is still a little bit left here: …". A still-open finding is said softly, with the same information.

In the comment, earlier points go under `### Since last time` and new points under the normal sections (`references/comment-layout.md` **Re-review**). `### Since last time` lists only points the reviewers saw. A new finding that matches a Point tagged `not posted` is shown in the chat with its mark and kept out of the comment unless the user says to include it (1.67.0). The ship-or-not rule counts still-open, partly-fixed, and new first-section findings.
