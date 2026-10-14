---
name: crav1-repos-to-spec
description: >-
  Renamed in 1.56.0 to /crav1-existing-to-specs. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-existing-to-specs. Passes the choice word repos only and one spec.
disable-model-invocation: true
---

# /crav1-repos-to-spec (renamed)

`/crav1-repos-to-spec` was renamed to **`/crav1-existing-to-specs`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-repos-to-spec` is now `/crav1-existing-to-specs`."
2. Run `/crav1-existing-to-specs` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Pass the choice word `repos only` and `one spec`, as in `/crav1-existing-to-specs repos only one spec`, so the new skill does not ask that question. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
