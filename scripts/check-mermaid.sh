#!/usr/bin/env bash
# 1.110.0: every mermaid block in templates, skill assets/references and test goldens must parse (mermaid 11.4.1).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mapfile -t files < <(git ls-files '*.md' | grep -E '^(docs/.*/_template/|\.cursor/skills/|\.cursor/agent-assets/|scripts/tests/goldens/)' | xargs grep -l '^```mermaid' || true)
[ ${#files[@]} -gt 0 ] || { echo "no mermaid blocks found"; exit 1; }
[ -d scripts/mermaid/node_modules/mermaid ] || (cd scripts/mermaid && npm install --silent --no-audit --no-fund >/dev/null)
node scripts/mermaid/check-mermaid.mjs "${files[@]}"
