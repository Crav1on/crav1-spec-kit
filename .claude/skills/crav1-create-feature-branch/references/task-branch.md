# Task branch (1.129.0)

Read this when a build prompt is for one task. The build map is the source of truth for that task's branch. Do not invent a name, and do not compute one by hand.

Run this and use the line it prints. It is the same name as that task's row in `docs/specs/<slug>/build-map.md`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

```text
<interpreter> <skill crav1-tasks-ready-to-build>/scripts/build_map.py docs/specs/<slug> --recommend T1
```

`--recommend` does not write the map. On that branch already, no prompt.

## How the name is chosen

The script checks, in order, and build-tasks uses that same result:

1. `(map: <branch>)` on the task. A repo prefix is ignored; the branch is the last word.
2. `(branch: <branch>)` on the task, the same way, when no `(map:)` is set.
3. The plan step's branch, `feat/<slug>-<words>`, when the task sits on a numbered Approach step.
4. A branch the task text names as `committed later on <branch>`, when the task is not on a step and has neither mark.
5. `feat/<slug>-<words>` from the task text.

A `(host setup)` task uses this same name. Do not offer an arbitrary new branch ahead of it.

## The card

One card. Do not put the permissions question on it. Permissions come after, on their own card (skill `crav1-build-tasks`, `references/tool-approvals.md`).

1. **`<name> (Recommended)`**. When the branch does not exist: **Create `<name>` from `<into>` (Recommended)**. When `<name>` is a sub-branch (the spec's Match `Branch:` list has a `(spec branch)` S, or `<name>` has an `(into S)` entry), the option is **Create `<name>` from S (Recommended)** instead, from local `S`, else `origin/S`, never a fetch (1.68.0). A `(host setup)` label says the script will live on this branch. When the task text names a different branch as `committed later on <branch>`, the label also says that branch is cut later.
2. **`feat/<slug>`**, when it is not already option 1.
3. **Use an existing branch**.
4. **Stop**.

Stay only off a base, in place of nothing on a base. No Stay on a base. A typed branch name on this card is the answer. There is no follow-up card to collect a name.

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
