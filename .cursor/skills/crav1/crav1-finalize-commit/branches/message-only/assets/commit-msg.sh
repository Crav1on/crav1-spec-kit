#!/bin/sh
# Written by /crav1-finalize-commit (CRAV1 Spec Kit). Strips known tool
# trailers from every commit message. Every other line stays, including
# Signed-off-by and a real person's Co-authored-by (1.94.0).
# This file is the single list of known tool trailers; finalize-commit's
# added-lines check reads the same list (references/tool-trailers.md lists
# the sources). Turn on: git config core.hooksPath .githooks
# Undo: git config --unset core.hooksPath (and delete .githooks/commit-msg).
msg="$1"
[ -f "$msg" ] || exit 0
tmp="$msg.crav1.$$"
# Known tool lines (case-insensitive, whole line):
#   Co-authored-by: <any name> <tool email>, tool emails:
#     cursoragent@cursor.com, cursor[bot]                    (Cursor)
#     any @anthropic.com, claude[bot]                        (Claude Code, Anthropic)
#     Copilot, copilot[bot], copilot-swe-agent[bot], copilot@github.com (GitHub Copilot)
#     aider@aider.chat, noreply@aider.chat, noreply@aider.dev, aider-chat-bot (Aider)
#     codex, chatgpt-codex-connector[bot], openai-codex[bot], noreply@/codex@openai.com (OpenAI Codex)
#     gemini-code-assist(-[bot]), gemini@google.com          (Gemini)
#     google-labs-jules[bot], jules@google.com               (Jules)
#     devin-ai-integration[bot], devin@cognition.ai, bot@devin.ai (Devin)
#     any @codeium.com                                       (Windsurf / Codeium)
#     amazon-q-developer[bot]                                (Amazon Q)
#     cline[bot], cline@cline.ai                             (Cline)
#     amp@ampcode.com, noreply@sourcegraph.com               (Sourcegraph Amp)
#     jetbrains-ai[bot]                                      (JetBrains AI)
#   Made-with: Cursor                                        (Cursor)
#   ... Generated with [Claude Code](...)                    (Claude Code)
#   Claude-Session: <url>                                    (Claude Code web)
#   Amp-Thread-ID: <url>                                     (Sourcegraph Amp)
gh='users\.noreply\.github\.com'
grep -v -i -E \
  -e '^co-authored-by:.*<(cursoragent@cursor\.com|[^>@]*@anthropic\.com|[^>@]*@aider\.(chat|dev)|(noreply|codex)@openai\.com|(gemini|jules)@google\.com|copilot@github\.com|[^>@]*@codeium\.com|devin@cognition\.ai|bot@devin\.ai|amp@ampcode\.com|noreply@sourcegraph\.com|cline@cline\.ai)>[[:space:]]*$' \
  -e "^co-authored-by:.*<([0-9]+\+)?((copilot|codex|gemini-code-assist|aider-chat-bot)|(cursor|claude|copilot|copilot-swe-agent|chatgpt-codex-connector|openai-codex|gemini-code-assist|google-labs-jules|devin-ai-integration|amazon-q-developer|cline|jetbrains-ai)\[bot\])@$gh>[[:space:]]*\$" \
  -e '^made-with:[[:space:]]*cursor[[:space:]]*$' \
  -e 'generated with \[claude code\]' \
  -e '^(claude-session|amp-thread-id):' \
  "$msg" | awk '{ l[NR] = $0 } END { n = NR; while (n > 0 && l[n] ~ /^[[:space:]]*$/) n--; for (i = 1; i <= n; i++) print l[i] }' > "$tmp" || { rm -f "$tmp"; exit 0; }
cat "$tmp" > "$msg"
rm -f "$tmp"
exit 0
