# Cursor attribution

Read after a successful commit when HEAD has a Cursor trailer that was not in the draft (commit step 6).

After a successful commit, if HEAD’s message is the draft **plus** a Cursor co-author/trailer:

1. Tell them in one short sentence: Cursor appended it; it was not part of the message they accepted.
2. **Strip it once** when all of these are true: this process created HEAD, HEAD is not pushed, they have not asked to keep the trailer.
   - `git commit --amend --no-verify` with **exactly** the drafted Summary + Description (same `-m` / HEREDOC as the original commit). No extra trailers. When the Description ends with the work-item mention, that line stays the last line of the amended message.
   - Read `git log -1 --format=%B` again. If the trailer is gone, show the clean hash/message, then the optional `/crav1-open-pr` line from the commit steps. Do not amend again.
   - If the trailer **came back**, Cursor wrapped `git commit` again. Do not loop amend. Offer `strip` (they should turn attribution off first) or `keep`.
3. How to stop it on **future local** commits: Cursor Settings → **Git & PRs → Attribution** (older: **Agent → Attribution**) → turn commit attribution off. CLI: `attribution.attributeCommitsToAgent` false in `~/.cursor/cli-config.json`. Enterprise admins can disable it org-wide. **Cloud / background agents** may still add co-author; the IDE toggle does not always apply there.
4. Do not install a `prepare-commit-msg` hook unless they ask.

If they say they **want** the Cursor trailer, leave it.
