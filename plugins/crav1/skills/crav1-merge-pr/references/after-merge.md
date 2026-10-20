# crav1-merge-pr: after merge

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## After it merged

Report the merge commit hash, the title, and `source` → `target`. Repeat the strategy: merge commit. On Azure DevOps, also say the merge commit has two parents. Reach this section only after that check passes.

When you only printed commands, stop after those commands. Do not invent a hash.

**Spec branches (1.64.0).** After a confirmed merge, when the source branch is a work branch of one or more specs (named in a spec's `Synced at` entries, Match `Branch:` list or task `(branch: …)` parts, in this repo or in the sibling spec repo `/crav1-open-pr` finds), say once per spec: `<n> of <m> branches of <slug> now merged into <target>`, counted with the merged tests in `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`). When that was the last one: `<slug> is now merged across all its branches; run /crav1-verify-build-against-spec`. A branch several specs list is reported under each, and counted once per spec. **Sub-branches and reverts (1.68.0):** when the source branch carries `(into <spec branch>)` and the target is that spec branch, say `<n> of <m> sub-branches merged into <spec branch>` instead, with `left behind: <branch> (not in <spec branch>)` for any that never merged once the spec branch has reached the base; sub-branches never count toward the `<n> of <m> branches` line, and after the spec branch merges into the base you give the normal done line. A merged branch of the spec whose change was later reverted on the base shows `<branch>: merged, reverted on <base> (<revert sha>)`; report only, it doesn't change the done line. Both follow that file under **Spec branch and sub-branches** and **Reverted**. **Promotion (1.69.0).** When the spec repo has `docs/environments/promotion.md`, add the `Promotion:` line after the after-merge line, as `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`) says under **Promotion**: per repo, the furthest environment reached and each later one not yet reached, as `on the branch that deploys to <env> (<branch>)` or `not yet on the branch that deploys to <env> (<branch>)`, release patterns as `on release/<x> (deploys to <env>)`, tag lines as `in tag <tag> (deploys to <env>)` or `not yet tagged`, the chain at the end, `Unclear:` for an unknown word with no `(after …)`, and `<branch>: not back on <base>` for a release fix. Branch reach, never `deployed to`. When a pipeline-sourced line is behind it, end with **Also check the latest pipeline runs?** (**Check pipeline runs** / **No, keep the git answer**); the choice word `pipeline runs` runs the check without asking; headless without it gives the git answer plus `Pipeline runs not checked. Add the word: pipeline runs.` Azure DevOps only, read-only; `az has no login` keeps the git answer. Report only: done stays merged into the base. Read-only: no file edits, no fetch, no status change.

**PR note (1.65.0).** After a confirmed merge, write or reuse the pull request's **PR note** in the specs repo, as `crav1-add-to-spec` `references/notes.md` **PR note** says (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/notes.md`; plugin: sibling `skills/crav1-add-to-spec/references/notes.md`): one note per pull request, `kind: pull request`, `source: PR <n> <repo URL path>`, filed by its created date (`createdAt`, or `creationDate` from the re-read), the description from the read above, a new `## Description as of <date>` section only when the description changed, `State on <date>: merged`, the personal-data and secrets check, and the four image options. A pull request that `/crav1-open-pr` made gets one too. The specs repo is this checkout when it has `docs/specs/`, else the workspace folder with `docs/specs/`, else a sibling `../*/docs/system/repos.md` with a row for this repo; write the note there, never commit it, and name its full path: `PR note: <full path> (written | reused | updated)`. When no specs repo is found, print the note with the path it would have. Run the notes index generator after the note changes. Name `/crav1-finalize-commit` for that note; do not run it.

## Local main

Run this only after a confirmed merge commit. On Azure DevOps that includes a completed pull request whose merge commit has two parents, counted with `git rev-list` or, when git cannot see the commit, the commits API. If that check stopped the skill, do not fast-forward.

When the working tree is clean, fast-forward local `main`:

```text
git checkout main && git pull --ff-only
```

Clean means `git status --porcelain` is empty, ignoring `agent-tools/`. If anything else is dirty, skip the checkout and say so. The merge on the host still stands.

When the pull request target is not `main`, use that target branch name in the same two commands. If the local branch does not exist, say so. Do not create it. If the pull is not a fast-forward, show the error. Do not `reset`, rebase, or force.

## Branches

Do not delete the remote branch or the local branch unless the user asked in this turn. No `--delete-branch`. No `deleteSourceBranch`. If the user asked, delete only the source branch named in that ask: `git branch -d <branch>` and, when the user asked for the remote, `git push <remote> --delete <branch>`. Do not use `git branch -D` unless the user asked to force.

## Tracker

Tracker-neutral. Do not change work-item links.

Do not read or write `work-item.md`. Do not pass `--work-items` or `--transition-work-items`. Do not call `az repos pr work-item`. Do not set `transitionWorkItems`. Do not edit the pull request title or description.
