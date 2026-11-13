# Permission block

Read this when a live command was refused, or when the next lines might say the user's yes is missing.

A live command is the `apply` of a `(Runs live)` task, or any other command this run was about to run because the user already said yes.

Run `scripts/permission_block.py` (this skill). Pick the interpreter as `crav1-docs/reference/running-scripts.md` says.

- `--user-yes yes` when the user said yes in this run, or the task line has `(live yes: …)`. `--user-yes no` otherwise.
- `--permission-refused yes` when the coding assistant's own permission check refused the command, for example as modifying shared resources. That check is not the user's yes.
- `--command` is the exact command that was refused.
- `--rerun` is the build step to run after that command has run. Here it is `/crav1-build-tasks T3`. When `/crav1-build-walk` is the running skill, it is `/crav1-build-walk`.
- `--task` is `T#` plus the short name when one task is in view.

Print the script's `lines`, in order. Do not add a line the script does not print.

`yes-missing` means the yes is not on record. Waiting says that. The task stays unticked. A named person's missing yes is still `needs_yes`, and skill `crav1-build-tasks`, `references/approval-needed.md` still applies. Do not use the permission-refused lines for that.

`permission-refused` means the yes is on record and the assistant's permission check blocked the command. Waiting says both of those. It does not say the yes is missing. The offer is only the two lines: the user runs that exact command, or allows that one command and reruns. Next names the rerun of the build step after the command has run. The task stays unticked. Do not return `needs_yes`. Do not suggest working around the check. Do not try a different command, a second tool, or a changed flag.

`run` means the command may proceed. This file does not apply.
