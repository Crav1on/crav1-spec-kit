# Persist commit style (complete-task / complete-tasks)

Same files as `/crav1-finalize-commit` / `/crav1-draft-commit-message`. After this, **every** later draft in this repo uses that style until they delete the rule file.

If a persist rule already exists, **do not ask**. Use it.

- Claude Code project: `.claude/rules/draft-commit-style.md` or `.claude/rules/draft-commit-gitlog.md` (legacy `.claude/rules/gitkraken-commit-style.md` or `.claude/rules/gitkraken-commit-gitlog.md`)
- Claude Code user: `~/.claude/rules/draft-commit-style.md` or `~/.claude/rules/draft-commit-gitlog.md` (legacy `~/.claude/rules/gitkraken-commit-style.md` or `~/.claude/rules/gitkraken-commit-gitlog.md`)

If none exists: **do not start implement**. Ask (questions tool OK). Only these two (both write a rule — there is no “this run only”):

| Id | Choice | Disk |
| --- | --- | --- |
| `onward` | CRAV1 style, this commit and onward | Write the style rule from `crav1-draft-commit-message` `assets/draft-commit-style.mdc`. Claude Code project: `.claude/rules/draft-commit-style.md`. Claude Code user, when the kit is not in this repo’s git: `~/.claude/rules/draft-commit-style.md`. Delete any git-log persist (including legacy). |
| `log-onward` | Git log, this commit and onward | Write the git-log rule from that skill’s `assets/draft-commit-gitlog.mdc`. Claude Code project: `.claude/rules/draft-commit-gitlog.md`. Claude Code user, when the kit is not in this repo’s git: `~/.claude/rules/draft-commit-gitlog.md`. Delete any CRAV1 style persist (including legacy). |

Templates: drop-in `.claude/skills/crav1-draft-commit-message/assets/` or plugin sibling `skills/crav1-draft-commit-message/assets/`. Claude Code reads the same assets from `.claude/skills/crav1-draft-commit-message/assets/` or `~/.claude/skills/crav1-draft-commit-message/assets/`.

Tell them they undo by deleting that rule file.
