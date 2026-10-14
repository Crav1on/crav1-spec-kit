---
name: crav1-match-to-specs
description: >-
  Renamed in 1.56.0 to /crav1-existing-to-specs. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-existing-to-specs. Pre-answers the opening question: repos plus a bundle (the second question is still asked).
disable-model-invocation: true
---

# /crav1-match-to-specs (renamed)

`/crav1-match-to-specs` was renamed to **`/crav1-existing-to-specs`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-match-to-specs` is now `/crav1-existing-to-specs`."
2. Run `/crav1-existing-to-specs` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Treat its opening question as already answered: **repos plus a bundle (the second question is still asked)**. Do not ask it. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
