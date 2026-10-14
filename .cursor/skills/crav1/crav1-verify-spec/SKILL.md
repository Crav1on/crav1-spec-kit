---
name: crav1-verify-spec
description: >-
  Renamed in 1.56.0 to /crav1-verify-build-against-spec. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-verify-build-against-spec.
disable-model-invocation: true
---

# /crav1-verify-spec (renamed)

`/crav1-verify-spec` was renamed to **`/crav1-verify-build-against-spec`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-verify-spec` is now `/crav1-verify-build-against-spec`."
2. Run `/crav1-verify-build-against-spec` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. The new skill keeps the same rules; nothing else changes.

This alias does nothing else on its own. It writes nothing and runs no other skill.
