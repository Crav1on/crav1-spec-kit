---
name: crav1-fix-live
description: Shortcut to /crav1-fix-from-verify when the verify gap is a live/inner-loop path (ports, proxy, SQL, unpublished URL). Stay inside the spec. Do not edit spec.md.
disable-model-invocation: true
icon: bug
color: red
---

# Fix live (alias)

Follow skill **`crav1-fix-from-verify`** in full (drop-in: `.cursor/skills/crav1/crav1-fix-from-verify/SKILL.md`; plugin: sibling `skills/crav1-fix-from-verify/SKILL.md`). Hint only: prefer live/untested wiring rows in the inner-loop queue (failed → unverified → `G#`). Omit Gap to take the next of those. Never auto-pick **not implemented**.

## Picture offer

After that skill’s end, when the fix this turn changes how the parts connect, ask once. A connection change is which part talks to which: talks to, calls, sends, or reads from, including a line stated as does not. A port, a timeout, or a check that does not change which part talks to which does not get this question.

The question is exactly:

The system picture may now be out of date. Run `/crav1-keep-current`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-keep-current`. Do not edit the picture in this turn.

Do not add this question to `/crav1-fix-from-verify`, `/crav1-implement-task`, or `/crav1-complete-task`.
