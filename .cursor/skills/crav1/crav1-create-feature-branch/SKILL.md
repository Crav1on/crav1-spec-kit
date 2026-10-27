---
name: crav1-create-feature-branch
description: >-
  Create or check out feat/<slug> (one branch for spec+build) or spec/<slug>
  (specify-only; build later on feat/<slug>). Use on brownfield specify or
  before implement on a base branch (main, develop, Merges into, release/*);
  no Stay there. Prompt; never silent checkout. Do not push. Do not open a PR.
disable-model-invocation: true
icon: git-branch
color: blue
---

# Feature branch

Get this change **off the default branch**. Prompt; do not silently `git checkout -b`. Do not push. Do not open a pull request unless they **explicitly** ask in this chat.

Other skills follow this file (drop-in: `.cursor/skills/crav1/crav1-create-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-create-feature-branch/SKILL.md`). Standalone command: `/crav1-create-feature-branch`.

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

- On a **base branch** (main, master, develop, the `Merges into` branch, `release/*`): **Create `feat/<slug>` from `<into>` (Recommended)**, **Use an existing branch**, **Other name**, **Stop**. No Stay on a base.
- On **another** branch (`chore/x`, detached HEAD): the same, with **Stay on `<current>`** in place of Other name.
- Headless with no person: stop before any code, unless the invocation has the choice word `new branch`.

Do not offer `spec/<slug>` on a build prompt.

**Task branch (1.64.0).** When the task being built ends with `(branch: X)` (or `(branch: <repo> X)` for the open repo):

- On X already: skip the prompt.
- Otherwise the Build prompt is **X (Recommended)** first, then `feat/<slug>`, **Other name** and **Stop** (Stay only off a base).
- When X is a base branch, the task is `blocked: branch X is a base branch`; never switch to it.
- When X exists only as `origin/X`, `git checkout X` makes the local branch.
- When X exists nowhere and the spec's Match `Branch:` list has a `(spec branch)` S, or X has an `(into S)` entry (1.68.0, setup 4 in `crav1-add-to-spec` `references/branches.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/branches.md`; plugin: sibling `skills/crav1-add-to-spec/references/branches.md`)): the prompt is **Create X from S (Recommended)**, then `feat/<slug>`, **Other name** and **Stop**. After that yes, create X from S (local `S`, else `origin/S`; never fetch) and write `(into S)` on X's Match `Branch:` line (adding the line in sorted place, 1.86.0). A headless run doesn't create X.
- When X exists nowhere otherwise, say so and offer `feat/<slug>` or **Other**. Never create X from the default branch without asking.
- A `(branch: <repo> X)` for another repo is not built here; say which checkout it belongs to.

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

- Next: `/crav1-finalize-commit` (no push), then **they** open a PR for this branch when they want the spec on default
- Do **not** start `/crav1-build-tasks` on `spec/<slug>`
- After that PR is merged (they say so): `/crav1-create-feature-branch` with this slug → `feat/<slug>` from default, then implement / build-tasks

If they planned on `feat/<slug>` (one-branch default), skip spec-first. Implement on the same branch.

## Hard rules

- Implementation code is never built on a base branch (1.99.0, [references/code-branch.md](references/code-branch.md)); no Stay on a base.
- Prompt; never silent checkout. A task's named branch comes first, marked (Recommended); it is never created from default without asking.
- `feat/<slug>` is the default one-branch flow. `spec/<slug>` is the optional specify-then-build split.
- No push, no PR, no `git commit` in this skill.
- Do not throw away uncommitted work.
- Do not create branches in an empty repo with no commits.
