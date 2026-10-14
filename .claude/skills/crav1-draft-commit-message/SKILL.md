---
name: crav1-draft-commit-message
description: >-
  Renamed in 1.56.0 to /crav1-finalize-commit. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-finalize-commit. Passes the choice word message only.
disable-model-invocation: true
---

# /crav1-draft-commit-message (renamed)

`/crav1-draft-commit-message` was renamed to **`/crav1-finalize-commit`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-draft-commit-message` is now `/crav1-finalize-commit`."
2. Run `/crav1-finalize-commit` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Pass the choice word `message only`, as in `/crav1-finalize-commit message only`, so the new skill does not ask that question. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
