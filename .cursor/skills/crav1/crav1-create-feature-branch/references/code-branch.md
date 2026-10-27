# Code branch guard (1.99.0)

Implementation code is never written or committed on a base branch. Every skill that writes or commits implementation code follows this file before the first code edit and before every commit: the `/crav1-build-tasks` branches and their worker (`run.md`), `/crav1-build-features`, `/crav1-fix-build-gaps` and `/crav1-finalize-commit`. This is about where code goes, not where the spec lives.

## What counts as code

- **Implementation code** is any path that is not under `docs/` and is not a Markdown file at the repo root: product code, tests, config, pipelines and infra.
- **Spec and doc writes** are never guarded. They may stay on a base branch.
- **The specs repo is exempt.** A checkout that holds `docs/specs/`, has no `docs/system/repos.md` row for itself (by folder name or `origin` URL), and has a row for a repo checked out next to it (`../<Repo>` exists) is the source-of-truth (platform) repo: anything written there may stay on its base. When the specs and the code share one repo (a row names it, or the only row has no sibling checkout), only spec and doc writes are exempt.

## Detect

- **Current branch:** `git branch --show-current`. Empty means a detached HEAD.
- **Default branch:** `origin/HEAD`, else `gh repo view --json defaultBranchRef` when `gh` is logged in, else `main`, else `master`.
- **Into branch:** the branch's `(into …)` marker, else this repo's `Merges into` cell (`docs/system/repos.md`, also read-only from sibling checkouts, as `crav1-open-pr` `references/base.md` says), else the default branch.
- **Base branches:** the `Merges into` branch, the default branch, any of `main`, `master`, `develop`, `development`, `dev` and `integration` that exist locally or on `origin`, and every `release/*` branch.
- **Work branch:** an existing branch outside the base set whose name starts with `feat/`, `feature/`, `bug/`, `bugfix/`, `fix/` or `hotfix/`, or that a spec names (Match `Branch:`, a task's `(branch: X)`). `spec/<slug>` keeps its own rule: specify only, see **Build on a spec-only branch** in `SKILL.md`.
- **Other:** everything else, for example `chore/x`, `users/thomas/try` or a detached HEAD.

## What to do

- **On a work branch:** go ahead. No prompt.
- **On another branch:** offer a new branch but allow staying: `Create feat/<slug> from <into> (Recommended)`, `Use an existing branch`, `Stay on <current>`, `Stop`.
- **On a base branch:** never write code there and never offer Stay. One prompt, at most 4 options:
  1. `Create feat/<slug> from <into> (Recommended)`. When `feat/<slug>` exists: `Check out feat/<slug> (Recommended)`. `/crav1-fix-build-gaps` offers `fix/<slug>`. On `release/<x>`: `Create fix/<slug> from release/<x> (Recommended)`, then write `(into release/<x>)` on its Match `Branch:` entry.
  2. `Use an existing branch`: the repo's branches outside the base set (local and `origin`, no `spec/`), the spec's own branches first. Show up to 10 names in the prompt; with several, the pick is a follow-up list (at most 4 options, the last `Other name`), part of this prompt.
  3. `Other name`: they name the branch. A base name is refused; a missing branch is created from `<into>`.
  4. `Stop`: no code.

  After a pick that the spec doesn't list, write it on the spec's Match `Branch:` list in sorted place with `(into <into>)`, in the specs repo, not committed.

**Creating.** When HEAD is the into branch, `git switch -c <new>` carries any uncommitted changes over and commits nothing on the base. Otherwise `git switch -c <new> <into>` on a clean tree only; when uncommitted changes would block it, say so and stop. Checking out an existing branch also needs a clean tree. Never send a dirty base tree to `/crav1-finalize-commit` and never stash unless they ask.

**Task on a base.** A task `(branch: X)` where X is a base branch is `blocked: branch X is a base branch`. No switch.

**Headless.** With no person to answer, stop before any code edit, in one line: `Stopped: on base branch <b>. Implementation is never built on a base branch. Re-run with "new branch" or check out a feat/ or fix/ branch.` The choice word `new branch` answers the prompt with option 1. Starting `/crav1-build-features` is that answer for each slug.

**Worker.** The worker checks before its first edit and before every commit. On a base branch it returns `STATUS: blocked` with the reason `on base branch <b>`, even when the parent passed `branch: already-done`.
