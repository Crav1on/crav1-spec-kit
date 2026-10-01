#!/usr/bin/env bash
# Generate .claude/ from the Cursor drop-in, or fail if the committed tree is stale.
# Maintainer entry point is scripts/sync-crav1-plugin.sh, which calls this.
# Check: scripts/sync-crav1-claude.sh --check
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/sync-crav1-claude.py" --root "$ROOT" "$@"
