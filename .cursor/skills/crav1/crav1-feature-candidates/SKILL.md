---
name: crav1-feature-candidates
description: >-
  Renamed in 1.56.0 to /crav1-ado-sync. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-ado-sync. Passes the choice word suggest features.
disable-model-invocation: true
---

# /crav1-feature-candidates (renamed)

`/crav1-feature-candidates` was renamed to **`/crav1-ado-sync`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-feature-candidates` is now `/crav1-ado-sync`."
2. Run `/crav1-ado-sync` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Pass the choice word `suggest features`, as in `/crav1-ado-sync suggest features`, so the new skill does not ask that question. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
