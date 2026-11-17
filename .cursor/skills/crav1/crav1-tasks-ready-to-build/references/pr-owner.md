# PR owner and code repo (1.177.1, 1.177.2, 1.178.0, 1.179.0)

## Repo first (1.178.0)

The repo question always comes first. Once the kit knows which code repo a pull request is in, one read-only lookup on that host (`gh` or `az`, only the one the repo names, run by its full path with no prompts; 20-second timeout for `az`, 8 seconds for `gh`, or `CRAV1_HOST_TIMEOUT`) gives both who opened it and whether it merged. The ready check records the owner as `PR author:` and a merge as a merge result in that same run. Ask who opened a pull request only when its repo is known, the host answered, and it still named no one. The order is repo, then host, then owner: the `--full` JSON says which comes first in `ask_first` (`code-repo`, `host`, `pr-author`, or null).

## Code repo (1.177.2)

`Waiting: PR <n>: code repo not recorded, so the host was not asked whether it merged.` means no `Code repo:` line names where the pull request lives and `docs/system/repos.md` has zero or several rows. The `--full` JSON lists them under `code_repo_unknown`. Its merge-list line can also say `owner not recorded`; ask for the repo, not the owner.

Ask the user once which repo the pull request is in, with one question for all the listed pull requests when they are on the same repo. Offer the `docs/system/repos.md` rows as choices: `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py code-repo --root <spec-folder> --pr <n>` lists them. Record the answer with the same command and `--repo <name-or-url>`, which writes `Code repo: <url>` in that pull request's build-progress file. When they do not know, leave it and go on.

A merged or completed pull request gets a merge result in its build-progress file, its tasks count as done, and it leaves the merge list in that same run. `Waiting: PR <n> was closed without merging; its tasks are not done.` means the host says it was closed or abandoned; nothing is recorded.

## Host not reached (1.179.0)

When the pull request's host is known but its CLI could not be read, the ready check says why in **Catch up first**, one label on its own line above the command that fixes it, then `Run the ready check again:` above `/crav1-tasks-ready-to-build <slug>`. For example `Azure DevOps was not reached for PR 71 and PR 73: not signed in. Sign in to Azure DevOps:` above `az login`, or `... the azure-devops extension is missing. Add the Azure DevOps extension:` above `az extension add --name azure-devops`. Its merge-list line says `owner unknown: Azure DevOps not reached` instead of `owner not recorded`.

The `--full` JSON lists these pull requests under `host_unread`, each with `pr`, `branch`, `host`, `error` and `detail`, and `ask_first` is `host`. The error is one of `cli-missing`, `cli-not-runnable`, `timeout`, `not-signed-in`, `extension-missing`, `not-found`, `bad-output`, `unknown-status` or `host-error`. Do not ask who opened these pull requests: they are left out of `owner_unknown`. Show the fix, and run the ready check again once the user has run it. Ask who opened one only when the user says they cannot fix the host CLI; `pr-author` then returns `status: host-unread` with the reason, the fix and the `choices`.

## Owner (1.177.1)

A merge-list line that says `owner not recorded`, for a pull request whose repo is known, means neither the kit's records nor the pull request's own host named who opened it. The `--full` JSON lists these under `owner_unknown`.

Ask the user once who opened PR <n>. Offer the names the kit already knows as choices, then `Don't know`: `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py pr-author --root <spec-folder> --pr <n>` asks the host, and when the host names no one it lists them under `choices` (people in `claims.md`, PR notes' `author:`, build-progress `PR author:` and `Opened by:` lines, and since 1.179.0 the people open questions wait on; never a team or organisation, and never a literal `other`, because the question's own Other field covers that). The `--full` JSON has the same list as `owner_choices`. Record the answer with the same command and `--name "<who>"`, which writes `PR author: <who>` in that pull request's own build-progress file, picked by branch (1.179.0). The reply's `commit` names that file: tell the user to commit it with the specs so the answer is kept. When several files name the pull request the status is `ambiguous`; ask which branch it is on and pass `--branch`. `code-repo --repo` works the same way. On `Don't know`, leave it.

## Run the check again (1.178.0, 1.179.0)

After any answer is recorded (repo or owner), and after the user runs a host fix, run the ready check again in this same run (step 4 of the skill) and print the new reply, so the merge list and Run next show what the host said. The `rerun` field exists only in the `pr-author` and `code-repo` answers, not in the ready check's own JSON. Do not end with the earlier reply, and never say the earlier steps still stand. Never ask the user to edit a spec file.
