---
name: crav1-create-feature-branch
description: >-
  Use before specifying or building on a base branch (main, develop,
  release/*). Prompts for feat/<slug> or specify-only spec/<slug>, then
  creates or checks it out. Never checks out silently. Does not push or open a
  pull request.
disable-model-invocation: true
icon: git-branch
color: blue
---

# Feature branch

Get this change **off the default branch**. Prompt; do not silently `git checkout -b`. Do not push. Do not open a pull request unless they **explicitly** ask in this chat.

Other skills follow this file (this skill's `SKILL.md`). Standalone command: `/crav1-create-feature-branch`.

## Detect

Run git (PATH fallback if needed). If not a repo, skip.

- Current branch: `git branch --show-current`
- Base branches, work branches and the into branch: as [references/code-branch.md](references/code-branch.md) (1.99.0) says. The default branch is `origin/HEAD`, else `gh`, else `main`, else `master`
- Slug: from the spec folder they @, else the slug this specify pass is about to write, else ask
- Dirty: `git status --porcelain` ignoring `agent-tools/`

**Skip** (no prompt) when any of these is true:

- No git repo, or no commits yet (empty greenfield)
- Already on `feat/<slug>` or `spec/<slug>` for **this** slug
- Already on a **work branch** ([references/code-branch.md](references/code-branch.md)). Exception: they are on `spec/<slug>` and this is a **build** skill — see **Build on a spec-only branch**
- **Specify** prompt only: already on a non-default branch they chose (leave it)
- They already answered this prompt in this chat (`stay` / branch created)
- Parent passed `branch: already-done`

## Prompt (questions tool; first option is the default)

**Specify** (spark / ideas / intake, before writing spec files):

1. **`feat/<slug>`** — one branch for this spec **and** later build (default, **first/top**)
2. **`spec/<slug>`** — specify-only. Merge this to the default branch (PR in GitKraken or your git host when they want). Build later on `feat/<slug>` from that default so another feature can be specified while this one is built
3. **Stay** on the current branch
4. **Other** — they name the branch

Intake (several slugs): one branch for the dump. Slug = short landscape kebab, or `system` if unnamed. Options are `feat/<that>` vs `spec/<that>`.

**Build** (implement / build-tasks / fix-build-gaps, before the first code change or worker): follow [references/code-branch.md](references/code-branch.md) (1.99.0).

- On a **base branch** (main, master, develop, the `Merges into` branch, `release/*`): **Create `feat/<slug>` from `<into>` (Recommended)**, **Use an existing branch**, a typed branch name on this same card, **Stop**. No Stay on a base. There is no second card to collect the name (1.129.0).
- On **another** branch (`chore/x`, detached HEAD): the same, with **Stay on `<current>`** in place of the typed name.
- When the prompt is for a task, option 1 is that task's branch from [references/task-branch.md](references/task-branch.md), not a new name. The branch card is alone. Permissions are the next card.
- Headless with no person: stop before any code, unless the invocation has the choice word `new branch`.

Do not offer `spec/<slug>` on a build prompt.

**Task branch (1.129.0).** Follow [references/task-branch.md](references/task-branch.md). Option 1 is the branch `scripts/build_map.py --recommend T#` prints (skill `crav1-tasks-ready-to-build`), the same name as the build map row. On that branch already, no prompt. A base branch is still `blocked: branch X is a base branch`. A sub-branch is created from its parent only after a yes, and never from the default without asking. Another repo's branch is not built here. A picked name that is not the recommended one is written back as `(map: <picked>)` on that task, in the specs repo, and not committed.

If the working tree is dirty (other than `agent-tools/`), **do not checkout** an existing branch. On a base branch, creating the new branch from HEAD with `git switch -c` carries the changes over (see the reference); never send a dirty base tree to `/crav1-finalize-commit`. Otherwise tell them to commit on their branch or stash themselves. Re-ask branch after the tree is clean.

## Checkout

Only after they pick a branch name that is not “stay”:

```text
git checkout -b <name>
```

On a base branch, create it as [references/code-branch.md](references/code-branch.md) **Creating** says (from the into branch, carrying uncommitted changes only when HEAD is that branch).

If `<name>` already exists: `git checkout <name>` (do not `-B`, do not reset).

Never `git push`. Never create a PR. Never commit as part of this skill.

Then continue the parent skill on the new branch (write spec, or start the worker).

## Build on a spec-only branch

If they start implement / build-tasks while **on `spec/<slug>`**:

Stop. Do not write application code on a specify-only branch.

Offer:

1. Wait until `spec/<slug>` is on the default branch, then `/crav1-create-feature-branch` → `feat/<slug>` (Recommended)
2. Convert: rename/check out `feat/<slug>` from here and treat it as the one-branch flow (spec+build together)
3. Stay and specify more (no code)

## Spec-first (after plan)

When `/crav1-plan-from-spec` has written `plan.md` / `tasks.md` on `spec/<slug>` (or they chose specify-only earlier):

- On `spec/<slug>`: `Next: /crav1-open-pr, because this specify-only branch is not on the default branch yet.` Add the Uncommitted line when spec files are not committed. Do not start build on that branch. Do not list the feat branch; it waits until this pull request has merged.
- On `feat/<slug>`: skip this list. Implement on the same branch when they ask. Do not start it here.

If they planned on `feat/<slug>` (one-branch default), skip spec-first. Implement on the same branch.

## Hard rules

- Implementation code is never built on a base branch (1.99.0, [references/code-branch.md](references/code-branch.md)); no Stay on a base.
- Prompt; never silent checkout. A task's named branch comes first, marked (Recommended); it is never created from default without asking.
- `feat/<slug>` is the default one-branch flow. `spec/<slug>` is the optional specify-then-build split.
- No push, no PR, no `git commit` in this skill.
- Do not throw away uncommitted work.
- Do not create branches in an empty repo with no commits.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
