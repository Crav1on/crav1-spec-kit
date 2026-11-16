# PR owner and code repo (1.177.1, 1.177.2)

A merge-list line that says `owner not recorded` means neither the kit's records nor the pull request's own host named who opened it. The ready check already asked that host read-only (`gh` or `az`, only the one the records name) and recorded any name it found.

Ask the user once who opened PR <n>. Record the answer with `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py pr-author --root <spec-folder> --pr <n> --name "<who>"`, which writes `PR author: <who>` in that pull request's build-progress file. Never ask them to edit a spec file. When they do not know, leave it and go on.

## Code repo (1.177.2)

Before it reads anything else, the ready check asks each waiting pull request's own host, read-only, whether it merged. A merged or completed pull request gets a merge result in its build-progress file, its tasks count as done, and it leaves the merge list in that same run. `Waiting: PR <n> was closed without merging; its tasks are not done.` means the host says it was closed or abandoned; nothing is recorded.

`Waiting: PR <n>: code repo not recorded, so the host was not asked whether it merged.` means no `Code repo:` line names where the pull request lives and `docs/system/repos.md` has zero or several rows. The `--full` JSON lists them under `code_repo_unknown`.

Ask the user once which repo the pull request is in, with one question for all the listed pull requests when they are on the same repo. Offer the `docs/system/repos.md` rows as choices: `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py code-repo --root <spec-folder> --pr <n>` lists them. Record the answer with the same command and `--repo <name-or-url>`, which writes `Code repo: <url>` in that pull request's build-progress file. Then run the ready check again (step 4) and print the new reply, so the merge list and Run next show what merged. The owner, merge-state and bare-number lookups all use that line from then on. Never ask the user to edit a spec file. When they do not know, leave it and go on.
