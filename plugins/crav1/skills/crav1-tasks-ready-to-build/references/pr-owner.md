# PR owner (1.177.1)

A merge-list line that says `owner not recorded` means neither the kit's records nor the pull request's own host named who opened it. The ready check already asked that host read-only (`gh` or `az`, only the one the records name) and recorded any name it found.

Ask the user once who opened PR <n>. Record the answer with `<interpreter> -X utf8 <skill crav1-tighten-and-plan-ready-to-build>/scripts/walk_progress.py pr-author --root <spec-folder> --pr <n> --name "<who>"`, which writes `PR author: <who>` in that pull request's build-progress file. Never ask them to edit a spec file. When they do not know, leave it and go on.
