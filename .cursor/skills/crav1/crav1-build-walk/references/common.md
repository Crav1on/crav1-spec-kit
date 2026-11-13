# Build walk, shared rules

Read this once, from `SKILL.md`. A step file does not repeat it.

The walk opens a step skill by its sibling path, for example `../crav1-build-tasks/SKILL.md`, and follows that file. It does not start a slash command. A command-only refusal is not a reason to stop. The rule is `crav1-docs/reference/open-skill-file.md`.

## One Next

For one branch in progress, the reply has exactly one next line. It is the line `scripts/build_walk.py next --json <file>` prints.

The step skill's own suggestion is not printed. That includes `/crav1-open-pr` after a build or a commit, and `/crav1-review-pr` after a pull request opens.

`Waiting:` is one line when a step is blocked or waits on a yes. `Uncommitted:` stays the commit reminder. It is not a second Next.

## Yes before a write

A step that writes, pushes, opens, or merges shows the action, then one card. `yes` (Recommended) does that action and then the walk opens the step skill. `stop` does not. There is no Edits option. A missing word is asked again. Do not guess.

The card that merges names the pull request number. That `yes` is the explicit ask `/crav1-merge-pr` requires. The walk opens `../crav1-merge-pr/SKILL.md` only after it.

Never rebase. A branch that is behind is fixed by merging the base into it, after `yes`.

## Script

`scripts/build_walk.py` in this skill. The interpreter is `crav1-docs/reference/running-scripts.md`. The kit repo wrapper is `scripts/build-walk.py`. Pass state as `--json`. The script does not push, open, merge, or run a live change.
