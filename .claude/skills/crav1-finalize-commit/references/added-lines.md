# Added lines

Read after a successful commit when HEAD's message has any line the draft did not have (commit step 6).

Rule: the final commit message is exactly the drafted Summary + Description, nothing more. finalize-commit writes no trailers, so any trailer or extra line is someone else's: a host, an agent, a hook or a tool. Examples: `Co-authored-by: Cursor <cursoragent@cursor.com>`, `Made-with: Cursor`, `🤖 Generated with [Claude Code](https://claude.com/claude-code)`, `Co-Authored-By: Claude <noreply@anthropic.com>`, and any other `Co-authored-by:`, `Signed-off-by:` or `Generated with` line. The list is examples only; compare against the draft, not against names.

A last line of `#<id>` or `AB#<id>` that the draft has is the work-item mention. Keep it.

1. Tell them in one short sentence which lines were added and that they were not part of the message they accepted.
2. **Strip them once** when this process created HEAD and HEAD is not pushed.
   - `git commit --amend --no-verify` with **exactly** the drafted Summary + Description (same `-m` / HEREDOC as the original commit). When the Description ends with the work-item mention, that line stays the last line.
   - Read `git log -1 --format=%B` again. If it matches the draft, show the clean hash/message, then the optional `/crav1-open-pr` line from the commit steps. Do not amend again.
   - If lines **came back**, the tool wraps `git commit` itself. Do not loop amend. Stop, name the lines, and tell them to turn that tool's attribution off, then run the skill again.
3. HEAD already pushed, or not made by this process: do not amend. Name the lines and stop.
4. How to stop it on future commits: Cursor Settings → **Git & PRs → Attribution** (older: **Agent → Attribution**), or `attribution.attributeCommitsToAgent` false in `~/.cursor/cli-config.json`; cloud agents may still add it. Claude Code: `"includeCoAuthoredBy": false` in `settings.json`. Other tools: their own attribution or sign-off setting.
5. Do not install a `prepare-commit-msg` hook unless they ask.
