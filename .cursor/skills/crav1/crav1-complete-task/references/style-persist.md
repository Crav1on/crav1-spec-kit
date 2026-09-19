# Persist commit style (complete-task / complete-tasks)

Same files as `/crav1-finalize-commit` / `/crav1-draft-commit-message`. After this, **every** later draft in this repo uses that style until they delete the rule file.

If a persist rule already exists (`.cursor/rules/draft-commit-style.mdc` or `draft-commit-gitlog.mdc`, or legacy `gitkraken-commit-*.mdc`): **do not ask**. Use it.

If none exists: **do not start implement**. Ask (questions tool OK). Only these two (both write a rule — there is no “this run only”):

| Id | Choice | Disk |
| --- | --- | --- |
| `onward` | `style.md`, this commit and onward | Write `draft-commit-style.mdc` from `crav1-draft-commit-message` `assets/draft-commit-style.mdc`. Delete any git-log persist (including legacy). |
| `log-onward` | Git log, this commit and onward | Write `draft-commit-gitlog.mdc` from that skill’s `assets/`. Delete any style.md persist (including legacy). |

Templates: drop-in `.cursor/skills/crav1/crav1-draft-commit-message/assets/` or plugin sibling `skills/crav1-draft-commit-message/assets/`.

Tell them they undo by deleting that rule file.
