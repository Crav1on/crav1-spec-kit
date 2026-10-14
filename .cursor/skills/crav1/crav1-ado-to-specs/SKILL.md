---
name: crav1-ado-to-specs
description: >-
  Renamed in 1.56.0 to /crav1-ado-sync. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-ado-sync. Pre-answers the opening question: pull spec changes.
disable-model-invocation: true
---

# /crav1-ado-to-specs (renamed)

`/crav1-ado-to-specs` was renamed to **`/crav1-ado-sync`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-ado-to-specs` is now `/crav1-ado-sync`."
2. Run `/crav1-ado-sync` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Treat its opening question as already answered: **pull spec changes**. Do not ask it. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
