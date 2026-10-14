# Persist commit style (build-tasks / build-tasks)

Same files as `/crav1-finalize-commit` / the message only branch of `/crav1-finalize-commit`. After this, **every** later draft in this repo uses that style until they delete the rule file.

If a persist rule already exists, **do not ask**. Use it. Cursor and Claude Code both count.

- Cursor: `.cursor/rules/draft-commit-style.mdc` or `.cursor/rules/draft-commit-gitlog.mdc` (legacy `.cursor/rules/gitkraken-commit-style.mdc` or `.cursor/rules/gitkraken-commit-gitlog.mdc`)
- Claude Code project: `.claude/rules/draft-commit-style.md` or `.claude/rules/draft-commit-gitlog.md` (legacy `.claude/rules/gitkraken-commit-style.md` or `.claude/rules/gitkraken-commit-gitlog.md`)
- Claude Code user: `~/.claude/rules/draft-commit-style.md` or `~/.claude/rules/draft-commit-gitlog.md` (legacy `~/.claude/rules/gitkraken-commit-style.md` or `~/.claude/rules/gitkraken-commit-gitlog.md`)

If none exists: **do not start implement**. Ask (questions tool OK). Only these two (both write a rule — there is no “this run only”):

| Id | Choice | Disk |
| --- | --- | --- |
| `onward` | CRAV1 style, this commit and onward | Write the style rule from the message only branch of `crav1-finalize-commit` `assets/draft-commit-style.mdc`. Cursor: `.cursor/rules/draft-commit-style.mdc`. Claude Code project: `.claude/rules/draft-commit-style.md`. Claude Code user, when the kit is not in this repo’s git: `~/.claude/rules/draft-commit-style.md`. Delete any git-log persist (including legacy). |
| `log-onward` | Git log, this commit and onward | Write the git-log rule from that skill’s `assets/draft-commit-gitlog.mdc`. Cursor: `.cursor/rules/draft-commit-gitlog.mdc`. Claude Code project: `.claude/rules/draft-commit-gitlog.md`. Claude Code user, when the kit is not in this repo’s git: `~/.claude/rules/draft-commit-gitlog.md`. Delete any CRAV1 style persist (including legacy). |

Templates: drop-in `.cursor/skills/crav1/crav1-finalize-commit/branches/message-only/assets/` or plugin sibling `skills/crav1-finalize-commit/branches/message-only/assets/`. Claude Code reads the same assets from `.claude/skills/crav1-finalize-commit/branches/message-only/assets/` or `~/.claude/skills/crav1-finalize-commit/branches/message-only/assets/`.

Tell them they undo by deleting that rule file.
