# Added lines

Read after a successful commit when HEAD's message has any line the draft did not have (commit step 6).

Rule: the final commit message is the drafted Summary + Description plus any added line that is not a known tool trailer. finalize-commit writes no trailers, so any extra line is someone else's: a host, an agent, a hook or a tool. The known tool trailers are listed in [tool-trailers.md](tool-trailers.md) and, as patterns, in the trailer hook `branches/message-only/assets/commit-msg.sh` (1.94.0). Only those are stripped. `Signed-off-by`, a real person's `Co-authored-by:` and any other line stay: name them and do not remove them.

A last line of `#<id>` or `AB#<id>` that the draft has is the work-item mention. Keep it.

1. Tell them in one short sentence which lines were added and that they were not part of the message they accepted.
2. **Strip them once** when this process created HEAD and HEAD is not pushed.
   - `git commit --amend` with the drafted Summary + Description (same `-m` / HEREDOC as the original commit) plus every added line that is not in [tool-trailers.md](tool-trailers.md), such as `Signed-off-by` or a real person's `Co-authored-by:`, in its original order. When the Description ends with the work-item mention, that line stays the last line.
   - Never add `--no-verify`: the repo's hooks, including the trailer hook `.githooks/commit-msg`, must run on the amend.
   - If a hook fails the amend, show the error and stop. Do not retry, and never retry with `--no-verify`.
   - Read `git log -1 --format=%B` again. If it matches the draft plus the kept lines, show the clean hash/message, then the optional `/crav1-open-pr` line from the commit steps. Do not amend again.
   - If lines **came back**, the tool wraps `git commit` itself. Do not loop amend. Stop, name the lines, and tell them to turn that tool's attribution off, then run the skill again.
3. HEAD already pushed, or not made by this process: do not amend. Name the lines and stop.
4. How to stop it on future commits. Only these tools document an off switch (checked October 2026):
   - Cursor: Settings → **Git & PRs → Attribution** (before 3.11: **Agent → Attribution**); CLI: `attribution.attributeCommitsToAgent` and `attribution.attributePRsToAgent` false in `~/.cursor/cli-config.json`. An enterprise admin setting can override it, and cloud agents may still add it. ([Git help](https://cursor.com/help/integrations/git), [CLI configuration](https://cursor.com/docs/cli/reference/configuration))
   - Claude Code: `"attribution": false` in `settings.json`; older versions: `attribution.commit` and `attribution.pr` set to `""` and `attribution.sessionUrl` false. `includeCoAuthoredBy` is deprecated. ([Settings](https://code.claude.com/docs/en/settings-reference))
   - Copilot in VS Code: `git.addAICoAuthor` set to `off` (the default). ([Commits](https://code.visualstudio.com/docs/sourcecontrol/staging-commits))
   - Aider: `--no-attribute-co-authored-by`, and `--no-attribute-author` and `--no-attribute-committer` for the `(aider)` name. ([Options](https://aider.chat/docs/config/options.html))
   - Amp: `amp.git.commit.coauthor.enabled` and `amp.git.commit.ampThread.enabled` false in `settings.json`. ([Settings](https://ampcode.com/docs/cli/settings))
   - Jules: Settings → **Commit Authoring** → **User only**. ([Changelog](https://jules.google/docs/changelog/2026-02-19/))
   - Devin: Settings → Preferences → **Git commit author** → **You only**; an enterprise setting can override it. ([GitHub integration](https://docs.devin.ai/integrations/gh))

   The other tools in the strip list (the Copilot cloud agent, Codex, Gemini, Windsurf, Amazon Q, Cline, JetBrains AI) document no off switch; rely on `strip trailers` and the trailer hook ([trailer-hook.md](trailer-hook.md)), which works for every tool.
5. Install no other hook. The trailer hook is installed only after `strip trailers`.
