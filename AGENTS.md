# Agent instructions for this repo

This repository is a **process guide** for spec-driven development in Cursor, not an application.

- Do not scaffold an app unless the user explicitly asks for one.
- Keep the README accurate against current Cursor docs when you update it.
- Put per-change work under `docs/specs/<change-id>/` using `_template/` (human starter). Skills also carry copies in their `assets/`; keep both in sync.
- Keep [docs/install.md](docs/install.md) and [plugins/crav1/README.md](plugins/crav1/README.md) current when install or first-run steps change.
- When adding or updating a crav1 skill/agent, edit `.cursor/skills/crav1/crav1-<name>/` (agents: `.cursor/agents/crav1-<name>.md`, templates: that skill’s `assets/` and `.cursor/agent-assets/crav1-<name>/`), then run `scripts/sync-crav1-plugin.sh` so `plugins/crav1/` matches. See `.cursor/rules/crav1-self-contained-skills.mdc`.
- From a one-sentence spark, use `/crav1-spark-to-spec` then `/crav1-tighten-spec`. Do not code first.
- From a pile of ideas plus technical hunches, use `/crav1-ideas-to-spec` (diagrams + ADRs + chosen export). Do not code first.
- Critique with `/crav1-architecture-reviewer`, then `/crav1-tighten-spec` one issue at a time.
- After tightening, `/crav1-resolve-questions` to keep or answer each remaining Open question.
- When the spec is accepted, `/crav1-plan-from-spec` writes `plan.md` and `tasks.md`. Do not code in that step.
- Build with `/crav1-implement-task` (one `T#` per turn). Prove the slice with `/crav1-verify-spec`.
- After `/crav1-verify-spec`, `/crav1-fix-from-verify` with **no Gap** walks the inner-loop queue: verify failed → claimed/unverified → `G#`. Not unimplemented tasks. Do not edit `spec.md`. `/crav1-fix-live` is the same queue with a live-path hint.
- Prefer editing the spec or plan over long patch-prompt threads when implementation drifts.
- For a paste-ready GitKraken Summary/Description, `/crav1-draft-commit-message`. It asks `style.md` vs live git log, this commit only vs onward (writes `draft-commit-style.mdc` or `draft-commit-gitlog.mdc`; delete that file to undo). Do not commit unless they asked. To change the wording and then optionally `git commit` (no push), `/crav1-review-commit`.
