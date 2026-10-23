# crav1-open-pr: open only

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.3; the rules are unchanged.

## Open only

Only after they pick `open` on the current draft.

1. `git ls-remote --heads <remote> <head>`. If it is missing, say the remote has no such branch. Do not create a pull request. They can pick **push and open PR**.
2. If the local head has commits that are not on that remote head, say so and **do not push**. The pull request would miss them. They can pick **push and open PR**, or stop.
3. Open one pull request (below). If one already exists for this head → base, print that URL instead.
