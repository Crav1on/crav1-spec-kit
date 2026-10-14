---
name: crav1-tasks-to-ado
description: >-
  Renamed in 1.56.0 to /crav1-ado-sync. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-ado-sync. Passes the choice word push tasks.
disable-model-invocation: true
---

# /crav1-tasks-to-ado (renamed)

`/crav1-tasks-to-ado` was renamed to **`/crav1-ado-sync`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-tasks-to-ado` is now `/crav1-ado-sync`."
2. Run `/crav1-ado-sync` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Pass the choice word `push tasks`, as in `/crav1-ado-sync push tasks`, so the new skill does not ask that question. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
