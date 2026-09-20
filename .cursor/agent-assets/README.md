Templates for **crav1** subagents (`crav1-spec-reviewer`, `crav1-architecture-reviewer`, `crav1-plan-reviewer`, `crav1-intake-slice`). Do not put these files under `.cursor/agents/` or `plugins/crav1/agents/` — those directories are only for agent prompts (YAML frontmatter + name).

This folder is mirrored to `plugins/crav1/agent-assets/`. When you change a template, update `docs/specs/_template/` and `docs/system/_template/`, every skill `assets/` copy, and both agent-assets trees (`scripts/sync-crav1-plugin.sh`).
