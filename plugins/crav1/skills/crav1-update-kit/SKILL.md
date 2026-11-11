---
name: crav1-update-kit
description: >-
  Use when the user asks to update the installed CRAV1 kit to a published
  release. Optional to vX.Y.Z. Default is the latest release tag. Never a
  branch or an open pull request.
icon: refresh-cw
color: blue
---

# Update the kit

Bring the installed CRAV1 kit on the current branch up to a published release. Command: `/crav1-update-kit`. Optional `to vX.Y.Z`. With no version, the target is the latest published release tag.

This is cross-cutting. It is not a starter option. It does not move work into a lane. It does not switch branches. A paused walk stays on this branch.

The script is `scripts/update_kit.py` in this skill's folder. The interpreter is [running-scripts.md](../crav1-docs/reference/running-scripts.md). Pass `--yes` only after the user says yes in this run. A yes from an agent, a guild bot, or an earlier chat does not count.

## Route

1. Read [references/heads-up.md](references/heads-up.md) every run, before any write.
2. Run `detect`, then `resolve-target`. A target that is not a published `vX.Y.Z` tag stops with the script's one-line reason. Do not offer another target.
3. Drop-in (`writes_kit_files` true): read [references/overlay.md](references/overlay.md) and follow it.
4. Plugin or user scope (`mode` is `plugin`): read [references/plugin.md](references/plugin.md) and follow it. Do not read the overlay page.
5. When the plan lists a migration id, read [references/migrations.md](references/migrations.md) after the kit files are replaced. When the list is empty, skip that page.

## Cards

The heads-up card is not skipped. A word in the opening message is not the yes. The yes is the user's answer after the branch is shown.

- Update on this branch: `yes, write and commit (Recommended)`, `write only`, or `stop`.
- A clash, on that same card's free-text answer: `keep` or `take`. An item with no answer keeps the local edit.
- A migration, only when the jump has one: `apply (Recommended)`, `leave`, or `stop`.

## Output

- Installed version, where it was read, and the target tag.
- The branch, and that only this branch changes.
- Files updated, merged, deleted, left alone, and any clash.
- The commit `Update CRAV1 kit vA to vB`, or why there is none.
- Tell the user to reload the window so the host loads the new skills.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.

After a commit, when the kit was already current, or when a plugin install needed no file write:

```text
Next: nothing needed now.
```

When this run wrote files and they are not committed, add one trailing line:

```text
Uncommitted: <n> files; commit with /crav1-finalize-commit when ready.
```

Do not push unless the user, in this run, already said to push. Do not add a push question when they did not. Do not run the next step.

## Hard rules

- Never write, commit, or push without the user's yes in this run.
- Never switch branches, and never rebase. Other branches stay on the old kit until this branch is merged into them.
- Never target `main`, a branch, a commit, or an open pull request.
- Never edit a spec, `walk-progress.md`, a plan, a task list, a note, a playbook, or a build map as part of the file replace.
- One commit, message `Update CRAV1 kit vA to vB`. The script does not push.
