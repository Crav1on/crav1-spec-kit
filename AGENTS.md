# Agent instructions for this repo

This repository is a **process guide** for spec-driven development in Cursor, not an application.

- Do not scaffold an app unless the user explicitly asks for one.
- Keep the README accurate against current Cursor docs when you update it.
- Put per-change work under `docs/specs/<change-id>/` using `_template/`.
- From a one-sentence spark, use `/spark-to-spec` then `/tighten-spec`. Do not code first.
- Prefer editing the spec or plan over long patch-prompt threads when implementation drifts.
