# Agent instructions for this repo

This repository is a **process guide** for spec-driven development in Cursor, not an application.

- Do not scaffold an app unless the user explicitly asks for one.
- Keep the README accurate against current Cursor docs when you update it.
- Put per-change work under `docs/specs/<change-id>/` using `_template/`.
- From a one-sentence spark, use `/spark-to-spec` then `/tighten-spec`. Do not code first.
- From a pile of ideas plus technical hunches, use `/ideas-to-spec` (diagrams + ADRs + chosen export). Do not code first.
- Critique with `/architecture-reviewer`, then `/tighten-spec` one issue at a time.
- After tightening, `/resolve-questions` to keep or answer each remaining Open question.
- When the spec is accepted, `/plan-from-spec` writes `plan.md` and `tasks.md`. Do not code in that step.
- Build with `/implement-task` (one `T#` per turn). Prove the slice with `/verify-spec`.
- Prefer editing the spec or plan over long patch-prompt threads when implementation drifts.
