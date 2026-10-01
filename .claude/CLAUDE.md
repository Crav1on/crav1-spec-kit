# crav1 kit

Specs, not chat history, are the source of truth. Put change work under `docs/specs/<change-id>/`. Multi-feature intake landscape lives under `docs/system/`.

Type `/crav1` to list kit skills. Typical order: spark, ideas, or intake → feature branch (`feat/<slug>` or specify-only `spec/<slug>`) → architecture review → tighten → resolve questions → plan → review-plan → tighten-plan → implement (or `/crav1-complete-task` / `/crav1-complete-tasks` / `/crav1-complete-features`) → verify → fix-from-verify (do not edit `spec.md` in the fix loop). `/crav1-spark-to-spec` is greenfield, a brownfield feature, or a later feature on `docs/system/` (new slug unless they extend). `/crav1-intake-to-specs` writes the landscape plus one spec per v0 feature.

Do not scaffold an application unless the user asked for one. Prefer editing the spec or plan when implementation drifts.

Full install paths: `docs/install.md` in the kit repo. After a plugin install, start with the plugin README.

On Claude Code this file is the project instruction (`.claude/CLAUDE.md`). A user-scope install uses the same text in `~/.claude/CLAUDE.md` and does not commit the kit into a client repo. Playbook paths that start with `.claude/` are the project drop-in. If that file is not in the repo, read the same path under `~/.claude/`.
