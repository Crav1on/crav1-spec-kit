# Choice words

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.95.1; the rules are unchanged.

Exact words for bots and scripted runs. There are no `--flags`.

- Commit or message: `commit` / `commit now` / `message only` (draft, show, done: the same as `copy`, no git commit).
- Base branch (1.99.0): `new branch` (create `feat/<slug>` from the into branch and commit there).
- Style: `crav1` / `git log`.
- Trailer hook: `strip trailers` / `keep trailers`.
- Pull: `pull` (1.81.0) runs the pull path with no commit first.

`commit now`, and `commit` typed in the invocation (1.76.1): draft, show the paste blocks, then commit with no choice question. When `agent-tools/` or build output is in the file set, warn and offer the normal choices instead. On a base branch with implementation code staged (1.99.0), ask the base-branch prompt instead ([base-branch.md](base-branch.md)); `new branch` answers it.

When the invocation contains one of these words (for example `/crav1-finalize-commit commit`), take that choice and do not ask. This holds for a person, a bot, or a headless run.
