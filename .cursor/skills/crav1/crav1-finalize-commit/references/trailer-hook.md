# Trailer hook (1.90.0)

A one-time offer: a committed `commit-msg` hook that strips the known tool trailers on every commit, including from tools that ignore their own attribution setting.

## When to ask

Before the choices prompt, check in this order:

1. A saved answer exists. Cursor: `.cursor/rules/trailer-hook.mdc`. Claude Code project: `.claude/rules/trailer-hook.md`. Claude Code user: `~/.claude/rules/trailer-hook.md` (same project/user rule as the style rule in the message only branch).
   - `Answer: no`: do not ask. Done.
   - `Answer: yes`: go to step 2 without asking.
2. `.githooks/commit-msg` exists in the repo and `git config core.hooksPath` is not `.githooks`: run `git config core.hooksPath .githooks` (a teammate's first run) and say so in one line. Do not ask.
3. `.githooks/commit-msg` exists and `core.hooksPath` is `.githooks`: nothing to do.
4. No saved answer and the hook is missing or not turned on: add one question to the same choices prompt.

Never a separate prompt and never before the paste blocks. A headless or bot run with no person does not ask and writes nothing.

## The question

`Strip tool trailers on every commit for this repo?` Options: `strip trailers` (recommended) / `keep trailers`. Both are choice words; typed in the invocation they answer it without asking.

## On `strip trailers`

1. Copy [../branches/message-only/assets/commit-msg.sh](../branches/message-only/assets/commit-msg.sh) to `.githooks/commit-msg`, unchanged, and make it executable (`chmod +x`, and `git update-index --chmod=+x` once it is staged).
2. Run `git config core.hooksPath .githooks`. When `core.hooksPath` already points at another folder, do not change it: say so and leave the hook file for them to wire up.
3. Write the saved answer from [../branches/message-only/assets/trailer-hook.mdc](../branches/message-only/assets/trailer-hook.mdc) with `Answer: yes`.
4. Do this before the commit step, so this commit is already clean.
5. Commit the hook with this commit (1.90.6), so teammates get it: on `commit`, stage `.githooks/commit-msg` and the saved answer when it is a project rule in the repo (`.cursor/rules/trailer-hook.mdc` or `.claude/rules/trailer-hook.md`, never `~/.claude/`) together with the commit's files, and name them in the result. Add them by path only (`git add -- .githooks/commit-msg <rule file>`), never `git add -A`, `-u` or `.`, so no other unstaged file joins the commit (1.91.0). The drafted message stays as it is. On `copy`, `stop`, or `message only`, nothing is committed: say the two files are ready to commit.

## On `keep trailers`

Write the saved answer with `Answer: no`. No hook, no config change.

## The list

The hook file is the single list of known tool trailers: Cursor (`Co-authored-by: Cursor <cursoragent@cursor.com>`, `Made-with: Cursor`), Claude Code (`Generated with [Claude Code](...)`), and Anthropic (`Co-Authored-By: Claude <...@anthropic.com>`). [added-lines.md](added-lines.md) names these from the same file. Any other `Co-authored-by:` line, such as a real person, stays.
