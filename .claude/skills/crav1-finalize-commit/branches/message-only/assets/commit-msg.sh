#!/bin/sh
# Written by /crav1-finalize-commit (CRAV1 Spec Kit). Strips known tool
# trailers from every commit message. Human Co-authored-by lines stay.
# This file is the single list of known tool trailers; finalize-commit's
# added-lines check reads the same list. Turn on: git config core.hooksPath .githooks
# Undo: git config --unset core.hooksPath (and delete .githooks/commit-msg).
msg="$1"
[ -f "$msg" ] || exit 0
tmp="$msg.crav1.$$"
# Known tool trailers (case-insensitive, whole line):
#   Co-authored-by: Cursor <cursoragent@cursor.com>   (Cursor)
#   Made-with: Cursor                                  (Cursor)
#   Generated with [Claude Code](https://claude.com/claude-code)  (Claude Code)
#   Co-Authored-By: Claude <noreply@anthropic.com>     (Anthropic, any @anthropic.com)
grep -v -i -E \
  -e '^co-authored-by:.*<(cursoragent@cursor\.com|[^>]*@anthropic\.com)>[[:space:]]*$' \
  -e '^made-with:[[:space:]]*cursor[[:space:]]*$' \
  -e 'generated with \[claude code\]' \
  "$msg" | awk '{ l[NR] = $0 } END { n = NR; while (n > 0 && l[n] ~ /^[[:space:]]*$/) n--; for (i = 1; i <= n; i++) print l[i] }' > "$tmp" || { rm -f "$tmp"; exit 0; }
cat "$tmp" > "$msg"
rm -f "$tmp"
exit 0
