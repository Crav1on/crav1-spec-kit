# Fix live (alias)

Follow skill **the verify gaps branch of `crav1-fix-build-gaps`** in full (drop-in: `.claude/skills/crav1-fix-build-gaps/branches/verify-gaps/BRANCH.md`; plugin: sibling `skills/crav1-fix-build-gaps/branches/verify-gaps/BRANCH.md`). Hint only: prefer live/untested wiring rows in the inner-loop queue (failed → unverified → `G#`). Omit Gap to take the next of those. Never auto-pick **not implemented**.

## Picture offer

After that skill’s end, when the fix this turn changes how the parts connect, ask once. A connection change is which part talks to which: talks to, calls, sends, or reads from, including a line stated as does not. A port, a timeout, or a check that does not change which part talks to which does not get this question.

The question is exactly:

The system picture may now be out of date. Run `/crav1-refresh-system-notes`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-refresh-system-notes`. Do not edit the picture in this turn.

Do not add this question to the verify gaps branch of `/crav1-fix-build-gaps`, `/crav1-build-tasks`.
