# From commit to merge

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the change is built and verified and you want it committed, in a pull request, and merged. Each step is its own command. None of them runs the next one. Push and merge happen only after you say so in that turn.

## First prompt

```text
/crav1-finalize-commit
```

Only want the message to paste into your own git client:

```text
/crav1-finalize-commit
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Commit style (first time) | Pick CRAV1 style or the style of this repo's git log, once or onward | That turn is the style question only. Onward writes a commit-style rule so you are not asked again. Delete the rule to choose again |
| Draft | — | Reads the diff, recent `git log`, the commit-style rule, and `docs/specs/<slug>/work-item.md` when it exists. Drafts a Summary and Description. A work item id becomes the last description line: `#<id>` on Azure Repos, `AB#<id>` on GitHub |
| Commit | Pick commit, copy, edit, rewrite, or stop | `/crav1-finalize-commit` offers commit first. After the commit, it checks the message, and when the host added an attribution trailer to that unpushed commit, strips it once and keeps the work item line. `/crav1-finalize-commit` commits only when you also asked for that in the same turn |
| Pull request | `/crav1-open-pr`, then pick push and open, open only, or stop | Shows the title and the body (what and why, spec links, verify, and a Work item section when `work-item.md` exists) before asking. Pushes only after an explicit yes. Opens one pull request against the default branch. Does not merge |
| Review (optional, later turn) | `/crav1-review-pr <pull request>` | Reads the diff against the spec, plan, and `verify.md`, and says whether it can ship. Writes nothing. See [From a pull request review](from-review-pr.md) |
| Merge (later turn) | `/crav1-merge-pr <pull request>` and say merge | Merges only when that turn asks. Always a merge commit: no squash, no rebase, no policy bypass. Stops when a required host check is red. Confirms two parents, then fast-forwards the local default branch when the tree is clean. Does not run the review |

A review is not a merge ask. Opening a pull request is not a merge ask either.

## What gets written

- The commit-style rule, when you pick onward.
- The git commit, when you pick commit.
- A push of the change branch and one pull request, after a yes.
- A merge commit on the host, when you ask to merge.

Not written: branch deletion, work item links, squash or rebase merges.

## After

After an outside pull request merges, `/crav1-review-pr` names `/crav1-keep-current` to catch the picture up: [Keep the picture current](from-keep-current.md).

Reference pages: [finalize-commit](reference/skills/crav1-finalize-commit.md) · [finalize-commit](reference/skills/crav1-finalize-commit.md) · [open-pr](reference/skills/crav1-open-pr.md) · [merge-pr](reference/skills/crav1-merge-pr.md)
