# From commit to merge

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the change is built and verified and you want it committed, in a pull request, and merged. Each step is its own command. None of them runs the next one. Push and merge happen only after you say so in that turn.

## First prompt

```text
/crav1-finalize-commit
```

It drafts first, then offers commit, copy, change, or stop (1.83.0: there is no opening question).

Only want the message to paste into your own git client:

```text
/crav1-finalize-commit message only
```

`message only` drafts and shows the Summary and Description, then stops, the same as picking copy. A headless or bot run with no choice word ends the same way.

Commit in one go, with no questions (1.73.0):

```text
/crav1-finalize-commit commit now crav1
```

`commit now`, or just `commit` (1.76.1), drafts, shows the Summary and Description, then commits without the choice question. It never pushes. When `agent-tools/` or build output is in the file set, it warns and offers the normal choices instead. `crav1` (CRAV1 style) or `git log` (match the repo's log) answers the style question for this commit; a saved style rule still works as before.

Pull and check only, with no commit (1.81.0):

```text
/crav1-finalize-commit pull
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Commit style (first time) | Pick CRAV1 style or the style of this repo's git log, once or onward | Asked in the same question as the commit choice, with the message drafted in the recommended style. Onward writes a commit-style rule so you are not asked again. Delete the rule to choose again |
| Draft | — | Reads the diff, recent `git log`, the commit-style rule, and `docs/specs/<slug>/work-item.md` when it exists. Drafts a Summary and Description. A work item id becomes the last description line: `#<id>` on Azure Repos, `AB#<id>` on GitHub |
| Commit | Pick commit, copy, change, or stop | `/crav1-finalize-commit` offers commit first. After the commit, it checks the message, and when a host or tool added any trailer or line to that unpushed commit (Cursor, Claude Code, any `Co-authored-by`), strips it once and keeps the work item line. `/crav1-finalize-commit` commits only when you also asked for that in the same turn |
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

## Behind, conflicts, or a rejected push (1.66.0)

The kit's advice is always to merge the base branch into your branch, never to rebase it:

- `/crav1-merge-pr` stops when the branch is behind the base or has conflicts, and says: `Merge develop into feat/orders-retry (resolve any conflicts there), push, then ask to merge again.` On GitHub, **Update branch** with **Update with merge commit** does the same for a branch that is only behind.
- `/crav1-open-pr` shows the error when a push is rejected because the remote branch moved, and says to pull with `git pull --no-rebase`, resolve any conflicts, and push again. It never force-pushes.

The steps, when you want them:

```text
git switch develop
git pull --ff-only
git switch feat/orders-retry
git merge develop
git push
```

## Someone else pushed first (1.81.0)

After the commit, `/crav1-finalize-commit` fetches. It never pushes; it ends with `Ready to push.`

- **Behind:** it runs `git pull --no-rebase`, never a rebase. Conflicts in specs, system files and notes are resolved by the kit's rules: both sides' new lines are kept (yours first), each repo and branch keeps its newest `Synced at` line, and the note indexes are rebuilt rather than merged. Before the merge commit, it checks that every line either side added is still there. If one is missing, it does not commit.
- **A real disagreement:** when both sides changed the same line in different ways, you get one question: keep both (theirs becomes a `**Conflict:**` line under yours), mine, theirs, or stop.
- **Code files:** conflicts there stay with you, as before.
- **Not behind:** it checks any merge you have not pushed yet, including one you resolved by hand. A merge that kept your `**New:** Retries stop after 3 attempts` line but silently dropped the other side's `**New:** Retries back off for 30 seconds` line is listed, with restore / show me / stop.

`/crav1-finalize-commit pull` does the same without committing first. With uncommitted changes it stops and names `commit` instead.

## PR note (1.65.0)

`/crav1-open-pr` does not save the body it drafts: that is its own summary of the spec, plan and verify. After a confirmed merge, `/crav1-merge-pr` writes or updates the pull request's PR note in the specs repo (`docs/notes/YYYY-MM/YYYY-MM-DD-pr-<repo>-<n>.md`, its title and description, `kind: pull request`), with any edits made to the description since. It is not committed. A review with `/crav1-review-pr` writes the same note. From the specs repo, a pull request in another repo is reviewed with `/crav1-review-pr <repo> <n>`.

## After

After an outside pull request merges, `/crav1-review-pr` names `/crav1-refresh-system-notes` to catch the picture up: [Keep the picture current](from-refresh-system-notes.md).

Reference pages: [finalize-commit](reference/skills/crav1-finalize-commit.md) · [finalize-commit](reference/skills/crav1-finalize-commit.md) · [open-pr](reference/skills/crav1-open-pr.md) · [merge-pr](reference/skills/crav1-merge-pr.md)
