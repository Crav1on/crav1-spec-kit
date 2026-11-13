# Dirty tree

Read only when `SKILL.md` says the working tree is dirty. Do not open this file on a clean tree. The rules are unchanged.

Working tree dirty except `agent-tools/` → **do not checkout**. On a base branch, offer to carry the changes onto `feat/<slug>` with `git switch -c` when HEAD is the into branch; never send them to `/crav1-finalize-commit` on a base. Otherwise they commit on their work branch or clean it. Wait. Never stash unless they ask.
