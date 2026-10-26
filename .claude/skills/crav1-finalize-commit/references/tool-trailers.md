# Known tool trailers (1.94.0)

The lines finalize-commit and the trailer hook strip. The hook `branches/message-only/assets/commit-msg.sh` holds the same list as patterns; keep the two in step. Everything not listed stays: `Signed-off-by`, a real person's `Co-authored-by`, the work-item mention and any other line. A tool missing here is added in a later release.

| Tool | Line (any name, case-insensitive) |
|---|---|
| Cursor | `Co-authored-by: … <cursoragent@cursor.com>` or `<…cursor[bot]@users.noreply.github.com>`; `Made-with: Cursor` |
| Claude Code / Anthropic | `Co-Authored-By: … <…@anthropic.com>` or `<…claude[bot]@users.noreply.github.com>`; `🤖 Generated with [Claude Code](…)`; `Claude-Session: …` |
| GitHub Copilot | `Co-authored-by: … <…Copilot@users.noreply.github.com>`, `copilot[bot]`, `copilot-swe-agent[bot]`, `copilot@github.com` |
| Aider | `Co-authored-by: aider (<model>) <aider@aider.chat>` (also `noreply@aider.chat`, `noreply@aider.dev`, `aider-chat-bot`) |
| OpenAI Codex | `Co-authored-by: Codex <…codex@users.noreply.github.com>`, `chatgpt-codex-connector[bot]`, `openai-codex[bot]`, `noreply@openai.com`, `codex@openai.com` |
| Gemini | `gemini-code-assist` / `gemini-code-assist[bot]` noreply, `gemini@google.com` |
| Jules | `google-labs-jules[bot]` noreply, `jules@google.com` |
| Devin | `devin-ai-integration[bot]` noreply, `devin@cognition.ai`, `bot@devin.ai` |
| Windsurf / Codeium | `…@codeium.com` |
| Amazon Q | `amazon-q-developer[bot]` noreply |
| Cline | `cline[bot]` noreply, `cline@cline.ai` |
| Sourcegraph Amp | `Co-authored-by: Amp <amp@ampcode.com>`, `noreply@sourcegraph.com`; `Amp-Thread-ID: …` |
| JetBrains AI | `jetbrains-ai[bot]` noreply |

Not stripped: Aider's optional `aider: ` subject prefix (part of the subject, not a line), and `Signed-off-by` from any source.
