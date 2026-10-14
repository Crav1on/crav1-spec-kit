---
name: crav1-fix-from-verify
description: >-
  Renamed in 1.56.0 to /crav1-fix-build-gaps. Deprecated alias, removed in 1.58.0.
  Hands off to /crav1-fix-build-gaps. Passes the choice word verify gaps.
disable-model-invocation: true
---

# /crav1-fix-from-verify (renamed)

`/crav1-fix-from-verify` was renamed to **`/crav1-fix-build-gaps`** in 1.56.0. This alias stays for two releases and is removed in 1.58.0.

1. Say once, in one line: "`/crav1-fix-from-verify` is now `/crav1-fix-build-gaps`."
2. Run `/crav1-fix-build-gaps` with the same message, `@` files, and arguments, and follow its `SKILL.md` from the start.
3. Pass the choice word `verify gaps`, as in `/crav1-fix-build-gaps verify gaps`, so the new skill does not ask that question. Ask any other question the new skill still needs.

This alias does nothing else on its own. It writes nothing and runs no other skill.
