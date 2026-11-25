#!/usr/bin/env bash
# Mirror drop-in .cursor/ kit files into plugins/crav1/. Plugin-only files are left alone.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/plugins/crav1"

# template copies: generated from docs/*/_template/ (1.107.0), before any mirror.
python3 "$ROOT/scripts/gen-template-copies.py"

mkdir -p "$PLUGIN/skills" "$PLUGIN/agents" "$PLUGIN/rules" "$PLUGIN/agent-assets"

# docs: the compact edition an install reads. Human pages stay in docs/.
# Cursor drop-in: .cursor/skills/crav1/crav1-docs/. The plugin mirror and the
# Claude Code drop-in copy that tree. Also writes repo-root llms.txt.
# CI fails when a copy or llms.txt drifts.
python3 "$ROOT/scripts/gen-compact-docs.py"
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

echo "Wrote compact crav1-docs/ and llms.txt, and synced .cursor/ → plugins/crav1/ (skills incl. crav1-docs, agents, crav1.mdc, agent-assets)"

# Claude Code drop-in is generated. A stale .claude/ fails CI via --check.
"$ROOT/scripts/sync-crav1-claude.sh"

# Codex and Copilot trees are generated. A stale vendors/ tree fails CI via --check.
python3 "$ROOT/scripts/sync-crav1-vendors.py" --root "$ROOT"
