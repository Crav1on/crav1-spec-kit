# crav1-open-pr: checks

Read every run, before the draft, when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

## Checks (before the draft)

Run these first. Abort in one short message. Do not commit, stash, or check out.

| Condition | Stop |
| --- | --- |
| Not a git repo | Say so. |
| Detached HEAD (`git branch --show-current` empty) and they did not name an existing local head | There is no branch to open from. |
| Dirty tree | `git status --porcelain`, ignoring `agent-tools/`. Point them at `/crav1-finalize-commit`. This skill does not commit. |
| Head has no commits ahead of base | `git rev-list --count <base-ref>..<head>` is 0. Name the refs. Nothing to open. |
| Head branch does not exist locally | Ask for a local branch name. Do not create one. |

Compare against `refs/remotes/<remote>/<base>` when that ref exists, otherwise the local `<base>` branch. If neither ref exists, ask them to name the base. Do not treat a missing ref as “zero commits ahead.”

`agent-tools/` left dirty is fine. Mention that those paths stay uncommitted.

If the current branch **is** the base, ask for the head. Do not open a pull request of the default branch into itself.

If base or head is still ambiguous, that turn is the question only. No title, no body, no push menu.
