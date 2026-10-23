# crav1-open-pr: after

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## After it exists

When the host returned a pull request URL, print that URL and `base` ← `head`.

**PR number (1.75.0).** With that URL, add ` (PR <n>)` to the head's own Match `Branch:` line (replace an older `(PR …)`; on an old `; `-joined line, to the head's entry). When the head is `feat/<slug>` or `spec/<slug>` and is not listed, add `- Branch: <head> (PR <n>)` under `## Match` in sorted place (repo, then branch, 1.86.0), creating that heading at the end when missing. No spec: write nothing. Do not commit; say the file changed.

One sentence: they can review when they want. Next (optional): `/crav1-review-pr` when they name this pull request in a later turn (from the specs repo, a pull request in another repo is `/crav1-review-pr <repo> <n>`, 1.65.0). This skill does not save a PR note: the body is its own summary of the spec, plan and verify; `/crav1-review-pr` and `/crav1-merge-pr` save the description, with any later edits, as the PR note. This skill does not run that command. Merging stays `/crav1-merge-pr` when they explicitly ask, in a later turn, to merge this named pull request. A review is not that ask. This skill does not merge, and it does not delete the branch. Do not run `/crav1-review-pr` or `/crav1-merge-pr` from this step.

When you only printed commands, stop after those commands. Do not invent a URL.
