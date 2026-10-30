# crav1-finalize-commit: base branch (1.99.0)

Read only when the pointer in `SKILL.md` sends you here. Implementation code is never committed on a base branch. The guard is skill `crav1-create-feature-branch`, `references/code-branch.md`.

## When it applies

HEAD is a base branch (the `Merges into` branch, the default branch, main, master, develop, `release/*`), the repo is not the exempt specs repo, and at least one staged path, or one path in the draft's file set when the index is empty, is implementation code (outside `docs/` and not a root Markdown file). A commit of only spec and doc files on a base is unchanged.

## The prompt

The `Commit this message?` prompt becomes `Commit on a work branch?`, with these options in this order:

1. `Create feat/<slug> from <into> and commit (Recommended)`. The slug is the spec the staged files belong to, else the draft subject in kebab case (at most five words). On `release/<x>`: `fix/<slug>`, and `(into release/<x>)` is written on its Match `Branch:` entry.
2. `Use an existing branch`: as the guard says (non-base branches, the spec's own first).
3. `Other name`: they name a work branch. A base name is refused.
4. `stop`: no commit. They can still copy the blocks.

`copy` and `change` still work when typed. This prompt replaces the commit question, so it is the same one prompt.

## Moving the changes

When HEAD is the into branch, `git switch -c <new>` moves the index and the working tree over, then follow the normal commit steps on `<new>`. Otherwise, or for an existing branch, switch only when git keeps the staged changes without conflict; when git refuses, say so, commit nothing and end as `copy`. Never stash unless they ask. Never commit on the base.

## Choice words

`commit` and `commit now` on a base ask this prompt instead of committing. `new branch` answers it with option 1. A headless run without `new branch` ends as `copy` with the guard's one stop line.
