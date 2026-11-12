# Heads-up before any write

When this command is not installed yet, the first jump downloads the release asset. A kit script's interpreter is `running-scripts.md`. On bash:

```bash
curl -fsSL -o crav1-update-kit.py https://github.com/Crav1on/crav1-spec-kit/releases/latest/download/crav1-update-kit.py
python3 crav1-update-kit.py detect
```

On Windows PowerShell 5.1, `curl` is an alias for `Invoke-WebRequest`, so the curl flags fail. On Windows, `python3` is often missing. Use `python` or `py`.

```powershell
Invoke-WebRequest -Uri https://github.com/Crav1on/crav1-spec-kit/releases/latest/download/crav1-update-kit.py -OutFile crav1-update-kit.py
python crav1-update-kit.py detect
```

Run `detect` and `resolve-target` first. They do not write. For a drop-in, also run `plan` (it does not write) so the card can name the files. Then stop and show this card. Pass `--yes` only after the user answers `yes` or `write only` in this run.

A checkout that is the kit source (`mode` is `kit-repo`) stops with the script's one line. Do not overlay the kit onto itself.

When the installed version is already the target, say so and stop. There is no card.

## What the card says

Question: Update the kit on `<branch>`?

The body, in this order:

1. You are on `<branch>`. Only this branch gets the new kit. Other branches stay on the old kit until you merge this branch into them. Say merge develop into the branch. Never rebase.
2. If this branch should not get the new kit, merge first or switch branch, then run the command again. This command does not switch branches.
3. Uncommitted changes: list `uncommitted_kit` and `uncommitted_project`, or say there are none. Kit files with local edits go through the three-way merge. Specs, walk-progress, build-progress, plans, notes, the build map, and other project files stay as they are and are not part of the kit commit.
4. Installed version, the file it was read from, and the target tag.
5. The plan counts: files to update, merge, add, or delete; templates left alone; each clash, with both sides.

Options, in this order:

- `yes, write and commit (Recommended)`. Writes the kit files and commits `Update CRAV1 kit vA to vB` on this branch. Does not push.
- `write only`. Writes the kit files and does not commit.
- `stop`. Writes nothing.

The card's free-text answer. Hint: `Type a path and keep or take, e.g. crav1.mdc: keep`. An item the answer does not mention keeps the recommendation, which is to keep the local edit for that clash. The same answer may name a different published tag, for example `to v1.129.0`. There is no separate option whose only job is to point somewhere else to type.

`stop` writes nothing. Do not pass `--yes`.

## Who may say yes

The user says yes in this run. An agent, a guild bot, or a yes from an earlier chat does not count. If this run has no user yes, show the card and stop.

## Push

The script cannot push. After the local commit, push only when the user's own message in this run already asked for the push. That message is the yes. Do not ask a second time. When they did not ask, do not push and do not add a push question.
