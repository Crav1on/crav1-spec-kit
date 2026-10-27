# PR updates: `all` (1.76.0)

Read only on a PR ref followed by `all` (`/crav1-add-to-spec pr71 all`). The ref is parsed and found as [scope.md](scope.md) says.

## Steps

1. **Code.** Run the code-change branch for the PR. Its overlap check imports only new commits.
2. **Updates.** Add to the PR note ([notes.md](notes.md) **PR note**; write it first when missing) one `## PR updates as of <YYYY-MM-DD>` history section, in sorted place ([pr-record.md](pr-record.md)):
   - `### Description`, verbatim, only when it differs from the newest one in the note.
   - One `### <file>:<line>` or `### Conversation` heading per thread (1.97.0: no `(open)` or `(resolved)` mark; the thread's state goes in the record). Each comment: the author exactly as the host shows it, the date, the text verbatim; replies nested under it.
   - Skip bot and system threads (votes, pushes, policy and CI messages).
   - **Record (1.97.0).** In `## PR record`, a thread with no Point yet gets one: `open`, the first commenter's other side as owner (`-` when unclear), tags `thread <id>; host <status>; from add-to-spec <date>`, and the first comment's point in plain words. A thread that already has a Point gets only its `host <status>` tag updated. Classifying the points is `/crav1-pr-status`; this skill names it once when any Point is `open`, and does not run it.
3. **Check.** Run the personal-data and secrets check of [sources.md](sources.md) on everything first. Secrets are always redacted, by kind.

## Read again

Add only what is new or edited since the newest section: an edited comment in full, marked `(edited)`. A thread state change updates that Point's `host <status>` tag in the record (1.97.0), not a line in the section. Nothing new: say so. Never rewrite an earlier section.

## Answers

A comment that clearly answers an open question is linked under it as `Answered:` ([open-questions.md](open-questions.md)). Unclear stays open. A decision raised in a comment becomes a new open question. Spec lines are never rewritten. The Point of that thread gets the tag `answered <date>`, and a Point taken into a spec gets `in spec <slug>` (1.97.0).

## Read with

Read-only, never log in, as [pr-threads.md](pr-threads.md) says (1.97.0): GitHub `gh pr view <n> --json body,comments`, `gh api repos/<owner>/<repo>/pulls/<n>/comments`, and `reviewThreads` (`isResolved`) through `gh api graphql`. Azure DevOps: `az devops invoke --area git --resource pullRequestThreads` with the project, repo and PR id; thread `status` gives open or resolved, comment type `system` marks system threads.

## Signed out

Check `gh auth status` and `az account show`. Neither reads the PR: ask, with the status as one line (`gh: not signed in. az: not installed.`):

PR <n>'s comments are on the host. To read them, sign in to GitHub (`gh auth login`) or Azure DevOps (`az login`) in a terminal, then pick A.

- A) I've signed in, look it up
- B) Paste the comments instead
- C) Stop

A runs one sign-in check; still signed out shows the question once more. Never poll. B takes the paste, with the same check. A headless or bot run prints the status line and `PR <n> comments not read.` and stops.
