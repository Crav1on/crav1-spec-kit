# Repos to spec: **What is already there**

Part of `branches/repos-only/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## What is already there

Check the destination before the read. Do not stop because a note is already in `docs/system/`. Do not stop because `docs/architecture/spec.md` is already there. Name which pass this is, then read.

A real note is a short description that is not the template sentence, a diagram that is not only the template sample, a connection line that is not the template intro, a repo row, a glossary row, an ADR, or a feature-index row with a slug. The template sentence `What this product/system is, in one short paragraph.` is not a short description. The template diagram `user[User] --> app[App]` with no other node is not a diagram of this system. A `docs/system/` that is missing, or that is only the untouched template, is not already written.

Three passes:

1. **First write.** `docs/architecture/spec.md` is missing, and `docs/system/` is missing or only the untouched template. Write the architecture spec, the left-out file, and the system notes.
2. **Missing architecture spec.** `docs/architecture/spec.md` is missing, and a real note is already in `docs/system/`. Write `docs/architecture/spec.md` and `docs/architecture/left-out.md`. Leave every system note as it is. Do not add a line to those notes. Do not rewrite them.
3. **Later re-read.** `docs/architecture/spec.md` is already there. Add only what is new to that file. Do not rewrite a line that is already there. The same rule for system notes that are already there. Update `docs/architecture/left-out.md` when a line is added, removed, or dismissed. When `docs/system/` is missing or only the untouched template, those notes are not already there, so this pass writes them and still only adds what is new to the architecture spec.

The architecture spec path is locked: `docs/architecture/spec.md`. The left-out path is locked beside it: `docs/architecture/left-out.md`. Both stay out of `docs/system` and out of `docs/specs`. Do not invent any other folder. Do not create `docs/specs/architecture/`. Do not put left-out guesses under a heading in `spec.md`.

Do not point this pass at `/crav1-explain-existing-system`. Do not run it.
