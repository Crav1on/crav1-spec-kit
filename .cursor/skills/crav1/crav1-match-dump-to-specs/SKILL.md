---
name: crav1-match-dump-to-specs
description: >-
  Renamed in 1.56.0 to /crav1-add-to-spec. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-add-to-spec. Pre-answers the opening question: a dump.
disable-model-invocation: true
---

# /crav1-match-dump-to-specs (renamed)

`/crav1-match-dump-to-specs` was renamed to **`/crav1-add-to-spec`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-match-dump-to-specs` is now `/crav1-add-to-spec`."
2. Run `/crav1-add-to-spec` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Treat its opening question as already answered: **a dump**. Do not ask it. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
