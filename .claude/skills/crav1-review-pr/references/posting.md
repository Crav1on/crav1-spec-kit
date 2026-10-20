# crav1-review-pr: posting

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Post it

After the paste-ready block, offer to post. One question. Use the questions tool when it is available. Say it posts under the user's own account as one comment, and name the vote it will set. Options: **post**, **I'll post it myself**, or **do not post** (1.67.0). Nothing posts without that yes. **I'll post it myself** ends the run with `When it's posted, say "posted" here, or run /crav1-review-pr <repo> <n> comment posted.`

On yes (1.66.0):

1. Post the block as **one comment**. No inline threads. GitHub: one review whose body is the block, submitted with the vote (`gh api repos/<owner>/<repo>/pulls/<n>/reviews` with `body` and `event`). Azure DevOps: one pull request thread whose comment is the block, then the vote.
2. The vote follows the verdict: Changes needed is **Request changes** (GitHub) or **Wait for author** (Azure DevOps); Approve with comments is **Comment** or **Approve with suggestions**; Approve is **Approve**. Never Reject.
3. On a re-review, post the new block as a reply in the earlier comment's thread (Azure DevOps) or as a new review (GitHub). Reply in an earlier inline thread only when one exists.
4. Follow-ups are never posted.
5. Save the posted text at once (1.67.0): the body the host returns, its URL and date, under `## Comment as posted, <YYYY-MM-DD> (by <name>)` with the source line `Posted from this review on the user's yes: <comment URL>. …` (`references/comment-as-posted.md`). A failed post saves nothing.
6. On GitHub, when the signed-in user is the pull request's author, the host does not allow Approve or Request changes: post with event `COMMENT` and say `GitHub doesn't allow a vote on your own PR; posted as a comment.`
7. Never resolve a thread. On a re-review, after posting, offer to resolve existing threads whose points are now fixed. Resolve only on that yes.

When a post fails, say what failed and what already posted. Do not retry by another route.
