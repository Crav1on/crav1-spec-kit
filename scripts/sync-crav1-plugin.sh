#!/usr/bin/env bash
# Mirror drop-in .cursor/ kit files into plugins/crav1/. Plugin-only files are left alone.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/plugins/crav1"

mkdir -p "$PLUGIN/skills" "$PLUGIN/agents" "$PLUGIN/rules" "$PLUGIN/agent-assets"

# docs: every install carries this release's docs next to the skills, so
# /crav1-help answers locally for that exact version. Cursor drop-in:
# .cursor/skills/crav1/crav1-docs/; the plugin mirror and the Claude Code
# drop-in (.claude/skills/crav1-docs/) copy it from there. CI fails on drift.
rm -rf "$ROOT/.cursor/skills/crav1/crav1-docs"
mkdir -p "$ROOT/.cursor/skills/crav1/crav1-docs"
cp -a "$ROOT/docs/." "$ROOT/.cursor/skills/crav1/crav1-docs/"
rm -rf "$PLUGIN/docs"

# skills: replace tree
rm -rf "$PLUGIN/skills"
mkdir -p "$PLUGIN/skills"
cp -a "$ROOT/.cursor/skills/crav1/." "$PLUGIN/skills/"

# agents: crav1-*.md only
find "$PLUGIN/agents" -maxdepth 1 -type f -name 'crav1-*.md' -delete
cp -a "$ROOT/.cursor/agents/"crav1-*.md "$PLUGIN/agents/"

# consumer usage rule only (not kit-maintainer.mdc)
rm -f "$PLUGIN/rules/crav1.mdc"
cp -a "$ROOT/.cursor/rules/crav1.mdc" "$PLUGIN/rules/crav1.mdc"

# agent-assets: replace tree (includes README)
rm -rf "$PLUGIN/agent-assets"
mkdir -p "$PLUGIN/agent-assets"
cp -a "$ROOT/.cursor/agent-assets/." "$PLUGIN/agent-assets/"

echo "Synced docs/ → .cursor/skills/crav1/crav1-docs/, and .cursor/ → plugins/crav1/ (skills incl. crav1-docs, agents, crav1.mdc, agent-assets)"

# Claude Code drop-in is generated. A stale .claude/ fails CI via --check.
"$ROOT/scripts/sync-crav1-claude.sh"
