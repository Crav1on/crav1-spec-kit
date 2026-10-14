---
name: crav1-complete-tasks
description: >-
  Renamed in 1.56.0 to /crav1-build-tasks. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-build-tasks. Passes the choice word range (when the message names T#-T#) or all tasks.
disable-model-invocation: true
---

# /crav1-complete-tasks (renamed)

`/crav1-complete-tasks` was renamed to **`/crav1-build-tasks`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-complete-tasks` is now `/crav1-build-tasks`."
2. Run `/crav1-build-tasks` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Pass the choice word `range` (when the message names `T#-T#`) or `all tasks`, as in `/crav1-build-tasks all tasks`, so the new skill does not ask that question. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
