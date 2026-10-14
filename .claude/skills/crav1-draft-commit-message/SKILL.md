---
name: crav1-draft-commit-message
description: >-
  Renamed in 1.56.0 to /crav1-finalize-commit. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-finalize-commit. Pre-answers the opening question: only write the message.
disable-model-invocation: true
---

# /crav1-draft-commit-message (renamed)

`/crav1-draft-commit-message` was renamed to **`/crav1-finalize-commit`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-draft-commit-message` is now `/crav1-finalize-commit`."
2. Run `/crav1-finalize-commit` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Treat its opening question as already answered: **only write the message**. Do not ask it. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
