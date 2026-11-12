# Task branch (1.140.0)

Read this when a build prompt is for one task. Do not invent a name, and do not compute one by hand.

Run this and use the first line it prints. That line is the branch. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

```text
<interpreter> <skill crav1-tasks-ready-to-build>/scripts/build_map.py docs/specs/<slug> --recommend T1
```

`--recommend` does not write the map. On that branch already, no prompt.

The later lines are `source: task line`, `source: build map`, or `source: new`. `from: develop` is present when the task line states a base. `because:` is one plain line when a merged or deleted branch was skipped, for example `feat/orders-one-commit-cleanup-main is already merged`.

## How the name is chosen

The script checks, in order, and build-tasks uses that same result:

1. A branch named on the task's own line. `(map: <branch>)` wins, then `(branch: <branch>)`, then a `feat/…` name written in the sentence, then `committed later on <branch>`. A repo prefix on a mark is ignored; the branch is the last word. `from <base>` after that branch is its base, for example `feat/orders-host-setup-scripts from develop`.
2. The plan step's branch, `feat/<slug>-<words>`, when the task line names no branch.
3. `feat/<slug>-<words>` from the task text, when there is no step either.

A merged branch is not offered. Merged means the pull request is recorded merged (`(PR n)` and the word merged on the task line or its Match `Branch:` line), or the branch tip is already in that base or the default branch and the tips differ. A branch that only sits on the base, with no commits of its own, is still offered. A branch that was checked out here and is now gone locally and on every remote is not offered. A name that does not exist yet is offered so it can be created. No fetch.

When the task-line branch is merged or deleted, the step name is used if that name is still usable. When no candidate is usable, the offer is a new branch from the stated base. `source` is `new` and `because` says why.

A task whose own line records the merge stays on that branch in the map. `--recommend` does not print that branch, including for that task.

A `(host setup)` task uses this same name. Do not offer an arbitrary new branch ahead of it.

The map row follows the same order. When the row is the task-line branch and the plan step's name differs, the note is `Plan step names feat/orders-one-commit-cleanup-main; built on feat/orders-host-setup-scripts`. When a `(map:)` row is not the branch the task text names, the note stays `Task text names feat/orders-cicd; built on feat/orders-retry`.

## The card

One card. The recommended option is first. Do not put the permissions question on it. Permissions come after, on their own card (skill `crav1-build-tasks`, `references/tool-approvals.md`).

The question is `Which branch for T1?`

1. **`<name> (Recommended)`**. When the branch does not exist: **Create `<name>` from `<base> (Recommended)`**. `<base>` is the `from:` line when the script prints one, otherwise the into branch. When there is no `from:` and `<name>` is a sub-branch (the spec's Match `Branch:` list has a `(spec branch)` S, or `<name>` has an `(into S)` entry), the option is **Create `<name>` from S (Recommended)** instead, from local `S`, else `origin/S`, never a fetch (1.68.0). The description says where the name came from: `From the task line.`, `From the build map.`, or `New.`. When the script prints `because:`, that sentence replaces the description, for example `New, because feat/orders-one-commit-cleanup-main is already merged.` A `(host setup)` label says the script will live on this branch. When the task text names a different branch as `committed later on <branch>`, and that branch is not the offer, the label also says that branch is cut later.
2. **`feat/<slug>`**, when it is not already option 1.
3. **Use an existing branch**.
4. **Stop**.

Stay only off a base, in place of nothing on a base. No Stay on a base. A typed branch name is this card's free-text answer, hint `Type a branch name`, not its own option. Do not offer an option labelled `Other name`. There is no follow-up card to collect a name. The rule is `crav1-docs/reference/question-cards.md`.

A missing answer, or `continue` / `click` / `stop` on this card, is asked again. Use skill `crav1-build-tasks`, `scripts/ask_order.py`. Do not guess.

## After the pick

Only after they pick a name that is not Stop:

- On a base, create it as `references/code-branch.md` **Creating** says. A sub-branch is created from S, and `(into S)` is written on its Match `Branch:` line in sorted place (1.86.0). A headless run does not create it.
- When the name exists only as `origin/<name>`, `git checkout <name>` makes the local branch.
- When the name is a base branch, the task is `blocked: branch <name> is a base branch`. Never switch to it.
- A `(branch: <repo> <name>)` or `(map: <repo> <name>)` for another repo is not built here. Say which checkout it belongs to.
- Never create the branch from the default without this yes.

The choice word `new branch` still creates `feat/<slug>` from the into branch. It does not switch the recommended name. On a one-task run, when `feat/<slug>` is not the recommended name, the different-pick write below applies. On a range, `new branch` only leaves the base. Each task still uses its own recommended name, and those tasks are not rewritten onto `feat/<slug>`.

## A different pick

When the picked name is not the recommended name, write `(map: <picked>)` on that task line in the specs repo's `tasks.md`. Replace a `(map:)` already there. Do not commit. Say `Recorded (map: <picked>) on T1 in tasks.md. Not committed.` The next map row uses `<picked>`. Write nothing when the pick is the recommended name, or when they stop. This is the same kind of uncommitted specs-repo write as a Match `Branch:` line.

## A range

A range or all-tasks run switches to each task's recommended name on a clean tree. Starting the run is consent to use that name. It does not ask again when the branch exists. When the name exists nowhere, use this card once for that task. Do not invent a different recommended name, and do not create the branch without a yes.
