# PR owner and code repo (1.177.1, 1.177.2, 1.178.0)

## Repo first (1.178.0)

The repo question always comes first. Once the kit knows which code repo a pull request is in, one read-only lookup on that host (`gh` or `az`, only the one the repo names, 8-second timeout) gives both who opened it and whether it merged. The ready check records the owner as `PR author:` and a merge as a merge result in that same run. Ask who opened a pull request only when its repo is known and that lookup still named no one, for example when the host CLI is not signed in. The `--full` JSON says which question comes first in `ask_first` (`code-repo`, `pr-author`, or null).

## Code repo (1.177.2)

`Waiting: PR <n>: code repo not recorded, so the host was not asked whether it merged.` means no `Code repo:` line names where the pull request lives and `docs/system/repos.md` has zero or several rows. The `--full` JSON lists them under `code_repo_unknown`. Its merge-list line can also say `owner not recorded`; ask for the repo, not the owner.

Ask the user once which repo the pull request is in, with one question for all the listed pull requests when they are on the same repo. Offer the `docs/system/repos.md` rows as choices: `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py code-repo --root <spec-folder> --pr <n>` lists them. Record the answer with the same command and `--repo <name-or-url>`, which writes `Code repo: <url>` in that pull request's build-progress file. When they do not know, leave it and go on.

A merged or completed pull request gets a merge result in its build-progress file, its tasks count as done, and it leaves the merge list in that same run. `Waiting: PR <n> was closed without merging; its tasks are not done.` means the host says it was closed or abandoned; nothing is recorded.

## Owner (1.177.1)

A merge-list line that says `owner not recorded`, for a pull request whose repo is known, means neither the kit's records nor the pull request's own host named who opened it. The `--full` JSON lists these under `owner_unknown`.

Ask the user once who opened PR <n>. Offer the names the kit already knows as choices, then `Don't know`: `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py pr-author --root <spec-folder> --pr <n>` asks the host, and when the host names no one it lists them under `choices` (people in `claims.md`, PR notes' `author:`, and build-progress `PR author:`, `Opened by:` and `Owner:` lines). The `--full` JSON has the same list as `owner_choices`. Record the answer with the same command and `--name "<who>"`, which writes `PR author: <who>` in that pull request's build-progress file. On `Don't know`, leave it.

## Run the check again (1.178.0)

After any answer is recorded (repo or owner), run the ready check again in this same run (step 4 of the skill; the command's `rerun` field names it) and print the new reply, so the merge list and Run next show what the host said. Do not end with the earlier reply, and never say the earlier steps still stand. Never ask the user to edit a spec file.
