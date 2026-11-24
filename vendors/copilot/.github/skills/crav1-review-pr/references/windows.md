# crav1-review-pr: windows

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Windows

On Windows, `git` may not be on `PATH`. Try `git`, then `C:\Program Files\Git\cmd\git.exe`. `az` may be `az.cmd`. Quote every `--query` value (`--query "user.name"`, 1.198.0); `cmd.exe` breaks on unquoted parentheses and braces. List and post Azure DevOps threads with `scripts/ado_threads.py` (1.172.0), not `az devops invoke … > file`, which writes the console code page.
