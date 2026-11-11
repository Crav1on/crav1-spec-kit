# Opening another kit skill

A kit skill with `disable-model-invocation: true` is command-only. It runs when a person types its slash command. Since 1.88.0 that is the usual frontmatter. 1.134.0 keeps it.

When this skill runs another kit skill, open that skill's file with the file-read tool and follow it. Do not start it as a slash command or with a skill tool. If a command or skill start is refused because the skill is command-only, open the file instead and continue. That refusal is never a reason to stop. In `/crav1-tighten-and-plan-ready-to-build`, that refusal is never a reason to stop the walk.

A `Command:` line inside the file you opened is the command a person types to start that skill. You already opened the file. Do not start that command again.

A `Next:` line that names a command is not a start. When this skill says not to run that command, do not open its file. A refused start is expected. Continue this run.

## The file path

The path is from this skill's folder, the folder that contains the running `SKILL.md`. A `references/` file uses that same folder, not its own directory.

`../crav1-<name>/SKILL.md`

A file inside that skill:

`../crav1-<name>/references/<file>.md`

`../crav1-<name>/branches/<branch>/BRANCH.md`

That relative path is the installed file in every layout, because the skills are siblings:

- Claude Code project drop-in: `.claude/skills/crav1-<name>/SKILL.md`
- Claude Code user scope: `~/.claude/skills/crav1-<name>/SKILL.md`
- Cursor drop-in: `.cursor/skills/crav1/crav1-<name>/SKILL.md`
- Cursor plugin: `skills/crav1-<name>/SKILL.md` inside the installed `crav1` plugin folder (local install: `~/.cursor/plugins/local/crav1/skills/crav1-<name>/SKILL.md`)

Open the sibling path. Do not search the workspace for the skill. Do not fetch it from the web.

The step that runs the skill names the exact path, for example `../crav1-review-architecture/SKILL.md` for the orders-api spec walk. Follow only the section that step names when it names one.
